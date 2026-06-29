from __future__ import annotations

from typing import Any, cast

import pytest

from pytunnel import (
    AsyncSSHTunnel,
    SSHAuthConfig,
    SSHTunnelConfig,
    TunnelAlreadyOpenError,
    TunnelConnectionError,
    TunnelStatus,
)


class FakeListener:
    def __init__(self, port: int = 45000) -> None:
        self.port = port
        self.closed = False

    def get_port(self) -> int:
        return self.port

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


class FakeConnection:
    def __init__(self) -> None:
        self.closed = False
        self.listener = FakeListener()

    async def forward_local_port(self, *args: Any, **kwargs: Any) -> FakeListener:
        return self.listener

    def is_closed(self) -> bool:
        return self.closed

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return None


def _config() -> SSHTunnelConfig:
    return SSHTunnelConfig(
        ssh_host="ssh.example.com",
        auth=SSHAuthConfig(username="alice", password="secret"),
        remote_host="db.internal",
        remote_port=5432,
    )


@pytest.mark.asyncio
async def test_async_tunnel_open_close() -> None:
    connection = FakeConnection()

    async def connect_factory(*args: Any, **kwargs: Any) -> FakeConnection:
        return connection

    tunnel = AsyncSSHTunnel(_config(), connect_factory=cast(Any, connect_factory))

    await tunnel.open()

    assert tunnel.status is TunnelStatus.CONNECTED
    assert tunnel.local_port == 45000

    await tunnel.close()

    assert tunnel.status is TunnelStatus.DISCONNECTED
    assert connection.closed is True
    assert connection.listener.closed is True


@pytest.mark.asyncio
async def test_async_tunnel_rejects_double_open() -> None:
    connection = FakeConnection()

    async def connect_factory(*args: Any, **kwargs: Any) -> FakeConnection:
        return connection

    tunnel = AsyncSSHTunnel(_config(), connect_factory=cast(Any, connect_factory))
    await tunnel.open()

    with pytest.raises(TunnelAlreadyOpenError):
        await tunnel.open()

    await tunnel.close()


@pytest.mark.asyncio
async def test_async_status_detects_lost_connection() -> None:
    connection = FakeConnection()

    async def connect_factory(*args: Any, **kwargs: Any) -> FakeConnection:
        return connection

    tunnel = AsyncSSHTunnel(_config(), connect_factory=cast(Any, connect_factory))
    await tunnel.open()
    connection.closed = True

    assert tunnel.status is TunnelStatus.LOST_CONNECTION

    await tunnel.close()


@pytest.mark.asyncio
async def test_async_wraps_open_errors() -> None:
    async def connect_factory(*args: Any, **kwargs: Any) -> FakeConnection:
        raise OSError("no route")

    tunnel = AsyncSSHTunnel(_config(), connect_factory=cast(Any, connect_factory))

    with pytest.raises(TunnelConnectionError):
        await tunnel.open()


@pytest.mark.asyncio
async def test_async_context_manager_closes() -> None:
    connection = FakeConnection()

    async def connect_factory(*args: Any, **kwargs: Any) -> FakeConnection:
        return connection

    tunnel = AsyncSSHTunnel(_config(), connect_factory=cast(Any, connect_factory))

    async with tunnel as opened:
        assert opened.status is TunnelStatus.CONNECTED

    assert tunnel.status is TunnelStatus.DISCONNECTED
