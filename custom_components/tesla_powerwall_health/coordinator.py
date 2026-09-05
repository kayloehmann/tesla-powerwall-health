"""DataUpdateCoordinator for the Tesla Powerwall Health integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TeslaGatewayApiClient, TeslaGatewayAuthError, TeslaGatewayConnectionError
from .const import CONF_NAMEPLATE_CAPACITY_WH, DEFAULT_NAMEPLATE_CAPACITY_WH, DEFAULT_SCAN_INTERVAL_SECONDS, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TeslaPowerwallDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches a battery-health snapshot from the Gateway on a fixed interval."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, client: TeslaGatewayApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self.client = client
        self.nameplate_capacity_wh = config_entry.data.get(
            CONF_NAMEPLATE_CAPACITY_WH, DEFAULT_NAMEPLATE_CAPACITY_WH
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.async_get_status()
        except TeslaGatewayAuthError as err:
            raise UpdateFailed(f"Anmeldung am Gateway fehlgeschlagen: {err}") from err
        except TeslaGatewayConnectionError as err:
            raise UpdateFailed(f"Gateway nicht erreichbar: {err}") from err

        full_pack_energy = data.get("nominal_full_pack_energy")
        if full_pack_energy is not None and self.nameplate_capacity_wh:
            data["capacity_degradation_percent"] = round(
                100 * full_pack_energy / self.nameplate_capacity_wh, 1
            )
        else:
            data["capacity_degradation_percent"] = None

        discharged = data.get("energy_discharged_wh")
        if discharged is not None and full_pack_energy:
            data["equivalent_full_cycles"] = round(discharged / full_pack_energy, 1)
        else:
            data["equivalent_full_cycles"] = None

        return data
