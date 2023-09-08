#!/usr/bin/env python
#
#  __init__.py
"""
JSON and YAML serializers for :class:`~apeye.slumber_url.SlumberURL`.

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

# stdlib
import json
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Type

# this package
from apeye.slumber_url.exceptions import SlumberBaseException
from apeye.slumber_url.serializers._abc import Serializer

__all__ = ["JsonSerializer", "YamlSerializer", "SerializerRegistry", "Serializer", "SerializerNotAvailable"]


class JsonSerializer(Serializer):
	"""
	Serializer for JSON data.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.serializers`
	"""

	content_types = [
			"application/json",
			"application/x-javascript",
			"text/javascript",
			"text/x-javascript",
			"text/x-json",
			]
	key = "json"

	def loads(self, data: str) -> MutableMapping[str, Any]:
		"""
		Deserialize data using this :class:`~.Serializer`.

		:param data:
		"""

		return json.loads(data)

	def dumps(self, data: Mapping[str, Any]) -> str:
		"""
		Serialize data using this :class:`~.Serializer`.

		:param data:
		"""

		return json.dumps(data)


_SERIALIZERS: List[Type[Serializer]] = [JsonSerializer]

YamlSerializer: Type[Serializer]

try:
	# this package
	from apeye.slumber_url.serializers._pyyaml_serializer import YamlSerializer
	_SERIALIZERS.append(YamlSerializer)

except ImportError:
	try:
		# this package
		from apeye.slumber_url.serializers._ruamel_serializer import YamlSerializer
		_SERIALIZERS.append(YamlSerializer)

	except ImportError:

		class YamlSerializer(Serializer):  # type: ignore[no-redef]
			"""
			Serializer for YAML data.

			.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.serializers`

			.. attention::

				Either `PyYaml <https://pypi.org/project/PyYAML/>`_ or
				`ruamel.yaml <https://pypi.org/project/ruamel.yaml/>`_
				must be installed to use this serializer.
			"""

			content_types = ["text/yaml"]
			key = "yaml"

			def __init__(self):
				raise NotImplementedError("'PyYAML' or 'ruamel.yaml' package not available.")


class SerializerRegistry:
	"""
	Serializes and deserializes data for transfer to and from a REST API.

	:param default: The default serializer to use if none is specified.
		Corresponds to the :attr:`~.Serializer.key` of a :class:`~.Serializer`.
	:param serializers: List of :class:`~.Serializer` objects to use.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.serializers`
	"""

	def __init__(self, default: str = "json", serializers: Optional[List[Serializer]] = None):

		#: Mapping of formats to :class:`~.Serializer` objects.
		self.serializers: Dict[str, Serializer] = {}

		for serializer in serializers or [x() for x in _SERIALIZERS]:
			self.serializers[serializer.key] = serializer

		#: The default serializer to use if none is specified.
		self.default: str = default

	def get_serializer(self, name: Optional[str] = None, content_type: Optional[str] = None):
		"""
		Returns the first :class:`~.Serializer` that supports either the given
		format or the given content type.

		:param name:
		:param content_type:
		"""  # noqa: D400

		if content_type is None:
			if name is None:
				return self.serializers[self.default]
			else:
				if name not in self.serializers:
					raise SerializerNotAvailable(name)
				return self.serializers[name]
		else:
			for x in self.serializers.values():
				for ctype in x.content_types:
					if content_type == ctype:
						return x

			raise SerializerNotAvailable(content_type)

	def loads(
			self,
			data: str,
			format: Optional[str] = None,  # noqa: A002  # pylint: disable=redefined-builtin
			) -> MutableMapping[str, Any]:
		"""
		Deserialize data of the given format.

		:param data:
		:param format: The serialization format to use.
		"""

		s = self.get_serializer(format)
		return s.loads(data)

	def dumps(
			self,
			data: Mapping[str, Any],
			format: Optional[str] = None,  # noqa: A002  # pylint: disable=redefined-builtin
			) -> str:
		"""
		Serialize data of the given format.

		:param data:
		:param format: The serialization format to use.
		"""

		s = self.get_serializer(format)
		return s.dumps(data)

	def get_content_type(
			self,
			format: Optional[str] = None,  # noqa: A002  # pylint: disable=redefined-builtin
			):
		"""
		Returns the content type for the serializer that supports the given format.

		:param format: The desired serialization format.
		"""

		s = self.get_serializer(format)
		return s.get_content_type()


class SerializerNotAvailable(SlumberBaseException):
	"""
	The chosen :class:`Serializer` is not available.

	.. versionchanged:: 0.6.0  Moved to :mod:`apeye.slumber_url.serializers`
	"""

	def __init__(self, content_type: str):
		super().__init__(f"No serializer available for {content_type!r}.")


Serializer.__module__ = JsonSerializer.__module__
