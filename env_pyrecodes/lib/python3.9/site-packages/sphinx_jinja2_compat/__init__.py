#!/usr/bin/env python3
#
#  __init__.py
"""
Patches Jinja2 v3 to restore compatibility with earlier Sphinx versions.
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
import os
import sys
from typing import List

# this package
from sphinx_jinja2_compat._installers import install_jinja2, install_markupsafe

__all__: List[str] = []

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2022 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.0"
__email__: str = "dominic@davis-foster.co.uk"

if "NO_SPHINX_JINJA2_COMPAT" not in os.environ:

	if sys.version_info >= (3, 10):
		# stdlib
		import types
		types.Union = types.UnionType

	try:

		# 3rd party
		import markupsafe

		install_markupsafe(markupsafe)

		# 3rd party
		import jinja2
		import jinja2.filters
		import jinja2.utils

		install_jinja2(jinja2, jinja2.filters, jinja2.utils)

	except ImportError:
		# Unable to import one module
		# Perhaps they are in global site-packages and we're not,
		# so they aren't available yet?

		# this package
		from sphinx_jinja2_compat._meta_path import _Finder
		sys.meta_path.insert(0, _Finder())
