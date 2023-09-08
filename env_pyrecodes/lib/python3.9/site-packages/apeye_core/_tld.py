#!/usr/bin/env python
#
#  _tld.py
"""
Functions for parsing top-level domains (TLDs).

A stripped back version of https://github.com/john-kurkowski/tldextract
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Adapted from https://github.com/john-kurkowski/tldextract
#  Licensed under the BSD 3-Clause License
#
#  Copyright (c) 2020, John Kurkowski
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import functools
import re
import socket
from typing import List, Tuple
from urllib.parse import scheme_chars

# 3rd party
import idna
from domdf_python_tools.compat import importlib_resources

__all__ = [
		"determine_suffix_index",
		"extract_tld",
		"extract_tlds_from_suffix_list",
		"load_suffix_list",
		"looks_like_ip"
		]

PUBLIC_SUFFIX_RE = re.compile(r"^(?P<suffix>[.*!]*\w[\S]*)", re.UNICODE | re.MULTILINE)
PUBLIC_PRIVATE_SUFFIX_SEPARATOR: str = "// ===BEGIN PRIVATE DOMAINS==="
IP_RE = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')  # pylint: disable=line-too-long
SCHEME_RE = re.compile(fr'^([{scheme_chars}]+:)?//')


def extract_tlds_from_suffix_list(suffix_list_text: str) -> Tuple[List[str], List[str]]:
	"""
	Parse the raw suffix list text for its different designations of suffixes.

	:param suffix_list_text:

	:returns: A two element tuple of ``(public TLDs, private TLDs)``.
	"""

	public_text, _, private_text = suffix_list_text.partition(PUBLIC_PRIVATE_SUFFIX_SEPARATOR)
	public_tlds = [m.group("suffix") for m in PUBLIC_SUFFIX_RE.finditer(public_text)]
	private_tlds = [m.group("suffix") for m in PUBLIC_SUFFIX_RE.finditer(private_text)]
	return public_tlds, private_tlds


@functools.lru_cache(1)
def load_suffix_list() -> Tuple[List[str], List[str]]:
	"""
	Load the public suffix list from disk.

	:returns: A two element tuple of ``(public TLDs, private TLDs)``.
	"""

	return extract_tlds_from_suffix_list(importlib_resources.read_text("apeye_core", "public_suffix_list.dat"))


def _decode_punycode(label: str) -> str:
	lowered = label.lower()
	looks_like_puny = lowered.startswith("xn--")

	if looks_like_puny:
		try:
			return idna.decode(label.encode("ascii")).lower()
		except (UnicodeError, IndexError):
			pass

	return lowered


def determine_suffix_index(tlds: List[str], elements: List[str]) -> int:
	"""
	Returns the index of the first suffix label, or ``len(elements)`` if no suffix is found.

	:param tlds: The list of public TLDs.
	:param elements: The elements of the domain, e.g. ``['forums', 'bbc', 'co', 'uk']``.
	"""

	length = len(elements)
	for i in range(length):
		maybe_tld = '.'.join(elements[i:])
		exception_tld = '!' + maybe_tld

		if exception_tld in tlds:
			return i + 1

		if maybe_tld in tlds:
			return i

		wildcard_tld = "*." + '.'.join(elements[i + 1:])
		if wildcard_tld in tlds:
			return i

	return length


def looks_like_ip(maybe_ip: str) -> bool:
	"""
	Returns whether the given string looks like an IP address.

	:param maybe_ip:
	"""

	if not maybe_ip[0].isdigit():
		return False

	try:
		socket.inet_aton(maybe_ip)
		return True

	except (AttributeError, UnicodeError):
		if IP_RE.match(maybe_ip):
			return True
		return False

	except OSError:
		return False


def extract_tld(url: str) -> Tuple[str, str, str]:
	"""
	Takes a string URL and splits it into its subdomain, domain, and suffix
	(effective TLD, gTLD, ccTLD, etc.) component.

	.. versionadded:: 1.0.0 (undocumented)

	.. code-block:: python

		>>> Domain._make(extract_tld('https://forums.news.cnn.com/'))
		Domain(subdomain='forums.news', domain='cnn', suffix='com')
		>>> Domain._make(extract_tld('https://forums.bbc.co.uk/')
		Domain(subdomain='forums', domain='bbc', suffix='co.uk')
	"""  # noqa: D400

	netloc_ = SCHEME_RE.sub('', url).partition('/')[0].partition('?')[0].partition('#')[0]
	netloc = netloc_.split('@')[-1].partition(':')[0].strip().rstrip('.')

	labels = netloc.split('.')

	translations = [_decode_punycode(label) for label in labels]
	tlds, _ = load_suffix_list()
	suffix_index = determine_suffix_index(tlds, translations)
	suffix = '.'.join(labels[suffix_index:])

	if not suffix and netloc and looks_like_ip(netloc):
		return '', netloc, ''

	subdomain = '.'.join(labels[:suffix_index - 1]) if suffix_index else ''
	domain = labels[suffix_index - 1] if suffix_index else ''
	return subdomain, domain, suffix
