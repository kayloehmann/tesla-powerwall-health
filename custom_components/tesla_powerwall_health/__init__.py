"""The Tesla Powerwall Health integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

from .api import TeslaGatewayApiClient, create_gateway_session
from .coordinator import TeslaPowerwallDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

type TeslaPowerwallConfigEntry = ConfigEntry[TeslaPowerwallDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: TeslaPowerwallConfigEntry) -> bool:
    """Set up Tesla Powerwall Health from a config entry."""
    session = create_gateway_session()
    client = TeslaGatewayApiClient(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )
    coordinator = TeslaPowerwallDataUpdateCoordinator(hass, entry, client)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await session.close()
        raise

    entry.runtime_data = coordinator
    entry.async_on_unload(session.close)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TeslaPowerwallConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
