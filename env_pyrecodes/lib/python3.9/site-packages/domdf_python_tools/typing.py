#!/usr/bin/env python
#
#  typing.py
"""
Various type annotation aids.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os
import pathlib
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

# 3rd party
from typing_extensions import Protocol, runtime_checkable

# this package
import domdf_python_tools

if TYPE_CHECKING or domdf_python_tools.__docs:  # pragma: no cover
	# stdlib
	from json import JSONDecoder, JSONEncoder

	# 3rd party
	from pandas import DataFrame, Series

	Series.__module__ = "pandas"
	DataFrame.__module__ = "pandas"

	JSONDecoder.__module__ = "json"
	JSONEncoder.__module__ = "json"

#: .. versionadded:: 1.0.0
FrameOrSeries = TypeVar("FrameOrSeries", "Series", "DataFrame")

__all__ = [
		"PathLike",
		"PathType",
		"AnyNumber",
		"WrapperDescriptorType",
		"MethodWrapperType",
		"MethodDescriptorType",
		"ClassMethodDescriptorType",
		"JsonLibrary",
		"HasHead",
		"String",
		"FrameOrSeries",
		"SupportsIndex",
		"SupportsLessThan",
		"SupportsLessEqual",
		"SupportsGreaterThan",
		"SupportsGreaterEqual",
		"check_membership",
		]

PathLike = Union[str, pathlib.Path, os.PathLike]
"""
Type hint for objects that represent filesystem paths.

.. seealso:: :py:obj:`domdf_python_tools.typing.PathType`
"""

PathType = TypeVar("PathType", str, pathlib.Path, os.PathLike)
"""
Type variable for objects that represent filesystem paths.

.. versionadded:: 2.2.0

.. seealso:: :py:obj:`domdf_python_tools.typing.PathLike`
"""

AnyNumber = Union[float, int, Decimal]
"""
Type hint for numbers.

.. versionchanged:: 0.4.6

	Moved from :mod:`domdf_python_tools.pagesizes`
"""


def check_membership(obj: Any, type_: Union[Type, object]) -> bool:
	r"""
	Check if the type of ``obj`` is one of the types in a :py:data:`typing.Union`, :class:`typing.Sequence` etc.

	:param obj: The object to check the type of
	:param type\_: A :class:`~typing.Type` that has members,
		such as a :class:`typing.List`, :py:data:`typing.Union` or :py:class:`typing.Sequence`.
	"""

	return isinstance(obj, type_.__args__)  # type: ignore


class JsonLibrary(Protocol):
	"""
	:class:`typing.Protocol` for libraries that implement the same API as :mod:`json`.

	Useful for annotating functions which take a JSON serialisation-deserialisation library as an argument.
	"""

	@staticmethod
	def dumps(
			obj: Any,
			*,
			skipkeys: bool = ...,
			ensure_ascii: bool = ...,
			check_circular: bool = ...,
			allow_nan: bool = ...,
			cls: Optional[Type["JSONEncoder"]] = ...,
			indent: Union[None, int, str] = ...,
			separators: Optional[Tuple[str, str]] = ...,
			default: Optional[Callable[[Any], Any]] = ...,
			sort_keys: bool = ...,
			**kwds: Any,
			) -> str:
		"""
		Serialize ``obj`` to a JSON formatted :class:`str`.

		:param obj:
		:param skipkeys:
		:param ensure_ascii:
		:param check_circular:
		:param allow_nan:
		:param cls:
		:param indent:
		:param separators:
		:param default:
		:param sort_keys:
		:param kwds:
		"""

	@staticmethod
	def loads(
			s: Union[str, bytes],
			*,
			cls: Optional[Type["JSONDecoder"]] = ...,
			object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = ...,
			parse_float: Optional[Callable[[str], Any]] = ...,
			parse_int: Optional[Callable[[str], Any]] = ...,
			parse_constant: Optional[Callable[[str], Any]] = ...,
			object_pairs_hook: Optional[Callable[[List[Tuple[Any, Any]]], Any]] = ...,
			**kwds: Any,
			) -> Any:
		"""
		Deserialize ``s`` to a Python object.

		:param s:
		:param cls:
		:param object_hook:
		:param parse_float:
		:param parse_int:
		:param parse_constant:
		:param object_pairs_hook:
		:param kwds:

		:rtype:

		.. latex:clearpage::
		"""


#  Backported from https://github.com/python/cpython/blob/master/Lib/types.py
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.

WrapperDescriptorType = type(object.__init__)
MethodWrapperType = type(object().__str__)
MethodDescriptorType = type(str.join)
ClassMethodDescriptorType = type(dict.__dict__["fromkeys"])


@runtime_checkable
class String(Protocol):
	"""
	:class:`~typing.Protocol` for classes that implement ``__str__``.

	.. versionchanged:: 0.8.0

		Moved from :mod:`domdf_python_tools.stringlist`.
	"""

	def __str__(self) -> str: ...


@runtime_checkable
class HasHead(Protocol):
	"""
	:class:`typing.Protocol` for classes that have a ``head`` method.

	This includes :class:`pandas.DataFrame` and :class:`pandas.Series`.

	.. versionadded:: 0.8.0
	"""

	def head(self: "HasHead", n: int = 5) -> "HasHead":
		"""
		Return the first n rows.

		:param n: Number of rows to select.

		:return: The first n rows of the caller object.
		"""

	def to_string(self, *args, **kwargs) -> Optional[str]:
		"""
		Render the object to a console-friendly tabular output.
		"""


# class SupportsLessThan(Protocol):
#
# 	def __lt__(self, other: Any) -> bool:
# 		...  # pragma: no cover


class SupportsIndex(Protocol):
	"""
	:class:`typing.Protocol` for classes that support ``__index__``.

	.. versionadded:: 2.0.0
	"""

	def __index__(self) -> int: ...


class SupportsLessThan(Protocol):
	"""
	:class:`typing.Protocol` for classes that support ``__lt__``.

	.. versionadded:: 3.0.0
	"""

	def __lt__(self, __other: Any) -> bool:
		"""
		Return ``self < value``.
		"""


class SupportsLessEqual(Protocol):
	"""
	:class:`typing.Protocol` for classes that support ``__le__``.

	.. versionadded:: 3.0.0
	"""

	def __le__(self, __other: Any) -> bool:
		"""
		Return ``self <= value``.
		"""


class SupportsGreaterThan(Protocol):
	"""
	:class:`typing.Protocol` for classes that support ``__gt__``.

	.. versionadded:: 3.0.0
	"""

	def __gt__(self, __other: Any) -> bool:
		"""
		Return ``self > value``.
		"""


class SupportsGreaterEqual(Protocol):
	"""
	:class:`typing.Protocol` for classes that support ``__ge__``.

	.. versionadded:: 3.0.0
	"""

	def __ge__(self, __other: Any) -> bool:
		"""
		Return ``self >= value``.
		"""
