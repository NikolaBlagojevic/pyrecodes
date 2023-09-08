#!/usr/bin/env python3
#
#  __init__.py
"""
A μ-library for constructing cascasing style sheets from Python dictionaries.

.. latex:vspace:: 10px
.. seealso:: `css-parser <https://github.com/ebook-utils/css-parser>`_, which this library builds upon.
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
from io import TextIOBase
from typing import IO, Any, Dict, Mapping, MutableMapping, Sequence, Union, cast

# 3rd party
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike
from domdf_python_tools.words import TAB

try:
	# 3rd party
	import css_parser  # type: ignore
except ImportError:  # pragma: no cover
	import cssutils as css_parser  # type: ignore

# this package
from dict2css.helpers import em, px, rem
from dict2css.serializer import CSSSerializer

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.3.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = [
		"IMPORTANT",
		"Style",
		"dumps",
		"dump",
		"loads",
		"load",
		"StyleSheet",
		"make_style",
		]

IMPORTANT = "important"
"""
The string ``'important'``.

.. latex:vspace:: 10px
"""

# Property = Union[Tuple[Union[str, int, None], str], str, int, None]
Property = Union[Sequence, str, int, None]

Style = Mapping[str, Property]
"""
Type annotation representing a style for :func:`~.make_style` and :func:`~.dumps`.

The keys are CSS properties.

The values can be either:

* A :class:`str`, :class:`float` or :py:obj:`None`, giving the value of the property.
* A :class:`tuple` of the property's value (as above) and the priority
  such as :data:`~.IMPORTANT` (which sets ``!important`` on the property).
"""


def dumps(
		styles: Mapping[str, Union[Style, Mapping]],
		*,
		indent: str = TAB,
		trailing_semicolon: bool = False,
		indent_closing_brace: bool = False,
		minify: bool = False,
		) -> str:
	r"""
	Construct a cascading style sheet from a dictionary.

	``styles`` is a mapping of CSS selector strings to styles, which map property names to their values:

	.. code-block:: python

		styles = {".wy-nav-content": {"max-width": (px(1200), IMPORTANT)}}
		print(dumps(styles))

	.. code-block:: css

		.wy-nav-content {
			max-width: 1200px !important
		}

	See the :py:obj:`~.Style` object for more information on the layout.

	The keys can also be media at-rules, with the values mappings of property names to their values:

	.. code-block:: python

		styles = {
			"@media screen and (min-width: 870px)": {
				".wy-nav-content": {"max-width": (px(1200), IMPORTANT)},
				},
			}
		print(dumps(styles))

	.. code-block:: css

		@media screen and (min-width: 870px) {
			.wy-nav-content {
				max-width: 1200px !important
			}
		}

	:param styles: A mapping of CSS selectors to styles.
	:param indent: The indent to use, such as a tab (``\t``), two spaces or four spaces.
	:param trailing_semicolon:  Whether to add a semicolon to the end of the final property.
	:param indent_closing_brace:
	:param minify: Minify the CSS. Overrides all other options.

	:return: The style sheet as a string.

	.. versionchanged:: 0.2.0  Added support for media at-rules.
	"""

	serializer = CSSSerializer(
			indent=indent,
			trailing_semicolon=trailing_semicolon,
			indent_closing_brace=indent_closing_brace,
			minify=minify,
			)

	stylesheet: str = ''

	with serializer.use():
		sheet = StyleSheet()

		for selector, style in styles.items():
			if selector.startswith("@media"):
				sheet.add_media_styles(selector.split("@media")[1].strip(), cast(Mapping[str, Style], style))
			elif selector.startswith('@'):
				raise NotImplementedError("Only @media at-rules are supported at this time.")
			else:
				sheet.add_style(selector, cast(Style, style))

		stylesheet = sheet.tostring()

	if not serializer.minify:
		stylesheet = stylesheet.replace('}', "}\n")

	return stylesheet


def dump(
		styles: Mapping[str, Union[Style, Mapping]],
		fp: Union[PathLike, IO],
		*,
		indent: str = TAB,
		trailing_semicolon: bool = False,
		indent_closing_brace: bool = False,
		minify: bool = False,
		) -> None:
	r"""
	Construct a style sheet from a dictionary and write it to ``fp``.

	.. code-block:: python

		styles = {".wy-nav-content": {"max-width": (px(1200), IMPORTANT)}}
		dump(styles, ...)

	.. code-block:: css

		.wy-nav-content {
			max-width: 1200px !important
		}

	See the :py:obj:`~.Style` object for more information on the layout.

	.. latex:clearpage::

	The keys can also be media at-rules, with the values mappings of property names to their values:

	.. code-block:: python

		styles = {
			"@media screen and (min-width: 870px)": {
				".wy-nav-content": {"max-width": (px(1200), IMPORTANT)},
				},
			}
		dump(styles, ...)

	.. code-block:: css

		@media screen and (min-width: 870px) {
			.wy-nav-content {
				max-width: 1200px !important
			}
		}

	:param styles: A mapping of CSS selectors to styles.
	:param fp: An open file handle, or the filename of a file to write to.
	:param indent: The indent to use, such as a tab (``\t``), two spaces or four spaces.
	:param trailing_semicolon:  Whether to add a semicolon to the end of the final property.
	:param indent_closing_brace:
	:param minify: Minify the CSS. Overrides all other options.

	.. versionchanged:: 0.2.0

		* ``fp`` now accepts :py:obj:`domdf_python_tools.typing.PathLike` objects,
		  representing the path of a file to write to.
		* Added support for media at-rules.
	"""

	css = dumps(
			styles,
			indent=indent,
			trailing_semicolon=trailing_semicolon,
			indent_closing_brace=indent_closing_brace,
			minify=minify,
			)

	if isinstance(fp, TextIOBase):
		fp.write(css)
	else:
		PathPlus(fp).write_clean(css)


def loads(styles: str) -> MutableMapping[str, MutableMapping[str, Any]]:
	r"""
	Parse a style sheet and return its dictionary representation.

	.. versionadded:: 0.2.0

	:param styles:

	:return: The style sheet as a dictionary.
	"""

	parser = css_parser.CSSParser(validate=False)
	stylesheet: css_parser.css.CSSStyleSheet = parser.parseString(styles)

	styles_dict: MutableMapping[str, MutableMapping[str, Any]] = {}

	def parse_style(style: css_parser.css.CSSStyleDeclaration) -> MutableMapping[str, Property]:
		style_dict: Dict[str, Property] = {}

		prop: css_parser.css.Property
		for prop in style.children():
			if prop.priority:
				style_dict[prop.name] = (prop.value, prop.priority)
			else:
				style_dict[prop.name] = prop.value

		return style_dict

	rule: css_parser.css.CSSRule
	for rule in stylesheet.cssRules:
		if isinstance(rule, css_parser.css.CSSStyleRule):
			styles_dict[rule.selectorText] = parse_style(rule.style)

		elif isinstance(rule, css_parser.css.CSSMediaRule):
			styles_dict[f"@media {rule.media.mediaText}"] = {}

			for child in rule.cssRules:
				styles_dict[f"@media {rule.media.mediaText}"][child.selectorText] = parse_style(child.style)

		else:
			raise NotImplementedError(rule)

	return styles_dict


def load(fp: Union[PathLike, IO]) -> MutableMapping[str, MutableMapping[str, Any]]:
	r"""
	Parse a cascading style sheet from the given file and return its dictionary representation.

	.. versionadded:: 0.2.0

	:param fp: An open file handle, or the filename of a file to write to.

	:return: The style sheet as a dictionary.
	"""

	if isinstance(fp, TextIOBase):
		styles = fp.read()
	else:
		styles = PathPlus(fp).read_text()

	return loads(styles)


class StyleSheet(css_parser.css.CSSStyleSheet):
	r"""
	Represents a CSS style sheet.

	.. raw:: latex

		\nopagebreak

	.. autosummary-widths:: 7/16

	"""

	def __init__(self):
		super().__init__(validating=False)

	def add(self, rule: css_parser.css.CSSRule) -> int:
		"""
		Add the ``rule`` to the style sheet.

		:param rule:
		:type rule: :class:`css_parser.css.CSSRule`
		"""

		return super().add(rule)

	def add_style(
			self,
			selector: str,
			styles: Style,
			) -> None:
		"""
		Add a style to the style sheet.

		:param selector:
		:param styles:
		"""

		self.add(make_style(selector, styles))

	def add_media_styles(
			self,
			media_query: str,
			styles: Mapping[str, Style],
			) -> None:
		"""
		Add a set of styles for a media query to the style sheet.

		.. versionadded:: 0.2.0

		:param media_query:
		:param styles:
		"""

		media = css_parser.css.CSSMediaRule(media_query)

		for selector, style in styles.items():
			media.add(make_style(selector, style))

		self.add(media)

	def tostring(self) -> str:
		"""
		Returns the style sheet as a string.
		"""

		return self.cssText.decode("UTF-8")


def make_style(selector: str, styles: Style) -> css_parser.css.CSSStyleRule:
	"""
	Create a CSS Style Rule from a dictionary.

	:param selector:
	:param styles:

	:rtype: :class:`css_parser.css.CSSStyleRule`
	"""

	style = css_parser.css.CSSStyleDeclaration()
	style.validating = False

	for name, properties in styles.items():
		if isinstance(properties, Sequence) and not isinstance(properties, str):
			style[name] = tuple(str(x) for x in properties)
		else:
			style[name] = str(properties)

	return css_parser.css.CSSStyleRule(selectorText=selector, style=style)
