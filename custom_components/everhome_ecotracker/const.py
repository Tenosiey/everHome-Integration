"""Constants for the everHome EcoTracker integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

# The integration domain. Must be unique across Home Assistant and match the
# folder name as well as the "domain" key in manifest.json.
DOMAIN: Final = "everhome_ecotracker"

# Human readable name used for the created device.
MANUFACTURER: Final = "everHome"
MODEL: Final = "EcoTracker"
DEFAULT_NAME: Final = "everHome EcoTracker"

# Path of the local REST endpoint exposed by the EcoTracker.
API_PATH: Final = "/v1/json"

# How often we poll the device. The EcoTracker updates frequently, so a short
# interval gives near real-time power readings without hammering the device.
DEFAULT_SCAN_INTERVAL: Final = 10
MIN_SCAN_INTERVAL: Final = 1
MAX_SCAN_INTERVAL: Final = 300
DEFAULT_UPDATE_INTERVAL: Final = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

# Timeout (seconds) for a single request to the device.
REQUEST_TIMEOUT: Final = 10
