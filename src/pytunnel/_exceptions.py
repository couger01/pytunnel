from __future__ import annotations


class PytunnelError(Exception):
    """Base exception for pytunnel errors."""


class TunnelConfigurationError(PytunnelError, ValueError):
    """Raised when tunnel configuration is invalid."""


class TunnelConnectionError(PytunnelError):
    """Raised when opening or maintaining a tunnel fails."""


class TunnelAlreadyOpenError(PytunnelError):
    """Raised when opening a tunnel that is already connected."""


class TunnelNotOpenError(PytunnelError):
    """Raised when an operation requires an open tunnel."""
