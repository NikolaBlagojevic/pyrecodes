#!/usr/bin/env python
#
#  url.py
"""
:mod:`pathlib`-like approach to URLs.

.. versionchanged:: 0.2.0

	:class:`~apeye.slumber_url.SlumberURL` and :class:`~apeye.requests_url.RequestsURL`
	moved to :mod:`apeye.slumber_url` and :mod:`apeye.requests_url` respectively.

.. note::

	The classes in this module can instead be imported from the
	`apeye_core <https://pypi.org/project/apeye-core/>`_ module instead.
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

# stdlib
import os
import sys
from typing import TYPE_CHECKING, Dict, List, Optional

# 3rd party
import apeye_core
from apeye_core import URL as URL
from apeye_core import Domain as Domain
from apeye_core import URLPath as URLPath
from apeye_core import URLPathType as URLPathType
from apeye_core import URLType as URLType

__all__ = ["URL", "URLPath", "Domain", "URLType", "URLPathType"]

if TYPE_CHECKING:
	pass
elif "_APEYE_DOCS" in os.environ:

	class URL(apeye_core.URL):  # noqa: D101
		#: URL scheme specifier
		scheme: str

		#: Network location part of the URL
		netloc: str

		#: The hierarchical path of the URL
		path: URLPath

		query: Dict[str, List[str]]
		"""
		The query parameters of the URL, if present.

		.. versionadded:: 0.7.0
		"""

		fragment: Optional[str]
		"""
		The URL fragment, used to identify a part of the document. :py:obj:`None` if absent from the URL.

		.. versionadded:: 0.7.0
		"""


URLPath.__module__ = "apeye.url"
URL.__module__ = "apeye.url"
Domain.__module__ = "apeye.url"

if sys.version_info >= (3, 7):
	URLType.__module__ = "apeye.url"
	URLPathType.__module__ = "apeye.url"
