from __future__ import annotations

import pytest

from pytunnel import SSHAuthConfig, SSHTunnelConfig, TunnelConfigurationError


def test_auth_requires_username() -> None:
    with pytest.raises(TunnelConfigurationError, match="username"):
        SSHAuthConfig(username="", password="secret")


def test_auth_requires_password_or_private_key() -> None:
    with pytest.raises(TunnelConfigurationError, match="password or private_key_path"):
        SSHAuthConfig(username="alice")


def test_tunnel_config_validates_ports() -> None:
    auth = SSHAuthConfig(username="alice", password="secret")

    with pytest.raises(TunnelConfigurationError, match="remote_port"):
        SSHTunnelConfig(ssh_host="ssh.example.com", auth=auth, remote_host="db", remote_port=0)


def test_config_accepts_ephemeral_local_port() -> None:
    auth = SSHAuthConfig(username="alice", password="secret")

    config = SSHTunnelConfig(
        ssh_host="ssh.example.com",
        auth=auth,
        remote_host="db.internal",
        remote_port=5432,
        local_port=0,
    )

    assert config.local_port == 0
