"""Base entity for the Tesla Powerwall Health integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import TeslaPowerwallDataUpdateCoordinator


class TeslaPowerwallEntity(CoordinatorEntity[TeslaPowerwallDataUpdateCoordinator]):
    """Base entity tied to one Gateway/battery device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TeslaPowerwallDataUpdateCoordinator, key: str) -> None:
        super().__init__(coordinator)
        host = coordinator.config_entry.data["host"]
        self._attr_unique_id = f"{host}_{key}"
        serial = (coordinator.data or {}).get("serial_number") or host
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            name="Tesla Powerwall",
            manufacturer=MANUFACTURER,
            model=(coordinator.data or {}).get("part_number") or "Gateway 2",
            serial_number=serial,
            configuration_url=f"https://{host}",
        )
