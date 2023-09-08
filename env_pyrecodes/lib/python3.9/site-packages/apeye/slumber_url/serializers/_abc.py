#!/usr/bin/env python
#
#  _abc.py
"""
Abstract Base Class for JSON and YAML serializers.
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

# stdlib
from abc import ABC, abstractmethod
from typing import Any, List, Mapping, MutableMapping

__all__ = ["Serializer"]


class Serializer(ABC):
	"""
	Base class for serializers.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.serializers`
	"""

	@property
	@abstractmethod
	def content_types(self) -> List[str]:  # pragma: no cover
		"""
		List of supported content types.
		"""

		return NotImplemented

	@property
	@abstractmethod
	def key(self) -> str:  # pragma: no cover
		"""
		An identifier for the supported data type.

		For example, a YAML serializer would set this to ``'yaml'``.
		"""

		return NotImplemented

	def get_content_type(self) -> str:
		"""
		Returns the first value from :attr:`~.Serializer.content_types`.
		"""

		return self.content_types[0]

	@abstractmethod
	def loads(self, data: str) -> MutableMapping[str, Any]:
		"""
		Deserialize data using this :class:`~.Serializer`.

		:param data:
		"""

		raise NotImplementedError()

	@abstractmethod
	def dumps(self, data: Mapping[str, Any]) -> str:
		"""
		Serialize data using this :class:`~.Serializer`.

		:param data:
		"""

		raise NotImplementedError()
