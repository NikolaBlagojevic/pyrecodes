#!/usr/bin/env python
#
#  words.py
"""
Functions for working with (English) words.

.. versionadded:: 0.4.5
"""
#
#  Copyright © 2020-2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  List of 10000 English words from https://github.com/first20hours/google-10000-english/
#  Derived from the Google Web Trillion Word Corpus,
#      as described by Thorsten Brants and Alex Franz,
#      and distributed by the Linguistic Data Consortium.
#
#  Subsets of this corpus distributed by Peter Novig.
#  Corpus editing and cleanup by Josh Kaufman.
#

# stdlib
import functools
import random
import re
import sys
from gettext import ngettext
from reprlib import recursive_repr
from string import ascii_lowercase, ascii_uppercase
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Tuple

# this package
import domdf_python_tools
from domdf_python_tools.compat import PYPY
from domdf_python_tools.doctools import prettify_docstrings

__all__ = [
		"greek_uppercase",
		"greek_lowercase",
		"get_words_list",
		"get_random_word",
		"make_font",
		"Font",
		"SERIF_BOLD_LETTERS",
		"SERIF_ITALIC_LETTERS",
		"SERIF_BOLD_ITALIC_LETTERS",
		"SANS_SERIF_LETTERS",
		"SANS_SERIF_BOLD_LETTERS",
		"SANS_SERIF_ITALIC_LETTERS",
		"SANS_SERIF_BOLD_ITALIC_LETTERS",
		"SCRIPT_LETTERS",
		"FRAKTUR_LETTERS",
		"MONOSPACE_LETTERS",
		"DOUBLESTRUCK_LETTERS",
		"alpha_sort",
		"as_text",
		"word_join",
		"TAB",
		"CR",
		"LF",
		"Plural",
		"PluralPhrase",
		"truncate_string",
		]

ascii_digits = "0123456789"
"""
ASCII numbers.

.. versionadded:: 0.7.0
"""

greek_uppercase = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡϴΣΤΥΦΧΨΩ"
"""
Uppercase Greek letters.

.. versionadded:: 0.7.0
"""

greek_lowercase = "αβγδεζηθικλμνξοπρςστυφχψω∂ϵϑϰϕϱϖ"
"""
Lowercase Greek letters.

.. versionadded:: 0.7.0
"""


@functools.lru_cache()
def get_words_list(min_length: int = 0, max_length: int = -1) -> List[str]:
	"""
	Returns the list of words, optionally only those whose length is between
	``min_length`` and ``max_length``.

	.. versionadded:: 0.4.5

	:param min_length: The minimum length of the words to return
	:param max_length: The maximum length of the words to return. A value of ``-1`` indicates no upper limit.
	:no-default max_length:

	:return: The list of words meeting the above specifiers.
	"""  # noqa: D400

	# this package
	from domdf_python_tools.compat import importlib_resources

	words: str = importlib_resources.read_text("domdf_python_tools", "google-10000-english-no-swears.txt")
	words_list: List[str] = words.splitlines()

	if min_length > 0 or max_length != -1:
		if max_length == -1:
			words_list = [word for word in words_list if min_length <= len(word)]
		else:
			words_list = [word for word in words_list if min_length <= len(word) <= max_length]

	return words_list


def get_random_word(min_length: int = 0, max_length: int = -1) -> str:
	"""
	Returns a random word, optionally only one whose length
	is between ``min_length`` and ``max_length``.

	.. versionadded:: 0.4.5

	:param min_length: The minimum length of the words to return
	:param max_length: The maximum length of the words to return. A value of ``-1`` indicates no upper limit.
	:no-default max_length:

	:return: A random word meeting the above specifiers.
	"""  # noqa: D400

	words_list = get_words_list(min_length=min_length, max_length=max_length)

	return random.choice(words_list)


# _default_unicode_sort_order: str = "".join(sorted(chr(i) for i in range(sys.maxunicode + 1)))


def alpha_sort(
		iterable: Iterable[str],
		alphabet: Iterable[str],  # = _default_unicode_sort_order
		reverse: bool = False,
		) -> List[str]:
	"""
	Sorts a list of strings using a custom alphabet.

	.. versionadded:: 0.7.0

	:param iterable: The strings to sort.
	:param alphabet: The custom alphabet to use for sorting.
	:param reverse:
	"""

	alphabet_ = list(alphabet)

	try:
		return sorted(iterable, key=lambda attr: [alphabet_.index(letter) for letter in attr], reverse=reverse)
	except ValueError as e:
		m = re.match(r"'(.*)' is not in list", str(e))
		if m:
			raise ValueError(f"The character {m.group(1)!r} was not found in the alphabet.") from None
		else:  # pragma: no cover
			raise e


class Font(Dict[str, str]):
	"""
	Represents a Unicode pseudo-font.

	Mapping of ASCII letters to their equivalents in the pseudo-font.

	Individual characters can be converted using the :meth:`Font.get <domdf_python_tools.words.Font.get>`
	method or the ``getitem`` syntax. Entire strings can be converted by calling the
	:class:`~domdf_python_tools.words.Font` object and passing the string as the first argument.
	"""

	def __getitem__(self, char: str) -> str:
		"""
		Returns the given character in this font.

		If the character is not found in this font the character is returned unchanged.

		:param char: The character to convert.
		"""

		char = str(char)

		if char not in self:
			return str(char)

		else:
			return str(super().__getitem__(char))

	def __call__(self, text: str) -> str:
		"""
		Returns the given text in this font.

		:param text:
		"""

		return ''.join(self[char] for char in text)

	def get(self, char: str, default: Optional[str] = None) -> str:  # type: ignore
		"""
		Returns the given character in this font.

		If the character is not found in this font the character is returned unchanged or,
		if a value for ``default`` is provided, that is returned instead.

		:param char: The character to convert.
		:param default: Optional default value.
		"""

		if char not in self and default is not None:
			return str(default)
		else:
			return self[char]


def make_font(
		uppers: Iterable[str],
		lowers: Iterable[str],
		digits: Optional[Iterable[str]] = None,
		greek_uppers: Optional[Iterable[str]] = None,
		greek_lowers: Optional[Iterable[str]] = None,
		) -> Font:
	"""
	Returns a dictionary mapping ASCII alphabetical characters and digits to the Unicode equivalents
	in a different pseudo-font.

	.. versionadded:: 0.7.0

	:param uppers: Iterable of uppercase letters (A-Z, 26 characters).
	:param lowers: Iterable of lowercase letters (a-z, 26 characters).
	:param digits: Optional iterable of digits (0-9).
	:param greek_uppers: Optional iterable of uppercase Greek letters (A-Ω, 25 characters).
	:param greek_lowers: Optional iterable of lowercase Greek letters (α-ϖ, 32 characters).
	"""  # noqa: D400

	font = Font({
			**dict(zip(ascii_uppercase, uppers)),
			**dict(zip(ascii_lowercase, lowers)),
			})

	if digits:
		font.update({char: unichar for char, unichar in zip(ascii_digits, digits)})

	if greek_uppers:
		font.update({char: unichar for char, unichar in zip(greek_uppercase, greek_uppers)})

	if greek_lowers:
		font.update({char: unichar for char, unichar in zip(greek_lowercase, greek_lowers)})

	return font


#: Bold Serif letters (uppercase)
SERIF_BOLD_UPPER = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
#: Bold Serif letters (lowercase)
SERIF_BOLD_LOWER = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
#: Bold Serif digits
SERIF_BOLD_DIGITS = "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
#: Bold Serif Greek letters (uppercase)
SERIF_BOLD_GREEK_UPPER = "𝚨𝚩𝚪𝚫𝚬𝚭𝚮𝚯𝚰𝚱𝚲𝚳𝚴𝚵𝚶𝚷𝚸𝚹𝚺𝚻𝚼𝚽𝚾𝚿𝛀"
#: Bold Serif Greek letters (lowercase)
SERIF_BOLD_GREEK_LOWER = "𝛂𝛃𝛄𝛅𝛆𝛇𝛈𝛉𝛊𝛋𝛌𝛍𝛎𝛏𝛐𝛑𝛒𝛓𝛔𝛕𝛖𝛗𝛘𝛙𝛚𝛛𝛜𝛝𝛞𝛟𝛠𝛡"

SERIF_BOLD_LETTERS = make_font(
		uppers=SERIF_BOLD_UPPER,
		lowers=SERIF_BOLD_LOWER,
		digits=SERIF_BOLD_DIGITS,
		greek_uppers=SERIF_BOLD_GREEK_UPPER,
		greek_lowers=SERIF_BOLD_GREEK_LOWER,
		)
"""
Bold Serif :class:`~domdf_python_tools.words.Font`.

This font includes numbers and Greek letters.

.. versionadded:: 0.7.0
"""

#: Italic Serif letters (uppercase)
SERIF_ITALIC_UPPER = "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍"
#: Italic Serif letters (lowercase)
SERIF_ITALIC_LOWER = "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧"
#: Italic Serif Greek letters (uppercase)
SERIF_ITALIC_GREEK_UPPER = "𝛢𝛣𝛤𝛥𝛦𝛧𝛨𝛩𝛪𝛫𝛬𝛭𝛮𝛯𝛰𝛱𝛲𝛳𝛴𝛵𝛶𝛷𝛸𝛹𝛺𝛻"
#: Italic Serif Greek letters (lowercase)
SERIF_ITALIC_GREEK_LOWER = "𝛼𝛽𝛾𝛿𝜀𝜁𝜂𝜃𝜄𝜅𝜆𝜇𝜈𝜉𝜊𝜋𝜌𝜍𝜎𝜏𝜐𝜑𝜒𝜓𝜔𝜕𝜖𝜗𝜘𝜙𝜚𝜛"

SERIF_ITALIC_LETTERS = make_font(
		uppers=SERIF_ITALIC_UPPER,
		lowers=SERIF_ITALIC_LOWER,
		greek_uppers=SERIF_ITALIC_GREEK_UPPER,
		greek_lowers=SERIF_ITALIC_GREEK_LOWER,
		)
"""
Italic Serif :class:`~domdf_python_tools.words.Font`.

This font includes Greek letters.

.. versionadded:: 0.7.0
"""

#: Bold and Italic Serif letters (uppercase)
SERIF_BOLD_ITALIC_UPPER = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁"
#: Bold and Italic Serif letters (lowercase)
SERIF_BOLD_ITALIC_LOWER = "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛"
#: Bold and Italic Serif Greek letters (uppercase)
SERIF_BOLD_ITALIC_GREEK_UPPER = "𝜜𝜝𝜞𝜟𝜠𝜡𝜢𝜣𝜤𝜥𝜦𝜧𝜨𝜩𝜪𝜫𝜬𝜭𝜮𝜯𝜰𝜱𝜲𝜳𝜴𝜵"
#: Bold and Italic Serif Greek letters (lowercase)
SERIF_BOLD_ITALIC_GREEK_LOWER = "𝜶𝜷𝜸𝜹𝜺𝜻𝜼𝜽𝜾𝜿𝝀𝝁𝝂𝝃𝝄𝝅𝝆𝝇𝝈𝝉𝝊𝝋𝝌𝝍𝝎𝝏𝝐𝝑𝝒𝝓𝝔𝝕"

SERIF_BOLD_ITALIC_LETTERS = make_font(
		uppers=SERIF_BOLD_ITALIC_UPPER,
		lowers=SERIF_BOLD_ITALIC_LOWER,
		greek_uppers=SERIF_BOLD_ITALIC_GREEK_UPPER,
		greek_lowers=SERIF_BOLD_ITALIC_GREEK_LOWER,
		)
"""
Bold and Italic Serif :class:`~domdf_python_tools.words.Font`.

This font includes Greek letters.

.. versionadded:: 0.7.0
"""

#: Normal Sans-Serif letters (uppercase)
SANS_SERIF_UPPER = "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹"
#: Normal Sans-Serif letters (lowercase)
SANS_SERIF_LOWER = "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓"
#: Normal Sans-Serif digits
SANS_SERIF_DIGITS = "𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"

SANS_SERIF_LETTERS = make_font(
		uppers=SANS_SERIF_UPPER,
		lowers=SANS_SERIF_LOWER,
		digits=SANS_SERIF_DIGITS,
		)
"""
Normal Sans-Serif :class:`~domdf_python_tools.words.Font`.

This font includes numbers.

.. versionadded:: 0.7.0
"""

#: Bold Sans-Serif letters (uppercase)
SANS_SERIF_BOLD_UPPER = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
#: Bold Sans-Serif letters (lowercase)
SANS_SERIF_BOLD_LOWER = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
#: Bold Sans-Serif digits
SANS_SERIF_BOLD_DIGITS = "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"

SANS_SERIF_BOLD_LETTERS = make_font(
		uppers=SANS_SERIF_BOLD_UPPER,
		lowers=SANS_SERIF_BOLD_LOWER,
		digits=SANS_SERIF_BOLD_DIGITS,
		)
"""
Bold Sans-Serif :class:`~domdf_python_tools.words.Font`.

This font includes numbers.

.. versionadded:: 0.7.0
"""

#: Italic Sans-Serif letters (uppercase)
SANS_SERIF_ITALIC_UPPER = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
#: Italic Sans-Serif letters (lowercase)
SANS_SERIF_ITALIC_LOWER = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"

SANS_SERIF_ITALIC_LETTERS = make_font(
		uppers=SANS_SERIF_ITALIC_UPPER,
		lowers=SANS_SERIF_ITALIC_LOWER,
		)
"""
Italic Sans-Serif :class:`~domdf_python_tools.words.Font`.

.. versionadded:: 0.7.0
"""

#: Bold and Italic Sans-Serif letters (uppercase)
SANS_SERIF_BOLD_ITALIC_UPPER = "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
#: Bold and Italic Sans-Serif letters (lowercase)
SANS_SERIF_BOLD_ITALIC_LOWER = "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
#: Bold and Italic Sans-Serif letters (uppercase)
SANS_SERIF_BOLD_ITALIC_GREEK_UPPER = "𝞐𝞑𝞒𝞓𝞔𝞕𝞖𝞗𝞘𝞙𝞚𝞛𝞜𝞝𝞞𝞟𝞠𝞡𝞢𝞣𝞤𝞥𝞦𝞧𝞨𝞩"
#: Bold and Italic Sans-Serif letters (lowercase)
SANS_SERIF_BOLD_ITALIC_GREEK_LOWER = "𝞪𝞫𝞬𝞭𝞮𝞯𝞰𝞱𝞲𝞳𝞴𝞵𝞶𝞷𝞸𝞹𝞺𝞻𝞼𝞽𝞾𝞿𝟀𝟁𝟂𝟃𝟄𝟅𝟆𝟇𝟈𝟉"

SANS_SERIF_BOLD_ITALIC_LETTERS = make_font(
		uppers=SANS_SERIF_BOLD_ITALIC_UPPER,
		lowers=SANS_SERIF_BOLD_ITALIC_LOWER,
		greek_uppers=SANS_SERIF_BOLD_ITALIC_GREEK_UPPER,
		greek_lowers=SANS_SERIF_BOLD_ITALIC_GREEK_LOWER,
		)
"""
Bold and Italic Sans-Serif :class:`~domdf_python_tools.words.Font`.

This font includes Greek letters.

.. versionadded:: 0.7.0
"""

#: Script letters (uppercase)
SCRIPT_UPPER = "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
#: Script letters (lowercase)
SCRIPT_LOWER = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"

SCRIPT_LETTERS = make_font(SCRIPT_UPPER, SCRIPT_LOWER)
"""
Script :class:`~domdf_python_tools.words.Font`.

.. versionadded:: 0.7.0
"""

#: Fraktur letters (uppercase)
FRAKTUR_UPPER = "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
#: Fraktur letters (lowercase)
FRAKTUR_LOWER = "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"

FRAKTUR_LETTERS = make_font(FRAKTUR_UPPER, FRAKTUR_LOWER)
"""
Fraktur :class:`~domdf_python_tools.words.Font`.

.. versionadded:: 0.7.0
"""

#: Monospace letters (uppercase)
MONOSPACE_UPPER = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
#: Monospace letters (lowercase)
MONOSPACE_LOWER = "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"
#: Monospace digits
MONOSPACE_DIGITS = "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"

MONOSPACE_LETTERS = make_font(MONOSPACE_UPPER, MONOSPACE_LOWER, MONOSPACE_DIGITS)
"""
Monospace :class:`~domdf_python_tools.words.Font`.

This font includes numbers.

.. versionadded:: 0.7.0
"""

#: Doublestruck letters (uppercase)
DOUBLESTRUCK_UPPER = "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ"
#: Doublestruck letters (lowercase)
DOUBLESTRUCK_LOWER = "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫"
#: Doublestruck digits
DOUBLESTRUCK_DIGITS = "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"

DOUBLESTRUCK_LETTERS = make_font(DOUBLESTRUCK_UPPER, DOUBLESTRUCK_LOWER, DOUBLESTRUCK_DIGITS)
"""
Doublestruck :class:`~domdf_python_tools.words.Font`.

This font includes numbers.

.. versionadded:: 0.7.0
"""


def as_text(value: Any) -> str:
	"""
	Convert the given value to a string. :py:obj:`None` is converted to ``''``.

	:param value: The value to convert to a string.

	:rtype:

	.. versionchanged:: 0.8.0

		Moved from :mod:`domdf_python_tools.utils`.
	"""

	if value is None:
		return ''

	return str(value)


def word_join(
		iterable: Iterable[str],
		use_repr: bool = False,
		oxford: bool = False,
		delimiter: str = ',',
		connective: str = "and",
		) -> str:
	"""
	Join the given list of strings in a natural manner, with 'and' to join the last two elements.

	:param iterable:
	:param use_repr: Whether to join the ``repr`` of each object.
	:param oxford: Whether to use an oxford comma when joining the last two elements.
	:default oxford: :py:obj:`False`. Always :py:obj:`False` if there are fewer than three elements
	:param delimiter: A single character to use between the words.
	:param connective: The connective to join the final two words with.

	:rtype:

	.. versionchanged:: 0.11.0

		Added ``delimiter`` and ``connective`` arguments.
	"""

	delimiter = f"{delimiter} "

	if use_repr:
		words = [repr(w) for w in iterable]
	else:
		words = list(iterable)

	if len(words) == 0:
		return ''
	elif len(words) == 1:
		return words[0]
	elif len(words) == 2:
		return f" {connective} ".join(words)
	else:
		if oxford:
			return delimiter.join(words[:-1]) + f"{delimiter}{connective} {words[-1]}"
		else:
			return delimiter.join(words[:-1]) + f" {connective} {words[-1]}"


TAB = '\t'
"""
A literal ``TAB`` (``\\t``) character for use in f-strings.

.. versionadded:: 1.3.0
"""

CR = '\r'
"""
The carriage return character (``\\r``) for use in f-strings.

.. versionadded:: 1.3.0
"""

LF = '\n'
"""
The newline character (``\\n``) for use in f-strings.

.. versionadded:: 1.3.0
"""

_docs = domdf_python_tools.__docs


@prettify_docstrings
class Plural(functools.partial):
	"""
	Represents a word as its singular and plural.

	.. versionadded:: 2.0.0

	:param singular: The singular form of the word.
	:param plural: The plural form of the word.

	.. code-block:: python

		>>> cow = Plural("cow", "cows")
		>>> n = 1
		>>> print(f"The farmer has {n} {cow(n)}.")
		The farmer has 1 cow.
		>>> n = 2
		>>> print(f"The farmer has {n} {cow(n)}.")
		The farmer has 2 cows.
		>>> n = 3
		>>> print(f"The farmer has {n} {cow(n)}.")
		The farmer has 3 cows.
	"""

	if _docs:  # pragma: no cover

		def __init__(self, singular: str, plural: str):
			pass

		def __call__(self, n: int) -> str:  # type: ignore
			"""
			Returns either the singular or plural form of the word depending on the value of ``n``.

			:param n:
			"""

	# if PYPY:  # pragma: no cover (!PyPy)
	if PYPY and sys.version_info < (3, 9):  # pragma: no cover (!PyPy)

		def __init__(self, singular: str, plural: str):
			super().__init__(ngettext, singular, plural)  # type: ignore[call-arg]
	else:  # pragma: no cover (!CPython)

		def __new__(cls, singular: str, plural: str):  # noqa: D102
			return functools.partial.__new__(cls, ngettext, singular, plural)

	@recursive_repr()
	def __repr__(self):
		qualname = type(self).__qualname__
		args: List[str] = []
		args.extend(repr(x) for x in self.args)
		args.extend(f"{k}={v!r}" for (k, v) in self.keywords.items())
		return f"{qualname}({', '.join(args)})"


@prettify_docstrings
class PluralPhrase(NamedTuple):
	"""
	Represents a phrase which varies depending on a numerical count.

	.. versionadded:: 3.3.0

	:param template: The phrase template.
	:param words: The words to insert into the template.

	For example, consider the phase::

		The proposed changes are to ...

	The "phrase template" would be:

	.. code-block:: python

		"The proposed {} {} to ..."

	and the two words to insert are:

	.. code-block:: python

		Plural("change", "changes")
		Plural("is", "are")

	The phrase is constructed as follows:

	.. code-block:: python

		>>> phrase = PluralPhrase(
		...     "The proposed {} {} to ...",
		...     (Plural("change", "changes"), Plural("is", "are"))
		... )
		>>> phrase(1)
		'The proposed change is to ...'
		>>> phrase(2)
		'The proposed changes are to ...'

	The phrase template can use any `valid syntax`_ for :meth:`str.format`,
	except for keyword arguments. The exception if the keyword ``n``,
	which is replaced with the count (e.g. ``2``) passed in when the phrase is constructed.
	For example:

	.. code-block:: python

		>>> phrase2 = PluralPhrase("The farmer has {n} {0}.", (Plural("cow", "cows"), ))
		>>> phrase2(2)
		'The farmer has 2 cows.'

	.. _valid syntax: https://docs.python.org/3/library/string.html#formatstrings

	"""

	template: str
	words: Tuple[Plural, ...]

	def __call__(self, n: int) -> str:  # noqa: TYP004  # TODO
		"""
		Construct the phrase based on the value of ``n``.

		:param n:
		"""

		plural_words = [x(n) for x in self.words]
		return self.template.format(*plural_words, n=n)


@functools.lru_cache()
def _slice_end(max_length: int, ending: str = "...") -> slice:
	slice_end = max_length - len(ending)
	return slice(slice_end)


def truncate_string(string: str, max_length: int, ending: str = "...") -> str:
	"""
	Truncate a string to ``max_length`` characters, and put ``ending`` on the end.

	The truncated string is further truncated by the length of ``ending`` so the returned string is no more then ``max_length``.

	.. versionadded:: 3.3.0

	:param string:
	:param max_length:
	:param ending:
	"""

	string_length = len(string)

	if string_length > max_length:
		return string[_slice_end(max_length, ending)] + ending
	else:
		return string
