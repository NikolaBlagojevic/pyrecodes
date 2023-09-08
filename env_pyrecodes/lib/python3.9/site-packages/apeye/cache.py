#!/usr/bin/env python3
#
#  cache.py
"""
Caching functions for functions.

.. latex:vspace:: 10px

.. seealso::

	* The `cachier project <https://pypi.org/project/cachier/>`_
	* `DiskCache <http://www.grantjenks.com/docs/diskcache/index.html>`_

.. automodulesumm:: apeye.cache
	:autosummary-sections: ;;
"""
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import inspect
import json
import shutil
import warnings
from functools import wraps
from typing import Any, Callable, Dict, Iterable, Optional

# 3rd party
import platformdirs
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.utils import posargs2kwargs

__all__ = ["Cache"]


class Cache:
	"""
	Cache function arguments to and in-memory dictionary and a JSON file.

	:param app_name: The name of the app. This dictates the name of the cache directory.
	"""

	app_name: str  #: The name of the app. This dictates the name of the cache directory.
	cache_dir: PathPlus  #: The location of the cache directory on disk.
	caches: Dict[str, Dict[str, Any]]  #: Mapping of function names to their caches.

	def __init__(self, app_name: str):
		self.app_name: str = str(app_name)
		self.cache_dir = PathPlus(platformdirs.user_cache_dir(f"{self.app_name}_cache"))
		self.cache_dir.maybe_make(parents=True)

		# Mapping of function names to their caches
		self.caches: Dict[str, Dict[str, Any]] = {}

	def clear(self, func: Optional[Callable] = None) -> bool:
		"""
		Clear the cache.

		:param func: Optional function to clear the cache for.
			By default, the whole cache is cleared.
		:no-default func:

		:returns: True to indicate success. False otherwise.
		"""

		try:
			if func is None:
				shutil.rmtree(self.cache_dir)
				self.cache_dir.maybe_make()
				for function in self.caches:
					self.caches[function] = {}
			else:
				function_name = func.__name__
				cache_file = self.cache_dir / f"{function_name}.json"
				if cache_file.is_file():
					cache_file.unlink()

				if function_name in self.caches:
					del self.caches[function_name]
				self.caches[function_name] = {}

			return True

		except Exception as e:  # pragma: no cover
			warnings.warn(f"Could not remove cache. The error was: {e}")
			return False

	def load_cache(self, func: Callable) -> None:
		"""
		Loads the cache for the given function.

		:param func:
		"""

		cache_file: PathPlus = self.cache_dir / f"{func.__name__}.json"

		if cache_file.is_file():
			cache = json.loads(cache_file.read_text())
		else:
			cache = {}

		self.caches[func.__name__] = cache
		return cache

	def __call__(self, func: Callable):
		"""
		Decorator to cache the return values of a function based on its inputs.

		:param func:
		"""

		function_name = func.__name__
		posargs: Iterable[str] = inspect.getfullargspec(func).args
		cache_file: PathPlus = self.cache_dir / f"{function_name}.json"
		self.load_cache(func)

		@wraps(func)
		def wrapper(*args, **kwargs: Any):
			kwargs: Dict[str, Any] = posargs2kwargs(args, posargs, kwargs)  # type: ignore
			key: str = json.dumps(kwargs)
			response: Any

			cache = self.caches[function_name]
			if key in cache:
				# Return cached response
				response = json.loads(cache[key])
			else:
				response = func(**kwargs)

				if response is not None:
					# Don't cache None values.
					cache[key] = json.dumps(response)

			cache_file.write_text(json.dumps(cache))

			return response

		return wrapper
