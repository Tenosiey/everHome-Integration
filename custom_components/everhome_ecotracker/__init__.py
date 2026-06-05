"""The everHome EcoTracker integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EcoTrackerApiClient
from .const import DEFAULT_SCAN_INTERVAL
from .coordinator import EcoTrackerDataUpdateCoordinator

# Typed config entry: ``entry.runtime_data`` holds our coordinator instance.
type EcoTrackerConfigEntry = ConfigEntry[EcoTrackerDataUpdateCoordinator]

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: EcoTrackerConfigEntry
) -> bool:
    """Set up everHome EcoTracker from a config entry."""
    session = async_get_clientsession(hass)
    client = EcoTrackerApiClient(entry.data[CONF_HOST], session)

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = EcoTrackerDataUpdateCoordinator(
        hass, client, timedelta(seconds=scan_interval)
    )

    # Perform the first refresh before forwarding to platforms so that the
    # sensors are created with data already available (and setup fails cleanly
    # if the device is unreachable).
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry when the user changes options (e.g. the scan interval).
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: EcoTrackerConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant, entry: EcoTrackerConfigEntry
) -> None:
    """Reload the config entry when its options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
