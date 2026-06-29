from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from pytunnel import (
    SSHAuthConfig,
    SSHTunnel,
    SSHTunnelConfig,
    TunnelAlreadyOpenError,
    TunnelConnectionError,
    TunnelStatus,
)


class FakeTransport:
    def __init__(self, *, active: bool = True) -> None:
        self.active = active

    def is_active(self) -> bool:
        return self.active


class FakeClient:
    def __init__(self, transport: FakeTransport | None = None) -> None:
        self.transport = transport or FakeTransport()
        self.closed = False
        self.connected = False

    def set_missing_host_key_policy(self, policy: object) -> None:
        self.policy = policy

    def load_system_host_keys(self) -> None:
        self.loaded_system_keys = True

    def connect(self, *args: Any, **kwargs: Any) -> None:
        self.connected = True

    def get_transport(self) -> FakeTransport | None:
        return self.transport

    def close(self) -> None:
        self.closed = True


def _config() -> SSHTunnelConfig:
    return SSHTunnelConfig(
        ssh_host="ssh.example.com",
        auth=SSHAuthConfig(username="alice", password="secret"),
        remote_host="db.internal",
        remote_port=5432,
    )


def test_sync_tunnel_open_close(monkeypatch: pytest.MonkeyPatch) -> None:
    server = MagicMock()
    server.server_address = ("127.0.0.1", 45000)
    server.remote_host = ""
    server.remote_port = 0
    server.transport = None
    monkeypatch.setattr("pytunnel._sync._ForwardServer", MagicMock(return_value=server))

    thread = MagicMock()
    monkeypatch.setattr("pytunnel._sync.threading.Thread", MagicMock(return_value=thread))

    tunnel = SSHTunnel(_config(), client_factory=cast(Any, FakeClient))

    tunnel.open()

    assert tunnel.status is TunnelStatus.CONNECTED
    assert tunnel.local_port == 45000
    thread.start.assert_called_once_with()

    tunnel.close()

    assert tunnel.status is TunnelStatus.DISCONNECTED
    server.shutdown.assert_called_once_with()
    server.server_close.assert_called_once_with()


def test_sync_tunnel_rejects_double_open(monkeypatch: pytest.MonkeyPatch) -> None:
    server = MagicMock()
    server.server_address = ("127.0.0.1", 45000)
    monkeypatch.setattr("pytunnel._sync._ForwardServer", MagicMock(return_value=server))
    monkeypatch.setattr("pytunnel._sync.threading.Thread", MagicMock())

    tunnel = SSHTunnel(_config(), client_factory=cast(Any, FakeClient))
    tunnel.open()

    with pytest.raises(TunnelAlreadyOpenError):
        tunnel.open()

    tunnel.close()


def test_sync_status_detects_lost_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = FakeTransport()
    client = FakeClient(transport)
    server = MagicMock()
    server.server_address = ("127.0.0.1", 45000)
    monkeypatch.setattr("pytunnel._sync._ForwardServer", MagicMock(return_value=server))
    monkeypatch.setattr("pytunnel._sync.threading.Thread", MagicMock())

    tunnel = SSHTunnel(_config(), client_factory=cast(Any, lambda: client))
    tunnel.open()
    transport.active = False

    assert tunnel.status is TunnelStatus.LOST_CONNECTION

    tunnel.close()


def test_sync_wraps_open_errors() -> None:
    class BrokenClient(FakeClient):
        def connect(self, *args: Any, **kwargs: Any) -> None:
            raise OSError("no route")

    tunnel = SSHTunnel(_config(), client_factory=cast(Any, BrokenClient))

    with pytest.raises(TunnelConnectionError):
        tunnel.open()


def test_sync_context_manager_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    server = MagicMock()
    server.server_address = ("127.0.0.1", 45000)
    monkeypatch.setattr("pytunnel._sync._ForwardServer", MagicMock(return_value=server))
    monkeypatch.setattr("pytunnel._sync.threading.Thread", MagicMock())

    tunnel = SSHTunnel(_config(), client_factory=cast(Any, FakeClient))

    with tunnel as opened:
        assert opened.status is TunnelStatus.CONNECTED

    assert tunnel.status is TunnelStatus.DISCONNECTED
