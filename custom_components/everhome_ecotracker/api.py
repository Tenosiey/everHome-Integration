"""Small async client for the everHome EcoTracker local REST API."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import API_PATH, REQUEST_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class EcoTrackerError(Exception):
    """Base error for the EcoTracker client."""


class EcoTrackerConnectionError(EcoTrackerError):
    """Raised when the device cannot be reached or returns an error."""


class EcoTrackerApiClient:
    """Minimal client that reads the EcoTracker's local ``/v1/json`` endpoint."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Initialize the client.

        Args:
            host: IP address or hostname of the EcoTracker on the local network.
            session: Shared aiohttp session (provided by Home Assistant).
        """
        # Strip an accidentally pasted scheme / trailing slash so the user can
        # enter "http://1.2.3.4/" or "1.2.3.4" and both work.
        self._host = host.replace("http://", "").replace("https://", "").strip("/")
        self._session = session

    @property
    def host(self) -> str:
        """Return the normalized host."""
        return self._host

    @property
    def url(self) -> str:
        """Return the full URL of the JSON endpoint."""
        return f"http://{self._host}{API_PATH}"

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch the latest values from the device.

        Returns:
            The decoded JSON payload as a dict, e.g. ``{"power": 125, ...}``.

        Raises:
            EcoTrackerConnectionError: If the device is unreachable, times out,
                returns a non-200 status or sends a body that is not JSON.
        """
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.get(self.url)
                response.raise_for_status()
                # Some firmware versions return the JSON with a generic or
                # missing content-type, so we disable the strict check.
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise EcoTrackerConnectionError(
                f"Error communicating with EcoTracker at {self._host}: {err}"
            ) from err
        except ValueError as err:
            raise EcoTrackerConnectionError(
                f"EcoTracker at {self._host} returned invalid JSON: {err}"
            ) from err

        if not isinstance(data, dict):
            raise EcoTrackerConnectionError(
                f"Unexpected response from EcoTracker at {self._host}: {data!r}"
            )

        return data
