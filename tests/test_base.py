from __future__ import annotations

import pytest

from pytunnel import (
    AsyncSimulatedSSHTunnel,
    AsyncSSHTunnel,
    AsyncTunnel,
    SimulatedSSHTunnel,
    SSHAuthConfig,
    SSHTunnel,
    SSHTunnelConfig,
    Tunnel,
)


def _config() -> SSHTunnelConfig:
    return SSHTunnelConfig(
        ssh_host="ssh.example.com",
        auth=SSHAuthConfig(username="alice", password="secret"),
        remote_host="db.internal",
        remote_port=5432,
    )


def test_sync_tunnels_implement_tunnel_abc() -> None:
    assert isinstance(SSHTunnel(_config()), Tunnel)
    assert isinstance(SimulatedSSHTunnel(_config()), Tunnel)


def test_async_tunnels_implement_async_tunnel_abc() -> None:
    assert isinstance(AsyncSSHTunnel(_config()), AsyncTunnel)
    assert isinstance(AsyncSimulatedSSHTunnel(_config()), AsyncTunnel)


def test_tunnel_abc_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Tunnel(_config())


def test_async_tunnel_abc_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        AsyncTunnel(_config())
