"""Binary sensor platform for the Tesla Powerwall Health integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeslaPowerwallConfigEntry
from .entity import TeslaPowerwallEntity

FAULT_DESCRIPTION = BinarySensorEntityDescription(
    key="battery_fault",
    translation_key="battery_fault",
    device_class=BinarySensorDeviceClass.PROBLEM,
)

GRID_DESCRIPTION = BinarySensorEntityDescription(
    key="grid_connected",
    translation_key="grid_connected",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeslaPowerwallConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Powerwall Health binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            TeslaPowerwallFaultBinarySensor(coordinator, FAULT_DESCRIPTION),
            TeslaPowerwallGridBinarySensor(coordinator, GRID_DESCRIPTION),
        ]
    )


class TeslaPowerwallFaultBinarySensor(TeslaPowerwallEntity, BinarySensorEntity):
    """On when the Gateway reports an active grid fault or disabled reason."""

    def __init__(self, coordinator, description: BinarySensorEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        return bool(data.get("grid_faults")) or bool(data.get("disabled_reasons"))

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        return {
            "grid_faults": data.get("grid_faults", []),
            "disabled_reasons": data.get("disabled_reasons", []),
        }


class TeslaPowerwallGridBinarySensor(TeslaPowerwallEntity, BinarySensorEntity):
    """On while the Gateway is grid-connected."""

    def __init__(self, coordinator, description: BinarySensorEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        return data.get("grid_status") == "SystemGridConnected"
