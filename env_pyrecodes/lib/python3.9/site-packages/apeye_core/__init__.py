#!/usr/bin/env python3
#
#  __init__.py
"""
Core (offline) functionality for the apeye library.
"""
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright notice,
#        this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.
#      * Neither the name of the copyright holder nor the names of its contributors
#        may be used to endorse or promote products derived from this software without
#        specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER
#  OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  Based on the "pathlib" module from CPython.
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#
#  Based on Slumber <https://slumber.readthedocs.io>
#  Copyright (c) 2011 Donald Stufft
#  Licensed under the 2-clause BSD License
#

# stdlib
import ipaddress
import os
import pathlib
import re
import sys
from operator import attrgetter
from typing import (
		TYPE_CHECKING,
		Any,
		Dict,
		Iterable,
		List,
		Mapping,
		NamedTuple,
		Optional,
		Tuple,
		Type,
		TypeVar,
		Union,
		cast
		)
from urllib.parse import ParseResult, parse_qs, urlencode, urlparse, urlunparse

# 3rd party
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.typing import PathLike

# this package
from apeye_core import _tld

if TYPE_CHECKING:
	# stdlib
	from typing import NoReturn

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2022 Dominic Davis-Foster"
__license__: str = "BSD 3-Clause License"
__version__: str = "1.1.4"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["URL", "URLPath", "Domain", "URLType", "URLPathType"]

# NOTE: Use the relevant version numbers for apeye itself.

URLType = TypeVar("URLType", bound="URL")

URLPathType = TypeVar("URLPathType", bound="URLPath")
"""
.. versionadded:: 1.1.0
"""


@prettify_docstrings
class URLPath(pathlib.PurePosixPath):
	"""
	Represents the path part of a URL.

	Subclass of :class:`pathlib.PurePosixPath` that provides a subset of its methods.

	.. versionchanged:: 1.1.0

		Implemented :meth:`~.apeye.url.URLPath.is_absolute`, :meth:`~.apeye.url.URLPath.joinpath`,
		:meth:`~.apeye.url.URLPath.relative_to`, :meth:`~.pathlib.PurePath.match`,
		``anchor``, ``drive``, and support for rich comparisons (``<``, ``<=``, ``>`` and ``>=``),
		which previously raised :exc:`NotImplementedError`.

	.. latex:clearpage::
	"""

	def __str__(self) -> str:
		"""
		Return the string representation of the path, suitable for passing to system calls.
		"""

		if not hasattr(self, "_root"):
			self._load_parts()  # type: ignore[attr-defined]

		try:
			return self._str  # type: ignore
		except AttributeError:
			if hasattr(self, "_parts"):
				parts = self._parts  # type: ignore[attr-defined]
			else:
				parts = self._tail  # type: ignore[attr-defined]

			self._str = self._format_parsed_parts(self._drv, self._root, parts) or ''  # type: ignore
			return self._str

	def __repr__(self) -> str:
		return super().__repr__()

	@classmethod
	def _format_parsed_parts(cls, drv, root, parts):

		if drv or root:
			if sys.version_info > (3, 12):
				return drv + root + '/'.join(parts)
			else:
				return drv + root + '/'.join(parts[1:])
		else:
			return '/'.join(parts)

	def is_absolute(self) -> bool:
		"""
		Returns whether the path is absolute (i.e. starts with ``/``).

		.. versionadded:: 1.1.0  previously raised :exc:`NotImplementedError`.
		"""

		return self.root == '/'

	def joinpath(self: URLPathType, *args) -> URLPathType:
		"""
		Combine this :class:`~.apeye.url.URLPath` with one or several arguments.

		.. versionadded:: 1.1.0  previously raised :exc:`NotImplementedError`.

		:returns: A new :class:`~.apeye.url.URLPath` representing either a subpath
			(if all arguments are relative paths) or a totally different path
			(if one of the arguments is absolute).
		"""

		return super().joinpath(*args)

	def relative_to(self: URLPathType, *other: PathLike) -> URLPathType:
		r"""
		Returns the relative path to another path identified by the passed arguments.

		The arguments are joined together to form a single path, and therefore the following behave identically:

		.. code-block:: pycon

			>>> URLPath("/news/sport").relative_to("/", "news")
			URLPath('sport')
			>>> URLPath("/news/sport").relative_to("/news")
			URLPath('sport')

		.. versionadded:: 1.1.0  previously raised :exc:`NotImplementedError`.

		:param \*other:

		:raises ValueError: if the operation is not possible (because this is not a subpath of the other path)

		.. latex:clearpage::

		.. seealso::

			:meth:`~.apeye.url.URL.relative_to`, which is recommended when constructing a relative path from a :class:`~URL`.
			This method cannot correctly handle some cases, such as:

			.. code-block:: pycon

				>>> URL("https://github.com/domdfcoding").path.relative_to(URL("https://github.com").path)
				Traceback (most recent call last):
				ValueError: '/domdfcoding' does not start with ''

			Since ``URL("https://github.com").path`` is ``URLPath('')``.

			Instead, use:

				>>> URL("https://github.com/domdfcoding").relative_to(URL("https://github.com"))
				URLPath('domdfcoding')
		"""

		return super().relative_to(*other)

	def as_uri(self, *args, **kwargs) -> "NoReturn":  # noqa: D102
		raise NotImplementedError


class URL(os.PathLike):
	r"""
	:mod:`pathlib`-like class for URLs.

	:param url: The URL to construct the :class:`~apeye.url.URL` object from.

	.. versionchanged:: 0.3.0  The ``url`` parameter can now be a string or a :class:`~.apeye.url.URL`.

	.. versionchanged:: 1.1.0

		Added support for sorting and rich comparisons (``<``, ``<=``, ``>`` and ``>=``).

	.. autoclasssumm:: URL
		:autosummary-sections: Methods
		:autosummary-exclude-members: __lt__,__le__,__gt__,__ge__,__init__,__hash__

	.. autosummary-widths:: 1/5

	.. autoclasssumm:: URL
		:autosummary-sections: Attributes
	"""

	#: URL scheme specifier
	scheme: str

	#: Network location part of the URL
	netloc: str

	#: The hierarchical path of the URL
	path: URLPath

	query: Dict[str, List[str]]
	"""
	The query parameters of the URL, if present.

	.. versionadded:: 0.7.0
	"""

	fragment: Optional[str]
	"""
	The URL fragment, used to identify a part of the document. :py:obj:`None` if absent from the URL.

	.. versionadded:: 0.7.0
	"""

	def __init__(self, url: Union[str, "URL"] = ''):
		if isinstance(url, URL):
			url = str(url)

		if not re.match("([A-Za-z-.]+:)?//", url):
			url = "//" + str(url)

		scheme, netloc, parts, params, query, fragment = urlparse(url)

		self.scheme: str = scheme
		self.netloc: str = netloc
		self.path = URLPath(parts)
		self.query = parse_qs(query or '')
		self.fragment = fragment or None

	@property
	def port(self) -> Optional[int]:
		"""
		The port of number of the URL as an integer, if present. Default :py:obj:`None`.

		.. versionadded:: 0.7.0
		"""

		if ':' not in self.netloc:
			return None
		else:
			return int(self.netloc.split(':')[-1])

	@classmethod
	def from_parts(
			cls: Type[URLType],
			scheme: str,
			netloc: str,
			path: PathLike,
			query: Optional[Mapping[Any, List]] = None,
			fragment: Optional[str] = None,
			) -> URLType:
		"""
		Construct a :class:`~apeye.url.URL` from a scheme, netloc and path.

		:param scheme: The scheme of the URL, e.g ``'http'``.
		:param netloc: The netloc of the URl, e.g. ``'bbc.co.uk:80'``.
		:param path: The path of the URL, e.g. ``'/news'``.
		:param query: The query parameters of the URL, if present.
		:param fragment: The URL fragment, used to identify a part of the document.
			:py:obj:`None` if absent from the URL.

		Put together, the resulting path would be ``'http://bbc.co.uk:80/news'``

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``query`` and ``fragment`` arguments.
		"""

		obj = cls('')
		obj.scheme = scheme
		obj.netloc = netloc
		obj.query = dict(query or {})
		obj.fragment = fragment or None

		path = URLPath(path)

		if path.root == '/':
			obj.path = path
		else:
			obj.path = URLPath('/' + str(path))

		return obj

	def __str__(self) -> str:
		"""
		Returns the :class:`~apeye.url.URL` as a string.
		"""

		query = urlencode(self.query, doseq=True)
		url = urlunparse([self.scheme, self.netloc, str(self.path), None, query, self.fragment])

		if url.startswith("//"):
			return url[2:]
		else:
			return url

	def __repr__(self) -> str:
		"""
		Returns the string representation of the :class:`~apeye.url.URL`.
		"""

		return f"{self.__class__.__name__}({str(self)!r})"

	def __truediv__(self: URLType, key: Union[PathLike, int]) -> URLType:
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0

			* Added support for division by integers.

			* Now officially supports the new path having a URL fragment and/or query parameters.
			  Any URL fragment or query parameters from the parent URL are not inherited by its children.
		"""

		try:
			return self._make_child((key, ))
		except TypeError:
			return NotImplemented

	def _make_child(self: URLType, args: Iterable[Union[PathLike, int]]) -> URLType:
		"""
		Construct a new :class:`~apeye.url.URL` object by combining the given arguments with this instance's path part.

		.. versionadded:: 1.1.0  (private)

		Except for the final path element any queries and fragments are ignored.

		:returns: A new :class:`~.apeye.url.URL` representing either a subpath
			(if all arguments are relative paths) or a totally different path
			(if one of the arguments is absolute).
		"""

		parsed_args: List[ParseResult] = []

		for arg in args:

			raw_arg = arg

			if isinstance(arg, pathlib.PurePath):
				arg = arg.as_posix()
			elif isinstance(arg, os.PathLike):
				arg = os.fspath(arg)
			elif isinstance(arg, int):
				arg = str(arg)

			try:
				parse_result = urlparse(arg)
			except AttributeError as e:
				if str(e).endswith("'decode'"):
					msg = f"Cannot join {type(raw_arg).__name__!r} to a {type(self.path).__name__!r}"
					raise TypeError(msg) from None
				else:
					raise

			parsed_args.append(parse_result)

		try:
			new_path = self.from_parts(
					self.scheme,
					self.netloc,
					self.path.joinpath(*map(attrgetter("path"), parsed_args)),
					)
		except TypeError:
			return NotImplemented

		if parsed_args:
			new_path.query = parse_qs(parsed_args[-1].query)
			new_path.fragment = parsed_args[-1].fragment or None

		return new_path

	def joinurl(self: URLType, *args) -> URLType:
		"""
		Construct a new :class:`~apeye.url.URL` object by combining the given arguments with this instance's path part.

		.. versionadded:: 1.1.0

		Except for the final path element any queries and fragments are ignored.

		:returns: A new :class:`~.apeye.url.URL` representing either a subpath
			(if all arguments are relative paths) or a totally different path
			(if one of the arguments is absolute).
		"""

		return self._make_child(args)

	def __fspath__(self) -> str:
		"""
		Returns the file system path representation of the :class:`~.apeye.url.URL`.

		This is comprised of the ``netloc`` and ``path`` attributes.
		"""

		return f"{self.netloc}{self.path}"

	def __eq__(self, other) -> bool:
		"""
		Return ``self == other``.

		.. latex:vspace:: -10px

		.. attention::

			URL fragments and query parameters are not compared.

			.. seealso:: :meth:`.URL.strict_compare`, which *does* consider those attributes.

		.. latex:vspace:: -20px
		"""

		if isinstance(other, URL):
			return self.netloc == other.netloc and self.scheme == other.scheme and self.path == other.path
		else:
			return NotImplemented

	def __lt__(self, other):
		if isinstance(other, URL):
			return self._parts_port < other._parts_port
		else:
			return NotImplemented

	def __le__(self, other):
		if isinstance(other, URL):
			return self._parts_port <= other._parts_port
		else:
			return NotImplemented

	def __gt__(self, other):
		if isinstance(other, URL):
			return self._parts_port > other._parts_port
		else:
			return NotImplemented

	def __ge__(self, other):
		if isinstance(other, URL):
			return self._parts_port >= other._parts_port
		else:
			return NotImplemented

	def strict_compare(self, other) -> bool:
		"""
		Return ``self ≡ other``, comparing the scheme, netloc, path, fragment and query parameters.

		.. versionadded:: 0.7.0
		"""

		if isinstance(other, URL):
			return (
					self.netloc == other.netloc and self.scheme == other.scheme and self.path == other.path
					and self.query == other.query and self.fragment == other.fragment
					)
		else:
			return NotImplemented

	def __hash__(self) -> int:
		"""
		Returns the has of the :class:`~apeye.url.URL` .
		"""

		return hash((self.scheme, self.netloc, self.path))

	@property
	def name(self) -> str:
		"""
		The final path component, if any.
		"""

		return self.path.name

	@property
	def suffix(self) -> str:
		"""
		The final component's last suffix, if any.

		This includes the leading period. For example: ``'.txt'``.
		"""
		return self.path.suffix

	@property
	def suffixes(self) -> List[str]:
		"""
		A list of the final component's suffixes, if any.

		These include the leading periods. For example: ``['.tar', '.gz']``.
		"""
		return self.path.suffixes

	@property
	def stem(self) -> str:
		"""
		The final path component, minus its last suffix.
		"""

		return self.path.stem

	def with_name(self: URLType, name: str, inherit: bool = True) -> URLType:
		"""
		Return a new :class:`~apeye.url.URL` with the file name changed.

		:param name:
		:param inherit: Whether the new :class:`~apeye.url.URL` should inherit the query string
			and fragment from this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``inherit`` parameter.
		"""

		if inherit:
			kwargs = {"query": self.query, "fragment": self.fragment}
		else:
			kwargs = {}

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path.with_name(name),
				**kwargs,  # type: ignore
				)

	def with_suffix(self: URLType, suffix: str, inherit: bool = True) -> URLType:
		"""
		Returns a new :class:`~apeye.url.URL` with the file suffix changed.

		If the :class:`~apeye.url.URL` has no suffix, add the given suffix.

		If the given suffix is an empty string, remove the suffix from the :class:`~apeye.url.URL`.

		:param suffix:
		:param inherit: Whether the new :class:`~apeye.url.URL` should inherit the query string
			and fragment from this :class:`~apeye.url.URL`.

		:rtype:

		.. versionchanged:: 0.7.0  Added the ``inherit`` parameter.
		"""

		if inherit:
			kwargs = {"query": self.query, "fragment": self.fragment}
		else:
			kwargs = {}

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path.with_suffix(suffix),
				**kwargs,  # type: ignore
				)

	@property
	def parts(self) -> Tuple[str, ...]:
		"""
		An object providing sequence-like access to the components in the URL.

		To retrieve only the parts of the path, use :meth:`URL.path.parts <URLPath.parts>`.
		"""

		return (
				self.scheme,
				self.domain.subdomain,
				self.domain.domain,
				self.domain.suffix,
				*('/' / self.path).parts[1:],
				)

	@property
	def _parts_port(self) -> Tuple:
		"""
		An object providing sequence-like access to the components in the URL.

		Unlike ``.parts`` this includes the port.

		To retrieve only the parts of the path, use :meth:`URL.path.parts <URLPath.parts>`.

		.. versionadded:: 1.1.0  (private)
		"""

		return (
				self.scheme,
				self.domain.subdomain,
				self.domain.domain,
				self.domain.suffix,
				self.port or 0,
				*('/' / self.path).parts[1:],
				)

	@property
	def parent(self: URLType) -> URLType:
		"""
		The logical parent of the :class:`~apeye.url.URL`.
		"""

		return self.from_parts(self.scheme, self.netloc, self.path.parent)

	@property
	def parents(self: URLType) -> Tuple[URLType, ...]:
		"""
		An immutable sequence providing access to the logical ancestors of the :class:`~apeye.url.URL`.
		"""

		return tuple(self.from_parts(self.scheme, self.netloc, path) for path in self.path.parents)

	@property
	def fqdn(self) -> str:
		"""
		Returns the Fully Qualified Domain Name of the :class:`~apeye.url.URL` .
		"""

		return self.domain.fqdn

	@property
	def domain(self) -> "Domain":
		"""
		Returns a :class:`apeye.url.Domain` object representing the domain part of the URL.
		"""

		return Domain._make(_tld.extract_tld(self.netloc))

	@property
	def base_url(self: URLType) -> URLType:
		"""
		Returns a :class:`apeye.url.URL` object representing the URL without query strings or URL fragments.

		.. versionadded:: 0.7.0
		"""

		return self.from_parts(
				self.scheme,
				self.netloc,
				self.path,
				)

	def relative_to(self, other: Union[str, "URL", URLPath]) -> URLPath:
		"""
		Returns a version of this URL's path relative to ``other``.

		.. versionadded:: 1.1.0

		:param other: Either a :class:`~.apeye.url.URL`, or a string or :class:`~.apeye.url.URLPath` representing an *absolute* path.
			If a :class:`~.apeye.url.URL`, the :attr:`~.apeye.url.URL.netloc` must match this URL's.

		:raises ValueError: if the operation is not possible
			(i.e. because this URL's path is not a subpath of the other path)
		"""

		if isinstance(other, URLPath):
			if not other.is_absolute():
				raise ValueError("'URL.relative_to' cannot be used with relative URLPath objects")
			else:
				other = URL('/') / other
		elif not isinstance(other, URL):
			# Parse other as a URL
			other = URL(other)

		# Compare netloc, if both have one
		if self.netloc and other.netloc and self.netloc.lower() != other.netloc.lower():
			raise ValueError(f"{self!r} does not start with {other!r}")

		# Make the paths absolute
		# If coming from a URL they must always be absolute
		our_path = '/' / self.path
		other_path = '/' / other.path

		relative_path = our_path.relative_to(other_path)

		return relative_path


class Domain(NamedTuple):
	"""
	:class:`typing.NamedTuple` of a URL's subdomain, domain, and suffix.
	"""

	subdomain: str
	domain: str
	suffix: str

	@property
	def registered_domain(self):
		"""
		Joins the domain and suffix fields with a dot, if they're both set.

		.. code-block:: python

			>>> URL('https://forums.bbc.co.uk').domain.registered_domain
			'bbc.co.uk'
			>>> URL('https://localhost:8080').domain.registered_domain
			''
		"""
		if self.domain and self.suffix:
			return self.domain + '.' + self.suffix
		return ''

	@property
	def fqdn(self):
		"""
		Returns a Fully Qualified Domain Name, if there is a proper domain/suffix.

		.. code-block:: python

			>>> URL('https://forums.bbc.co.uk/path/to/file').domain.fqdn
			'forums.bbc.co.uk'
			>>> URL('https://localhost:8080').domain.fqdn
			''
		"""
		if self.domain and self.suffix:
			# self is the namedtuple (subdomain domain suffix)
			return '.'.join(i for i in self if i)
		return ''

	@property
	def ipv4(self) -> Optional[ipaddress.IPv4Address]:
		"""
		Returns the ipv4 if that is what the presented domain/url is.

		.. code-block:: python

			>>> URL('https://127.0.0.1/path/to/file').domain.ipv4
			IPv4Address('127.0.0.1')
			>>> URL('https://127.0.0.1.1/path/to/file').domain.ipv4
			>>> URL('https://256.1.1.1').domain.ipv4
		"""

		if not (self.suffix or self.subdomain) and _tld.IP_RE.match(self.domain):
			return cast(ipaddress.IPv4Address, ipaddress.ip_address(self.domain))
		return None

	def __repr__(self) -> str:
		"""
		Return a string representation of the :class:`~.Domain`.
		"""

		# This is necessary to get the custom docstring

		repr_fmt = f"({', '.join(f'{name}=%r' for name in self._fields)})"
		return f"{self.__class__.__name__}{repr_fmt % self}"
