#!/usr/bin/env python
#
#  url.py
"""
Email address validation functions.

.. versionadded:: 1.0.0

This module is a subset of https://pypi.org/project/email-validator

.. note::

	The classes in this module can instead be imported from the
	`apeye_core.email_validator <https://pypi.org/project/apeye-core/>`_ module instead.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
# Based on https://github.com/JoshData/python-email-validator
# Licensed under the CC0 License
#

# stdlib
import sys

# 3rd party
from apeye_core import email_validator

__all__ = [
		"EmailSyntaxError",
		"ValidatedEmail",
		"main",
		"validate_email",
		"validate_email_domain_part",
		"validate_email_local_part"
		]

EmailSyntaxError = email_validator.EmailSyntaxError
ValidatedEmail = email_validator.ValidatedEmail
ValidatedEmail.__module__ = "apeye.email_validator"

validate_email = email_validator.validate_email
validate_email_local_part = email_validator.validate_email_local_part
validate_email_domain_part = email_validator.validate_email_domain_part

main = email_validator.main

if __name__ == "__main__":
	sys.exit(email_validator.main())
