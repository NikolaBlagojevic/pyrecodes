#!/usr/bin/env python
# cython: language_level=3
#
#  utils.py
"""
Functions and classes for pretty printing.

.. versionadded:: 0.10.0
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
#  Based on CPython.
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#

# stdlib
import sys
from io import StringIO
from typing import IO, Any, Callable, Iterator, MutableMapping, Optional, Tuple, Type, TypeVar

try:  # pragma: no cover

	# 3rd party
	from pprint36 import PrettyPrinter
	from pprint36._pprint import _safe_key  # type: ignore

	supports_sort_dicts = True

except ImportError:

	# stdlib
	from pprint import PrettyPrinter, _safe_key  # type: ignore

	supports_sort_dicts = sys.version_info >= (3, 8)

__all__ = ["FancyPrinter", "simple_repr"]

_T = TypeVar("_T", bound=Type)


class FancyPrinter(PrettyPrinter):
	"""
	Subclass of :class:`~.pprint.PrettyPrinter` with different formatting.

	:param indent: Number of spaces to indent for each level of nesting.
	:param width: Attempted maximum number of columns in the output.
	:param depth: The maximum depth to print out nested structures.
	:param stream: The desired output stream.  If omitted (or :py:obj:`False`), the standard
		output stream available at construction will be used.
	:param compact: If :py:obj:`True`, several items will be combined in one line.
	:param sort_dicts: If :py:obj:`True`, dict keys are sorted.
		Only takes effect on Python 3.8 and later,
		or if `pprint36 <https://pypi.org/project/pprint36/>`_ is installed.
	"""

	def __init__(
			self,
			indent: int = 1,
			width: int = 80,
			depth: Optional[int] = None,
			stream: Optional[IO[str]] = None,
			*,
			compact: bool = False,
			sort_dicts: bool = True,
			):
		if supports_sort_dicts:
			super().__init__(
					indent=indent,
					width=width,
					depth=depth,
					stream=stream,
					compact=compact,
					sort_dicts=sort_dicts,
					)
		else:
			super().__init__(
					indent=indent,
					width=width,
					depth=depth,
					stream=stream,
					compact=compact,
					)

	_dispatch: MutableMapping[Callable, Callable]
	_indent_per_level: int
	_format_items: Callable[[PrettyPrinter, Any, Any, Any, Any, Any, Any], None]
	_dispatch = dict(PrettyPrinter._dispatch)  # type: ignore

	def _make_open(self, char: str, indent: int, obj):
		if self._indent_per_level > 1:
			the_indent = ' ' * (indent + 1)
		else:
			the_indent = ' ' * (indent + self._indent_per_level)

		if obj and not self._compact:  # type: ignore
			return f"{char}\n{the_indent}"
		else:
			return char

	def _make_close(self, char: str, indent: int, obj):
		if obj and not self._compact:  # type: ignore
			return f",\n{' ' * (indent + self._indent_per_level)}{char}"
		else:
			return char

	def _pprint_dict(
			self,
			object,  # noqa: A002  # pylint: disable=redefined-builtin
			stream,
			indent,
			allowance,
			context,
			level,
			):
		obj = object
		write = stream.write
		write(self._make_open('{', indent, obj))

		if self._indent_per_level > 1:
			write((self._indent_per_level - 1) * ' ')

		if obj:
			self._format_dict_items(  # type: ignore
					obj.items(),
					stream,
					indent,
					allowance + 1,
					context,
					level,
					)

		write(self._make_close('}', indent, obj))

	_dispatch[dict.__repr__] = _pprint_dict

	def _pprint_list(self, obj, stream, indent, allowance, context, level):
		stream.write(self._make_open('[', indent, obj))
		self._format_items(obj, stream, indent, allowance + 1, context, level)
		stream.write(self._make_close(']', indent, obj))

	_dispatch[list.__repr__] = _pprint_list

	def _pprint_tuple(self, obj, stream, indent, allowance, context, level):
		stream.write(self._make_open('(', indent, obj))
		endchar = ",)" if len(obj) == 1 else self._make_close(')', indent, obj)
		self._format_items(obj, stream, indent, allowance + len(endchar), context, level)
		stream.write(endchar)

	_dispatch[tuple.__repr__] = _pprint_tuple

	def _pprint_set(self, obj, stream, indent, allowance, context, level):
		if not obj:
			stream.write(repr(obj))
			return

		typ = obj.__class__
		if typ is set:
			stream.write(self._make_open('{', indent, obj))
			endchar = self._make_close('}', indent, obj)
		else:
			stream.write(typ.__name__ + f"({{\n{' ' * (indent + self._indent_per_level + len(typ.__name__) + 1)}")
			endchar = f",\n{' ' * (indent + self._indent_per_level + len(typ.__name__) + 1)}}})"
			indent += len(typ.__name__) + 1

		obj = sorted(obj, key=_safe_key)
		self._format_items(obj, stream, indent, allowance + len(endchar), context, level)
		stream.write(endchar)

	_dispatch[set.__repr__] = _pprint_set
	_dispatch[frozenset.__repr__] = _pprint_set


class Attributes:

	def __init__(self, obj: object, *attributes: str):
		self.obj = obj
		self.attributes = attributes

	def __iter__(self) -> Iterator[Tuple[str, Any]]:
		for attr in self.attributes:
			yield attr, getattr(self.obj, attr)

	def __len__(self) -> int:
		return len(self.attributes)

	def __repr__(self) -> str:
		return f"Attributes{self.attributes}"


class ReprPrettyPrinter(FancyPrinter):

	_dispatch = dict(FancyPrinter._dispatch)

	def format_attributes(self, obj: Attributes):
		stream = StringIO()
		context = {}

		context[id(obj)] = 1

		stream.write(f"(\n{self._indent_per_level * ' '}")

		if self._indent_per_level > 1:
			stream.write((self._indent_per_level - 1) * ' ')

		if obj:
			self._format_attribute_items(list(obj), stream, 0, 0 + 1, context, 1)
		stream.write(f"\n{self._indent_per_level * ' '})")

		del context[id(obj)]
		return stream.getvalue()

	def _format_attribute_items(self, items, stream, indent, allowance, context, level):

		write = stream.write
		indent += self._indent_per_level
		delimnl = ",\n" + ' ' * indent
		last_index = len(items) - 1

		for i, (key, ent) in enumerate(items):
			last = i == last_index
			write(key)
			write('=')
			self._format(  # type: ignore
				ent,
				stream,
				indent + len(key) + 2,
				allowance if last else 1,
				context,
				level,
				)

			if not last:
				write(delimnl)


_default_formatter = ReprPrettyPrinter()


def simple_repr(*attributes: str, show_module: bool = False, **kwargs):
	r"""
	Adds a simple ``__repr__`` method to the decorated class.

	:param attributes: The attributes to include in the ``__repr__``.
	:param show_module: Whether to show the name of the module in the ``__repr__``.
	:param \*\*kwargs: Keyword arguments passed on to :class:`pprint.PrettyPrinter`.
	"""

	def deco(obj: _T) -> _T:

		def __repr__(self) -> str:
			if kwargs:
				formatter = ReprPrettyPrinter(**kwargs)
			else:
				formatter = _default_formatter

			class_name = f"{type(self).__module__}.{type(self).__name__}" if show_module else type(self).__name__

			return f"{class_name}{formatter.format_attributes(Attributes(self, *attributes))}"

		__repr__.__doc__ = f"Return a string representation of the :class:`~{obj.__module__}.{obj.__name__}`."
		__repr__.__name__ = "__repr__"
		__repr__.__module__ = obj.__module__
		__repr__.__qualname__ = f"{obj.__module__}.__repr__"
		obj.__repr__ = __repr__  # type: ignore

		return obj

	return deco
