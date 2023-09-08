#!/usr/bin/env python
# cython: language_level=3
#
#  delegators.py
"""
Decorators for functions that delegate parts of their functionality to other functions.

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
#  delegate_kwargs based on https://github.com/fastai/fastcore
#  |  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  |  not use this file except in compliance with the License. You may obtain
#  |  a copy of the License at
#  |
#  |      http://www.apache.org/licenses/LICENSE-2.0
#  |
#  |  Unless required by applicable law or agreed to in writing, software
#  |  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  |  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  |  License for the specific language governing permissions and limitations
#  |  under the License.
#

# stdlib
import inspect
from typing import Callable, TypeVar, get_type_hints

__all__ = ["delegate_kwargs", "delegates"]

_C = TypeVar("_C", bound="Callable")


def delegate_kwargs(to: Callable, *except_: str) -> Callable[[_C], _C]:
	r"""
	Decorator to replace ``**kwargs`` in function signatures with the
	parameter names from the delegated function.

	:param to: The function \*\*kwargs is passed on to.
	:param \*except\_: Parameter names not to delegate.

	:raises ValueError: if a non-default argument follows a default argument.
	"""  # noqa: D400

	# TODO: return annotation

	def _f(f: _C) -> _C:
		to_f, from_f = to, f

		to_sig = inspect.signature(to_f)
		from_sig = inspect.signature(from_f)
		to_annotations = get_type_hints(to_f)
		from_annotations = get_type_hints(from_f)
		to_params = {k: v for k, v in to_sig.parameters.items() if k not in except_}
		from_params = dict(from_sig.parameters)

		if from_params.pop("kwargs", False):
			if "kwargs" in from_annotations:
				del from_annotations["kwargs"]

			for param in from_params:
				if param in to_params:
					del to_params[param]

			f.__signature__ = from_sig.replace(  # type: ignore
				parameters=[*from_params.values(), *to_params.values()]
				)
			f.__annotations__ = {**to_annotations, **from_annotations}

		return f

	return _f


def delegates(to: Callable) -> Callable[[_C], _C]:
	r"""
	Decorator to replace ``*args, **kwargs``  function signatures
	with the signature of the delegated function.

	:param to: The function the arguments are passed on to.
	"""  # noqa: D400

	def copy_annotations(f):
		if hasattr(to, "__annotations__"):
			if hasattr(f, "__annotations__"):
				return_annotation = f.__annotations__.get("return", inspect.Parameter.empty)
				f.__annotations__.update(to.__annotations__)
				if return_annotation is not inspect.Parameter.empty:
					f.__annotations__["return"] = return_annotation
			else:
				f.__annotations__ = to.__annotations__

	def _f(f: _C) -> _C:
		to_sig = inspect.signature(to)
		from_sig = inspect.signature(f)
		from_params = dict(from_sig.parameters)

		if tuple(from_params.keys()) == ("args", "kwargs"):
			f.__signature__ = to_sig  # type: ignore
			copy_annotations(f)

		elif tuple(from_params.keys()) == ("self", "args", "kwargs"):
			f.__signature__ = from_sig.replace(  # type: ignore
				parameters=[from_params["self"], *to_sig.parameters.values()]
				)

			copy_annotations(f)

		return f

	return _f
