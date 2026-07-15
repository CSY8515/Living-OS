"""Compatibility alias for a relocated Living OS v1.2 engine."""

from importlib import import_module as _import_module
import sys as _sys

_sys.modules[__name__] = _import_module('subsystems.foundation.engines.backup')
