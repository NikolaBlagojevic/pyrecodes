#  !/usr/bin/env python
#
#  classes.py
"""
Classes representing pagesizes.
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

# stdlib
from collections import namedtuple
from typing import List, Tuple

# this package
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.typing import AnyNumber

# this package
from .units import Unit, _rounders, cm, inch, mm, pica, pt, um
from .utils import convert_from

__all__ = [
		"BaseSize",
		"Size_mm",
		"Size_inch",
		"Size_cm",
		"Size_um",
		"Size_pica",
		"PageSize",
		]


@prettify_docstrings
class BaseSize(namedtuple("__BaseSize", "width, height")):
	"""
	Base class namedtuple representing a page size, in point.
	"""

	__slots__: List[str] = []
	_unit: Unit = pt

	#: The page width.
	width: Unit

	#: The page height.
	height: Unit

	def __new__(cls, width: AnyNumber, height: AnyNumber):
		"""
		Create a new :class:`~.BaseSize` object.

		:param width: The page width.
		:param height: The page height.
		"""

		return super().__new__(
				cls,
				cls._unit(width),
				cls._unit(height),
				)

	def __str__(self) -> str:
		return f"{self.__class__.__name__}(width={_rounders(self.width, '0')}, height={_rounders(self.height, '0')})"

	@classmethod
	def from_pt(cls, size: Tuple[float, float]):
		"""
		Create a :class:`~domdf_python_tools.pagesizes.classes.BaseSize` object from a
		page size in point.

		:param size: The size, in point, to convert from.

		:rtype: A subclass of :class:`~domdf_python_tools.pagesizes.classes.BaseSize`
		"""  # noqa: D400

		assert isinstance(size, PageSize)

		return cls(cls._unit.from_pt(size[0]), cls._unit.from_pt(size[1]))

	@classmethod
	def from_size(cls, size: Tuple[AnyNumber, AnyNumber]) -> "BaseSize":
		"""
		Create a :class:`~domdf_python_tools.pagesizes.classes.BaseSize` object from a tuple.
		"""

		return cls(*size)

	def is_landscape(self) -> bool:
		"""
		Returns whether the page is in the landscape orientation.
		"""

		return self.width >= self.height

	def is_portrait(self) -> bool:
		"""
		Returns whether the page is in the portrait orientation.
		"""

		return self.width < self.height

	def is_square(self) -> bool:
		"""
		Returns whether the given pagesize is square.
		"""

		return self.width == self.height

	def landscape(self) -> "BaseSize":
		"""
		Returns the pagesize in landscape orientation.
		"""

		if self.is_portrait():
			return self.__class__(self.height, self.width)
		else:
			return self

	def portrait(self) -> "BaseSize":
		"""
		Returns the pagesize in portrait orientation.
		"""

		if self.is_landscape():
			return self.__class__(self.height, self.width)
		else:
			return self

	def to_pt(self) -> "PageSize":
		"""
		Returns the page size in point.
		"""

		return PageSize(self.width.as_pt(), self.height.as_pt())


# TODO: conversion to Point for the __eq__ function in the below


class Size_mm(BaseSize):
	"""
	Represents a pagesize in millimeters.
	"""

	_unit = mm


class Size_inch(BaseSize):
	"""
	Represents a pagesize in inches.
	"""

	_unit = inch


class Size_cm(BaseSize):
	"""
	Represents a pagesize in centimeters.
	"""

	_unit = cm


class Size_um(BaseSize):
	"""
	Represents a pagesize in micrometers.
	"""

	_unit = um


class Size_pica(BaseSize):
	"""
	Represents a pagesize in pica.
	"""

	_unit = pica


class PageSize(BaseSize):
	"""
	Represents a pagesize in point.

	:param width: The page width
	:param height: The page height

	The pagesize can be converted to other units using the properties below.
	"""

	__slots__: List[str] = []

	def __new__(
			cls,
			width: AnyNumber,
			height: AnyNumber,
			unit: AnyNumber = pt,  # pylint: disable=used-before-assignment
			):
		"""
		Create a new :class:`~domdf_python_tools.pagesizes.classes.PageSize` object.

		:param width: The page width.
		:param height: The page height.
		:param unit:
		"""

		width, height = convert_from((width, height), unit)
		return super().__new__(cls, width, height)

	@property
	def pt(self) -> "PageSize":
		"""
		Returns the pagesize in pt.
		"""

		return self

	@property
	def inch(self) -> Size_inch:
		"""
		Returns the pagesize in inches.
		"""

		return Size_inch.from_pt(self)

	@property
	def cm(self) -> Size_cm:
		"""
		Returns the pagesize in centimeters.
		"""

		return Size_cm.from_pt(self)

	@property
	def mm(self) -> Size_mm:
		"""
		Returns the pagesize in millimeters.
		"""

		return Size_mm.from_pt(self)

	@property
	def um(self) -> Size_um:
		"""
		Returns the pagesize in micrometers.
		"""

		return Size_um.from_pt(self)

	µm = um

	@property
	def pc(self) -> Size_pica:
		"""
		Returns the pagesize in pica.
		"""

		return Size_pica.from_pt(self)

	pica = pc
