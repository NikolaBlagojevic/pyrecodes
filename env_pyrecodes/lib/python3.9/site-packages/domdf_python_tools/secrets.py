#  !/usr/bin/env python
#
#  secrets.py
"""
Functions for working with secrets, such as API tokens.

.. versionadded:: 0.4.6
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

# this package
from domdf_python_tools.doctools import prettify_docstrings

__all__ = ["Secret"]


@prettify_docstrings
class Secret(str):
	"""
	Subclass of :py:class:`str` that guards against accidentally printing a secret to the terminal.

	The actual value of the secret is accessed via the ``.value`` attribute.

	The protection should be maintained even when the secret is in a list, tuple, set or dict,
	but you should still refrain from printing objects containing the secret.

	The secret overrides the :meth:`~.__eq__` method of :class:`str`, so:

	.. code-block:: python

		>>> Secret("Barry as FLUFL") == "Barry as FLUFL"
		True

	.. versionadded:: 0.4.6
	.. autosummary-widths:: 1/2
	"""

	__slots__ = ("value", )

	value: str  #: The actual value of the secret.

	def __new__(cls, value) -> "Secret":  # noqa: D102
		obj: Secret = super().__new__(cls, "<SECRET>")
		obj.value = str(value)
		return obj

	def __eq__(self, other) -> bool:
		return self.value == other

	def __hash__(self):
		return hash(self.value)
