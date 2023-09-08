#!/usr/bin/env python
#
#  terminal.py
"""
Useful functions for terminal-based programs.

.. versionchanged:: 2.0.0

	:func:`domdf_python_tools.terminal.get_terminal_size` was removed.
	Use :func:`shutil.get_terminal_size` instead.
"""
#
#  Copyright © 2014-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Parts of the docstrings based on the Python 3.8.2 Documentation
#  Licensed under the Python Software Foundation License Version 2.
#  Copyright © 2001-2020 Python Software Foundation. All rights reserved.
#  Copyright © 2000 BeOpen.com. All rights reserved.
#  Copyright © 1995-2000 Corporation for National Research Initiatives. All rights reserved.
#  Copyright © 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
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
#  "Echo" based on ChemPy (https://github.com/bjodah/chempy)
#  |  Copyright (c) 2015-2018, Björn Dahlgren
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without modification,
#  |  are permitted provided that the following conditions are met:
#  |
#  |    Redistributions of source code must retain the above copyright notice, this
#  |    list of conditions and the following disclaimer.
#  |
#  |    Redistributions in binary form must reproduce the above copyright notice, this
#  |    list of conditions and the following disclaimer in the documentation and/or
#  |    other materials provided with the distribution.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  |  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  |  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  |  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#  |  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  |  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  |  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  |  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  |  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  |  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import inspect
import os
import pprint
import textwrap
from shutil import get_terminal_size
from typing import IO, Optional

# this package
from domdf_python_tools.words import CR

__all__ = [
		"clear",
		"br",
		"interrupt",
		"overtype",
		"get_terminal_size",
		"Echo",
		]


def clear() -> None:
	"""
	Clears the display.

	Works for Windows and POSIX, but does not clear the Python Interpreter or PyCharm's Console.
	"""

	if os.name == "nt":  # pragma: no cover (!Windows)
		os.system("cls")  # nosec: B607,B605
	else:  # pragma: no cover (!Linux)
		print("\u001bc", end='')


def br() -> None:
	"""
	Prints a blank line.
	"""

	print('')


def interrupt() -> None:
	"""
	Print the key combination needed to abort the script; dynamic depending on OS.

	Useful when you have a long-running script that you might want to
	interrupt part way through.

	**Example:**

	.. code-block:: python

		>>> interrupt()
		(Press Ctrl-C to quit at any time)

	"""

	print(f"(Press Ctrl-{'C' if os.name == 'nt' else 'D'} to quit at any time)")


def overtype(
		*objects,
		sep: str = ' ',
		end: str = '',
		file: Optional[IO] = None,
		flush: bool = False,
		) -> None:
	r"""
	Print ``*objects`` to the text stream ``file``, starting with ``'\\r'``, separated by ``sep``
	and followed by ``end``.

	All non-keyword arguments are converted to strings like :class:`str` does and written to the stream,
	separated by ``sep`` and followed by ``end``.

	If no objects are given, :func:`~.overtype` will just write ``"\\r"``.

	.. TODO:: This does not currently work in the PyCharm console, at least on Windows

	:param \*objects: A list of strings or string-like objects to write to the terminal.
	:param sep: The separator between values.
	:param end: The final value to print.
	:param file: An object with a ``write(string)`` method.
		If not present or :py:obj:`None`, :py:obj:`sys.stdout` will be used.
	:no-default file:
	:param flush: If :py:obj:`True` the stream is forcibly flushed after printing.
	"""  # noqa: D400

	object0 = f"{CR}{objects[0]}"
	objects = (object0, *objects[1:])
	print(*objects, sep=sep, end=end, file=file, flush=flush)


class Echo:
	"""
	Context manager for echoing variable assignments (in CPython).

	:param indent: The indentation of the dictionary of variable assignments.
	"""

	def __init__(self, indent: str = ' ' * 2):
		self.indent = indent

		frame = inspect.currentframe()
		if frame is None:  # pragma: no cover
			raise ValueError("Unable to obtain the frame of the caller.")
		else:
			self.parent_frame = inspect.currentframe().f_back  # type: ignore  # TODO

	def __enter__(self):
		"""
		Called when entering the context manager.
		"""

		self.locals_on_entry = self.parent_frame.f_locals.copy()  # type: ignore

	def __exit__(self, *args, **kwargs):
		"""
		Called when exiting the context manager.
		"""

		new_locals = {
				k: v
				for k,
				v in self.parent_frame.f_locals.items()  # type: ignore
				if k not in self.locals_on_entry
				}

		print(textwrap.indent(pprint.pformat(new_locals), self.indent))


if __name__ == "__main__":  # pragma: no cover
	size_x, size_y = get_terminal_size()
	print("width =", size_x, "height =", size_y)
