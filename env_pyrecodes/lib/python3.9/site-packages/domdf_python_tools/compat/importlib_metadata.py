# noqa: D100

# stdlib
import sys

if sys.version_info[:2] < (3, 9):  # pragma: no cover (py39+)
	# 3rd party
	import importlib_metadata
	globals().update(importlib_metadata.__dict__)

else:  # pragma: no cover (<py39)
	# stdlib
	import importlib.metadata
	globals().update(importlib.metadata.__dict__)
