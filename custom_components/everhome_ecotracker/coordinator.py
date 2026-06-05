"""DataUpdateCoordinator for the everHome EcoTracker integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EcoTrackerApiClient, EcoTrackerConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EcoTrackerDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the EcoTracker and shares the result with all sensor entities.

    Using a single coordinator means the device is queried only once per update
    interval, regardless of how many sensor entities are created from the data.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: EcoTrackerApiClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data from the device."""
        try:
            return await self.client.async_get_data()
        except EcoTrackerConnectionError as err:
            # UpdateFailed marks all entities unavailable and lets the
            # coordinator retry automatically on the next interval.
            raise UpdateFailed(str(err)) from err
