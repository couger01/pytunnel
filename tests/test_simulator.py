from __future__ import annotations

import socket

import pytest

from pytunnel import (
    AsyncSimulatedSSHTunnel,
    SimulatedSSHTunnel,
    SSHAuthConfig,
    SSHTunnelConfig,
    TunnelAlreadyOpenError,
    TunnelConnectionError,
    TunnelStatus,
)


def _config(*, local_port: int = 0) -> SSHTunnelConfig:
    return SSHTunnelConfig(
        ssh_host="ssh.example.com",
        auth=SSHAuthConfig(username="alice", password="secret"),
        remote_host="db.internal",
        remote_port=5432,
        local_port=local_port,
    )


def test_simulated_tunnel_open_close() -> None:
    tunnel = SimulatedSSHTunnel(_config())

    tunnel.open()

    assert tunnel.status is TunnelStatus.CONNECTED
    assert tunnel.is_connected() is True
    assert tunnel.local_port > 0

    tunnel.close()

    assert tunnel.status is TunnelStatus.DISCONNECTED
    assert tunnel.is_connected() is False


def test_simulated_tunnel_rejects_double_open() -> None:
    tunnel = SimulatedSSHTunnel(_config())
    tunnel.open()

    with pytest.raises(TunnelAlreadyOpenError):
        tunnel.open()

    tunnel.close()


def test_simulated_tunnel_reports_port_conflicts() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        port = int(sock.getsockname()[1])

        tunnel = SimulatedSSHTunnel(_config(local_port=port))

        with pytest.raises(TunnelConnectionError):
            tunnel.open()

        assert tunnel.status is TunnelStatus.DISCONNECTED


def test_simulated_tunnel_context_manager_closes() -> None:
    tunnel = SimulatedSSHTunnel(_config())

    with tunnel as opened:
        assert opened.status is TunnelStatus.CONNECTED

    assert tunnel.status is TunnelStatus.DISCONNECTED


def test_simulated_tunnel_can_simulate_connection_loss() -> None:
    tunnel = SimulatedSSHTunnel(_config())
    tunnel.open()

    tunnel.simulate_connection_loss()

    assert tunnel.status is TunnelStatus.LOST_CONNECTION
    assert tunnel.is_connected() is False


@pytest.mark.asyncio
async def test_async_simulated_tunnel_open_close() -> None:
    tunnel = AsyncSimulatedSSHTunnel(_config())

    await tunnel.open()

    assert tunnel.status is TunnelStatus.CONNECTED
    assert tunnel.is_connected() is True
    assert tunnel.local_port > 0

    await tunnel.close()

    assert tunnel.status is TunnelStatus.DISCONNECTED
    assert tunnel.is_connected() is False


@pytest.mark.asyncio
async def test_async_simulated_tunnel_rejects_double_open() -> None:
    tunnel = AsyncSimulatedSSHTunnel(_config())
    await tunnel.open()

    with pytest.raises(TunnelAlreadyOpenError):
        await tunnel.open()

    await tunnel.close()


@pytest.mark.asyncio
async def test_async_simulated_tunnel_reports_port_conflicts() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        port = int(sock.getsockname()[1])

        tunnel = AsyncSimulatedSSHTunnel(_config(local_port=port))

        with pytest.raises(TunnelConnectionError):
            await tunnel.open()

        assert tunnel.status is TunnelStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_async_simulated_tunnel_context_manager_closes() -> None:
    tunnel = AsyncSimulatedSSHTunnel(_config())

    async with tunnel as opened:
        assert opened.status is TunnelStatus.CONNECTED

    assert tunnel.status is TunnelStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_async_simulated_tunnel_can_simulate_connection_loss() -> None:
    tunnel = AsyncSimulatedSSHTunnel(_config())
    await tunnel.open()

    tunnel.simulate_connection_loss()

    assert tunnel.status is TunnelStatus.LOST_CONNECTION
    assert tunnel.is_connected() is False
