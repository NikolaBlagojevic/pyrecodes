# From https://github.com/dgilland/pydash
# Stripped back to the bare minimum.
#
# MIT License
#
# Copyright (c) 2020 Derrick Gilland
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import Iterable, Iterator

__all__ = ["is_match_with", "iterator"]


def is_match_with(obj, source):  # noqa: D103
	if (
			isinstance(obj, dict) and isinstance(source, dict)
			or isinstance(obj, list) and isinstance(source, list)
			or isinstance(obj, tuple) and isinstance(source, tuple)
			):
		# Set equal to True if source is empty, otherwise, False and then allow
		# deep comparison to determine equality.
		equal = not source

		# Walk a/b to determine equality.
		for key, value in iterator(source):
			try:
				equal = is_match_with(obj[key], value)
			except Exception:  # pylint: disable=broad-except
				equal = False

			if not equal:
				break
	else:
		equal = obj == source

	return equal


def iterator(obj) -> Iterator:  # noqa: D103
	if isinstance(obj, dict) or hasattr(obj, "items"):
		return iter(obj.items())
	elif isinstance(obj, Iterable):
		return enumerate(obj)
	else:  # pragma: no cover
		return iter(getattr(obj, "__dict__", {}).items())
