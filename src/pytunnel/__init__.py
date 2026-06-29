"""Public API for pytunnel."""

from pytunnel._async import AsyncSSHTunnel
from pytunnel._base import AsyncTunnel, Tunnel
from pytunnel._config import SSHAuthConfig, SSHTunnelConfig
from pytunnel._exceptions import (
    PytunnelError,
    TunnelAlreadyOpenError,
    TunnelConfigurationError,
    TunnelConnectionError,
    TunnelNotOpenError,
)
from pytunnel._simulator import AsyncSimulatedSSHTunnel, SimulatedSSHTunnel
from pytunnel._status import TunnelStatus
from pytunnel._sync import SSHTunnel

__all__ = [
    "AsyncSSHTunnel",
    "AsyncSimulatedSSHTunnel",
    "AsyncTunnel",
    "PytunnelError",
    "SSHAuthConfig",
    "SSHTunnel",
    "SSHTunnelConfig",
    "SimulatedSSHTunnel",
    "Tunnel",
    "TunnelAlreadyOpenError",
    "TunnelConfigurationError",
    "TunnelConnectionError",
    "TunnelNotOpenError",
    "TunnelStatus",
]
