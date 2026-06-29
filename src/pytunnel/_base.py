from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from typing_extensions import Self

from pytunnel._config import SSHTunnelConfig
from pytunnel._status import TunnelStatus


class _TunnelBase(ABC):
    """Shared tunnel lifecycle state."""

    def __init__(self, config: SSHTunnelConfig) -> None:
        self.config = config
        self._status = TunnelStatus.DISCONNECTED

    @property
    def status(self) -> TunnelStatus:
        """Current tunnel status.

        Returns
        -------
        TunnelStatus
            Current lifecycle state of the tunnel.
        """
        self._refresh_status()
        return self._status

    @property
    @abstractmethod
    def local_port(self) -> int:
        """Local port bound by the tunnel."""

    def is_connected(self) -> bool:
        """Return whether the tunnel is currently connected.

        Returns
        -------
        bool
            ``True`` when ``status`` is ``TunnelStatus.CONNECTED``.
        """
        return self.status is TunnelStatus.CONNECTED

    def _refresh_status(self) -> None:
        """Refresh backend-specific status before the status property returns."""
        if self._status is not TunnelStatus.CONNECTED:
            return


class Tunnel(_TunnelBase):
    """Abstract base class for synchronous tunnels."""

    @abstractmethod
    def open(self) -> None:
        """Open the tunnel."""

    @abstractmethod
    def close(self) -> None:
        """Close the tunnel."""

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


class AsyncTunnel(_TunnelBase):
    """Abstract base class for asynchronous tunnels."""

    @abstractmethod
    async def open(self) -> None:
        """Open the tunnel."""

    @abstractmethod
    async def close(self) -> None:
        """Close the tunnel."""

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
