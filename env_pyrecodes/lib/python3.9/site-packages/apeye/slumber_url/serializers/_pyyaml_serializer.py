#!/usr/bin/env python
#
#  _pyyaml_serializer.py
"""
PyYAML-backed YAML serializer for :class:`~apeye.slumber_url.SlumberURL`.

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
from typing import Any, Mapping, MutableMapping

# 3rd party
import yaml  # nodep

# this package
from apeye.slumber_url.serializers._abc import Serializer

__all__ = ["YamlSerializer"]


class YamlSerializer(Serializer):
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

	def loads(self, data: str) -> MutableMapping[str, Any]:
		"""
		Deserialize data using this :class:`~.Serializer`.

		:param data:
		"""

		return yaml.safe_load(str(data))

	def dumps(self, data: Mapping[str, Any]) -> str:
		"""
		Serialize data using this :class:`~.Serializer`.

		:param data:
		"""

		return yaml.dump(data)
