# pytunnel

`pytunnel` provides sync and async Python APIs for opening, closing, and monitoring SSH
tunnels.

The sync API uses `paramiko`. The async API uses `asyncssh`, so async callers get native
asyncio behavior instead of a thread-wrapped sync SSH client.

## Installation

```bash
uv add pytunnel
```

Both SSH backends are required runtime dependencies for now:

- `paramiko` for `SSHTunnel`
- `asyncssh` for `AsyncSSHTunnel`

## Sync Usage

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

You can also manage the lifecycle manually:

```python
tunnel = SSHTunnel(config)
tunnel.open()
try:
    assert tunnel.is_connected()
finally:
    tunnel.close()
```

## Async Usage

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

## Tunnel Status

`tunnel.status` returns a `TunnelStatus` value:

- `TunnelStatus.DISCONNECTED`: the tunnel is closed.
- `TunnelStatus.CONNECTED`: the SSH connection is active.
- `TunnelStatus.LOST_CONNECTION`: the tunnel was open, but the underlying SSH connection
  closed unexpectedly.

## Development

Install dependencies:

```bash
uv sync --group dev
```

Run all default nox checks:

```bash
uv run nox
```

Run individual checks:

```bash
uv run nox -s lint
uv run nox -s typecheck
uv run nox -s docs
uv run nox -s changelog
uv run nox -s tests
```

Format code:

```bash
uv run nox -s format
```

Install pre-commit hooks with `prek`:

```bash
uv run prek install
```

Run hooks across the repository:

```bash
uv run nox -s prek
```

The test matrix in `noxfile.py` targets Python 3.10 through Python 3.15.

### Changelog

This project uses Towncrier to build `CHANGELOG.md` from fragments in `newsfragments/`.
Every user-visible change should include one fragment. See `newsfragments/README.md` for
the fragment naming policy. See `RELEASE.md` for the release process and main branch
policy.
