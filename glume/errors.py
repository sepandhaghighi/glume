# -*- coding: utf-8 -*-
"""glume errors."""


class GlumeError(Exception):
    """Base exception for all Glume errors."""


class GlumeValidationError(GlumeError, ValueError):
    """Raised when Glume inputs are invalid."""
