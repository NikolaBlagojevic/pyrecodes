#!/usr/bin/env python
#
#  url.py
"""
Email address validation functions.

.. versionadded:: 1.0.0

This module is a subset of https://pypi.org/project/email-validator
"""
#
# Based on https://github.com/JoshData/python-email-validator
# Licensed under the CC0 License
#

# stdlib
import re
import sys
import unicodedata
from typing import Any, Dict, Optional, Union

# 3rd party
import idna  # implements IDNA 2008; Python's codec is only IDNA 2003
from domdf_python_tools.doctools import prettify_docstrings

__all__ = [
		"EmailSyntaxError",
		"ValidatedEmail",
		"main",
		"validate_email",
		"validate_email_domain_part",
		"validate_email_local_part"
		]

# Based on RFC 2822 section 3.2.4 / RFC 5322 section 3.2.3, these
# characters are permitted in email addresses (not taking into
# account internationalization):
ATEXT: str = r'a-zA-Z0-9_!#\$%&\'\*\+\-/=\?\^`\{\|\}~'

# A "dot atom text", per RFC 2822 3.2.4:
DOT_ATOM_TEXT: str = f'[{ATEXT}]+(?:\\.[{ATEXT}]+)*'

# RFC 6531 section 3.3 extends the allowed characters in internationalized
# addresses to also include three specific ranges of UTF8 defined in
# RFC3629 section 4, which appear to be the Unicode code points from
# U+0080 to U+10FFFF.
ATEXT_UTF8: str = ATEXT + "-􏿿"  # Don't convert to f-string
DOT_ATOM_TEXT_UTF8: str = f'[{ATEXT_UTF8}]+(?:\\.[{ATEXT_UTF8}]+)*'

# The domain part of the email address, after IDNA (ASCII) encoding,
# must also satisfy the requirements of RFC 952/RFC 1123 which restrict
# the allowed characters of hostnames further. The hyphen cannot be at
# the beginning or end of a *dot-atom component* of a hostname either.
ATEXT_HOSTNAME: str = r'(?:(?:[a-zA-Z0-9][a-zA-Z0-9\-]*)?[a-zA-Z0-9])'

# Length constants
# RFC 3696 + errata 1003 + errata 1690 (https://www.rfc-editor.org/errata_search.php?rfc=3696&eid=1690)
# explains the maximum length of an email address is 254 octets.
EMAIL_MAX_LENGTH: int = 254
LOCAL_PART_MAX_LENGTH: int = 64
DOMAIN_MAX_LENGTH: int = 255


class EmailSyntaxError(ValueError):
	"""
	Exception raised when an email address fails validation because of its form.
	"""


@prettify_docstrings
class ValidatedEmail:
	"""
	Represents the return type of the :func:`~apeye.email_validator.validate_email` function.

	This class holds the normalized form of the email address alongside other information.

	:param original_email: The original, unnormalized email address.
	:param email: The normalized email address, which should always be used in preference to the original address.
	:param local_part: The local part of the email address after Unicode normalization.
	:param domain: The domain part of the email address after Unicode normalization or conversion to Unicode from IDNA ascii.
	:param ascii_email: If not :py:obj:`None`, a form of the email address that uses 7-bit ASCII characters only.
	:param ascii_local_part: If not :py:obj:`None`, the local part of the email address using 7-bit ASCII characters only.
	:param ascii_domain: If not :py:obj:`None`, a form of the domain name that uses 7-bit ASCII characters only.
	:param smtputf8: Indicates whether SMTPUTF8 will be required to transmit messages to this address.

	.. autosummary-widths:: 1/4
	"""

	#: The email address that was passed to validate_email. (If passed as bytes, this will be a string.)
	original_email: str

	email: str
	"""
	The normalized email address, which should always be used in preference to the original address.

	The normalized address converts an IDNA ASCII domain name to Unicode, if possible,
	and performs Unicode normalization on the local part and on the domain (if originally Unicode).
	It is the concatenation of the local_part and domain attributes, separated by an @-sign.
	"""

	#: The local part of the email address after Unicode normalization.
	local_part: str

	#: The domain part of the email address after Unicode normalization or conversion to Unicode from IDNA ascii.
	domain: str

	#: If not :py:obj:`None`, a form of the email address that uses 7-bit ASCII characters only.
	ascii_email: Optional[str]

	#: If not :py:obj:`None`, the local part of the email address using 7-bit ASCII characters only.
	ascii_local_part: Optional[str]

	#: If not :py:obj:`None`, a form of the domain name that uses 7-bit ASCII characters only.
	ascii_domain: Optional[str]

	smtputf8: Optional[bool]
	"""
	If :py:obj:`True`, the SMTPUTF8 feature of your mail relay will be required to transmit messages
	to this address.

	This flag is :py:obj:`True` when :attr:`~.ascii_local_part` is missing.
	Otherwise it is :py:obj:`False`.
	"""

	def __init__(
			self,
			original_email: str,
			email: str,
			local_part: str,
			domain: str,
			*,
			ascii_email: Optional[str] = None,
			ascii_local_part: Optional[str] = None,
			ascii_domain: Optional[str] = None,
			smtputf8: Optional[bool] = None,
			):
		self.original_email = original_email
		self.email = email
		self.local_part = local_part
		self.domain = domain
		self.ascii_email = ascii_email
		self.ascii_local_part = ascii_local_part
		self.ascii_domain = ascii_domain
		self.smtputf8 = smtputf8

	def __str__(self) -> str:
		"""
		Return a string representation of the :class:`~apeye.email_validator.ValidatedEmail` object.
		"""

		return self.email

	def __repr__(self) -> str:
		"""
		Return a string representation of the :class:`~apeye.email_validator.ValidatedEmail` object.
		"""

		return f"<ValidatedEmail {self.email}>"

	def __eq__(self, other) -> bool:
		"""
		Return ``self == other``.
		"""

		return (
				self.email == other.email and self.local_part == other.local_part and self.domain == other.domain
				and self.ascii_email == other.ascii_email and self.ascii_local_part == other.ascii_local_part
				and self.ascii_domain == other.ascii_domain and self.smtputf8 == other.smtputf8
				)

	def as_dict(self) -> Dict[str, Any]:
		"""
		Convenience method for accessing the :class:`~apeye.email_validator.ValidatedEmail` as a dict.
		"""

		return {
				"original_email": self.original_email,
				"email": self.email,
				"local_part": self.local_part,
				"domain": self.domain,
				"ascii_email": self.ascii_email,
				"ascii_local_part": self.ascii_local_part,
				"ascii_domain": self.ascii_domain,
				"smtputf8": self.smtputf8,
				}


def __get_length_reason(addr: str, utf8: bool = False, limit: int = EMAIL_MAX_LENGTH):
	diff = len(addr) - limit
	prefix = "at least " if utf8 else ''
	suffix = 's' if diff > 1 else ''
	return f"({prefix}{diff} character{suffix} too many)"


def validate_email(
		email: Union[str, bytes],
		allow_smtputf8: bool = True,
		allow_empty_local: bool = False,
		) -> ValidatedEmail:
	"""
	Validates an email address.

	:param email: Either a string, or ASCII-encoded bytes.
	:param allow_smtputf8:
	:param allow_empty_local: Whether to allow the local part (the bit before the @-sign) to be empty.

	:raises EmailSyntaxError: if the address is not valid
	"""

	# Allow email to be a str or bytes instance. If bytes,
	# it must be ASCII because that's how the bytes work
	# on the wire with SMTP.
	if not isinstance(email, str):
		try:
			email = email.decode("ascii")
		except ValueError:
			raise EmailSyntaxError("The email address is not valid ASCII.")

	# At-sign.
	parts = email.split('@')
	if len(parts) != 2:
		raise EmailSyntaxError("The email address is not valid. It must have exactly one @-sign.")

	# Validate the email address's local part syntax and get a normalized form.
	local_part_info = validate_email_local_part(
			parts[0],
			allow_smtputf8=allow_smtputf8,
			allow_empty_local=allow_empty_local,
			)

	# Validate the email address's domain part syntax and get a normalized form.
	domain_part_info = validate_email_domain_part(parts[1])

	ret = ValidatedEmail(
			original_email=email,
			email=f"{local_part_info['local_part']}@{domain_part_info['domain']}",
			local_part=local_part_info["local_part"],
			domain=domain_part_info["domain"],
			ascii_local_part=local_part_info["ascii_local_part"],
			smtputf8=local_part_info["smtputf8"],
			ascii_domain=domain_part_info["ascii_domain"],
			)

	# If the email address has an ASCII form, add it.
	if not ret.smtputf8:
		ret.ascii_email = ret.ascii_local_part + '@' + ret.ascii_domain  # type: ignore[operator]

	# If the email address has an ASCII representation, then we assume it may be
	# transmitted in ASCII (we can't assume SMTPUTF8 will be used on all hops to
	# the destination) and the length limit applies to ASCII characters (which is
	# the same as octets). The number of characters in the internationalized form
	# may be many fewer (because IDNA ASCII is verbose) and could be less than 254
	# Unicode characters, and of course the number of octets over the limit may
	# not be the number of characters over the limit, so if the email address is
	# internationalized, we can't give any simple information about why the address
	# is too long.
	#
	# In addition, check that the UTF-8 encoding (i.e. not IDNA ASCII and not
	# Unicode characters) is at most 254 octets. If the addres is transmitted using
	# SMTPUTF8, then the length limit probably applies to the UTF-8 encoded octets.
	# If the email address has an ASCII form that differs from its internationalized
	# form, I don't think the internationalized form can be longer, and so the ASCII
	# form length check would be sufficient. If there is no ASCII form, then we have
	# to check the UTF-8 encoding. The UTF-8 encoding could be up to about four times
	# longer than the number of characters.
	#
	# See the length checks on the local part and the domain.

	if ret.ascii_email and len(ret.ascii_email) > EMAIL_MAX_LENGTH:
		if ret.ascii_email == ret.email:
			reason = __get_length_reason(ret.ascii_email)
		elif len(ret.email) > EMAIL_MAX_LENGTH:
			# If there are more than 254 characters, then the ASCII
			# form is definitely going to be too long.
			reason = __get_length_reason(ret.email, utf8=True)
		else:
			reason = "(when converted to IDNA ASCII)"
		raise EmailSyntaxError(f"The email address is too long {reason}.")

	if len(ret.email.encode("utf8")) > EMAIL_MAX_LENGTH:
		if len(ret.email) > EMAIL_MAX_LENGTH:
			# If there are more than 254 characters, then the UTF-8
			# encoding is definitely going to be too long.
			reason = __get_length_reason(ret.email, utf8=True)
		else:
			reason = "(when encoded in bytes)"
		raise EmailSyntaxError(f"The email address is too long {reason}.")

	return ret


def validate_email_local_part(
		local: str,
		allow_smtputf8: bool = True,
		allow_empty_local: bool = False,
		) -> Dict[str, Any]:
	"""
	Validates the local part of an email address  (the part before the @-sign).

	:param local:
	:param allow_smtputf8:
	:param allow_empty_local: Whether to allow the local part to be empty/
	"""

	if len(local) == 0:
		if not allow_empty_local:
			raise EmailSyntaxError("There must be something before the @-sign.")
		else:
			# The caller allows an empty local part. Useful for validating certain
			# Postfix aliases.
			return {
					"local_part": local,
					"ascii_local_part": local,
					"smtputf8": False,
					}

	# RFC 5321 4.5.3.1.1
	# We're checking the number of characters here. If the local part
	# is ASCII-only, then that's the same as bytes (octets). If it's
	# internationalized, then the UTF-8 encoding may be longer, but
	# that may not be relevant. We will check the total address length
	# instead.
	if len(local) > LOCAL_PART_MAX_LENGTH:
		reason = __get_length_reason(local, limit=LOCAL_PART_MAX_LENGTH)
		raise EmailSyntaxError(f"The email address is too long before the @-sign {reason}.")

	# Check the local part against the regular expression for the older ASCII requirements.
	m = re.match(DOT_ATOM_TEXT + "\\Z", local)
	if m:
		# Return the local part unchanged and flag that SMTPUTF8 is not needed.
		return {
				"local_part": local,
				"ascii_local_part": local,
				"smtputf8": False,
				}

	else:
		# The local part failed the ASCII check. Now try the extended internationalized requirements.
		m = re.match(DOT_ATOM_TEXT_UTF8 + "\\Z", local)
		if not m:
			# It's not a valid internationalized address either. Report which characters were not valid.
			bad_chars = ", ".join(
					sorted({
							c
							for c in local
							if not re.match('[' + (ATEXT if not allow_smtputf8 else ATEXT_UTF8) + ']', c)
							})
					)
			raise EmailSyntaxError(
					f"The email address contains invalid characters before the @-sign: {bad_chars}."
					)

		# It would be valid if internationalized characters were allowed by the caller.
		if not allow_smtputf8:
			raise EmailSyntaxError("Internationalized characters before the @-sign are not supported.")

		# It's valid.

		# RFC 6532 section 3.1 also says that Unicode NFC normalization should be applied,
		# so we'll return the normalized local part in the return value.
		local = unicodedata.normalize("NFC", local)

		# Flag that SMTPUTF8 will be required for deliverability.
		return {
				"local_part": local,
				"ascii_local_part": None,  # no ASCII form is possible
				"smtputf8": True,
				}


def validate_email_domain_part(domain: str) -> Dict[str, str]:
	"""
	Validate the domain part of an email address (the part after the @-sign).

	:param domain:
	"""

	# Empty?
	if len(domain) == 0:
		raise EmailSyntaxError("There must be something after the @-sign.")

	# Perform UTS-46 normalization, which includes casefolding, NFC normalization,
	# and converting all label separators (the period/full stop, fullwidth full stop,
	# ideographic full stop, and halfwidth ideographic full stop) to basic periods.
	# It will also raise an exception if there is an invalid character in the input,
	# such as "⒈" which is invalid because it would expand to include a period.
	try:
		domain = idna.uts46_remap(domain, std3_rules=False, transitional=False)
	except idna.IDNAError as e:
		raise EmailSyntaxError(f"The domain name {domain} contains invalid characters ({str(e)}).")

	# Now we can perform basic checks on the use of periods (since equivalent
	# symbols have been mapped to periods). These checks are needed because the
	# IDNA library doesn't handle well domains that have empty labels (i.e. initial
	# dot, trailing dot, or two dots in a row).
	if domain.endswith('.'):
		raise EmailSyntaxError("An email address cannot end with a period.")
	if domain.startswith('.'):
		raise EmailSyntaxError("An email address cannot have a period immediately after the @-sign.")
	if ".." in domain:
		raise EmailSyntaxError("An email address cannot have two periods in a row.")

	# Regardless of whether international characters are actually used,
	# first convert to IDNA ASCII. For ASCII-only domains, the transformation
	# does nothing. If internationalized characters are present, the MTA
	# must either support SMTPUTF8 or the mail client must convert the
	# domain name to IDNA before submission.
	#
	# Unfortunately this step incorrectly 'fixes' domain names with leading
	# periods by removing them, so we have to check for this above. It also gives
	# a funky error message ("No input") when there are two periods in a
	# row, also checked separately above.
	try:
		ascii_domain = idna.encode(domain, uts46=False).decode("ascii")
	except idna.IDNAError as e:
		if "Domain too long" in str(e):
			# We can't really be more specific because UTS-46 normalization means
			# the length check is applied to a string that is different from the
			# one the user supplied. Also I'm not sure if the length check applies
			# to the internationalized form, the IDNA ASCII form, or even both!
			raise EmailSyntaxError("The email address is too long after the @-sign.")
		raise EmailSyntaxError(f"The domain name {domain} contains invalid characters ({str(e)}).")

	# We may have been given an IDNA ASCII domain to begin with. Check
	# that the domain actually conforms to IDNA. It could look like IDNA
	# but not be actual IDNA. For ASCII-only domains, the conversion out
	# of IDNA just gives the same thing back.
	#
	# This gives us the canonical internationalized form of the domain,
	# which we should use in all error messages.
	try:
		domain_i18n = idna.decode(ascii_domain.encode("ascii"))
	except idna.IDNAError as e:
		raise EmailSyntaxError(f"The domain name {ascii_domain} is not valid IDNA ({str(e)}).")

	# RFC 5321 4.5.3.1.2
	# We're checking the number of bytes (octets) here, which can be much
	# higher than the number of characters in internationalized domains,
	# on the assumption that the domain may be transmitted without SMTPUTF8
	# as IDNA ASCII. This is also checked by idna.encode, so this exception
	# is never reached.
	if len(ascii_domain) > DOMAIN_MAX_LENGTH:
		raise EmailSyntaxError("The email address is too long after the @-sign.")

	# A "dot atom text", per RFC 2822 3.2.4, but using the restricted
	# characters allowed in a hostname (see ATEXT_HOSTNAME above).
	DOT_ATOM_TEXT = ATEXT_HOSTNAME + r'(?:\.' + ATEXT_HOSTNAME + r')*'

	# Check the regular expression. This is probably entirely redundant
	# with idna.decode, which also checks this format.
	m = re.match(DOT_ATOM_TEXT + "\\Z", ascii_domain)
	if not m:
		raise EmailSyntaxError("The email address contains invalid characters after the @-sign.")

	# All publicly deliverable addresses have domain named with at least
	# one period. We also know that all TLDs end with a letter.
	if '.' not in ascii_domain:
		raise EmailSyntaxError("The domain name %s is not valid. It should have a period." % domain_i18n)
	if not re.search(r"[A-Za-z]\Z", ascii_domain):
		raise EmailSyntaxError(
				"The domain name %s is not valid. It is not within a valid top-level domain." % domain_i18n
				)

	# Return the IDNA ASCII-encoded form of the domain, which is how it
	# would be transmitted on the wire (except when used with SMTPUTF8
	# possibly), as well as the canonical Unicode form of the domain,
	# which is better for display purposes. This should also take care
	# of RFC 6532 section 3.1's suggestion to apply Unicode NFC
	# normalization to addresses.
	return {
			"ascii_domain": ascii_domain,
			"domain": domain_i18n,
			}


def main():  # noqa: D103
	# stdlib
	import json

	if len(sys.argv) == 1:
		for line in sys.stdin:
			email = line.strip()
			try:
				validate_email(email)
			except EmailSyntaxError as e:
				print(f"{email} {e}")
	else:
		# Validate the email address passed on the command line.
		email = sys.argv[1]
		try:
			result = validate_email(email)
			print(json.dumps(result.as_dict(), indent=2, sort_keys=True, ensure_ascii=False))
		except EmailSyntaxError as e:
			print(e)


if __name__ == "__main__":
	sys.exit(main())
