#!/usr/bin/env python
#
#  requests_url.py
"""
Extension of :class:`~apeye.url.URL` with support for interacting with the website using the :requests:`.` library.

.. versionadded:: 0.2.0
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
#  Some docstrings from Requests <https://requests.readthedocs.io>
#  Copyright 2019 Kenneth Reitz
#  Licensed under the Apache License, Version 2.0

# stdlib
import sys
from typing import IO, Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, TypeVar, Union

# 3rd party
import requests

# this package
from apeye.url import URL

__all__ = ["RequestsURL", "TrailingRequestsURL", "_R"]

_ParamsMappingValueType = Union[str, bytes, int, float, Iterable[Union[str, bytes, int, float]]]
# _Data = Union[None, str, bytes, MutableMapping[str, Any], Iterable[Tuple[str, Optional[str]]], IO]
_Data = Union[
	None,
	str,
	bytes,
	MutableMapping[str, Any],
	List[Tuple[str, Optional[str]]],
	Tuple[Tuple[str, Optional[str]]],
	IO
	]
_ParamsType = Union[
	Mapping[Union[str, bytes, int, float], _ParamsMappingValueType],
	Union[str, bytes],
	Tuple[Union[str, bytes, int, float], _ParamsMappingValueType],
	None
	]

_R = TypeVar("_R", bound="RequestsURL")


# Ignore the LGTM warning as the "session" attribute should **not** affect equality.
class RequestsURL(URL):  # lgtm [py/missing-equals]
	"""
	Extension of :class:`~apeye.url.URL` with support for interacting with the website using the :requests:`.` library.

	The :class:`requests.Session` used for this object -- and all objects created using the
	``/`` or ``.parent`` operations -- can be accessed using the :attr:`~.session` attribute.
	If desired, this can be replaced with a different session object, such as one using caching.

	:param url: The url to construct the :class:`~apeye.url.URL` object from.

	.. latex:vspace:: 5px

	.. versionchanged:: 0.3.0  The ``url`` parameter can now be a string or a :class:`~.URL`.

	.. versionchanged:: 1.1.0

		When a :class:`~.RequestsURL` object is deleted or garbage collected,
		the underlying :class:`requests.Session` object it only closed if no objects hold references to the session.
		This prevents the session object of a global object from being inadvertently closed
		when one of its children is garbage collected.

	.. latex:vspace:: -4px
	"""

	#: The underlying requests session.
	session: requests.Session

	def __init__(self, url: Union[str, URL] = ''):
		super().__init__(url)
		self.session = requests.Session()

	def resolve(self: _R, timeout: Optional[int] = None) -> _R:
		"""
		Resolves the URL into its canonical form.

		This is done by making a ``HEAD`` request and following HTTP 302 redirects.

		.. versionadded:: 0.8.0

		.. versionchanged:: 1.1.0  Added the ``timeout`` argument.
		"""

		response: requests.Response = self.head(allow_redirects=True, timeout=timeout)

		if response.status_code != 200:
			raise requests.HTTPError(f"Could not resolve {self!r}: HTTP Status {response.status_code}")

		new_obj = self.__class__(response.url)
		new_obj.session = self.session
		return new_obj

	def get(self, params: _ParamsType = None, **kwargs) -> requests.Response:
		r"""
		Perform a GET request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET

		:param params: Dictionary, list of tuples or bytes to send
			in the query string for the :class:`requests.Request`.
		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.

		.. versionchanged:: 0.7.0

			If ``params`` is :py:obj:`None` but the URL has a query string,
			the query string will be parsed and used for ``params``.
		"""

		if params is None and self.query:
			params = self.query  # type: ignore

		return self.session.get(str(self.base_url), params=params, **kwargs)

	def options(self, **kwargs) -> requests.Response:
		r"""
		Send an OPTIONS request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS

		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.options(str(self.base_url), **kwargs)

	def head(self, **kwargs) -> requests.Response:
		r"""
		Send a HEAD request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD

		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
			If `allow_redirects` is not provided, it will be set to `False`
			(as opposed to the default :func:`requests.request` behavior).
		"""

		return self.session.head(str(self.base_url), **kwargs)

	def post(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		r"""
		Send a POST request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: json data to send in the body of the :class:`requests.Request`.
		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.post(str(self.base_url), data=data, json=json, **kwargs)

	def put(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		r"""
		Send a PUT request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: json data to send in the body of the :class:`requests.Request`.
		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.put(str(self.base_url), data=data, json=json, **kwargs)

	def patch(self, data: "_Data" = None, json=None, **kwargs) -> requests.Response:
		r"""
		Send a PATCH request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param json: json data to send in the body of the :class:`requests.Request`.
		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.patch(str(self.base_url), data=data, json=json, **kwargs)

	def delete(self, **kwargs) -> requests.Response:
		r"""
		Send a DELETE request using :requests:`.`.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE

		:param \*\*kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.delete(str(self.base_url), **kwargs)

	def __del__(self):  # pragma: no cover
		"""
		Attempt to close session when garbage collected to avoid leaving connections open.
		"""

		try:
			if sys.getrefcount(self.session) <= 2:
				self.session.close()
		except Exception:  # nosec: B110  # pylint: disable=bare-except
			pass

	def __truediv__(self, other):
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.
		"""

		new_obj = super().__truediv__(other)

		if new_obj is not NotImplemented:
			new_obj.session = self.session

		return new_obj


class TrailingRequestsURL(RequestsURL):
	"""
	Extension of :class:`~apeye.requests_url.RequestsURL` which adds a trailing slash to the end of the URL.

	.. versionadded:: 0.5.0

	:param url: The url to construct the :class:`~apeye.url.URL` object from.

	.. autoclasssumm:: TrailingRequestsURL
		:autosummary-sections: ;;
	"""

	def __str__(self) -> str:
		"""
		Returns the :class:`~.TrailingRequestsURL` as a string.
		"""

		return super().__str__().rstrip('/') + '/'
