#!/usr/bin/env python
#
#  getters.py
"""
Variants of :func:`operator.attrgetter`, :func:`operator.itemgetter` and :func:`operator.methodcaller`
which operate on values within sequences.

.. versionadded:: 3.2.0
"""  # noqa: D400
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Adapted from https://github.com/python/cpython/blob/master/Lib/operator.py
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#

# stdlib
from functools import partial
from typing import TYPE_CHECKING, Any, Dict, Tuple

__all__ = ["attrgetter", "itemgetter", "methodcaller"]


class attrgetter:
	"""
	Returns a callable object that fetches ``attr`` from the item at index ``idx`` in its operand.

	The attribute name can contain dots. For example:

	* After ``f = attrgetter(0, 'name')``, the call call ``f(b)`` returns ``b[0].name``.
	* After ``f = attrgetter(3, 'name.first')``, the call ``f(b)`` returns ``b[3].name.first``.

	.. code-block:: python

		>>> from pathlib import Path
		>>> attrgetter(0, 'name')([Path("dir/code.py")])
		'code.py'
		>>> attrgetter(2, 'parent.name')([Path("dir/coincidence.py"), Path("dir/wheel.py"), Path("dir/operator.py")])
		'dir'

	.. seealso:: :func:`operator.attrgetter` and :func:`operator.itemgetter`

	:param idx: The index of the item to obtain the attribute from.
	:param attr: The name of the attribute.
	"""

	__slots__ = ("_attrs", "_call")

	def __init__(self, idx: int, attr: str):
		if not isinstance(idx, int):
			raise TypeError("'idx' must be an integer")

		if not isinstance(attr, str):
			raise TypeError("attribute name must be a string")

		self._attrs: Dict[str, Any] = {"idx": idx, "attr": attr}

	def __call__(self, obj: Any) -> Any:  # noqa: D102
		names = self._attrs["attr"].split('.')

		obj = obj[self._attrs["idx"]]

		for name in names:
			obj = getattr(obj, name)

		return obj

	def __repr__(self) -> str:
		data = {**self._attrs, "module": self.__class__.__module__, "qualname": self.__class__.__qualname__}
		return "{module}.{qualname}(idx={idx}, attr={attr!r})".format_map(data)

	def __reduce__(self):
		return self.__class__, tuple(self._attrs.values())


class itemgetter:
	"""
	Returns a callable object that fetches ``item`` from the item at index ``idx`` in its operand,
	using the ``__getitem__()`` method.

	For example:

	* After ``f = itemgetter(0, 2)``, the call call ``f(r)`` returns ``r[0][2]``.
	* After ``g = itemgetter(3, 5)``, the call ``g(r)`` returns ``r[3][5]``.

	The items can be any type accepted by the item's ``__getitem__()`` method.
	Dictionaries accept any hashable value. Lists, tuples, and strings accept an index or a slice:

	.. code-block:: python

		>>> itemgetter(0, 1)(['ABCDEFG'])
		'B'
		>>> itemgetter(1, 2)(['ABC', 'DEF'])
		'F'
		>>> itemgetter(0, slice(2, None))(['ABCDEFG'])
		'CDEFG'
		>>> army = [dict(rank='captain', name='Blackadder'), dict(rank='Private', name='Baldrick')]
		>>> itemgetter(0, 'rank')(army)
		'captain'

	.. seealso:: :func:`operator.itemgetter`

	:param idx: The index of the item to call ``__getitem__()`` on.
	:param item: The value to pass to ``__getitem__()``.
	"""  # noqa: D400

	__slots__ = ("_items", "_call")

	def __init__(self, idx: int, item: Any):
		if not isinstance(idx, int):
			raise TypeError("'idx' must be an integer")

		self._items: Dict[str, Any] = {"idx": idx, "item": item}

	def __call__(self, obj: Any) -> Any:  # noqa: D102
		return obj[self._items["idx"]][self._items["item"]]

	def __repr__(self) -> str:
		data = {**self._items, "module": self.__class__.__module__, "qualname": self.__class__.__qualname__}
		return "{module}.{qualname}(idx={idx}, item={item!r})".format_map(data)

	def __reduce__(self):
		return self.__class__, tuple(self._items.values())


class methodcaller:
	r"""
	Returns a callable object that calls the method name on the item at index ``idx`` in its operand.

	If additional arguments and/or keyword arguments are given, they will be passed to the method as well.
	For example:

	* After ``f = methodcaller(0, 'name')``, the call ``f(b)`` returns ``b[0].name()``.
	* After ``f = methodcaller(1, 'name', 'foo', bar=1)``, the call ``f(b)`` returns ``b[1].name('foo', bar=1)``.

	.. code-block:: python

		>>> from datetime import date
		>>> methodcaller(0, 'upper')(["hello", "world"])
		'HELLO'
		>>> methodcaller(1, 'center', 9, "=")(["hello", "world"])
		'==world=='
		>>> methodcaller(0, 'replace', year=2019)([date(2021, 7, 6)])
		datetime.date(2019, 7, 6)

	.. seealso:: :func:`operator.methodcaller` and :func:`operator.itemgetter`

	:param \_idx: The index of the item to call the method on.
	:param \_attr: The name of the method to call.
	:param \*args: Positional arguments to pass to the method.
	:param \*\*kwargs: Keyword arguments to pass to the method.
	"""

	__slots__ = ("_idx", "_name", "_args", "_kwargs")

	_idx: int
	_name: str
	_args: Tuple[Any, ...]
	_kwargs: Dict[str, Any]

	if TYPE_CHECKING:

		def __init__(__self, __idx: int, __name: str, *args, **kwargs):
			if not isinstance(__idx, int):
				raise TypeError("'idx' must be an integer")

			if not isinstance(__name, str):
				raise TypeError("method name must be a string")

			__self._idx = __idx
			__self._name = __name
			__self._args = args
			__self._kwargs = kwargs

	else:

		def __init__(_self, _idx: int, _name: str, *args, **kwargs):
			if not isinstance(_idx, int):
				raise TypeError("'_idx' must be an integer")

			if not isinstance(_name, str):
				raise TypeError("method name must be a string")

			_self._idx = _idx
			_self._name = _name
			_self._args = args
			_self._kwargs = kwargs

	def __call__(self, obj: Any) -> Any:  # noqa: D102
		return getattr(obj[self._idx], self._name)(*self._args, **self._kwargs)

	def __repr__(self) -> str:
		args = [repr(self._idx), repr(self._name)]
		args.extend(map(repr, self._args))
		args.extend(f'{k}={v!r}' for k, v in self._kwargs.items())
		return f'{self.__class__.__module__}.{self.__class__.__name__}({", ".join(args)})'

	def __reduce__(self):
		if not self._kwargs:
			return self.__class__, (self._idx, self._name) + self._args
		else:
			return partial(self.__class__, self._idx, self._name, **self._kwargs), self._args
