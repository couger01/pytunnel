from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pytunnel._exceptions import TunnelConfigurationError


@dataclass(frozen=True, slots=True)
class SSHAuthConfig:
    username: str
    password: str | None = None
    private_key_path: Path | str | None = None
    private_key_passphrase: str | None = None

    def __post_init__(self) -> None:
        if not self.username:
            msg = "username is required"
            raise TunnelConfigurationError(msg)
        if self.password is None and self.private_key_path is None:
            msg = "password or private_key_path is required"
            raise TunnelConfigurationError(msg)

    @property
    def private_key_path_str(self) -> str | None:
        if self.private_key_path is None:
            return None
        return str(self.private_key_path)


@dataclass(frozen=True, slots=True)
class SSHTunnelConfig:
    ssh_host: str
    auth: SSHAuthConfig
    remote_host: str
    remote_port: int
    local_host: str = "127.0.0.1"
    local_port: int = 0
    ssh_port: int = 22
    connect_timeout: float | None = 10.0
    known_hosts: Path | str | None = None

    def __post_init__(self) -> None:
        _require_host(self.ssh_host, "ssh_host")
        _require_host(self.remote_host, "remote_host")
        _require_host(self.local_host, "local_host")
        _require_port(self.ssh_port, "ssh_port")
        _require_port(self.remote_port, "remote_port")
        _require_port(self.local_port, "local_port", allow_zero=True)
        if self.connect_timeout is not None and self.connect_timeout <= 0:
            msg = "connect_timeout must be positive"
            raise TunnelConfigurationError(msg)

    @property
    def known_hosts_str(self) -> str | None:
        if self.known_hosts is None:
            return None
        return str(self.known_hosts)


def _require_host(value: str, field_name: str) -> None:
    if not value:
        msg = f"{field_name} is required"
        raise TunnelConfigurationError(msg)


def _require_port(value: int, field_name: str, *, allow_zero: bool = False) -> None:
    minimum = 0 if allow_zero else 1
    if value < minimum or value > 65535:
        msg = f"{field_name} must be between {minimum} and 65535"
        raise TunnelConfigurationError(msg)
