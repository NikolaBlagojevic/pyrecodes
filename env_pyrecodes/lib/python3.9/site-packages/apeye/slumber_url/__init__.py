#!/usr/bin/env python
#
#  slumber_url.py
"""
Subclass of :class:`~apeye.url.URL` with support for interacting with
REST APIs with `Slumber <https://slumber.readthedocs.io>`__ and
`Requests <https://requests.readthedocs.io>`__.

.. versionadded:: 0.2.0
"""  # noqa: D400
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
#  Based on the "pathlib" module from CPython.
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
#
#  Based on Slumber <https://slumber.readthedocs.io>
#  Copyright (c) 2011 Donald Stufft
#  Licensed under the 2-clause BSD License
#
#  Some docstrings from Requests <https://requests.readthedocs.io>
#  Copyright 2019 Kenneth Reitz
#  Licensed under the Apache License, Version 2.0
#

# stdlib
import copy
import sys
from typing import Callable, Dict, MutableMapping, Optional, Tuple, Union
from urllib.parse import unquote

# 3rd party
from requests import PreparedRequest, Session
from requests.auth import AuthBase
from requests.structures import CaseInsensitiveDict
from requests.utils import guess_json_utf

# this package
from apeye.requests_url import _Data
from apeye.slumber_url.exceptions import (
		HttpClientError,
		HttpNotFoundError,
		HttpServerError,
		SlumberBaseException,
		SlumberHttpBaseException
		)
from apeye.slumber_url.serializers import (
		JsonSerializer,
		Serializer,
		SerializerNotAvailable,
		SerializerRegistry,
		YamlSerializer
		)
from apeye.url import URL

__all__ = [
		"SlumberURL",
		"SerializerRegistry",
		"YamlSerializer",
		"Serializer",
		"JsonSerializer",
		"SlumberBaseException",
		"SlumberHttpBaseException",
		"HttpClientError",
		"HttpNotFoundError",
		"HttpServerError",
		"SerializerNotAvailable",
		]


# Ignore the LGTM warning as the "session" etc. attributes should **not** affect equality.
# Equality should only consider the URL, not its attributes.
class SlumberURL(URL):  # lgtm [py/missing-equals]
	"""
	Subclass of :class:`~apeye.url.URL` with support for interacting with
	REST APIs with `Slumber <https://slumber.readthedocs.io>`__ and
	`Requests <https://requests.readthedocs.io>`__.

	:param url: The url to construct the :class:`~apeye.slumber_url.SlumberURL` object from.
	:param auth:
	:param format:
	:param append_slash:
	:param session:
	:param serializer:
	:param timeout: How long to wait for the server to send data before giving up.
	:param allow_redirects: Whether to allow redirects.
	:param proxies: Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
	:param verify: Either a boolean, in which case it controls whether we verify
		the server's TLS certificate, or a string, in which case it must be a path
		to a CA bundle to use.
	:param cert: Either the path to the SSL client cert file (``.pem``),
		or a tuple of ``('cert', 'key')``.

	``timeout``, ``allow_redirects``, ``proxies``, ``verify`` and ``cert`` are
	passed to Requests when making any HTTP requests, and are inherited by all children
	created from this URL.

	.. latex:vspace:: 10px
	.. versionchanged:: 0.3.0  The ``url`` parameter can now be a string or a :class:`~.URL`.

	.. versionchanged:: 1.1.0

		When a :class:`~.RequestsURL` object is deleted or garbage collected,
		the underlying :class:`requests.Session` object it only closed if no objects hold references to the session.
		This prevents the session object of a global object from being inadvertently closed
		when one of its children is garbage collected.
	"""  # noqa: D400

	serializer: SerializerRegistry
	"""
	The serializer used to (de)serialize the data when interacting with the API.

	.. versionadded:: 0.6.0
	"""

	session: Session
	"""
	The underlying requests session.

	.. versionadded:: 0.6.0
	"""

	#: How long to wait for the server to send data before giving up.
	timeout: Union[None, float, Tuple[float, float], Tuple[float, None]]

	#: Whether to allow redirects.
	allow_redirects: Optional[bool]

	#: Dictionary mapping protocol or protocol and hostname to the URL of the proxy.
	proxies: Optional[MutableMapping[str, str]]

	verify: Union[None, bool, str]
	"""
	Either a boolean, in which case it controls whether we verify
	the server's TLS certificate, or a string, in which case it must be a path
	to a CA bundle to use.
	"""

	#: The path to ssl client cert file or a tuple of ``('cert', 'key')``.
	cert: Union[str, Tuple[str, str], None]

	def __init__(
			self,
			url: Union[str, URL] = '',
			auth: Union[None, Tuple[str, str], AuthBase, Callable[[PreparedRequest], PreparedRequest]] = None,
			format: str = "json",  # noqa: A002  # pylint: disable=redefined-builtin
			append_slash: bool = True,
			session=None,
			serializer: Optional[SerializerRegistry] = None,
			*,
			timeout: Union[None, float, Tuple[float, float], Tuple[float, None]] = None,
			allow_redirects: Optional[bool] = True,
			proxies: Optional[MutableMapping[str, str]] = None,
			verify: Union[None, bool, str] = None,
			cert: Union[str, Tuple[str, str], None] = None,
			):
		super().__init__(url)

		if serializer is None:
			serializer = SerializerRegistry(default=format)

		if session is None:
			session = Session()

		self.serializer = serializer
		self.session = session

		if auth is not None:
			self.session.auth = auth

		self._store = {
				"format": format if format is not None else "json",
				"append_slash": append_slash,
				"session": self.session,
				"serializer": self.serializer,
				}

		self.timeout = timeout
		self.allow_redirects = allow_redirects
		self.proxies = proxies
		self.verify = verify
		self.cert = cert

	def url(self) -> str:
		"""
		Returns the URL as a string.
		"""

		url = str(self.base_url)

		if self._store["append_slash"] and not url.endswith('/'):
			url = url + '/'

		return url

	def _request(self, method, data=None, files=None, params=None):
		serializer = self.serializer
		url = self.url()

		headers = {"accept": serializer.get_content_type()}

		if not files:
			headers["content-type"] = serializer.get_content_type()
			if data is not None:
				data = serializer.dumps(data)

		resp = self.session.request(
				method,
				url,
				data=data,
				params=params,
				files=files,
				headers=headers,
				timeout=self.timeout,
				allow_redirects=self.allow_redirects,  # type: ignore[arg-type]
				proxies=self.proxies,
				verify=self.verify,
				cert=self.cert,
				)

		if 400 <= resp.status_code <= 499:
			exception_class = HttpNotFoundError if resp.status_code == 404 else HttpClientError
			raise exception_class(
					f"Client Error {resp.status_code}: {unquote(resp.url)}",
					response=resp,
					content=resp.content,
					)

		elif 500 <= resp.status_code <= 599:
			raise HttpServerError(
					f"Server Error {resp.status_code}: {unquote(resp.url)}",
					response=resp,
					content=resp.content,
					)

		self._ = resp

		return resp

	def _try_to_serialize_response(self, resp):
		s = self.serializer
		if resp.status_code in [204, 205]:
			return

		if resp.headers.get("content-type", None) and resp.content:
			content_type = resp.headers.get("content-type").split(';')[0].strip()

			try:
				stype = s.get_serializer(content_type=content_type)
			except SerializerNotAvailable:
				return resp.content

			if isinstance(resp.content, bytes):
				try:
					encoding = guess_json_utf(resp.content)
					return stype.loads(resp.content.decode(encoding))
				except Exception:
					return resp.content
			return stype.loads(resp.content)
		else:
			return resp.content

	def _process_response(self, resp):
		# TODO: something to expose headers and status

		if 200 <= resp.status_code <= 299:
			return self._try_to_serialize_response(resp)
		else:
			return  # @@@ We should probably do some sort of error here? (Is this even possible?)

	def get(self, **params) -> Dict:
		"""
		Perform a GET request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET

		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("GET", params=params)
		return self._process_response(resp)

	def post(self, data: _Data = None, files=None, **params) -> Dict:
		"""
		Perform a POST request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("POST", data=data, files=files, params=params)
		return self._process_response(resp)

	def patch(self, data=None, files=None, **params) -> Dict:
		"""
		Perform a PATCH request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("PATCH", data=data, files=files, params=params)
		return self._process_response(resp)

	def put(self, data=None, files=None, **params) -> Dict:
		"""
		Perform a PUT request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PUT

		:param data: Dictionary, list of tuples, bytes, or file-like
			object to send in the body of the :class:`requests.Request`.
		:param files: Dictionary of ``'name': file-like-objects``
			(or ``{'name': file-tuple}``) for multipart encoding upload.
			``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
			3-tuple ``('filename', fileobj, 'content_type')``
			or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``,
			where ``'content-type'`` is a string defining the content type of the
			given file and ``custom_headers`` a dict-like object containing additional
			headers to add for the file.
		:param params: Parameters to send in the query string of the :class:`requests.Request`.
		"""

		resp = self._request("PUT", data=data, files=files, params=params)
		return self._process_response(resp)

	def delete(self, **params) -> bool:
		"""
		Perform a DELETE request using `Slumber <https://slumber.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE

		:param params: Parameters to send in the query string of the :class:`requests.Request`.

		:returns: :py:obj:`True` if the DELETE request succeeded. :py:obj:`False` otherwise.
		"""

		resp = self._request("DELETE", params=params)
		# if 200 <= resp.status_code <= 299:
		# 	if resp.status_code == 204:
		# 		return True
		# 	else:
		# 		return True
		# else:
		# 	return False
		return 200 <= resp.status_code <= 299

	def __del__(self):  # pragma: no cover
		"""
		Attempt to close session when garbage collected to avoid leaving connections open.
		"""

		try:
			if sys.getrefcount(self.session) <= 2:
				self.session.close()
		except Exception:  # nosec: B110  # pylint: disable=bare-except
			pass

	def options(self, **kwargs) -> str:
		"""
		Send an OPTIONS request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS

		:param kwargs: Optional arguments that :func:`requests.request` takes.
		"""

		return self.session.options(str(self.base_url), **kwargs).headers.get("Allow", '')

	def head(self, **kwargs) -> CaseInsensitiveDict:
		"""
		Send a HEAD request using `Requests <https://requests.readthedocs.io>`__.

		https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/HEAD

		:param kwargs: Optional arguments that :func:`requests.request` takes.
			If `allow_redirects` is not provided, it will be set to :py:obj:`False`
			(as opposed to the default :func:`requests.request` behavior).
		"""

		return self.session.head(str(self.base_url), **kwargs).headers

	def __truediv__(self, other):
		"""
		Construct a new :class:`~apeye.url.URL` object for the given child of this :class:`~apeye.url.URL`.
		"""

		new_obj = super().__truediv__(other)

		if new_obj is not NotImplemented:
			new_obj._store = copy.copy(self._store)
			new_obj.serializer = self.serializer
			new_obj.session = self.session
			new_obj.timeout = self.timeout
			new_obj.allow_redirects = self.allow_redirects
			new_obj.proxies = self.proxies
			new_obj.verify = self.verify
			new_obj.cert = self.cert

		return new_obj
