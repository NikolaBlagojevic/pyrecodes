#!/usr/bin/env python3
#
#  rate_limiter.py
"""
Rate limiters for making calls to external APIs in a polite manner.

.. extras-require:: limiter
	:pyproject:

.. latex:vspace:: -15px
"""
#
#  Copyright (c) 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Based on CacheControl
#  Copyright 2015 Eric Larson
#  https://github.com/ionrock/cachecontrol
#  Apache-2.0 Licensed
#

# stdlib
import datetime
import logging
import os
import shutil
import time
import warnings
import zlib
from functools import wraps
from typing import Any, Callable, Collection, Dict, Optional

# 3rd party
import platformdirs
import requests
from cachecontrol import CacheControl, CacheControlAdapter  # nodep
from cachecontrol.caches.file_cache import FileCache  # nodep
from cachecontrol.heuristics import ExpiresAfter  # nodep
from domdf_python_tools.paths import PathPlus

# import codetiming

__all__ = [
		"rate_limit",
		"RateLimitAdapter",
		"HTTPCache",
		]

# Fixes intersphinx links
requests.PreparedRequest.__module__ = "requests"
requests.Response.__module__ = "requests"
requests.Request.__module__ = "requests"
requests.Session.__module__ = "requests"


def rate_limit(min_time: float = 0.2, logger: Optional[logging.Logger] = None) -> Callable[[Callable], Any]:
	"""
	Decorator to force a function to run no less than ``min_time`` seconds after it last ran.
	Used for rate limiting.

	:param min_time: The minimum interval between subsequent runs of the decorated function.
	:default min_time: ``0.2``, which gives a maximum rate of 5 calls per second
	:param logger: Optional logger to log information about requests to. Defaults to the root logger.
	:no-default logger:
	"""

	if logger is None:
		# Log to root logger
		logger_ = logging.getLogger()
	else:  # pragma: no cover
		logger_ = logger

	def decorator(func: Callable) -> Callable:

		function_name = func.__name__
		last_ran_message = f"{function_name}: Last ran %.2f seconds ago."
		waiting_message = f"{function_name}: Waiting %.2f seconds."

		@wraps(func)
		def rate_limit_wrapper(*args, **kwargs):
			now = datetime.datetime.now()

			time_since_last_run = (now - rate_limit_wrapper.last_run_time).total_seconds()  # type: ignore
			logger_.debug(last_ran_message % time_since_last_run)

			if time_since_last_run < min_time:
				wait_time = min_time - time_since_last_run
				logger_.debug(waiting_message % wait_time)
				time.sleep(wait_time)

			rate_limit_wrapper.last_run_time = now  # type: ignore
			res = func(*args, **kwargs)
			return res

		rate_limit_wrapper.last_run_time = datetime.datetime.fromtimestamp(0)  # type: ignore

		return rate_limit_wrapper

	return decorator


class RateLimitAdapter(CacheControlAdapter):
	r"""
	Custom :class:`cachecontrol.adapter.CacheControlAdapter` to limit the rate of requests to 5 per second.

	:param cache:
	:param cache_etags:
	:param controller_class:
	:param serializer:
	:param heuristic:
	:param cacheable_methods:

	.. autosummary-widths:: 7/16
	.. latex:clearpage::
	"""

	def send(  # type: ignore[override]  # Latest cachecontrol has changed the signature to put cacheable_methods last
		self,
		request: requests.PreparedRequest,
		cacheable_methods: Optional[Collection[str]] = None,
		**kwargs,
		) -> requests.Response:
		r"""
		Send a request.

		Use the request information to see if it exists in the cache and cache the response if we need to and can.

		:param request: The :class:`requests.PreparedRequest` being sent.
		:param cacheable_methods:
		:param \*\*kwargs: Additional arguments taken by :meth:`requests.adapters.HTTPAdapter.send` (e.g. ``timeout``).
		"""

		cacheable = cacheable_methods or self.cacheable_methods
		if request.method in cacheable:
			try:
				cached_response = self.controller.cached_request(request)
			except zlib.error:  # pragma: no cover
				cached_response = None
			if cached_response:
				return self.build_response(request, cached_response, from_cache=True)

			# check for etags and add headers if appropriate
			request.headers.update(self.controller.conditional_headers(request))

		resp = self.rate_limited_send(request, **kwargs)

		return resp

	@rate_limit(0.2)
	def rate_limited_send(self, *args, **kwargs) -> requests.Response:
		"""
		Wrapper around :meth:`CacheControlAdapter.send <cachecontrol.adapter.CacheControlAdapter.send>`
		to limit the rate of requests.
		"""  # noqa: D400

		return super(CacheControlAdapter, self).send(*args, **kwargs)  # lgtm [py/super-not-enclosing-class]


class HTTPCache:
	"""
	Cache HTTP requests for up to 28 days and limit the rate of requests to no more than 5/second.

	:param app_name: The name of the app. This dictates the name of the cache directory.
	:param expires_after: The maximum time to cache responses for.
	"""

	app_name: str  #: The name of the app. This dictates the name of the cache directory.
	cache_dir: PathPlus  #: The location of the cache directory on disk.
	caches: Dict[str, Dict[str, Any]]  #: Mapping of function names to their caches.

	def __init__(self, app_name: str, expires_after: datetime.timedelta = datetime.timedelta(days=28)):
		self.app_name: str = str(app_name)
		self.cache_dir = PathPlus(platformdirs.user_cache_dir(self.app_name))
		self.cache_dir.maybe_make(parents=True)

		self.session: requests.Session = CacheControl(
				sess=requests.Session(),
				cache=FileCache(os.fspath(self.cache_dir)),
				heuristic=ExpiresAfter(
						days=expires_after.days,
						seconds=expires_after.seconds,
						microseconds=expires_after.microseconds,
						),
				adapter_class=RateLimitAdapter
				)

	def clear(self) -> bool:
		"""
		Clear the cache.

		:returns: True to indicate success. False otherwise.
		"""

		try:
			shutil.rmtree(self.cache_dir)
			return True

		except Exception as e:  # pragma: no cover
			warnings.warn(f"Could not remove cache. The error was: {e}")
			return False


#
# class ForceMinTime:
# 	"""
# 	Decorator to force a function to take an amount of time to run.
# 	Used for rate limiting to external APIs.
#
# 	:param min_time: The minimum run time in seconds
# 	:type min_time: float
# 	"""
#
# 	def __init__(self, min_time: float):
# 		"""
# 		If there are decorator arguments, the function
# 		to be decorated is not passed to the constructor!
# 		"""
#
# 		self.min_time = min_time
#
# 	def __call__(self, func):
# 		"""
# 		If there are decorator arguments, __call__() is only called
# 		once, as part of the decoration process! You can only give
# 		it a single argument, which is the function object.
# 		"""
#
# 		def wrapper(*args, **kwargs):
# 			with codetiming.Timer(logger=None) as t:
# 				r = func(*args, **kwargs)
#
# 			sleep_time = self.min_time - t.last
# 			print(t.last)
#
# 			if sleep_time > 0:
# 				time.sleep(sleep_time)
#
# 			return r
#
# 		return wrapper
