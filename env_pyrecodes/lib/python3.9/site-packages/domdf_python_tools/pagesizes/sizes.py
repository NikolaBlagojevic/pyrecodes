#  !/usr/bin/env python
#
#  sizes.py
"""
Common pagesizes in point/pt.

.. TODO:: finish the list of the page sizes

.. |iso216| replace:: `ISO 216 <https://en.wikipedia.org/wiki/ISO_216>`__

Each pagesize is an instance of :class:`domdf_python_tools.pagesizes.PageSize`.
The following sizes are available:
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on reportlab.lib.pagesizes and reportlab.lib.units
#    www.reportlab.co.uk
#    Copyright ReportLab Europe Ltd. 2000-2017
#    Copyright (c) 2000-2018, ReportLab Inc.
#    All rights reserved.
#    Licensed under the BSD License
#
#  Includes data from en.wikipedia.org.
#  Licensed under the Creative Commons Attribution-ShareAlike License
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

__all__ = [
		"_4A0",
		"_2A0",
		"A0",
		"A1",
		"A2",
		"A3",
		"A4",
		"A5",
		"A6",
		"A7",
		"A8",
		"A9",
		"A10",
		"B0",
		"B1",
		"B2",
		"B3",
		"B4",
		"B5",
		"B6",
		"B7",
		"B8",
		"B9",
		"B10",
		"C0",
		"C1",
		"C2",
		"C3",
		"C4",
		"C5",
		"C6",
		"C7",
		"C8",
		"C9",
		"C10",
		"A2EXTRA",
		"A3EXTRA",
		"A3SUPER",
		"SUPERA3",
		"A4EXTRA",
		"A4SUPER",
		"SUPERA4",
		"A4LONG",
		"A5EXTRA",
		"SOB5EXTRA",
		"LETTER",
		"LEGAL",
		"TABLOID",
		"ELEVENSEVENTEEN",
		"JUNIOR_LEGAL",
		"HALF_LETTER",
		"GOV_LETTER",
		"GOV_LEGAL",
		"LEDGER",
		"EMPEROR",
		"QUAD_ROYAL",
		"QUAD_DEMY",
		"ANTIQUARIAN",
		"GRAND_EAGLE",
		"DOUBLE_ELEPHANT",
		"ATLAS",
		"DOUBLE_ROYAL",
		"COLOMBIER",
		"DOUBLE_DEMY_US",
		"DOUBLE_DEMY",
		"DOUBLE_DEMY_UK",
		"IMPERIAL",
		"DOUBLE_LARGE_POST",
		"ELEPHANT",
		"PRINCESS",
		"CARTRIDGE",
		"ROYAL",
		"SHEET",
		"HALF_POST",
		"DOUBLE_POST",
		"SUPER_ROYAL",
		"BROADSHEET",
		"MEDIUM_US",
		"MEDIUM_UK",
		"DEMY",
		"COPY_DRAUGHT",
		"LARGE_POST_US",
		"LARGE_POST_UK",
		"POST_US",
		"POST_UK",
		"CROWN",
		"PINCHED_POST",
		"FOOLSCAP_US",
		"FOOLSCAP_UK",
		"SMALL_FOOLSCAP",
		"BRIEF",
		"POTT",
		"QUARTO_US",
		"EXECUTIVE",
		"MONARCH",
		"FOLIO",
		"FOOLSCAP_FOLIO",
		"QUARTO",
		"QUARTO_UK",
		"KINGS",
		"DUKES",
		"ID_1",
		"ID_2",
		"ID_3",
		"ID_000",
		]

# this package
from .classes import Size_inch, Size_mm

# ISO 216 standard paper sizes; see eg https://en.wikipedia.org/wiki/ISO_216
# also http://www.printernational.org/iso-paper-sizes.php

_4A0 = Size_mm(1682, 2378).to_pt()  #: |iso216| 4A0 Paper
_2A0 = Size_mm(1189, 1682).to_pt()  #: |iso216| 2A0 Paper
A0 = Size_mm(841, 1189).to_pt()  #: |iso216| A0 Paper
A1 = Size_mm(594, 841).to_pt()  #: |iso216| A1 Paper
A2 = Size_mm(420, 594).to_pt()  #: |iso216| A2 Paper
A3 = Size_mm(297, 420).to_pt()  #: |iso216| A3 Paper
A4 = Size_mm(210, 297).to_pt()  #: |iso216| A3 Paper
A5 = Size_mm(148, 210).to_pt()  #: |iso216| A5 Paper
A6 = Size_mm(105, 148).to_pt()  #: |iso216| A6 Paper
A7 = Size_mm(74, 105).to_pt()  #: |iso216| A7 Paper
A8 = Size_mm(52, 74).to_pt()  #: |iso216| A8 Paper
A9 = Size_mm(37, 52).to_pt()  #: |iso216| A0 Paper
A10 = Size_mm(26, 37).to_pt()  #: |iso216| A10 Paper

# _W, _H = (21 * cm, 29.7 * cm)
# A6 = (_W * .5, _H * .5)
# A5 = (_H * .5, _W)
# A4 = (_W, _H)
# A3 = (_H, _W * 2)
# A2 = (_W * 2, _H * 2)
# A1 = (_H * 2, _W * 4)
# A0 = (_W * 4, _H * 4)

B0 = Size_mm(1000, 1414)  #: |iso216| B0 Paper
B1 = Size_mm(707, 1000)  #: |iso216| B1 Paper
B2 = Size_mm(500, 707)  #: |iso216| B2 Paper
B3 = Size_mm(353, 500)  #: |iso216| B3 Paper
B4 = Size_mm(250, 353)  #: |iso216| B4 Paper
B5 = Size_mm(176, 250)  #: |iso216| B5 Paper
B6 = Size_mm(125, 176)  #: |iso216| B6 Paper
B7 = Size_mm(88, 125)  #: |iso216| B7 Paper
B8 = Size_mm(62, 88)  #: |iso216| B8 Paper
B9 = Size_mm(44, 62)  #: |iso216| B9 Paper
B10 = Size_mm(31, 44)  #: |iso216| B10 Paper

# _BW, _BH = (25 * cm, 35.3 * cm)
# B6 = (_BW * .5, _BH * .5)
# B5 = (_BH * .5, _BW)
# B4 = (_BW, _BH)
# B3 = (_BH * 2, _BW)
# B2 = (_BW * 2, _BH * 2)
# B1 = (_BH * 4, _BW * 2)
# B0 = (_BW * 4, _BH * 4)

C0 = Size_mm(917, 1297)  #: |iso216| C0 Paper
C1 = Size_mm(648, 917)  #: |iso216| C1 Paper
C2 = Size_mm(458, 648)  #: |iso216| C2 Paper
C3 = Size_mm(324, 458)  #: |iso216| C3 Paper
C4 = Size_mm(229, 324)  #: |iso216| C4 Paper
C5 = Size_mm(162, 229)  #: |iso216| C5 Paper
C6 = Size_mm(114, 162)  #: |iso216| C6 Paper
C7 = Size_mm(81, 114)  #: |iso216| C7 Paper
C8 = Size_mm(57, 81)  #: |iso216| C8 Paper
C9 = Size_mm(40, 57)  #: |iso216| C9 Paper
C10 = Size_mm(28, 40)  #: |iso216| C10 Paper

A2EXTRA = Size_mm(445, 619)  #: A2 Extra Paper
A3EXTRA = Size_mm(322, 445)  #: A3 Extra Paper
A3SUPER = Size_mm(305, 508)  #: A3 Super Paper (different to (Super A3)
SUPERA3 = Size_mm(305, 487)  #: Super A3 Paper (different to A3 Super)
A4EXTRA = Size_mm(235, 322)  #: A4 Extra Paper
A4SUPER = Size_mm(229, 322)  #: A4 Super Paper (different to (Super A4)
SUPERA4 = Size_mm(227, 356)  #: Super A3 Paper (different to A4 Super)
A4LONG = Size_mm(210, 348)  #: A4 Long Paper
A5EXTRA = Size_mm(173, 235)  #: A4 Extra Paper
SOB5EXTRA = Size_mm(202, 276)  #: SO B5 Extra Paper

# American paper sizes
LETTER = Size_inch(8.5, 11).to_pt()  #: North American "Letter" Paper
LEGAL = Size_inch(8.5, 14).to_pt()  #: North American "Legal" Paper
TABLOID = ELEVENSEVENTEEN = Size_inch(11, 17).to_pt()

# From https://en.wikipedia.org/wiki/Paper_size
JUNIOR_LEGAL = Size_inch(5, 8).to_pt()  #: Junior Legal
HALF_LETTER = Size_inch(5.5, 8).to_pt()  #: Half Letter
GOV_LETTER = Size_inch(8, 10.5).to_pt()  #: Government Letter
GOV_LEGAL = Size_inch(8.5, 13).to_pt()  #: Government Legal
LEDGER = Size_inch(17, 11).to_pt()  #: Ledger
EMPEROR = Size_inch(48, 72).to_pt()  #: Emperor
QUAD_ROYAL = Size_inch(40, 50).to_pt()  #: Quad Royal
QUAD_DEMY = Size_inch(35, 40).to_pt()  #:
ANTIQUARIAN = Size_inch(31, 53).to_pt()  #:
GRAND_EAGLE = Size_inch(28.75, 42).to_pt()  #:
DOUBLE_ELEPHANT = Size_inch(26.75, 40).to_pt()  #:
ATLAS = Size_inch(26, 34).to_pt()  #:
DOUBLE_ROYAL = Size_inch(25, 40).to_pt()  #:
COLOMBIER = Size_inch(23.5, 34.5).to_pt()  #:
DOUBLE_DEMY_US = Size_inch(22.5, 35.5).to_pt()  #:
DOUBLE_DEMY = DOUBLE_DEMY_UK = Size_inch(22.5, 35).to_pt()  #:
IMPERIAL = Size_inch(22, 30).to_pt()  #:
DOUBLE_LARGE_POST = Size_inch(21, 33).to_pt()  #:
ELEPHANT = Size_inch(23, 28).to_pt()  #:
PRINCESS = Size_inch(22.5, 28).to_pt()  #:
CARTRIDGE = Size_inch(21, 26).to_pt()  #:
ROYAL = Size_inch(20, 25).to_pt()  #:
SHEET = HALF_POST = Size_inch(19.5, 23.5).to_pt()  #:
DOUBLE_POST = Size_inch(19, 30.5).to_pt()  #:
SUPER_ROYAL = Size_inch(19, 27).to_pt()  #:
BROADSHEET = Size_inch(18, 24).to_pt()  #:
MEDIUM_US = Size_inch(17.5, 23).to_pt()  #:
MEDIUM_UK = Size_inch(18, 23).to_pt()  #:
DEMY = Size_inch(17.5, 22.5).to_pt()  #:
COPY_DRAUGHT = Size_inch(16, 20).to_pt()  #:
LARGE_POST_US = Size_inch(15.5, 20).to_pt()  #:
LARGE_POST_UK = Size_inch(16.5, 21).to_pt()  #:
POST_US = Size_inch(15.5, 19.35).to_pt()  #:
POST_UK = Size_inch(15.5, 19.5).to_pt()  #:
CROWN = Size_inch(15, 20).to_pt()  #:
PINCHED_POST = Size_inch(14.75, 18.5).to_pt()  #:
FOOLSCAP_US = Size_inch(13.5, 17).to_pt()  #:
FOOLSCAP_UK = Size_inch(13, 18).to_pt()  #:
SMALL_FOOLSCAP = Size_inch(13.35, 16.5).to_pt()  #:
BRIEF = Size_inch(13.5, 16).to_pt()  #:
POTT = Size_inch(12.5, 15).to_pt()  #:
QUARTO_US = Size_inch(9, 11).to_pt()  #:
EXECUTIVE = MONARCH = Size_inch(7.35, 10.5).to_pt()  #:
FOLIO = FOOLSCAP_FOLIO = Size_inch(8, 13).to_pt()  #:
QUARTO = QUARTO_UK = Size_inch(8, 10).to_pt()  #:
# IMPERIAL = Size_inch(7*inch, 9*inch).to_pt()  there are two of these?
KINGS = Size_inch(6.5, 8).to_pt()  #:
DUKES = Size_inch(5.5, 7).to_pt()  #:

# https://en.wikipedia.org/wiki/ISO/IEC_7810
ID_1 = Size_mm(85.60, 53.98).to_pt()  #: Most banking cards and ID cards
ID_2 = Size_mm(105, 74).to_pt()  #: French and other ID cards; Visas
ID_3 = Size_mm(125, 88).to_pt()  #: US government ID cards
ID_000 = Size_mm(25, 15).to_pt()  #: SIM cards
