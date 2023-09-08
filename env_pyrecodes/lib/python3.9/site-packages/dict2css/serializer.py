#!/usr/bin/env python3
#
#  serializer.py
"""
Serializer for cascading style sheets.

.. versionadded:: 0.2.0
"""
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

# stdlib
from contextlib import contextmanager
from typing import Iterator

# 3rd party
from domdf_python_tools.words import TAB

try:
	# 3rd party
	import css_parser  # type: ignore
except ImportError:  # pragma: no cover
	# 3rd party
	import cssutils as css_parser  # type: ignore

__all__ = ["CSSSerializer"]


class CSSSerializer(css_parser.CSSSerializer):
	r"""
	Serializes a :class:`~.StyleSheet` and its parts.

	This controls the formatting of the style sheet.

	:param indent: The indent to use, such as a tab (``\t``), two spaces or four spaces.
	:param trailing_semicolon:  Whether to add a semicolon to the end of the final property.
	:param indent_closing_brace:
	:param minify: Minify the CSS. Overrides all other options.

	.. autosummary-widths:: 5/16
	"""

	def __init__(
			self,
			*,
			indent: str = TAB,
			trailing_semicolon: bool = False,
			indent_closing_brace: bool = False,
			minify: bool = False,
			):
		super().__init__()
		self.indent = str(indent)
		self.trailing_semicolon = trailing_semicolon
		self.indent_closing_brace = indent_closing_brace
		self.minify = minify

	def reset_style(self) -> None:
		"""
		Reset the serializer to its default style.
		"""

		# Reset CSS Parser to defaults
		self.prefs.useDefaults()

		if self.minify:
			self.prefs.useMinified()

		else:
			# Formatting preferences
			self.prefs.omitLastSemicolon = not self.trailing_semicolon
			self.prefs.indentClosingBrace = self.indent_closing_brace
			self.prefs.indent = self.indent

	@contextmanager
	def use(self) -> Iterator:
		"""
		Contextmanager to use this serializer for the scope of the ``with`` block.
		"""

		# if css_parser.ser is self:
		# 	yield
		# 	return
		#
		current_serializer = css_parser.ser
		self.reset_style()

		try:
			css_parser.ser = self
			yield

		finally:
			css_parser.ser = current_serializer
