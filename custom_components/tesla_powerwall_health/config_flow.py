"""Config flow for the Tesla Powerwall Health integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_HOST, CONF_PASSWORD

from .api import (
    TeslaGatewayApiClient,
    TeslaGatewayAuthError,
    TeslaGatewayConnectionError,
    create_gateway_session,
)
from .const import CONF_NAMEPLATE_CAPACITY_WH, DEFAULT_NAMEPLATE_CAPACITY_WH, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_NAMEPLATE_CAPACITY_WH, default=DEFAULT_NAMEPLATE_CAPACITY_WH): vol.Coerce(int),
    }
)


class TeslaPowerwallHealthConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesla Powerwall Health."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            async with create_gateway_session() as session:
                client = TeslaGatewayApiClient(
                    session,
                    user_input[CONF_HOST],
                    user_input[CONF_EMAIL],
                    user_input[CONF_PASSWORD],
                )
                try:
                    await client.async_login()
                except TeslaGatewayAuthError:
                    errors["base"] = "invalid_auth"
                except TeslaGatewayConnectionError:
                    errors["base"] = "cannot_connect"
                except aiohttp.ClientError:
                    _LOGGER.exception("Unerwarteter Fehler beim Verbindungstest")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=f"Tesla Powerwall ({user_input[CONF_HOST]})",
                        data=user_input,
                    )

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors)
