#!/usr/bin/env python3
#
#  _meta_path.py
"""
Meta path finder and loader to install patched at import time.
"""
#
#  Copyright © 2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import importlib.abc
import importlib.util
import sys

# this package
from sphinx_jinja2_compat._installers import install_jinja2, install_markupsafe


class _Finder(importlib.abc.MetaPathFinder):

	def __init__(self):
		# Stack stops us going round in circles
		self._stack = []

	def find_spec(self, fullname, path, target=None):
		if fullname in self._stack:
			return None

		if fullname == "markupsafe":

			if self in sys.meta_path:

				self._stack.append("markupsafe")
				markupsafe = importlib.import_module("markupsafe")
				self._stack.pop()

				# This is necessary to ensure the patched version gets loaded
				del sys.modules["markupsafe"]

				class _MarkupsafeLoader(importlib.abc.Loader):

					def create_module(self, spec):
						install_markupsafe(markupsafe)
						return markupsafe

					def exec_module(self, module):
						pass

				return importlib.util.spec_from_loader(
						"markupsafe",
						_MarkupsafeLoader(),
						origin=markupsafe.__file__,
						)

		elif fullname == "jinja2":

			if self in sys.meta_path:

				self._stack.append("jinja2")
				jinja2 = importlib.import_module("jinja2")
				filters = importlib.import_module("jinja2.filters")
				utils = importlib.import_module("jinja2.utils")
				self._stack.pop()

				# This is necessary to ensure the patched version gets loaded
				del sys.modules["jinja2"]

				class _Jinja2Loader(importlib.abc.Loader):

					def create_module(self, spec):
						install_jinja2(jinja2, filters, utils)
						return jinja2

					def exec_module(self, module):
						pass

				return importlib.util.spec_from_loader("jinja2", _Jinja2Loader(), origin=jinja2.__file__)
