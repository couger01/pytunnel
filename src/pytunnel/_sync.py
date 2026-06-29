from __future__ import annotations

import select
import socketserver
import threading
from collections.abc import Callable
from types import TracebackType

import paramiko
from typing_extensions import Self

from pytunnel._config import SSHTunnelConfig
from pytunnel._exceptions import (
    TunnelAlreadyOpenError,
    TunnelConnectionError,
)
from pytunnel._status import TunnelStatus

_BUFFER_SIZE = 65_536


class SSHTunnel:
    def __init__(
        self,
        config: SSHTunnelConfig,
        *,
        client_factory: Callable[[], paramiko.SSHClient] | None = None,
    ) -> None:
        self.config = config
        self._client_factory = client_factory or paramiko.SSHClient
        self._client: paramiko.SSHClient | None = None
        self._server: _ForwardServer | None = None
        self._thread: threading.Thread | None = None
        self._status = TunnelStatus.DISCONNECTED

    @property
    def status(self) -> TunnelStatus:
        if self._status is TunnelStatus.CONNECTED and not self._is_transport_active():
            self._status = TunnelStatus.LOST_CONNECTION
        return self._status

    @property
    def local_port(self) -> int:
        if self._server is None:
            return self.config.local_port
        return int(self._server.server_address[1])

    def is_connected(self) -> bool:
        return self.status is TunnelStatus.CONNECTED

    def open(self) -> None:
        if self.status is TunnelStatus.CONNECTED:
            msg = "tunnel is already open"
            raise TunnelAlreadyOpenError(msg)

        client = self._client_factory()
        try:
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
            if self.config.known_hosts_str is not None:
                client.load_host_keys(self.config.known_hosts_str)
            else:
                client.load_system_host_keys()

            client.connect(
                self.config.ssh_host,
                port=self.config.ssh_port,
                username=self.config.auth.username,
                password=self.config.auth.password,
                key_filename=self.config.auth.private_key_path_str,
                passphrase=self.config.auth.private_key_passphrase,
                timeout=self.config.connect_timeout,
            )
            transport = client.get_transport()
            if transport is None or not transport.is_active():
                msg = "SSH transport did not become active"
                raise TunnelConnectionError(msg)

            server = _ForwardServer(
                (self.config.local_host, self.config.local_port),
                _ForwardHandler,
            )
            server.remote_host = self.config.remote_host
            server.remote_port = self.config.remote_port
            server.transport = transport

            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            self._client = client
            self._server = server
            self._thread = thread
            self._status = TunnelStatus.CONNECTED
        except Exception as exc:
            self._status = TunnelStatus.DISCONNECTED
            client.close()
            if isinstance(exc, TunnelConnectionError):
                raise
            msg = "failed to open SSH tunnel"
            raise TunnelConnectionError(msg) from exc

    def close(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
        if self._client is not None:
            self._client.close()
            self._client = None
        self._status = TunnelStatus.DISCONNECTED

    def __enter__(self) -> Self:
        self.open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _is_transport_active(self) -> bool:
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return transport is not None and transport.is_active()


class _ForwardServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    remote_host: str
    remote_port: int
    transport: paramiko.Transport


class _ForwardHandler(socketserver.BaseRequestHandler):
    server: _ForwardServer

    def handle(self) -> None:
        channel = self.server.transport.open_channel(
            "direct-tcpip",
            (self.server.remote_host, self.server.remote_port),
            self.request.getpeername(),
        )
        if channel is None:
            return

        try:
            while True:
                readable, _, _ = select.select([self.request, channel], [], [])
                if self.request in readable:
                    data = self.request.recv(_BUFFER_SIZE)
                    if not data:
                        break
                    channel.sendall(data)
                if channel in readable:
                    data = channel.recv(_BUFFER_SIZE)
                    if not data:
                        break
                    self.request.sendall(data)
        finally:
            channel.close()
            self.request.close()
