"""Sensor platform for the everHome EcoTracker integration.

Every value exposed by the device's ``/v1/json`` endpoint is mapped to a Home
Assistant sensor entity. Optional values (per-phase power and high/low tariff
counters) are only created when the device actually reports them.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EcoTrackerConfigEntry
from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL
from .coordinator import EcoTrackerDataUpdateCoordinator

# Each description's ``key`` matches a field name in the JSON payload.
SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="powerAvg",
        translation_key="power_avg",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="powerPhase1",
        translation_key="power_phase1",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="powerPhase2",
        translation_key="power_phase2",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="powerPhase3",
        translation_key="power_phase3",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="energyCounterIn",
        translation_key="energy_counter_in",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="energyCounterInT1",
        translation_key="energy_counter_in_t1",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="energyCounterInT2",
        translation_key="energy_counter_in_t2",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="energyCounterOut",
        translation_key="energy_counter_out",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EcoTrackerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the EcoTracker sensors from a config entry."""
    coordinator = entry.runtime_data
    data: Mapping[str, Any] = coordinator.data or {}

    # Only create entities for fields the device actually reports. Some meters
    # do not provide per-phase power or high/low tariff counters.
    entities = [
        EcoTrackerSensor(coordinator, description, entry.unique_id or entry.entry_id)
        for description in SENSOR_DESCRIPTIONS
        if description.key in data
    ]

    async_add_entities(entities)


class EcoTrackerSensor(
    CoordinatorEntity[EcoTrackerDataUpdateCoordinator], SensorEntity
):
    """Representation of a single value read from the EcoTracker."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoTrackerDataUpdateCoordinator,
        description: SensorEntityDescription,
        device_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=DEFAULT_NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{coordinator.client.host}",
        )

    @property
    def native_value(self) -> float | int | None:
        """Return the current value for this sensor."""
        value = self.coordinator.data.get(self.entity_description.key)
        if isinstance(value, (int, float)):
            return value
        return None

    @property
    def available(self) -> bool:
        """Return True if the device is reachable and reports this value."""
        return (
            super().available
            and self.entity_description.key in self.coordinator.data
        )
