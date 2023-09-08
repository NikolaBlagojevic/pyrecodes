#!/usr/bin/env python
#
#  paths.py
"""
Functions for paths and files.

.. versionchanged:: 1.0.0

	Removed ``relpath2``.
	Use :func:`domdf_python_tools.paths.relpath` instead.
"""
#
#  Copyright © 2018-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Parts of the docstrings, the PathPlus class and the DirComparator class
#  based on Python and its Documentation
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2021 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#
#  copytree based on https://stackoverflow.com/a/12514470/3092681
#      Copyright © 2012 atzz
#      Licensed under CC-BY-SA
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import contextlib
import filecmp
import fnmatch
import gzip
import json
import os
import pathlib
import shutil
import stat
import sys
import tempfile
import urllib.parse
from collections import defaultdict, deque
from operator import methodcaller
from typing import (
		IO,
		Any,
		Callable,
		ContextManager,
		Dict,
		Iterable,
		Iterator,
		List,
		Optional,
		Sequence,
		Type,
		TypeVar,
		Union
		)

# this package
from domdf_python_tools.compat import nullcontext
from domdf_python_tools.typing import JsonLibrary, PathLike

__all__ = [
		"append",
		"copytree",
		"delete",
		"maybe_make",
		"parent_path",
		"read",
		"relpath",
		"write",
		"clean_writer",
		"make_executable",
		"PathPlus",
		"PosixPathPlus",
		"WindowsPathPlus",
		"in_directory",
		"_P",
		"_PP",
		"traverse_to_file",
		"matchglob",
		"unwanted_dirs",
		"TemporaryPathPlus",
		"sort_paths",
		"DirComparator",
		"compare_dirs",
		]

NEWLINE_DEFAULT = type("NEWLINE_DEFAULT", (object, ), {"__repr__": lambda self: "NEWLINE_DEFAULT"})()

_P = TypeVar("_P", bound=pathlib.Path)
"""
.. versionadded:: 0.11.0

.. versionchanged:: 1.7.0  Now bound to :class:`pathlib.Path`.
"""

_PP = TypeVar("_PP", bound="PathPlus")
"""
.. versionadded:: 2.3.0
"""

unwanted_dirs = (
		".git",
		".hg",
		"venv",
		".venv",
		".mypy_cache",
		"__pycache__",
		".pytest_cache",
		".tox",
		".tox4",
		".nox",
		"__pypackages__",
		)
"""
A list of directories which will likely be unwanted when searching directory trees for files.

.. versionadded:: 2.3.0
.. versionchanged:: 2.9.0  Added ``.hg`` (`mercurial <https://www.mercurial-scm.org>`_)
.. versionchanged:: 3.0.0  Added ``__pypackages__`` (:pep:`582`)
.. versionchanged:: 3.2.0  Added ``.nox`` (https://nox.thea.codes/)
"""


def append(var: str, filename: PathLike, **kwargs) -> int:
	"""
	Append ``var`` to the file ``filename`` in the current directory.

	.. TODO:: make this the file in the given directory, by default the current directory

	:param var: The value to append to the file
	:param filename: The file to append to
	"""

	kwargs.setdefault("encoding", "UTF-8")

	with open(os.path.join(os.getcwd(), filename), 'a', **kwargs) as f:  # noqa: ENC001
		return f.write(var)


def copytree(
		src: PathLike,
		dst: PathLike,
		symlinks: bool = False,
		ignore: Optional[Callable] = None,
		) -> PathLike:
	"""
	Alternative to :func:`shutil.copytree` to support copying to a directory that already exists.

	Based on https://stackoverflow.com/a/12514470 by https://stackoverflow.com/users/23252/atzz

	In Python 3.8 and above :func:`shutil.copytree` takes a ``dirs_exist_ok`` argument,
	which has the same result.

	:param src: Source file to copy
	:param dst: Destination to copy file to
	:param symlinks: Whether to represent symbolic links in the source as symbolic
		links in the destination. If false or omitted, the contents and metadata
		of the linked files are copied to the new tree. When symlinks is false,
		if the file pointed by the symlink doesn't exist, an exception will be
		added in the list of errors raised in an Error exception at the end of
		the copy process. You can set the optional ignore_dangling_symlinks
		flag to true if you want to silence this exception. Notice that this
		option has no effect on platforms that don’t support :func:`os.symlink`.
	:param ignore: A callable that will receive as its arguments the source
		directory, and a list of its contents. The ignore callable will be
		called once for each directory that is copied. The callable must return
		a sequence of directory and file names relative to the current
		directory (i.e. a subset of the items in its second argument); these
		names will then be ignored in the copy process.
		:func:`shutil.ignore_patterns` can be used to create such a callable
		that ignores names based on
		glob-style patterns.
	"""

	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)

	return dst


def delete(filename: PathLike, **kwargs):
	"""
	Delete the file in the current directory.

	.. TODO:: make this the file in the given directory, by default the current directory

	:param filename: The file to delete
	"""

	os.remove(os.path.join(os.getcwd(), filename), **kwargs)


def maybe_make(directory: PathLike, mode: int = 0o777, parents: bool = False):
	"""
	Create a directory at the given path, but only if the directory does not already exist.

	.. attention::

		This will fail silently if a file with the same name already exists.
		This appears to be due to the behaviour of :func:`os.mkdir`.

	:param directory: Directory to create
	:param mode: Combined with the process's umask value to determine the file mode and access flags
	:param parents: If :py:obj:`False` (the default), a missing parent raises a :class:`FileNotFoundError`.
		If :py:obj:`True`, any missing parents of this path are created as needed; they are created with the
		default permissions without taking mode into account (mimicking the POSIX ``mkdir -p`` command).
	:no-default parents:

	.. versionchanged:: 1.6.0  Removed the ``'exist_ok'`` option, since it made no sense in this context.

	"""

	if not isinstance(directory, pathlib.Path):
		directory = pathlib.Path(directory)

	try:
		directory.mkdir(mode, parents, exist_ok=True)
	except FileExistsError:
		pass


def parent_path(path: PathLike) -> pathlib.Path:
	"""
	Returns the path of the parent directory for the given file or directory.

	:param path: Path to find the parent for

	:return: The parent directory
	"""

	if not isinstance(path, pathlib.Path):
		path = pathlib.Path(path)

	return path.parent


def read(filename: PathLike, **kwargs) -> str:
	"""
	Read a file in the current directory (in text mode).

	.. TODO:: make this the file in the given directory, by default the current directory

	:param filename: The file to read from.

	:return: The contents of the file.
	"""

	kwargs.setdefault("encoding", "UTF-8")

	with open(os.path.join(os.getcwd(), filename), **kwargs) as f:  # noqa: ENC001
		return f.read()


def relpath(path: PathLike, relative_to: Optional[PathLike] = None) -> pathlib.Path:
	"""
	Returns the path for the given file or directory relative to the given
	directory or, if that would require path traversal, returns the absolute path.

	:param path: Path to find the relative path for
	:param relative_to: The directory to find the path relative to.
		Defaults to the current directory.
	:no-default relative_to:
	"""  # noqa: D400

	if not isinstance(path, pathlib.Path):
		path = pathlib.Path(path)

	abs_path = path.absolute()

	if relative_to is None:
		relative_to = pathlib.Path().absolute()

	if not isinstance(relative_to, pathlib.Path):
		relative_to = pathlib.Path(relative_to)

	relative_to = relative_to.absolute()

	try:
		return abs_path.relative_to(relative_to)
	except ValueError:
		return abs_path


def write(var: str, filename: PathLike, **kwargs) -> None:
	"""
	Write a variable to file in the current directory.

	.. TODO:: make this the file in the given directory, by default the current directory

	:param var: The value to write to the file.
	:param filename: The file to write to.
	"""

	kwargs.setdefault("encoding", "UTF-8")

	with open(os.path.join(os.getcwd(), filename), 'w', **kwargs) as f:  # noqa: ENC001
		f.write(var)


def clean_writer(string: str, fp: IO) -> None:
	"""
	Write string to ``fp`` without trailing spaces.

	:param string:
	:param fp:
	"""

	# this package
	from domdf_python_tools.stringlist import StringList

	buffer = StringList(string)
	buffer.blankline(ensure_single=True)
	fp.write(str(buffer))


def make_executable(filename: PathLike) -> None:
	"""
	Make the given file executable.

	:param filename:
	"""

	if not isinstance(filename, pathlib.Path):
		filename = pathlib.Path(filename)

	st = os.stat(str(filename))
	os.chmod(str(filename), st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@contextlib.contextmanager
def in_directory(directory: PathLike):
	"""
	Context manager to change into the given directory for the
	duration of the ``with`` block.

	:param directory:
	"""  # noqa: D400

	oldwd = os.getcwd()
	try:
		os.chdir(str(directory))
		yield
	finally:
		os.chdir(oldwd)


class PathPlus(pathlib.Path):
	"""
	Subclass of :class:`pathlib.Path` with additional methods and a default encoding of UTF-8.

	Path represents a filesystem path but, unlike :class:`pathlib.PurePath`, also offers
	methods to do system calls on path objects.
	Depending on your system, instantiating a :class:`~.PathPlus` will return
	either a :class:`~.PosixPathPlus` or a :class:`~.WindowsPathPlus`. object.
	You can also instantiate a :class:`~.PosixPathPlus` or :class:`WindowsPath` directly,
	but cannot instantiate a :class:`~.WindowsPathPlus` on a POSIX system or vice versa.

	.. versionadded:: 0.3.8
	.. versionchanged:: 0.5.1  Defaults to Unix line endings (``LF``) on all platforms.
	"""

	__slots__ = ()

	if sys.version_info < (3, 11):
		_accessor = pathlib._normal_accessor  # type: ignore
	_closed = False

	def _init(self, *args, **kwargs):
		pass

	@classmethod
	def _from_parts(cls, args, init=True):
		return super()._from_parts(args)  # type: ignore

	def __new__(cls: Type[_PP], *args, **kwargs) -> _PP:  # noqa: D102
		if cls is PathPlus:
			cls = WindowsPathPlus if os.name == "nt" else PosixPathPlus  # type: ignore

		return super().__new__(cls, *args, **kwargs)

	def make_executable(self) -> None:
		"""
		Make the file executable.

		.. versionadded:: 0.3.8
		"""

		make_executable(self)

	def write_clean(
			self,
			string: str,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			):
		"""
		Write to the file without trailing whitespace, and with a newline at the end of the file.

		.. versionadded:: 0.3.8

		:param string:
		:param encoding: The encoding to write to the file in.
		:param errors:
		"""

		with self.open('w', encoding=encoding, errors=errors) as fp:
			clean_writer(string, fp)

	def maybe_make(
			self,
			mode: int = 0o777,
			parents: bool = False,
			):
		"""
		Create a directory at this path, but only if the directory does not already exist.

		.. versionadded:: 0.3.8

		:param mode: Combined with the process’ umask value to determine the file mode and access flags
		:param parents: If :py:obj:`False` (the default), a missing parent raises a :class:`FileNotFoundError`.
			If :py:obj:`True`, any missing parents of this path are created as needed; they are created with the
			default permissions without taking mode into account (mimicking the POSIX mkdir -p command).
		:no-default parents:

		.. versionchanged:: 1.6.0  Removed the ``'exist_ok'`` option, since it made no sense in this context.

		.. attention::

			This will fail silently if a file with the same name already exists.
			This appears to be due to the behaviour of :func:`os.mkdir`.

		"""

		try:
			self.mkdir(mode, parents, exist_ok=True)
		except FileExistsError:
			pass

	def append_text(
			self,
			string: str,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			):
		"""
		Open the file in text mode, append the given string to it, and close the file.

		.. versionadded:: 0.3.8

		:param string:
		:param encoding: The encoding to write to the file in.
		:param errors:
		"""

		with self.open('a', encoding=encoding, errors=errors) as fp:
			fp.write(string)

	def write_text(
			self,
			data: str,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			newline: Optional[str] = NEWLINE_DEFAULT,
			) -> int:
		"""
		Open the file in text mode, write to it, and close the file.

		.. versionadded:: 0.3.8

		:param data:
		:param encoding: The encoding to write to the file in.
		:param errors:
		:param newline:
		:default newline: `universal newlines <https://docs.python.org/3/glossary.html#term-universal-newlines>`__ for reading, Unix line endings (``LF``) for writing.

		.. versionchanged:: 3.1.0

			Added the ``newline`` argument to match Python 3.10.
			(see :github:pull:`22420 <python/cpython>`)
		"""

		if not isinstance(data, str):
			raise TypeError(f'data must be str, not {data.__class__.__name__}')

		with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
			return f.write(data)

	def write_lines(
			self,
			data: Iterable[str],
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			*,
			trailing_whitespace: bool = False
			) -> None:
		"""
		Write the given list of lines to the file without trailing whitespace.

		.. versionadded:: 0.5.0

		:param data:
		:param encoding: The encoding to write to the file in.
		:param errors:
		:param trailing_whitespace: If :py:obj:`True` trailing whitespace is preserved.

		.. versionchanged:: 2.4.0  Added the ``trailing_whitespace`` option.
		"""

		if trailing_whitespace:
			data = list(data)
			if data[-1].strip():
				data.append('')

			self.write_text('\n'.join(data), encoding=encoding, errors=errors)
		else:
			self.write_clean('\n'.join(data), encoding=encoding, errors=errors)

	def read_text(
			self,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			) -> str:
		"""
		Open the file in text mode, read it, and close the file.

		.. versionadded:: 0.3.8

		:param encoding: The encoding to write to the file in.
		:param errors:

		:return: The content of the file.
		"""

		return super().read_text(encoding=encoding, errors=errors)

	def read_lines(
			self,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			) -> List[str]:
		"""
		Open the file in text mode, return a list containing the lines in the file,
		and close the file.

		.. versionadded:: 0.5.0

		:param encoding: The encoding to write to the file in.
		:param errors:

		:return: The content of the file.
		"""  # noqa: D400

		return self.read_text(encoding=encoding, errors=errors).split('\n')

	def open(  # type: ignore  # noqa: A003  # pylint: disable=redefined-builtin
		self,
		mode: str = 'r',
		buffering: int = -1,
		encoding: Optional[str] = "UTF-8",
		errors: Optional[str] = None,
		newline: Optional[str] = NEWLINE_DEFAULT,
		) -> IO[Any]:
		"""
		Open the file pointed by this path and return a file object, as
		the built-in :func:`open` function does.

		.. versionadded:: 0.3.8

		:param mode: The mode to open the file in.
		:default mode: ``'r'`` (read only)
		:param buffering:
		:param encoding:
		:param errors:
		:param newline:
		:default newline: `universal newlines <https://docs.python.org/3/glossary.html#term-universal-newlines>`__ for reading, Unix line endings (``LF``) for writing.

		:rtype:

		.. versionchanged:: 0.5.1

			Defaults to Unix line endings (``LF``) on all platforms.
		"""  # noqa: D400

		if 'b' in mode:
			encoding = None
			newline = None

		if newline is NEWLINE_DEFAULT:
			if 'r' in mode:
				newline = None
			else:
				newline = '\n'

		return super().open(
				mode,
				buffering=buffering,
				encoding=encoding,
				errors=errors,
				newline=newline,
				)

	def dump_json(
			self,
			data: Any,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			json_library: JsonLibrary = json,  # type: ignore
			*,
			compress: bool = False,
			**kwargs,
			) -> None:
		r"""
		Dump ``data`` to the file as JSON.

		.. versionadded:: 0.5.0

		:param data: The object to serialise to JSON.
		:param encoding: The encoding to write to the file in.
		:param errors:
		:param json_library: The JSON serialisation library to use.
		:default json_library: :mod:`json`
		:param compress: Whether to compress the JSON file using gzip.
		:param \*\*kwargs: Keyword arguments to pass to the JSON serialisation function.

		:rtype:

		.. versionchanged:: 1.0.0

			Now uses :meth:`PathPlus.write_clean <domdf_python_tools.paths.PathPlus.write_clean>`
			rather than :meth:`PathPlus.write_text <domdf_python_tools.paths.PathPlus.write_text>`,
			and as a result returns :py:obj:`None` rather than :class:`int`.

		.. versionchanged:: 1.9.0  Added the ``compress`` keyword-only argument.
		"""

		if compress:
			with gzip.open(self, mode="wt", encoding=encoding, errors=errors) as fp:
				fp.write(json_library.dumps(data, **kwargs))

		else:
			self.write_clean(
					json_library.dumps(data, **kwargs),
					encoding=encoding,
					errors=errors,
					)

	def load_json(
			self,
			encoding: Optional[str] = "UTF-8",
			errors: Optional[str] = None,
			json_library: JsonLibrary = json,  # type: ignore
			*,
			decompress: bool = False,
			**kwargs,
			) -> Any:
		r"""
		Load JSON data from the file.

		.. versionadded:: 0.5.0

		:param encoding: The encoding to write to the file in.
		:param errors:
		:param json_library: The JSON serialisation library to use.
		:default json_library: :mod:`json`
		:param decompress: Whether to decompress the JSON file using gzip.
			Will raise an exception if the file is not compressed.
		:param \*\*kwargs: Keyword arguments to pass to the JSON deserialisation function.

		:return: The deserialised JSON data.

		.. versionchanged:: 1.9.0  Added the ``compress`` keyword-only argument.
		"""

		if decompress:
			with gzip.open(self, mode="rt", encoding=encoding, errors=errors) as fp:
				content = fp.read()
		else:
			content = self.read_text(encoding=encoding, errors=errors)

		return json_library.loads(
				content,
				**kwargs,
				)

	if sys.version_info < (3, 10):  # pragma: no cover (py310+)

		def is_mount(self) -> bool:
			"""
			Check if this path is a POSIX mount point.

			.. versionadded:: 0.3.8 for Python 3.7 and above
			.. versionadded:: 0.11.0 for Python 3.6
			"""

			# Need to exist and be a dir
			if not self.exists() or not self.is_dir():
				return False

			# https://github.com/python/cpython/pull/18839/files
			try:
				parent_dev = self.parent.stat().st_dev
			except OSError:
				return False

			dev = self.stat().st_dev
			if dev != parent_dev:
				return True
			ino = self.stat().st_ino
			parent_ino = self.parent.stat().st_ino
			return ino == parent_ino

	if sys.version_info < (3, 8):  # pragma: no cover (py38+)

		def rename(self: _P, target: Union[str, pathlib.PurePath]) -> _P:  # type: ignore
			"""
			Rename this path to the target path.

			The target path may be absolute or relative. Relative paths are
			interpreted relative to the current working directory, *not* the
			directory of the Path object.

			.. versionadded:: 0.3.8 for Python 3.8 and above
			.. versionadded:: 0.11.0 for Python 3.6 and Python 3.7

			:param target:

			:returns: The new Path instance pointing to the target path.
			"""

			os.rename(self, target)
			return self.__class__(target)

		def replace(self: _P, target: Union[str, pathlib.PurePath]) -> _P:  # type: ignore
			"""
			Rename this path to the target path, overwriting if that path exists.

			The target path may be absolute or relative. Relative paths are
			interpreted relative to the current working directory, *not* the
			directory of the Path object.

			Returns the new Path instance pointing to the target path.

			.. versionadded:: 0.3.8 for Python 3.8 and above
			.. versionadded:: 0.11.0 for Python 3.6 and Python 3.7

			:param target:

			:returns: The new Path instance pointing to the target path.
			"""

			os.replace(self, target)
			return self.__class__(target)

		def unlink(self, missing_ok: bool = False) -> None:
			"""
			Remove this file or link.

			If the path is a directory, use :meth:`~domdf_python_tools.paths.PathPlus.rmdir()` instead.

			.. versionadded:: 0.3.8 for Python 3.8 and above
			.. versionadded:: 0.11.0 for Python 3.6 and Python 3.7
			"""

			try:
				os.unlink(self)
			except FileNotFoundError:
				if not missing_ok:
					raise

	def __enter__(self):
		return self

	def __exit__(self, t, v, tb):
		# https://bugs.python.org/issue39682
		# In previous versions of pathlib, this method marked this path as
		# closed; subsequent attempts to perform I/O would raise an IOError.
		# This functionality was never documented, and had the effect of
		# making Path objects mutable, contrary to PEP 428. In Python 3.9 the
		# _closed attribute was removed, and this method made a no-op.
		# This method and __enter__()/__exit__() should be deprecated and
		# removed in the future.
		pass

	if sys.version_info < (3, 9):  # pragma: no cover (py39+)

		def is_relative_to(self, *other: Union[str, os.PathLike]) -> bool:
			r"""
			Returns whether the path is relative to another path.

			.. versionadded:: 0.3.8 for Python 3.9 and above.
			.. latex:vspace:: -10px
			.. versionadded:: 1.4.0 for Python 3.6 and Python 3.7.
			.. latex:vspace:: -10px

			:param \*other:

			.. latex:vspace:: -20px

			:rtype:

			.. latex:vspace:: -20px
			"""

			try:
				self.relative_to(*other)
				return True
			except ValueError:
				return False

	def abspath(self) -> "PathPlus":
		"""
		Return the absolute version of the path.

		.. versionadded:: 1.3.0
		"""

		return self.__class__(os.path.abspath(self))

	def iterchildren(
			self: _PP,
			exclude_dirs: Optional[Iterable[str]] = unwanted_dirs,
			match: Optional[str] = None,
			matchcase: bool = True,
			) -> Iterator[_PP]:
		"""
		Returns an iterator over all children (files and directories) of the current path object.

		.. versionadded:: 2.3.0

		:param exclude_dirs: A list of directory names which should be excluded from the output,
			together with their children.
		:param match: A pattern to match filenames against.
			The pattern should be in the format taken by :func:`~.matchglob`.
		:param matchcase: Whether the filename's case should match the pattern.

		:rtype:

		.. versionchanged:: 2.5.0  Added the ``matchcase`` option.
		"""

		if not self.abspath().is_dir():
			return

		if exclude_dirs is None:
			exclude_dirs = ()

		if match and not os.path.isabs(match) and self.is_absolute():
			match = (self / match).as_posix()

		file: _PP
		for file in self.iterdir():
			parts = file.parts
			if any(d in parts for d in exclude_dirs):
				continue

			if match is None or (match is not None and matchglob(file, match, matchcase)):
				yield file

			if file.is_dir():
				yield from file.iterchildren(exclude_dirs, match)

	@classmethod
	def from_uri(cls: Type[_PP], uri: str) -> _PP:
		"""
		Construct a :class:`~.PathPlus` from a ``file`` URI returned by :meth:`pathlib.PurePath.as_uri`.

		.. versionadded:: 2.9.0

		:param uri:

		:rtype: :class:`~.PathPlus`
		"""

		parseresult = urllib.parse.urlparse(uri)

		if parseresult.scheme != "file":
			raise ValueError(f"Unsupported URI scheme {parseresult.scheme!r}")
		if parseresult.params or parseresult.query or parseresult.fragment:
			raise ValueError("Malformed file URI")

		if sys.platform == "win32":  # pragma: no cover (!Windows)

			if parseresult.netloc:
				path = ''.join([
						"//",
						urllib.parse.unquote_to_bytes(parseresult.netloc).decode("UTF-8"),
						urllib.parse.unquote_to_bytes(parseresult.path).decode("UTF-8"),
						])
			else:
				path = urllib.parse.unquote_to_bytes(parseresult.path).decode("UTF-8").lstrip('/')

		else:  # pragma: no cover (Windows)
			if parseresult.netloc:
				raise ValueError("Malformed file URI")

			path = urllib.parse.unquote_to_bytes(parseresult.path).decode("UTF-8")

		return cls(path)

	def move(self: _PP, dst: PathLike) -> _PP:
		"""
		Recursively move ``self`` to ``dst``.

		``self`` may be a file or a directory.

		See :func:`shutil.move` for more details.

		.. versionadded:: 3.2.0

		:param dst:

		:returns: The new location of ``self``.
		:rtype: :class:`~.PathPlus`
		"""

		new_path = shutil.move(os.fspath(self), dst)
		return self.__class__(new_path)

	def stream(self, chunk_size: int = 1024) -> Iterator[bytes]:
		"""
		Stream the file in ``chunk_size`` sized chunks.

		:param chunk_size: The chunk size, in bytes

		.. versionadded:: 3.2.0
		"""

		with self.open("rb") as fp:
			while True:
				chunk = fp.read(chunk_size)
				if not chunk:
					break
				yield chunk


class PosixPathPlus(PathPlus, pathlib.PurePosixPath):
	"""
	:class:`~.PathPlus` subclass for non-Windows systems.

	On a POSIX system, instantiating a :class:`~.PathPlus` object should return an instance of this class.

	.. versionadded:: 0.3.8
	"""

	__slots__ = ()


class WindowsPathPlus(PathPlus, pathlib.PureWindowsPath):
	"""
	:class:`~.PathPlus` subclass for Windows systems.

	On a Windows system, instantiating a :class:`~.PathPlus`  object should return an instance of this class.

	.. versionadded:: 0.3.8

	.. autoclasssumm:: WindowsPathPlus
		:autosummary-sections: ;;

	The following methods are unsupported on Windows:

	* :meth:`~pathlib.Path.group`
	* :meth:`~pathlib.Path.is_mount`
	* :meth:`~pathlib.Path.owner`
	"""

	__slots__ = ()

	def owner(self):  # pragma: no cover
		"""
		Unsupported on Windows.
		"""

		raise NotImplementedError("Path.owner() is unsupported on this system")

	def group(self):  # pragma: no cover
		"""
		Unsupported on Windows.
		"""

		raise NotImplementedError("Path.group() is unsupported on this system")

	def is_mount(self):  # pragma: no cover
		"""
		Unsupported on Windows.
		"""

		raise NotImplementedError("Path.is_mount() is unsupported on this system")


def traverse_to_file(base_directory: _P, *filename: PathLike, height: int = -1) -> _P:
	r"""
	Traverse the parents of the given directory until the desired file is found.

	.. versionadded:: 1.7.0

	:param base_directory: The directory to start searching from
	:param \*filename: The filename(s) to search for
	:param height: The maximum height to traverse to.
	"""

	if not filename:
		raise TypeError("traverse_to_file expected 2 or more arguments, got 1")

	for level, directory in enumerate((base_directory, *base_directory.parents)):
		if height > 0 and ((level - 1) > height):
			break

		for file in filename:
			if (directory / file).is_file():
				return directory

	raise FileNotFoundError(f"'{filename[0]!s}' not found in {base_directory}")


def matchglob(filename: PathLike, pattern: str, matchcase: bool = True) -> bool:
	"""
	Given a filename and a glob pattern, return whether the filename matches the glob.

	.. versionadded:: 2.3.0

	:param filename:
	:param pattern: A pattern structured like a filesystem path, where each element consists of the glob syntax.
		Each element is matched by :mod:`fnmatch`.
		The special element ``**`` matches zero or more files or directories.
	:param matchcase: Whether the filename's case should match the pattern.

	:rtype:

	.. seealso:: :wikipedia:`Glob (programming)#Syntax` on Wikipedia
	.. versionchanged:: 2.5.0  Added the ``matchcase`` option.
	"""

	match_func = fnmatch.fnmatchcase if matchcase else fnmatch.fnmatch

	filename = PathPlus(filename)

	pattern_parts = deque(pathlib.PurePath(pattern).parts)
	filename_parts = deque(filename.parts)

	if not pattern_parts[-1]:
		pattern_parts.pop()

	while True:
		if not pattern_parts and not filename_parts:
			return True
		elif not pattern_parts and filename_parts:
			# Pattern exhausted but still filename elements
			return False

		pattern_part = pattern_parts.popleft()

		if pattern_part == "**" and not filename_parts:
			return True
		else:
			filename_part = filename_parts.popleft()

		if pattern_part == "**":
			if not pattern_parts:
				return True

			while pattern_part == "**":
				if not pattern_parts:
					return True

				pattern_part = pattern_parts.popleft()

			if pattern_parts and not filename_parts:
				# Filename must match everything after **
				return False

			if match_func(filename_part, pattern_part):
				continue
			else:
				while not match_func(filename_part, pattern_part):
					if not filename_parts:
						return False

					filename_part = filename_parts.popleft()

		elif match_func(filename_part, pattern_part):
			continue
		else:
			return False


class TemporaryPathPlus(tempfile.TemporaryDirectory):
	"""
	Securely creates a temporary directory using the same rules as :func:`tempfile.mkdtemp`.
	The resulting object can be used as a context manager.
	On completion of the context or destruction of the object
	the newly created temporary directory and all its contents are removed from the filesystem.

	Unlike :func:`tempfile.TemporaryDirectory` this class is based around a :class:`~.PathPlus` object.

	.. versionadded:: 2.4.0
	.. autosummary-widths:: 6/16
	"""

	name: PathPlus
	"""
	The temporary directory itself.

	This will be assigned to the target of the :keyword:`as` clause if the :class:`~.TemporaryPathPlus`
	is used as a context manager.
	"""

	def __init__(
			self,
			suffix: Optional[str] = None,
			prefix: Optional[str] = None,
			dir: Optional[PathLike] = None,  # noqa: A002  # pylint: disable=redefined-builtin
			) -> None:

		super().__init__(suffix, prefix, dir)
		self.name = PathPlus(self.name)

	def cleanup(self) -> None:
		"""
		Cleanup the temporary directory by removing it and its contents.

		If the :class:`~.TemporaryPathPlus` is used as a context manager
		this is called when leaving the :keyword:`with` block.
		"""

		context: ContextManager

		if sys.platform == "win32":  # pragma: no cover (!Windows)
			context = contextlib.suppress(PermissionError, NotADirectoryError)
		else:  # pragma: no cover (Windows)
			context = nullcontext()

		with context:
			super().cleanup()

	def __enter__(self) -> PathPlus:
		return self.name


def sort_paths(*paths: PathLike) -> List[PathPlus]:
	"""
	Sort the ``paths`` by directory, then by file.

	.. versionadded:: 2.6.0

	:param paths:
	"""

	directories: Dict[str, List[PathPlus]] = defaultdict(list)
	local_contents: List[PathPlus] = []
	files: List[PathPlus] = []

	for obj in [PathPlus(path) for path in paths]:
		if len(obj.parts) > 1:
			key = obj.parts[0]
			directories[key].append(obj)
		else:
			local_contents.append(obj)

	# sort directories
	directories = {directory: directories[directory] for directory in sorted(directories.keys())}

	for directory, contents in directories.items():
		contents = [path.relative_to(directory) for path in contents]
		files.extend(PathPlus(directory) / path for path in sort_paths(*contents))

	return files + sorted(local_contents, key=methodcaller("as_posix"))


class DirComparator(filecmp.dircmp):
	r"""
	Compare the content of ``a`` and ``a``.

	In contrast with :class:`filecmp.dircmp`, this
	subclass compares the content of files with the same path.

	.. versionadded:: 2.7.0

	:param a: The "left" directory to compare.
	:param b: The "right" directory to compare.
	:param ignore: A list of names to ignore.
	:default ignore: :py:obj:`filecmp.DEFAULT_IGNORES`
	:param hide: A list of names to hide.
	:default hide: ``[`` :py:obj:`os.curdir`, :py:obj:`os.pardir` ``]``
	"""

	# From https://stackoverflow.com/a/24860799, public domain.
	# Thanks Philippe

	def __init__(
			self,
			a: PathLike,
			b: PathLike,
			ignore: Optional[Sequence[str]] = None,
			hide: Optional[Sequence[str]] = None,
			):
		super().__init__(a, b, ignore=ignore, hide=hide)

	def phase3(self) -> None:  # noqa: D102
		# Find out differences between common files.
		# Ensure we are using content comparison with shallow=False.

		fcomp = filecmp.cmpfiles(self.left, self.right, self.common_files, shallow=False)
		self.same_files, self.diff_files, self.funny_files = fcomp

	def phase4(self) -> None:  # noqa: D102
		# Find out differences between common subdirectories

		# From https://github.com/python/cpython/pull/23424

		self.subdirs = {}

		for x in self.common_dirs:
			a_x = os.path.join(self.left, x)
			b_x = os.path.join(self.right, x)
			self.subdirs[x] = self.__class__(a_x, b_x, self.ignore, self.hide)

	_methodmap = {
			"subdirs": phase4,
			"same_files": phase3,
			"diff_files": phase3,
			"funny_files": phase3,
			"common_dirs": filecmp.dircmp.phase2,
			"common_files": filecmp.dircmp.phase2,
			"common_funny": filecmp.dircmp.phase2,
			"common": filecmp.dircmp.phase1,
			"left_only": filecmp.dircmp.phase1,
			"right_only": filecmp.dircmp.phase1,
			"left_list": filecmp.dircmp.phase0,
			"right_list": filecmp.dircmp.phase0
			}

	methodmap = _methodmap  # type: ignore


def compare_dirs(a: PathLike, b: PathLike) -> bool:
	"""
	Compare the content of two directory trees.

	.. versionadded:: 2.7.0

	:param a: The "left" directory to compare.
	:param b: The "right" directory to compare.

	:returns: :py:obj:`False` if they differ, :py:obj:`True` is they are the same.
	"""

	compared = DirComparator(a, b)

	if compared.left_only or compared.right_only or compared.diff_files or compared.funny_files:
		return False

	for subdir in compared.common_dirs:
		if not compare_dirs(os.path.join(a, subdir), os.path.join(b, subdir)):
			return False

	return True
