#!/usr/bin/env python3
#
#  _installers.py
"""
Functions to install the various patches.
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
from types import ModuleType
from typing import Any, Callable, TypeVar

__all__ = ["install_jinja2", "install_markupsafe"]

F = TypeVar('F', bound=Callable[..., Any])


def install_markupsafe(markupsafe: ModuleType) -> None:
	"""
	Install the markupsafe patch.

	:param markupsafe: The ``markupsafe`` module.
	"""

	if not hasattr(markupsafe, "soft_unicode"):

		def soft_unicode(s: Any) -> str:
			return markupsafe.soft_str(s)

		markupsafe.soft_unicode = soft_unicode  # type: ignore[attr-defined]


def install_jinja2(jinja2: ModuleType, filters: ModuleType, utils: ModuleType) -> None:
	"""
	Install the jinja2 patch.

	:param jinja2: The ``jinja2`` module.
	:param filters: The ``jinja2.filters`` module.
	:param utils: The ``jinja2.utils`` module.
	"""

	if not hasattr(filters, "environmentfilter"):

		def environmentfilter(f: F) -> F:
			return utils.pass_environment(f)

		filters.environmentfilter = environmentfilter  # type: ignore[attr-defined]
		jinja2.environmentfilter = environmentfilter  # type: ignore[attr-defined]

	if not hasattr(utils, "contextfunction"):

		def contextfunction(f: F) -> F:
			return utils.pass_context(f)

		utils.contextfunction = contextfunction  # type: ignore[attr-defined]
		jinja2.contextfunction = contextfunction  # type: ignore[attr-defined]
