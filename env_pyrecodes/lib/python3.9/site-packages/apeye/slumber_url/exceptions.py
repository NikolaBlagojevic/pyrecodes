#!/usr/bin/env python
#
#  slumber_url.py
"""
Exceptions for :class:`~apeye.slumber_url.SlumberURL`.

.. versionadded:: 0.6.0
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Based on Slumber <https://slumber.readthedocs.io>
#  Copyright (c) 2011 Donald Stufft
#  Licensed under the 2-clause BSD License
#

__all__ = [
		"HttpClientError",
		"HttpNotFoundError",
		"HttpServerError",
		"SlumberBaseException",
		"SlumberHttpBaseException"
		]


class SlumberBaseException(Exception):
	"""
	All Slumber exceptions inherit from this exception.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.exceptions`
	"""


class SlumberHttpBaseException(SlumberBaseException):
	"""
	All Slumber HTTP Exceptions inherit from this exception.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.exceptions`
	"""

	def __init__(self, *args, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)
		super().__init__(*args)


class HttpClientError(SlumberHttpBaseException):
	"""
	Raised when the server tells us there was a client error (4xx).

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.exceptions`
	"""


class HttpNotFoundError(HttpClientError):
	"""
	Raised when the server sends a 404 error.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.exceptions`
	"""


class HttpServerError(SlumberHttpBaseException):
	"""
	Raised when the server tells us there was a server error (5xx).

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.exceptions`
	"""
