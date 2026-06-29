# Usage

## Sync API

```python
from pytunnel import SSHAuthConfig, SSHTunnel, SSHTunnelConfig

config = SSHTunnelConfig(
    ssh_host="bastion.example.com",
    auth=SSHAuthConfig(
        username="alice",
        private_key_path="~/.ssh/id_ed25519",
    ),
    remote_host="database.internal",
    remote_port=5432,
    local_host="127.0.0.1",
    local_port=15432,
)

with SSHTunnel(config) as tunnel:
    print(tunnel.status)
    print(f"Database is available on localhost:{tunnel.local_port}")
```

## Async API

```python
import asyncio

from pytunnel import AsyncSSHTunnel, SSHAuthConfig, SSHTunnelConfig


async def main() -> None:
    config = SSHTunnelConfig(
        ssh_host="bastion.example.com",
        auth=SSHAuthConfig(username="alice", password="secret"),
        remote_host="database.internal",
        remote_port=5432,
        local_port=15432,
    )

    async with AsyncSSHTunnel(config) as tunnel:
        print(tunnel.status)
        print(f"Database is available on localhost:{tunnel.local_port}")


asyncio.run(main())
```

## Simulator API

Use the simulator classes when tests or local development need the tunnel lifecycle
without opening an SSH connection:

```python
from pytunnel import SSHAuthConfig, SSHTunnelConfig, SimulatedSSHTunnel

config = SSHTunnelConfig(
    ssh_host="bastion.example.com",
    auth=SSHAuthConfig(username="alice", password="secret"),
    remote_host="database.internal",
    remote_port=5432,
)

with SimulatedSSHTunnel(config) as tunnel:
    assert tunnel.is_connected()
    print(tunnel.local_port)
```

## Tunnel status

`tunnel.status` returns a `TunnelStatus` value:

- `TunnelStatus.DISCONNECTED`: the tunnel is closed.
- `TunnelStatus.CONNECTED`: the SSH connection is active.
- `TunnelStatus.LOST_CONNECTION`: the tunnel was open, but the underlying SSH connection
  closed unexpectedly.
