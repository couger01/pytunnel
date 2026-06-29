from __future__ import annotations

from enum import Enum


class TunnelStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    LOST_CONNECTION = "lost_connection"
