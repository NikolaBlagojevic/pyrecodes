#!/usr/bin/env python
#
#  stringlist.py
"""
A list of strings that represent lines in a multiline string.

.. versionchanged:: 1.0.0

	:class:`~domdf_python_tools.typing.String` should now be imported from :mod:`domdf_python_tools.typing`.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from contextlib import contextmanager
from itertools import chain
from typing import Any, Iterable, Iterator, List, Reversible, Tuple, TypeVar, Union, cast, overload

# this package
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.typing import String, SupportsIndex
from domdf_python_tools.utils import convert_indents

__all__ = ["Indent", "StringList", "DelimitedList", "_SL", "splitlines", "joinlines"]

_S = TypeVar("_S")
_SL = TypeVar("_SL", bound="StringList")


@prettify_docstrings
class Indent:
	"""
	Represents an indent, having a symbol/type and a size.

	:param size: The indent size.
	:param type: The indent character.
	"""

	def __init__(self, size: int = 0, type: str = '\t'):  # noqa: A002  # pylint: disable=redefined-builtin
		self.size = int(size)
		self.type = str(type)

	def __iter__(self) -> Iterator[Union[str, Any]]:
		"""
		Returns the size and type of the :class:`~domdf_python_tools.stringlist.Indent`.
		"""

		yield self.size
		yield self.type

	@property
	def size(self) -> int:
		"""
		The indent size.
		"""

		return self._size

	@size.setter
	def size(self, size: int) -> None:
		self._size = int(size)

	@property  # noqa: A003  # pylint: disable=redefined-builtin
	def type(self) -> str:
		"""
		The indent character.
		"""

		return self._type

	@type.setter  # noqa: A003  # pylint: disable=redefined-builtin
	def type(self, type: str) -> None:  # noqa: A002  # pylint: disable=redefined-builtin
		if not str(type):
			raise ValueError("'type' cannot an empty string.")

		self._type = str(type)

	def __str__(self) -> str:
		"""
		Returns the :class:`~domdf_python_tools.stringlist.Indent` as a string.
		"""

		return self.type * self.size

	def __repr__(self) -> str:
		"""
		Returns the string representation of the :class:`~domdf_python_tools.stringlist.Indent`.
		"""

		return f"{type(self).__name__}(size={self.size}, type={self.type!r})"

	def __eq__(self, other):
		if isinstance(other, Indent):
			return other.size == self.size and other.type == self.type
		elif isinstance(other, str):
			return str(self) == other
		elif isinstance(other, tuple):
			return tuple(self) == other
		else:
			return NotImplemented


class StringList(List[str]):
	"""
	A list of strings that represent lines in a multiline string.

	:param iterable: Content to populate the StringList with.
	:param convert_indents: Whether indents at the start of lines should be converted.
	"""

	#: The indent to insert at the beginning of new lines.
	indent: Indent

	convert_indents: bool
	"""
	Whether indents at the start of lines should be converted.

	Only applies to lines added after this is enabled/disabled.

	Can only be used when the indent is ``'\\t'`` or ``'␣'``.
	"""

	def __init__(
			self,
			iterable: Iterable[String] = (),
			convert_indents: bool = False,
			) -> None:

		if isinstance(iterable, str):
			iterable = iterable.split('\n')

		self.indent = Indent()
		self.convert_indents = convert_indents
		super().__init__([self._make_line(str(x)) for x in iterable])

	def _make_line(self, line: str) -> str:
		if not str(self.indent_type).strip(" \t") and self.convert_indents:
			if self.indent_type == '\t':
				line = convert_indents(line, tab_width=1, from_="    ", to='\t')
			else:  # pragma: no cover
				line = convert_indents(line, tab_width=1, from_='\t', to=self.indent_type)

		return f"{self.indent}{line}".rstrip()

	def append(self, line: String) -> None:
		"""
		Append a line to the end of the :class:`~domdf_python_tools.stringlist.StringList`.

		:param line:
		"""

		for inner_line in str(line).split('\n'):
			super().append(self._make_line(inner_line))

	def extend(self, iterable: Iterable[String]) -> None:
		"""
		Extend the :class:`~domdf_python_tools.stringlist.StringList` with lines from ``iterable``.

		:param iterable: An iterable of string-like objects to add to the end of the
			:class:`~domdf_python_tools.stringlist.StringList`.
		"""

		for line in iterable:
			self.append(line)

	def copy(self: _SL) -> _SL:
		"""
		Returns a shallow copy of the :class:`~domdf_python_tools.stringlist.StringList`.

		Equivalent to ``a[:]``.

		:rtype: :class:`~domdf_python_tools.stringlist.StringList`
		"""

		return self.__class__(super().copy())

	def count_blanklines(self) -> int:
		"""
		Returns a count of the blank lines in the :class:`~domdf_python_tools.stringlist.StringList`.

		.. versionadded:: 0.7.1
		"""

		return self.count('')

	def insert(self, index: SupportsIndex, line: String) -> None:
		"""
		Insert a line into the :class:`~domdf_python_tools.stringlist.StringList` at the given position.

		:param index:
		:param line:

		.. versionchanged:: 3.2.0  Changed :class:`int` in the type annotation to :protocol:`~.SupportsIndex`.
		"""

		lines: List[str]

		index = index.__index__()

		if index < 0 or index > len(self):
			lines = str(line).split('\n')
		else:
			lines = cast(list, reversed(str(line).split('\n')))

		for inner_line in lines:
			super().insert(index, self._make_line(inner_line))

	@overload
	def __setitem__(self, index: SupportsIndex, line: String) -> None: ...

	@overload
	def __setitem__(self, index: slice, line: Iterable[String]) -> None: ...

	def __setitem__(self, index: Union[SupportsIndex, slice], line: Union[String, Iterable[String]]):
		"""
		Replaces the given line with new content.

		If the new content consists of multiple lines subsequent content in the
		:class:`~domdf_python_tools.stringlist.StringList` will be shifted down.

		:param index:
		:param line:

		.. versionchanged:: 3.2.0  Changed :class:`int` in the type annotation to :protocol:`~.SupportsIndex`.
		"""

		if isinstance(index, slice):
			line = cast(Iterable[String], line)

			if not isinstance(line, Reversible):
				line = tuple(line)

			for lline, idx in zip(
				reversed(line),
				reversed(range(index.start or 0, index.stop + 1, index.step or 1)),
				):
				self[idx] = lline
		else:
			line = cast(String, line)
			index = index.__index__()

			if self and index < len(self):
				self.pop(index)
			if index < 0:
				index = len(self) + index + 1

			self.insert(index, line)

	@overload
	def __getitem__(self, index: SupportsIndex) -> str: ...

	@overload
	def __getitem__(self: _SL, index: slice) -> _SL: ...

	def __getitem__(self: _SL, index: Union[SupportsIndex, slice]) -> Union[str, _SL]:
		r"""
		Returns the line with the given index.

		:param index:

		:rtype: :py:obj:`~typing.Union`\[:class:`str`, :class:`~domdf_python_tools.stringlist.StringList`\]

		.. versionchanged:: 1.8.0

			Now returns a :class:`~domdf_python_tools.stringlist.StringList` when ``index`` is a :class:`slice`.

		.. versionchanged:: 3.2.0  Changed :class:`int` in the type annotation to :protocol:`~.SupportsIndex`.
		"""

		if isinstance(index, slice):
			return self.__class__(super().__getitem__(index))
		else:
			return super().__getitem__(index)

	def blankline(self, ensure_single: bool = False):
		"""
		Append a blank line to the end of the :class:`~domdf_python_tools.stringlist.StringList`.

		:param ensure_single: Ensure only a single blank line exists after the previous line of text.
		"""

		if ensure_single:
			while self and not self[-1]:
				self.pop(-1)

		self.append('')

	def set_indent_size(self, size: int = 0):
		"""
		Sets the size of the indent to insert at the beginning of new lines.

		:param size: The indent size to use for new lines.
		"""

		self.indent.size = int(size)

	def set_indent_type(self, indent_type: str = '\t'):
		"""
		Sets the type of the indent to insert at the beginning of new lines.

		:param indent_type: The type of indent to use for new lines.
		"""

		self.indent.type = str(indent_type)

	def set_indent(self, indent: Union[String, Indent], size: int = 0):
		"""
		Sets the indent to insert at the beginning of new lines.

		:param indent: The :class:`~.Indent` to use for new lines, or the indent type.
		:param size: If ``indent`` is an indent type, the indent size to use for new lines.
		"""

		if isinstance(indent, Indent):
			if size:
				raise TypeError("'size' argument cannot be used when providing an 'Indent' object.")

			self.indent = indent
		else:
			self.indent = Indent(int(size), str(indent))

	@property
	def indent_size(self) -> int:
		"""
		The current indent size.
		"""

		return int(self.indent.size)

	@indent_size.setter
	def indent_size(self, size: int) -> None:
		"""
		Sets the indent size.
		"""

		self.indent.size = int(size)

	@property
	def indent_type(self) -> str:
		"""
		The current indent type.
		"""

		return str(self.indent.type)

	@indent_type.setter
	def indent_type(self, type: str) -> None:  # noqa: A002  # pylint: disable=redefined-builtin
		"""
		Sets the indent type.
		"""

		self.indent.type = str(type)

	def __str__(self) -> str:
		"""
		Returns the :class:`~domdf_python_tools.stringlist.StringList` as a string.
		"""

		return '\n'.join(self)

	def __bytes__(self) -> bytes:
		"""
		Returns the :class:`~domdf_python_tools.stringlist.StringList` as bytes.

		.. versionadded:: 2.1.0
		"""

		return str(self).encode("UTF-8")

	def __eq__(self, other) -> bool:
		"""
		Returns whether the other object is equal to this :class:`~domdf_python_tools.stringlist.StringList`.
		"""

		if isinstance(other, str):
			return str(self) == other
		else:
			return super().__eq__(other)

	@contextmanager
	def with_indent(self, indent: Union[String, Indent], size: int = 0):
		"""
		Context manager to temporarily use a different indent.

		.. code-block:: python

			>>> sl = StringList()
			>>> with sl.with_indent("    ", 1):
			...     sl.append("Hello World")

		:param indent: The :class:`~.Indent` to use within the ``with`` block, or the indent type.
		:param size: If ``indent`` is an indent type, the indent size to use within the ``with`` block.
		"""

		original_indent: Tuple[int, str] = tuple(self.indent)  # type: ignore

		try:
			self.set_indent(indent, size)
			yield
		finally:
			self.indent = Indent(*original_indent)

	@contextmanager
	def with_indent_size(self, size: int = 0):
		"""
		Context manager to temporarily use a different indent size.

		.. code-block:: python

			>>> sl = StringList()
			>>> with sl.with_indent_size(1):
			...     sl.append("Hello World")

		:param size: The indent size to use within the ``with`` block.
		"""

		original_indent_size = self.indent_size

		try:
			self.indent_size = size
			yield
		finally:
			self.indent_size = original_indent_size

	@contextmanager
	def with_indent_type(self, indent_type: str = '\t'):
		"""
		Context manager to temporarily use a different indent type.

		.. code-block:: python

			>>> sl = StringList()
			>>> with sl.with_indent_type("    "):
			...     sl.append("Hello World")

		:param indent_type: The type of indent to use within the ``with`` block.
		"""

		original_indent_type = self.indent_type

		try:
			self.indent_type = indent_type
			yield
		finally:
			self.indent_type = original_indent_type


class DelimitedList(List[_S]):
	"""
	Subclass of :class:`list` that supports custom delimiters in format strings.

	**Example:**

	.. code-block:: python

		>>> l = DelimitedList([1, 2, 3, 4, 5])
		>>> format(l, ", ")
		'1, 2, 3, 4, 5'
		>>> f"Numbers: {l:, }"
		'Numbers: 1, 2, 3, 4, 5'

	.. autoclasssumm:: DelimitedList
		:autosummary-sections: ;;

	.. versionadded:: 1.1.0
	"""

	def __format__(self, format_spec: str) -> str:
		return format_spec.join([str(x) for x in self])  # pylint: disable=not-an-iterable


def splitlines(string: str) -> List[Tuple[str, str]]:
	"""
	Split ``string`` into a list of two-element tuples,
	containing the line content and the newline character(s), if any.

	.. versionadded:: 3.2.0

	:param string:

	:rtype:

	.. seealso:: :meth:`str.splitlines` and :func:`~.stringlist.joinlines`
	"""  # noqa: D400

	# Translated and adapted from https://github.com/python/cpython/blob/main/Objects/stringlib/split.h

	str_len: int = len(string)
	i: int = 0
	j: int = 0
	eol: int
	the_list: List[Tuple[str, str]] = []

	while i < str_len:

		# Find a line and append it
		while i < str_len and not string[i] in "\n\r":
			i += 1

		# Skip the line break reading CRLF as one line break
		eol = i
		if i < str_len:
			if (string[i] == '\r') and (i + 1 < str_len) and (string[i + 1] == '\n'):
				i += 2
			else:
				i += 1

		if j == 0 and eol == str_len and type(string) is str:  # pylint: disable=unidiomatic-typecheck
			# No whitespace in string, so just use it as the_list[0]
			the_list.append((string, ''))
			break

		the_list.append((string[j:eol], string[eol:i]))
		j = i

	return the_list


def joinlines(lines: List[Tuple[str, str]]) -> str:
	"""
	Given a list of two-element tuples, each containing a line and a newline character (or empty string),
	return a single string.

	.. versionadded:: 3.2.0

	:param lines:

	:rtype:

	.. seealso:: :func:`~.stringlist.splitlines`
	"""  # noqa: D400

	return ''.join(chain.from_iterable(lines))
