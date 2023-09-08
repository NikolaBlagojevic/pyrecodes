# noqa: D100,DALL000

# stdlib
import os
import sys
from typing import Any, BinaryIO, TextIO

if sys.version_info[:2] < (3, 7):  # pragma: no cover (py37+)
	# 3rd party
	import importlib_resources

	globals().update(importlib_resources.__dict__)

else:  # pragma: no cover (<py39)
	# stdlib
	import importlib.resources
	globals().update(importlib.resources.__dict__)

if not ((3, 7) <= sys.version_info < (3, 11)):  # pragma: no cover (py37 OR py38 OR py39 OR py310):

	def _normalize_path(path: Any) -> str:
		"""
		Normalize a path by ensuring it is a string.

		If the resulting string contains path separators, an exception is raised.
		"""

		parent, file_name = os.path.split(str(path))
		if parent:
			raise ValueError(f'{path!r} must be only a file name')
		return file_name

	def open_binary(package: Package, resource: Resource) -> BinaryIO:
		"""
		Return a file-like object opened for binary reading of the resource.
		"""

		return (files(package) / _normalize_path(resource)).open("rb")

	def read_binary(package: Package, resource: Resource) -> bytes:
		"""
		Return the binary contents of the resource.
		"""

		return (files(package) / _normalize_path(resource)).read_bytes()

	def open_text(
			package: Package,
			resource: Resource,
			encoding: str = "utf-8",
			errors: str = "strict",
			) -> TextIO:
		"""
		Return a file-like object opened for text reading of the resource.
		"""

		return (files(package) / _normalize_path(resource)).open(
				'r',
				encoding=encoding,
				errors=errors,
				)

	def read_text(
			package: Package,
			resource: Resource,
			encoding: str = "utf-8",
			errors: str = "strict",
			) -> str:
		"""
		Return the decoded string of the resource.
		"""

		with open_text(package, resource, encoding, errors) as fp:
			return fp.read()
