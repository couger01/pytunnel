from __future__ import annotations

from enum import Enum


class TunnelStatus(str, Enum):
    """Lifecycle state of an SSH tunnel.

    Attributes
    ----------
    DISCONNECTED
        The tunnel is closed.
    CONNECTED
        The tunnel is open and the underlying SSH connection is active.
    LOST_CONNECTION
        The tunnel was open, but the underlying SSH connection is no longer active.
    """

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    LOST_CONNECTION = "lost_connection"
