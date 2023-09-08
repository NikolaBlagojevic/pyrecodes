#!/usr/bin/env python
#
#  units.py
"""
Provides a variety of units for use with pagesizes.
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
import math
from decimal import ROUND_HALF_UP, Decimal
from typing import SupportsFloat, Union

# this package
from domdf_python_tools.doctools import prettify_docstrings

__all__ = [
		"pt",
		"inch",
		"cm",
		"mm",
		"um",
		"pc",
		"pica",
		"Unit",
		"Unitpt",
		"UnitInch",
		"Unitcm",
		"Unitmm",
		"Unitum",
		"Unitpc",
		]


def _rounders(val_to_round: Union[str, int, float, Decimal], round_format: str) -> Decimal:
	return Decimal(Decimal(val_to_round).quantize(Decimal(str(round_format)), rounding=ROUND_HALF_UP))


@prettify_docstrings
class Unit(float):
	r"""
	Represents a unit, such as a point.

	Behaves much like a float (which it inherits from).


	:bold-title:`Addition`

	Units can be added to each other:

	.. code-block:: python

		>>> (3*mm) + (7*mm)
		<Unit '10.000 mm': 28.346pt>

	When adding different :class:`~domdf_python_tools.pagesizes.units.Unit` objects,
	the result has the type of the former unit:

	.. code-block:: python

		>>> (2.54*cm) + inch
		<Unit '5.080 cm': 144.000pt>
		>>> inch + (2.54*cm)
		<Unit '2.000 inch': 144.000pt>

	:class:`~domdf_python_tools.pagesizes.units.Unit` objects can also be added to :class:`float` and :class:`int` objects:

	.. code-block:: python

		>>> (3*cm) + 7
		<Unit '10.000 cm': 283.465pt>
		>>> 7 + (3*cm)
		<Unit '10.000 cm': 283.465pt>


	:bold-title:`Subtraction`

	Subtraction works the same as addition:

	.. code-block:: python

		>>> (17*mm) - (7*mm)
		<Unit '10.000 mm': 28.346pt>
		>>> (2.54*cm) - inch
		<Unit '0.000 cm': 0.000pt>
		>>> inch - (2.54*cm)
		<Unit '0.000 inch': 0.000pt>
		>>> (17*cm) - 7
		<Unit '10.000 cm': 283.465pt>
		>>> 17 - (7*cm)
		<Unit '10.000 cm': 283.465pt>


	:bold-title:`Multiplication`

	:class:`~domdf_python_tools.pagesizes.units.Unit` objects can only be multipled by
	:class:`float` and :class:`int` objects:

	.. code-block:: python

		>>> (3*mm) * 3
		<Unit '9.000 mm': 25.512pt>
		>>> 3 * (3*mm)
		<Unit '9.000 mm': 25.512pt>
		>>> 3.5 * (3*mm)
		<Unit '10.500 mm': 29.764pt>

	Multiplication works either way round.

	Multiplying by another :class:`~domdf_python_tools.pagesizes.units.Unit`
	results in a :exc:`NotImplementedError`:

	.. code-block:: python

		>>> inch * (7*cm)
		Traceback (most recent call last):
		NotImplementedError: Multiplying a unit by another unit is not allowed.

	:bold-title:`Division`

	:class:`~domdf_python_tools.pagesizes.units.Unit`\s can only be divided by
	:class:`float` and :class:`int` objects:

	.. code-block:: python

		>>> (3*mm) / 3
		<Unit '1.000 mm': 2.835pt>
		>>> (10*mm) / 2.5
		<Unit '4.000 mm': 11.339pt>

	Dividing by another unit results in a :exc:`NotImplementedError`:

	.. code-block:: python

		>>> inch / (7*cm)
		Traceback (most recent call last):
		NotImplementedError: Dividing a unit by another unit is not allowed.

	Likewise, trying to divide a:class:`float` and :class:`int` object by a unit
	results in a :exc:`NotImplementedError`:

	.. code-block:: python

		>>> 3 / (3*mm)
		Traceback (most recent call last):
		NotImplementedError: Dividing by a unit is not allowed.


	:bold-title:`Powers`

	Powers (using ``**``) are not officially supported.


	:bold-title:`Modulo Division`

	Modulo division of a :class:`~domdf_python_tools.pagesizes.units.Unit` by a
	:class:`float` or :class:`int` object is allowed:

	.. code-block:: python

		>>> (3*mm) % 2.5
		<Unit '0.500 mm': 1.417pt>

	Dividing by a unit, or modulo division of two units, is not officially supported.

	.. latex:clearpage::
	"""

	name: str = "pt"
	_in_pt: float = 1

	def __repr__(self):
		value = _rounders(float(self), "0.000")
		as_pt = _rounders(self.as_pt(), "0.000")
		return f"<Unit '{value} {self.name}': {as_pt}pt>"

	def __str__(self):
		value = _rounders(float(self), "0.000")
		as_pt = _rounders(self.as_pt(), "0.000")
		return f"<Unit '{value}\u205F{self.name}': {as_pt}pt>"

	def __mul__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			raise NotImplementedError("Multiplying a unit by another unit is not allowed.")

		return self.__class__(super().__mul__(other))

	__rmul__ = __mul__

	def __truediv__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			raise NotImplementedError("Dividing a unit by another unit is not allowed.")

		return self.__class__(super().__truediv__(other))

	def __floordiv__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			raise NotImplementedError("Dividing a unit by another unit is not allowed.")

		return self.__class__(super().__floordiv__(other))

	def __eq__(self, other: object) -> bool:
		if isinstance(other, Unit):
			if self._in_pt != 1:
				self_value = self.as_pt()
			else:
				self_value = self

			if other._in_pt != 1:
				other_value = other.as_pt()
			else:
				other_value = other

			return math.isclose(float(self_value), float(other_value), abs_tol=1e-8)
		else:
			return super().__eq__(other)

	def __mod__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			raise NotImplementedError("Modulo division of a unit by another unit is not allowed.")

		return self.__class__(super().__mod__(other))

	def __pow__(self, power, modulo=None):
		raise NotImplementedError("Powers are not supported for units.")

	def __rtruediv__(self, other):
		raise NotImplementedError("Dividing by a unit is not allowed.")

	__rdiv__ = __rtruediv__

	def __add__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			return self.__class__.from_pt(float(self.as_pt()) + float(other.as_pt()))
		else:
			return self.__class__(super().__add__(other))

	__radd__ = __add__

	def __sub__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):
			return self.__class__.from_pt(float(self.as_pt()) - float(other.as_pt()))
		else:
			return self.__class__(super().__sub__(other))

	def __rsub__(self, other: Union[float, "Unit"]) -> "Unit":
		if isinstance(other, Unit):  # pragma: no cover (sub should be called instead)
			return self.__class__.from_pt(float(other.as_pt()) - float(self.as_pt()))
		else:
			return self.__class__(super().__rsub__(other))

	def as_pt(self) -> "Unit":
		"""
		Returns the unit in point.
		"""

		return Unit(float(_rounders(float(self) * self._in_pt, "0.000000")))

	@classmethod
	def from_pt(cls, value: float) -> "Unit":
		"""
		Construct a :class:`~.Unit` object from a value in point.

		:param value:
		"""

		return cls(value / cls._in_pt)

	def __call__(self, value: Union[SupportsFloat, str, bytes, bytearray] = 0.0) -> "Unit":
		"""
		Returns an instance of the :class:`Unit` with the given value.

		:param value:
		"""

		return self.__class__(value)


class Unitpt(Unit):
	"""
	Point.
	"""

	name = "pt"
	_in_pt = 1


class UnitInch(Unit):
	"""
	Inch.
	"""

	name = "inch"
	_in_pt = 72.0


class Unitcm(Unit):
	"""
	Centimetres.
	"""

	name = "cm"
	_in_pt = 28.3464566929


class Unitmm(Unit):
	"""
	Millimetres.
	"""

	name = "mm"
	_in_pt = 2.83464566929


class Unitum(Unit):
	"""
	Micrometres.
	"""

	name = "µm"
	_in_pt = 0.00283464566929


class Unitpc(Unit):
	"""
	Pica.
	"""

	name = "pc"
	_in_pt = 12.0


# Units
pt = Unitpt(1)  #: Point
inch = UnitInch(1)  #: Inch
cm = Unitcm(1)  #: Centimetre
mm = Unitmm(1)  #: Millimetre
um = Unitum(1)  #: Micrometre
pc = pica = Unitpc(1)  #: Pica
