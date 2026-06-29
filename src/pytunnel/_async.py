from __future__ import annotations

from collections.abc import Awaitable, Callable

import asyncssh

from pytunnel._base import AsyncTunnel
from pytunnel._config import SSHTunnelConfig
from pytunnel._exceptions import TunnelAlreadyOpenError, TunnelConnectionError
from pytunnel._status import TunnelStatus

_ConnectFactory = Callable[..., Awaitable[asyncssh.SSHClientConnection]]


class AsyncSSHTunnel(AsyncTunnel):
    """Asynchronous SSH local port forward.

    ``AsyncSSHTunnel`` opens an SSH connection with AsyncSSH and forwards a local TCP
    port to a remote host and port reachable from the SSH server.

    Parameters
    ----------
    config
        Tunnel connection settings.
    connect_factory
        Optional coroutine factory used to create an AsyncSSH connection. This is
        primarily useful for tests or callers that need to inject a preconfigured
        connection implementation.
    """

    def __init__(
        self,
        config: SSHTunnelConfig,
        *,
        connect_factory: _ConnectFactory | None = None,
    ) -> None:
        super().__init__(config)
        self._connect_factory = connect_factory or asyncssh.connect
        self._connection: asyncssh.SSHClientConnection | None = None
        self._listener: asyncssh.SSHListener | None = None
        self._local_port = config.local_port

    def _refresh_status(self) -> None:
        if self._status is TunnelStatus.CONNECTED and not self._is_connection_active():
            self._status = TunnelStatus.LOST_CONNECTION

    @property
    def local_port(self) -> int:
        """Local port bound by the tunnel.

        Returns
        -------
        int
            The configured local port before the tunnel is opened, or the actual bound
            port after opening. This differs when ``config.local_port`` is ``0`` and the
            operating system chooses an ephemeral port.
        """
        return self._local_port

    async def open(self) -> None:
        """Open the SSH tunnel.

        Raises
        ------
        TunnelAlreadyOpenError
            If the tunnel is already connected.
        TunnelConnectionError
            If the SSH connection or local port forward cannot be established.
        """
        if self.status is TunnelStatus.CONNECTED:
            msg = "tunnel is already open"
            raise TunnelAlreadyOpenError(msg)

        try:
            connect_kwargs = {
                "port": self.config.ssh_port,
                "username": self.config.auth.username,
                "password": self.config.auth.password,
                "client_keys": [self.config.auth.private_key_path_str]
                if self.config.auth.private_key_path_str is not None
                else None,
                "passphrase": self.config.auth.private_key_passphrase,
                "connect_timeout": self.config.connect_timeout,
            }
            if self.config.known_hosts_str is not None:
                connect_kwargs["known_hosts"] = self.config.known_hosts_str

            connection = await self._connect_factory(
                self.config.ssh_host,
                **connect_kwargs,
            )
            listener = await connection.forward_local_port(
                self.config.local_host,
                self.config.local_port,
                self.config.remote_host,
                self.config.remote_port,
            )
            self._connection = connection
            self._listener = listener
            self._local_port = _listener_port(listener, self.config.local_port)
            self._status = TunnelStatus.CONNECTED
        except Exception as exc:
            self._status = TunnelStatus.DISCONNECTED
            msg = "failed to open SSH tunnel"
            raise TunnelConnectionError(msg) from exc

    async def close(self) -> None:
        """Close the SSH tunnel.

        The method is idempotent. Calling it on a disconnected tunnel leaves the tunnel
        disconnected.
        """
        if self._listener is not None:
            self._listener.close()
            await self._listener.wait_closed()
            self._listener = None
        if self._connection is not None:
            self._connection.close()
            await self._connection.wait_closed()
            self._connection = None
        self._status = TunnelStatus.DISCONNECTED

    def _is_connection_active(self) -> bool:
        return self._connection is not None and not self._connection.is_closed()


def _listener_port(listener: asyncssh.SSHListener, fallback: int) -> int:
    get_port = getattr(listener, "get_port", None)
    if get_port is None:
        return fallback
    port = get_port()
    return int(port)
