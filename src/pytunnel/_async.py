from __future__ import annotations

from collections.abc import Awaitable, Callable
from types import TracebackType

import asyncssh
from typing_extensions import Self

from pytunnel._config import SSHTunnelConfig
from pytunnel._exceptions import TunnelAlreadyOpenError, TunnelConnectionError
from pytunnel._status import TunnelStatus

_ConnectFactory = Callable[..., Awaitable[asyncssh.SSHClientConnection]]


class AsyncSSHTunnel:
    def __init__(
        self,
        config: SSHTunnelConfig,
        *,
        connect_factory: _ConnectFactory | None = None,
    ) -> None:
        self.config = config
        self._connect_factory = connect_factory or asyncssh.connect
        self._connection: asyncssh.SSHClientConnection | None = None
        self._listener: asyncssh.SSHListener | None = None
        self._status = TunnelStatus.DISCONNECTED
        self._local_port = config.local_port

    @property
    def status(self) -> TunnelStatus:
        if self._status is TunnelStatus.CONNECTED and not self._is_connection_active():
            self._status = TunnelStatus.LOST_CONNECTION
        return self._status

    @property
    def local_port(self) -> int:
        return self._local_port

    def is_connected(self) -> bool:
        return self.status is TunnelStatus.CONNECTED

    async def open(self) -> None:
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
        if self._listener is not None:
            self._listener.close()
            await self._listener.wait_closed()
            self._listener = None
        if self._connection is not None:
            self._connection.close()
            await self._connection.wait_closed()
            self._connection = None
        self._status = TunnelStatus.DISCONNECTED

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    def _is_connection_active(self) -> bool:
        return self._connection is not None and not self._connection.is_closed()


def _listener_port(listener: asyncssh.SSHListener, fallback: int) -> int:
    get_port = getattr(listener, "get_port", None)
    if get_port is None:
        return fallback
    port = get_port()
    return int(port)
