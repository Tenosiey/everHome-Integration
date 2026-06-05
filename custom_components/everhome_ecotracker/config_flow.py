"""Config and options flow for the everHome EcoTracker integration.

The config flow is the onboarding wizard shown when a user adds the integration
for the first time. It asks for the device IP address, verifies that the
EcoTracker can be reached and then creates the config entry.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    ConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EcoTrackerApiClient, EcoTrackerConnectionError
from .const import (
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class EcoTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the onboarding flow for a new EcoTracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where the user enters the device IP."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            client = EcoTrackerApiClient(host, async_get_clientsession(self.hass))

            try:
                await client.async_get_data()
            except EcoTrackerConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - surface any unexpected error
                _LOGGER.exception("Unexpected error connecting to EcoTracker")
                errors["base"] = "unknown"
            else:
                # Use the normalized host as the unique id so the same device
                # cannot be added twice.
                await self.async_set_unique_id(client.host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={CONF_HOST: client.host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> EcoTrackerOptionsFlow:
        """Return the options flow handler."""
        return EcoTrackerOptionsFlow()


class EcoTrackerOptionsFlow(OptionsFlow):
    """Allow the user to tweak the polling interval after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    )
                }
            ),
        )
