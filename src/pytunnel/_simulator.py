from __future__ import annotations

import socket

from pytunnel._base import AsyncTunnel, Tunnel
from pytunnel._config import SSHTunnelConfig
from pytunnel._exceptions import TunnelAlreadyOpenError, TunnelConnectionError
from pytunnel._status import TunnelStatus


class _SimulatedTunnelMixin:
    config: SSHTunnelConfig
    _socket: socket.socket | None
    _status: TunnelStatus
    _local_port: int

    def _init_simulated_tunnel(self) -> None:
        self._socket = None
        self._local_port = self.config.local_port

    @property
    def local_port(self) -> int:
        """Local port reserved by the simulated tunnel.

        Returns
        -------
        int
            The configured local port before the tunnel is opened, or the actual bound
            port after opening. This differs when ``config.local_port`` is ``0`` and the
            operating system chooses an ephemeral port.
        """
        return self._local_port

    def simulate_connection_loss(self) -> None:
        """Mark the simulated tunnel as having lost its connection."""
        if self._status is TunnelStatus.CONNECTED:
            self._close_simulated_tunnel()
            self._status = TunnelStatus.LOST_CONNECTION

    def _open_simulated_tunnel(self) -> None:
        if self._status is TunnelStatus.CONNECTED:
            msg = "tunnel is already open"
            raise TunnelAlreadyOpenError(msg)

        try:
            sock = _bind_socket(self.config.local_host, self.config.local_port)
        except OSError as exc:
            self._status = TunnelStatus.DISCONNECTED
            msg = "failed to open simulated SSH tunnel"
            raise TunnelConnectionError(msg) from exc

        self._socket = sock
        self._local_port = int(sock.getsockname()[1])
        self._status = TunnelStatus.CONNECTED

    def _close_simulated_tunnel(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self._status = TunnelStatus.DISCONNECTED


class SimulatedSSHTunnel(_SimulatedTunnelMixin, Tunnel):
    """Synchronous fake SSH local port forward.

    ``SimulatedSSHTunnel`` exposes the same lifecycle surface as ``SSHTunnel`` without
    opening an SSH connection or forwarding traffic. It binds a local TCP socket while
    open, which preserves local port allocation behavior for tests and local
    development.

    Parameters
    ----------
    config
        Tunnel connection settings.
    """

    def __init__(self, config: SSHTunnelConfig) -> None:
        super().__init__(config)
        self._init_simulated_tunnel()

    def open(self) -> None:
        """Open the simulated tunnel.

        Raises
        ------
        TunnelAlreadyOpenError
            If the simulated tunnel is already connected.
        TunnelConnectionError
            If the local port cannot be reserved.
        """
        self._open_simulated_tunnel()

    def close(self) -> None:
        """Close the simulated tunnel.

        The method is idempotent. Calling it on a disconnected simulated tunnel leaves
        the tunnel disconnected.
        """
        self._close_simulated_tunnel()


class AsyncSimulatedSSHTunnel(_SimulatedTunnelMixin, AsyncTunnel):
    """Asynchronous fake SSH local port forward.

    ``AsyncSimulatedSSHTunnel`` exposes the same lifecycle surface as
    ``AsyncSSHTunnel`` without opening an SSH connection or forwarding traffic. It binds
    a local TCP socket while open, which preserves local port allocation behavior for
    tests and local development.

    Parameters
    ----------
    config
        Tunnel connection settings.
    """

    def __init__(self, config: SSHTunnelConfig) -> None:
        super().__init__(config)
        self._init_simulated_tunnel()

    async def open(self) -> None:
        """Open the simulated tunnel.

        Raises
        ------
        TunnelAlreadyOpenError
            If the simulated tunnel is already connected.
        TunnelConnectionError
            If the local port cannot be reserved.
        """
        self._open_simulated_tunnel()

    async def close(self) -> None:
        """Close the simulated tunnel.

        The method is idempotent. Calling it on a disconnected simulated tunnel leaves
        the tunnel disconnected.
        """
        self._close_simulated_tunnel()


def _bind_socket(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()
    except Exception:
        sock.close()
        raise
    return sock
