#  !/usr/bin/env python
#
#  doctools.py
"""
Utilities for documenting functions, classes and methods.

.. autosummary-widths:: 5/16

.. automodulesumm:: domdf_python_tools.doctools
	:autosummary-sections: Data

.. autosummary-widths:: 17/32

.. automodulesumm:: domdf_python_tools.doctools
	:autosummary-sections: Functions
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#  Based on https://softwareengineering.stackexchange.com/a/386758
#  Copyright © amon (https://softwareengineering.stackexchange.com/users/60357/amon)
#  Licensed under CC BY-SA 4.0
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
import builtins
from contextlib import suppress
from inspect import cleandoc
from types import MethodType
from typing import Any, Callable, Dict, Optional, Sequence, Type, TypeVar, Union

# this package
from domdf_python_tools.compat import PYPY, PYPY37
from domdf_python_tools.typing import MethodDescriptorType, MethodWrapperType, WrapperDescriptorType

__all__ = [
		"_F",
		"_T",
		"deindent_string",
		"document_object_from_another",
		"append_doctring_from_another",
		"make_sphinx_links",
		"is_documented_by",
		"append_docstring_from",
		"sphinxify_docstring",
		"prettify_docstrings",
		]

_F = TypeVar("_F", bound=Callable[..., Any])
_T = TypeVar("_T", bound=Type)


def deindent_string(string: Optional[str]) -> str:
	"""
	Removes all indentation from the given string.

	:param string: The string to deindent

	:return: The string without indentation
	"""

	if not string:
		# Short circuit if empty string or None
		return ''

	split_string = string.split('\n')
	deindented_string = [line.lstrip("\t ") for line in split_string]
	return '\n'.join(deindented_string)


# Functions that do the work
def document_object_from_another(target: Union[Type, Callable], original: Union[Type, Callable]):
	"""
	Sets the docstring of the ``target`` function to that of the ``original`` function.

	This may be useful for subclasses or wrappers that use the same arguments.

	:param target: The object to set the docstring for
	:param original: The object to copy the docstring from
	"""

	target.__doc__ = original.__doc__


def append_doctring_from_another(target: Union[Type, Callable], original: Union[Type, Callable]):
	"""
	Sets the docstring of the ``target`` function to that of the ``original`` function.

	This may be useful for subclasses or wrappers that use the same arguments.

	Any indentation in either docstring is removed to
	ensure consistent indentation between the two docstrings.
	Bear this in mind if additional indentation is used in the docstring.

	:param target: The object to append the docstring to
	:param original: The object to copy the docstring from
	"""

	# this package
	from domdf_python_tools.stringlist import StringList

	target_doc = target.__doc__
	original_doc = original.__doc__

	if isinstance(original_doc, str) and isinstance(target_doc, str):
		docstring = StringList(cleandoc(target_doc))
		docstring.blankline(ensure_single=True)
		docstring.append(cleandoc(original_doc))
		docstring.blankline(ensure_single=True)
		target.__doc__ = str(docstring)

	elif not isinstance(target_doc, str) and isinstance(original_doc, str):
		docstring = StringList(cleandoc(original_doc))
		docstring.blankline(ensure_single=True)
		target.__doc__ = str(docstring)


def make_sphinx_links(input_string: str, builtins_list: Optional[Sequence[str]] = None) -> str:
	r"""
	Make proper sphinx links out of double-backticked strings in docstring.

	i.e. :inline-code:`\`\`str\`\`` becomes  :inline-code:`:class:\`str\``

	Make sure to include the following in your ``conf.py`` file for Sphinx:

	.. code-block:: python

		intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

	:param input_string: The string to process.
	:param builtins_list: A list of builtins to make links for.
	:default builtins_list: dir(:py:obj:`builtins`)

	:return: Processed string with links.
	"""

	if builtins_list is None:
		builtins_list = dir(builtins)

	working_string = f"{input_string}"

	for builtin in builtins_list:
		if builtin.startswith("__"):
			continue

		if builtin in {"None", "False", "None"}:
			working_string = working_string.replace(f"``{builtin}``", f":py:obj:`{builtin}`")
		else:
			working_string = working_string.replace(f"``{builtin}``", f":class:`{builtin}`")

	return working_string


# Decorators that call the above functions
def is_documented_by(original: Callable) -> Callable[[_F], _F]:
	"""
	Decorator to set the docstring of the ``target`` function to that of the ``original`` function.

	This may be useful for subclasses or wrappers that use the same arguments.

	:param original:
	"""

	def wrapper(target: _F) -> _F:
		document_object_from_another(target, original)
		return target

	return wrapper


def append_docstring_from(original: Callable) -> Callable[[_F], _F]:
	"""
	Decorator to appends the docstring from the ``original`` function to the ``target`` function.

	This may be useful for subclasses or wrappers that use the same arguments.

	Any indentation in either docstring is removed to
	ensure consistent indentation between the two docstrings.
	Bear this in mind if additional indentation is used in the docstring.

	:param original:
	"""

	def wrapper(target: _F) -> _F:
		append_doctring_from_another(target, original)
		return target

	return wrapper


def sphinxify_docstring() -> Callable[[_F], _F]:
	r"""
	Decorator to make proper sphinx links out of double-backticked strings in the docstring.

	i.e. :inline-code:`\`\`str\`\`` becomes  :inline-code:`:class:\`str\``

	Make sure to include the following in your ``conf.py`` file for Sphinx:

	.. code-block:: python

		intersphinx_mapping = {
			"python": ("https://docs.python.org/3/", None),
		}
	"""

	def wrapper(target: _F) -> _F:
		target_doc = target.__doc__

		if target_doc:
			target.__doc__ = make_sphinx_links(target_doc)

		return target

	return wrapper


# Check against object
base_new_docstrings = {
		"__delattr__": "Implement :func:`delattr(self, name) <delattr>`.",
		"__dir__": "Default :func:`dir` implementation.",
		"__eq__": "Return ``self == other``.",  # __format__
		"__getattribute__": "Return :func:`getattr(self, name) <getattr>`.",
		"__ge__": "Return ``self >= other``.",
		"__gt__": "Return ``self > other``.",
		"__hash__": "Return :func:`hash(self) <hash>`.",
		# __init_subclass__
		# __init__  # not usually shown in sphinx
		"__lt__": "Return ``self < other``.",
		"__le__": "Return ``self <= other``.",  # __new__
		"__ne__": "Return ``self != other``.",
		# __reduce_ex__
		# __reduce__
		# __repr__ is defined within the function
		"__setattr__": "Implement :func:`setattr(self, name) <setattr>`.",
		"__sizeof__": "Returns the size of the object in memory, in bytes.",
		"__str__": "Return :class:`str(self) <str>`.",  # __subclasshook__
		}

# Check against dict
container_docstrings = {
		"__contains__": "Return ``key in self``.",
		"__getitem__": "Return ``self[key]``.",
		"__setitem__": "Set ``self[key]`` to ``value``.",
		"__delitem__": "Delete ``self[key]``.",
		}

# Check against int
operator_docstrings = {
		"__and__": "Return ``self & value``.",
		"__add__": "Return ``self + value``.",
		"__abs__": "Return :func:`abs(self) <abs>`.",
		"__divmod__": "Return :func:`divmod(self, value) <divmod>`.",
		"__floordiv__": "Return ``self // value``.",
		"__invert__": "Return ``~ self``.",
		"__lshift__": "Return ``self << value``.",
		"__mod__": "Return ``self % value``.",
		"__mul__": "Return ``self * value``.",
		"__neg__": "Return ``- self``.",
		"__or__": "Return ``self | value``.",
		"__pos__": "Return ``+ self``.",
		"__pow__": "Return :func:`pow(self, value, mod) <pow>`.",
		"__radd__": "Return ``value + self``.",
		"__rand__": "Return ``value & self``.",
		"__rdivmod__": "Return :func:`divmod(value, self) <divmod>`.",
		"__rfloordiv__": "Return ``value // self``.",
		"__rlshift__": "Return ``value << self``.",
		"__rmod__": "Return ``value % self``.",
		"__rmul__": "Return ``value * self``.",
		"__ror__": "Return ``value | self``.",
		"__rpow__": "Return :func:`pow(value, self, mod) <pow>`.",
		"__rrshift__": "Return ``self >> value``.",
		"__rshift__": "Return ``self >> value``.",
		"__rsub__": "Return ``value - self``.",
		"__rtruediv__": "Return ``value / self``.",
		"__rxor__": "Return ``value ^ self``.",
		"__sub__": "Return ``value - self``.",
		"__truediv__": "Return ``self / value``.",
		"__xor__": "Return ``self ^ value``.",
		}

# Check against int
base_int_docstrings = {
		# "__bool__": "Return ``self != 0``.",  # TODO
		# __ceil__
		"__float__": "Return :class:`float(self) <float>`.",  # __floor__
		"__int__": "Return :class:`int(self) <int>`.",  # __round__
		}

new_return_types = {
		"__eq__": bool,
		"__ge__": bool,
		"__gt__": bool,
		"__lt__": bool,
		"__le__": bool,
		"__ne__": bool,
		"__repr__": str,
		"__str__": str,
		"__int__": int,
		"__float__": float,
		"__bool__": bool,
		}


def _do_prettify(obj: Type, base: Type, new_docstrings: Dict[str, str]):
	"""
	Perform the actual prettifying for :func`~.prettify_docstrings`.

	.. versionadded:: 0.8.0 (private)

	:param obj:
	:param base:
	:param new_docstrings:
	"""

	for attr_name in new_docstrings:

		if not hasattr(obj, attr_name):
			continue

		attribute = getattr(obj, attr_name)

		if not PYPY and isinstance(
				attribute,
				(WrapperDescriptorType, MethodDescriptorType, MethodWrapperType, MethodType),
				):
			continue  # pragma: no cover (!PyPy)
		elif PYPY and isinstance(attribute, MethodType):
			continue  # pragma: no cover
		elif PYPY37:  # pragma: no cover (not (PyPy and py37))
			if attribute is getattr(object, attr_name, None):
				continue
			elif attribute is getattr(float, attr_name, None):
				continue
			elif attribute is getattr(str, attr_name, None):
				continue

		if attribute is None:
			continue

		base_docstring: Optional[str] = None
		if hasattr(base, attr_name):
			base_docstring = getattr(base, attr_name).__doc__

		doc: Optional[str] = attribute.__doc__
		if doc in {None, base_docstring}:
			with suppress(AttributeError, TypeError):
				attribute.__doc__ = new_docstrings[attr_name]


def prettify_docstrings(obj: _T) -> _T:
	"""
	Decorator to prettify the default :class:`object` docstrings for use in Sphinx documentation.

	.. versionadded:: 0.8.0

	:param obj: The object to prettify the method docstrings for.
	"""

	repr_docstring = f"Return a string representation of the :class:`~{obj.__module__}.{obj.__name__}`."
	new_docstrings = {**base_new_docstrings, "__repr__": repr_docstring}

	_do_prettify(obj, object, new_docstrings)
	_do_prettify(obj, dict, container_docstrings)
	_do_prettify(obj, int, operator_docstrings)
	_do_prettify(obj, int, base_int_docstrings)

	for attribute in new_return_types:
		if hasattr(obj, attribute):
			annotations: Dict = getattr(getattr(obj, attribute), "__annotations__", {})

			if "return" not in annotations or annotations["return"] is Any:
				annotations["return"] = new_return_types[attribute]

			with suppress(AttributeError, TypeError):
				getattr(obj, attribute).__annotations__ = annotations

	if issubclass(obj, tuple) and obj.__repr__.__doc__ == "Return a nicely formatted representation string":
		obj.__repr__.__doc__ = repr_docstring

	return obj
