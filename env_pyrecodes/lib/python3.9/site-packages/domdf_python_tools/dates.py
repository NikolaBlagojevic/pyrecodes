#  !/usr/bin/env python
#
#  dates.py
"""
Utilities for working with dates and times.

.. extras-require:: dates
	:pyproject:


**Data:**

.. autosummary::

	~domdf_python_tools.dates.months
	~domdf_python_tools.dates.month_full_names
	~domdf_python_tools.dates.month_short_names

"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Parts of the docstrings based on the Python 3.8.2 Documentation
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
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
#  calc_easter from https://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
#  Copyright © 2008 Martin Diers
#  Licensed under the MIT License
#

# stdlib
import datetime
import sys
import time
import typing
from collections import OrderedDict
from types import ModuleType
from typing import Optional, Union

__all__ = [
		"current_tzinfo",
		"set_timezone",
		"utc_timestamp_to_datetime",
		"months",
		"parse_month",
		"get_month_number",
		"check_date",
		"calc_easter",
		"month_short_names",
		"month_full_names",
		"is_bst",
		]


def current_tzinfo() -> Optional[datetime.tzinfo]:
	"""
	Returns a tzinfo object for the current timezone.
	"""

	return datetime.datetime.now().astimezone().tzinfo  # pragma: no cover (hard to test)


#
# def datetime_to_utc_timestamp(datetime, current_tzinfo=None):
# 	"""
# 	Convert a :class:`datetime.datetime` object to seconds since UNIX epoch, in UTC time
#
# 	:param datetime:
# 	:type datetime: :class:`datetime.datetime`
# 	:param current_tzinfo: A tzinfo object representing the current timezone.
# 		If None it will be inferred.
# 	:type current_tzinfo: :class:`datetime.tzinfo`
#
# 	:return: Timestamp in UTC timezone
# 	:rtype: float
# 	"""
#
# 	return datetime.astimezone(current_tzinfo).timestamp()
#


def set_timezone(obj: datetime.datetime, tzinfo: datetime.tzinfo) -> datetime.datetime:
	"""
	Sets the timezone / tzinfo of the given :class:`datetime.datetime` object.
	This will not convert the time (i.e. the hours will stay the same).
	Use :meth:`datetime.datetime.astimezone` to accomplish that.

	:param obj:
	:param tzinfo:
	"""

	return obj.replace(tzinfo=tzinfo)


def utc_timestamp_to_datetime(
		utc_timestamp: Union[float, int],
		output_tz: Optional[datetime.tzinfo] = None,
		) -> datetime.datetime:
	"""
	Convert UTC timestamp (seconds from UNIX epoch) to a :class:`datetime.datetime` object.

	If ``output_tz`` is :py:obj:`None` the timestamp is converted to the platform’s local date and time,
	and the local timezone is inferred and set for the object.

	If ``output_tz`` is not :py:obj:`None`, it must be an instance of a :class:`datetime.tzinfo` subclass,
	and the timestamp is converted to ``output_tz``’s time zone.


	:param utc_timestamp: The timestamp to convert to a datetime object
	:param output_tz: The timezone to output the datetime object for.
		If :py:obj:`None` it will be inferred.

	:return: The timestamp as a datetime object.

	:raises OverflowError: if the timestamp is out of the range
		of values supported by the platform C localtime() or gmtime() functions,
		and OSError on localtime() or gmtime() failure. It’s common for this to
		be restricted to years in 1970 through 2038.
	"""

	new_datetime = datetime.datetime.fromtimestamp(utc_timestamp, output_tz)
	return new_datetime.astimezone(output_tz)


if sys.version_info <= (3, 7, 2):  # pragma: no cover (py37+)
	MonthsType = OrderedDict
else:  # pragma: no cover (<py37)
	MonthsType = typing.OrderedDict[str, str]  # type: ignore  # noqa: TYP006

#: Mapping of 3-character shortcodes to full month names.
months: MonthsType = OrderedDict(
		Jan="January",
		Feb="February",
		Mar="March",
		Apr="April",
		May="May",
		Jun="June",
		Jul="July",
		Aug="August",
		Sep="September",
		Oct="October",
		Nov="November",
		Dec="December",
		)

month_short_names = tuple(months.keys())
"""
List of the short names for months in the Gregorian calendar.

.. versionadded:: 2.0.0
"""

month_full_names = tuple(months.values())
"""
List of the full names for months in the Gregorian calendar.

.. versionadded:: 2.0.0
"""


def parse_month(month: Union[str, int]) -> str:
	"""
	Converts an integer or shorthand month into the full month name.

	:param month: The month number or shorthand name

	:return: The full name of the month
	"""

	error_text = f"The given month ({month!r}) is not recognised."

	try:
		month = int(month)
	except ValueError:
		try:
			return months[month.capitalize()[:3]]  # type: ignore
		except KeyError:
			raise ValueError(error_text)

	# Only get here if first try succeeded
	if 0 < month <= 12:
		return list(months.values())[month - 1]
	else:
		raise ValueError(error_text)


def get_month_number(month: Union[str, int]) -> int:
	"""
	Returns the number of the given month.
	If ``month`` is already a number between 1 and 12 it will be returned immediately.

	:param month: The month to convert to a number

	:return: The number of the month
	"""

	if isinstance(month, int):
		if 0 < month <= 12:
			return month
		else:
			raise ValueError(f"The given month ({month!r}) is not recognised.")
	else:
		month = parse_month(month)
		return list(months.values()).index(month) + 1


def check_date(month: Union[str, int], day: int, leap_year: bool = True) -> bool:
	"""
	Returns :py:obj:`True` if the day number is valid for the given month.

	.. note::

		This function will return :py:obj:`True` for the 29th Feb.
		If you don't want this behaviour set ``leap_year`` to :py:obj:`False`.

	.. latex:vspace:: -10px

	:param month: The month to test.
	:param day: The day number to test.
	:param leap_year: Whether to return :py:obj:`True` for 29th Feb.
	"""

	# Ensure day is an integer
	day = int(day)
	month = get_month_number(month)
	year = 2020 if leap_year else 2019

	try:
		datetime.date(year, month, day)
		return True
	except ValueError:
		return False


def calc_easter(year: int) -> datetime.date:
	"""
	Returns the date of Easter in the given year.

	.. versionadded:: 1.4.0

	:param year:
	"""

	a = year % 19
	b = year // 100
	c = year % 100
	d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
	e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
	f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
	month = f // 31
	day = f % 31 + 1

	return datetime.date(year, month, day)


def get_utc_offset(
		tz: Union[datetime.tzinfo, str],
		date: Optional[datetime.datetime] = None,
		) -> Optional[datetime.timedelta]:
	"""
	Returns the offset between UTC and the requested timezone on the given date.
	If ``date`` is :py:obj:`None` then the current date is used.

	:param tz: ``pytz.timezone`` or a string representing the timezone
	:param date: The date to obtain the UTC offset for
	"""

	if date is None:
		date = datetime.datetime.utcnow()

	timezone: Optional[datetime.tzinfo]

	if isinstance(tz, str):
		timezone = get_timezone(tz, date)
	else:
		timezone = tz  # pragma: no cover (hard to test)

	return date.replace(tzinfo=pytz.utc).astimezone(timezone).utcoffset()


def get_timezone(tz: str, date: Optional[datetime.datetime] = None) -> Optional[datetime.tzinfo]:
	"""
	Returns a localized ``pytz.timezone`` object for the given date.

	If ``date`` is :py:obj:`None` then the current date is used.

	.. latex:vspace:: -10px

	:param tz: A string representing a pytz timezone
	:param date: The date to obtain the timezone for
	"""

	if date is None:  # pragma: no cover (hard to test)
		date = datetime.datetime.utcnow()

	d = date.replace(tzinfo=None)

	return pytz.timezone(tz).localize(d).tzinfo


def is_bst(the_date: Union[time.struct_time, datetime.date]) -> bool:
	"""
	Calculates whether the given day falls within British Summer Time.

	This function should also be applicable to other timezones which change to summer time on the same date (e.g. Central European Summer Time).

	.. note::

		This function does not consider the time of day,
		and therefore does not handle the fact that the time changes at 1 AM GMT.
		It also does not account for historic deviations from the current norm.

	.. versionadded:: 3.5.0

	:param the_date: A :class:`time.struct_time`, :class:`datetime.date`
		or :class:`datetime.datetime` representing the target date.

	:returns: :py:obj:`True` if the date falls within British Summer Time, :py:obj:`False` otherwise.
	"""

	if isinstance(the_date, datetime.date):
		the_date = the_date.timetuple()

	day, month, dow = the_date.tm_mday, the_date.tm_mon, (the_date.tm_wday + 1) % 7

	if 3 > month > 10:
		return False
	elif 3 < month < 10:
		return True
	elif month == 3:
		return day - dow >= 25
	elif month == 10:
		return day - dow < 25
	else:
		return False


_pytz_functions = ["get_utc_offset", "get_timezone"]

try:

	# 3rd party
	import pytz

	__all__.extend(_pytz_functions)

except ImportError as e:

	if __name__ == "__main__":

		# stdlib
		import warnings

		# this package
		from domdf_python_tools.words import word_join

		warnings.warn(
				f"""\
		'{word_join(_pytz_functions)}' require pytz (https://pypi.org/project/pytz/), but it could not be imported.

		The error was: {e}.
		"""
				)

	else:
		_actual_module = sys.modules[__name__]

		class SelfWrapper(ModuleType):

			def __getattr__(self, name):
				if name in _pytz_functions:
					raise ImportError(
							f"{name!r} requires pytz (https://pypi.org/project/pytz/), but it could not be imported."
							)
				else:
					return getattr(_actual_module, name)

		sys.modules[__name__] = SelfWrapper(__name__)
