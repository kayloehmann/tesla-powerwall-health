"""Thin async client for the Tesla Gateway 2 local API.

Only the read-only endpoints needed for battery health monitoring are
covered. Authentication uses the Gateway's local ``customer`` login
(POST /api/login/Basic), which yields a session cookie -- there is no
long-lived API token on this API, so the client re-authenticates
transparently whenever a call comes back 401/403.
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

TIMEOUT = aiohttp.ClientTimeout(total=10)


class TeslaGatewayAuthError(Exception):
    """Raised when login fails (wrong credentials)."""


class TeslaGatewayConnectionError(Exception):
    """Raised when the Gateway cannot be reached."""


class TeslaGatewayApiClient:
    """Client for the Tesla Gateway 2 local API (https://<gateway-ip>/api/...)."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        email: str,
        password: str,
    ) -> None:
        self._session = session
        self._host = host
        self._email = email
        self._password = password
        self._base_url = f"https://{host}/api"
        self._logged_in = False

    async def async_login(self) -> None:
        """Authenticate against the Gateway and store the session cookie."""
        try:
            async with self._session.post(
                f"{self._base_url}/login/Basic",
                json={
                    "username": "customer",
                    "email": self._email,
                    "password": self._password,
                    "force_sm_off": False,
                },
                ssl=False,
                timeout=TIMEOUT,
            ) as resp:
                if resp.status == 401:
                    raise TeslaGatewayAuthError("Falscher Benutzername/Passwort am Gateway.")
                resp.raise_for_status()
                await resp.json()
        except aiohttp.ClientError as err:
            raise TeslaGatewayConnectionError(str(err)) from err
        self._logged_in = True

    async def async_get(self, path: str) -> Any:
        """GET a JSON endpoint, logging in first / again as needed."""
        if not self._logged_in:
            await self.async_login()

        for attempt in range(2):
            try:
                async with self._session.get(
                    f"{self._base_url}{path}", ssl=False, timeout=TIMEOUT
                ) as resp:
                    if resp.status in (401, 403) and attempt == 0:
                        _LOGGER.debug("Session abgelaufen, logge erneut ein (%s)", path)
                        await self.async_login()
                        continue
                    resp.raise_for_status()
                    return await resp.json()
            except aiohttp.ClientError as err:
                raise TeslaGatewayConnectionError(str(err)) from err
        raise TeslaGatewayAuthError(f"Zugriff auf {path} nach erneutem Login weiter verweigert.")

    async def async_get_status(self) -> dict[str, Any]:
        """Gather every endpoint needed for a battery-health snapshot."""
        soe = await self.async_get("/system_status/soe")
        system_status = await self.async_get("/system_status")
        aggregates = await self.async_get("/meters/aggregates")
        operation = await self.async_get("/operation")
        grid_status = await self.async_get("/system_status/grid_status")
        grid_faults = await self.async_get("/system_status/grid_faults")

        battery_block = (system_status.get("battery_blocks") or [{}])[0]

        return {
            "soe_percent": soe.get("percentage"),
            "nominal_full_pack_energy": system_status.get("nominal_full_pack_energy"),
            "nominal_energy_remaining": system_status.get("nominal_energy_remaining"),
            "battery_power": aggregates.get("battery", {}).get("instant_power"),
            "site_power": aggregates.get("site", {}).get("instant_power"),
            "load_power": aggregates.get("load", {}).get("instant_power"),
            "solar_power": aggregates.get("solar", {}).get("instant_power"),
            "backup_reserve_percent": operation.get("backup_reserve_percent"),
            "operating_mode": operation.get("real_mode"),
            "grid_status": grid_status.get("grid_status"),
            "grid_services_active": grid_status.get("grid_services_active"),
            "grid_faults": grid_faults or [],
            "pack_voltage": battery_block.get("v_out"),
            "pack_frequency": battery_block.get("f_out"),
            "pack_current": battery_block.get("i_out"),
            "energy_charged_wh": battery_block.get("energy_charged"),
            "energy_discharged_wh": battery_block.get("energy_discharged"),
            "disabled_reasons": battery_block.get("disabled_reasons") or [],
            "part_number": battery_block.get("PackagePartNumber"),
            "serial_number": battery_block.get("PackageSerialNumber"),
        }
