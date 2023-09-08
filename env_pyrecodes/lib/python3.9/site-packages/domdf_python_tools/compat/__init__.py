#  !/usr/bin/env python
#
#  compat.py
r"""
Cross-version compatibility helpers.

.. versionadded :: 0.12.0

-----

Provides the following:

.. autovariable:: domdf_python_tools.compat.PYPY
	:no-value:

.. raw:: latex

	\begin{multicols}{2}

.. autovariable:: domdf_python_tools.compat.PYPY36
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY37
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY37_PLUS
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY38
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY38_PLUS
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY39
	:no-value:

.. autovariable:: domdf_python_tools.compat.PYPY39_PLUS
	:no-value:

.. raw:: latex

	\end{multicols}

.. py:data:: importlib_resources

	`importlib_resources <https://importlib-resources.readthedocs.io/en/latest/>`_ on Python 3.6;
	:mod:`importlib.resources` on Python 3.7 and later.

.. py:data:: importlib_metadata

	`importlib_metadata <https://importlib-metadata.readthedocs.io/en/latest/>`_ on Python 3.8 and earlier;
	:mod:`importlib.metadata` on Python 3.9 and later.

	.. versionadded:: 1.1.0

	.. versionchanged:: 2.5.0

		`importlib_metadata <https://importlib-metadata.readthedocs.io/en/latest/>`__ is now used
		on Python 3.8 in place of the stdlib version.
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
import platform
import sys
from typing import TYPE_CHECKING, ContextManager, Optional, TypeVar

# this package
import domdf_python_tools

__all__ = [
		"importlib_resources",
		"importlib_metadata",
		"nullcontext",
		"PYPY",
		"PYPY36",
		"PYPY37",
		"PYPY37_PLUS",
		"PYPY38",
		"PYPY38_PLUS",
		"PYPY39",
		"PYPY39_PLUS",
		]

if sys.version_info[:2] < (3, 7) or domdf_python_tools.__docs or TYPE_CHECKING:  # pragma: no cover (py37+)

	_T = TypeVar("_T")

	class nullcontext(ContextManager[Optional[_T]]):
		"""
		Context manager that does no additional processing.

		Used as a stand-in for a normal context manager, when a particular
		block of code is only sometimes used with a normal context manager:

		.. code-block:: python

			cm = optional_cm if condition else nullcontext()
			with cm:
				# Perform operation, using optional_cm if condition is True

		.. versionadded:: 2.1.0

		In Python 3.7 and above the `version from the standard library`_ is used instead of this one,
		but the implementations are identical.

		.. _version from the standard library: https://docs.python.org/3/library/contextlib.html#contextlib.nullcontext

		:param enter_result: An optional value to return when entering the context.
		"""

		#  From CPython
		#  Licensed under the Python Software Foundation License Version 2.
		#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
		#  Copyright © 2000 BeOpen.com. All rights reserved.
		#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
		#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.

		def __init__(self, enter_result: Optional[_T] = None):
			self.enter_result: Optional[_T] = enter_result

		def __enter__(self) -> Optional[_T]:
			return self.enter_result

		def __exit__(self, *excinfo):
			pass

else:  # pragma: no cover (<py37)

	# stdlib
	from contextlib import nullcontext

PYPY: bool = platform.python_implementation() == "PyPy"
"""
:py:obj:`True` if running on PyPy rather than CPython.

.. versionadded:: 2.3.0
"""

PYPY36: bool = False
"""
:py:obj:`True` if running on PyPy 3.6.

.. versionadded:: 2.6.0
"""

PYPY37: bool = False
"""
:py:obj:`True` if running on PyPy 3.7.

.. versionadded:: 2.6.0
"""

PYPY38: bool = False
"""
:py:obj:`True` if running on PyPy 3.8.

.. versionadded:: 3.2.0
"""

PYPY39: bool = False
"""
:py:obj:`True` if running on PyPy 3.9.

.. versionadded:: 3.3.0
"""

PYPY37_PLUS: bool = False
"""
:py:obj:`True` if running on PyPy 3.7 or newer.

.. versionadded:: 3.3.0
"""

PYPY38_PLUS: bool = False
"""
:py:obj:`True` if running on PyPy 3.8 or newer.

.. versionadded:: 3.3.0
"""

PYPY39_PLUS: bool = False
"""
:py:obj:`True` if running on PyPy 3.9 or newer.

.. versionadded:: 3.3.0
"""

if PYPY:  # pragma: no cover
	if sys.version_info[:2] == (3, 6):
		PYPY36 = True
	elif sys.version_info[:2] == (3, 7):
		PYPY37 = True
		PYPY37_PLUS = True
	elif sys.version_info[:2] == (3, 8):
		PYPY38 = True
		PYPY38_PLUS = PYPY37_PLUS = True
	elif sys.version_info[:2] == (3, 9):
		PYPY39 = True
		PYPY39_PLUS = PYPY38_PLUS = PYPY37_PLUS = True
