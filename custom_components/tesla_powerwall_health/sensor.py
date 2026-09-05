"""Sensor platform for the Tesla Powerwall Health integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import TeslaPowerwallConfigEntry
from .entity import TeslaPowerwallEntity


@dataclass(frozen=True, kw_only=True)
class TeslaPowerwallSensorEntityDescription(SensorEntityDescription):
    """Describes a Tesla Powerwall Health sensor."""

    value_fn: Callable[[dict[str, Any]], StateType]


def _wh_to_kwh(value: float | None) -> float | None:
    return None if value is None else round(value / 1000, 2)


SENSOR_DESCRIPTIONS: tuple[TeslaPowerwallSensorEntityDescription, ...] = (
    TeslaPowerwallSensorEntityDescription(
        key="soe_percent",
        translation_key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("soe_percent"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="usable_capacity",
        translation_key="usable_capacity",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda d: _wh_to_kwh(d.get("nominal_full_pack_energy")),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="capacity_degradation_percent",
        translation_key="capacity_degradation",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("capacity_degradation_percent"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="backup_reserve_percent",
        translation_key="backup_reserve",
        icon="mdi:battery-lock",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("backup_reserve_percent"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="battery_power",
        translation_key="battery_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("battery_power"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="site_power",
        translation_key="site_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("site_power"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="load_power",
        translation_key="load_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("load_power"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="solar_power",
        translation_key="solar_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("solar_power"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="pack_voltage",
        translation_key="pack_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("pack_voltage"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="pack_frequency",
        translation_key="pack_frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("pack_frequency"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="pack_current",
        translation_key="pack_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.get("pack_current"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="energy_charged_wh",
        translation_key="energy_charged_lifetime",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda d: _wh_to_kwh(d.get("energy_charged_wh")),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="energy_discharged_wh",
        translation_key="energy_discharged_lifetime",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda d: _wh_to_kwh(d.get("energy_discharged_wh")),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="equivalent_full_cycles",
        translation_key="equivalent_full_cycles",
        icon="mdi:battery-sync",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: d.get("equivalent_full_cycles"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="operating_mode",
        translation_key="operating_mode",
        icon="mdi:cog",
        value_fn=lambda d: d.get("operating_mode"),
    ),
    TeslaPowerwallSensorEntityDescription(
        key="grid_status",
        translation_key="grid_status",
        icon="mdi:transmission-tower",
        value_fn=lambda d: d.get("grid_status"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeslaPowerwallConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Powerwall Health sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        TeslaPowerwallSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class TeslaPowerwallSensor(TeslaPowerwallEntity, SensorEntity):
    """A single Tesla Powerwall Health sensor."""

    entity_description: TeslaPowerwallSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: TeslaPowerwallSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data or {})
