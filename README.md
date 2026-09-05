# Tesla Powerwall Health for Home Assistant (HACS)

[![Validate](https://github.com/kayloehmann/tesla-powerwall-health/actions/workflows/validate.yml/badge.svg)](https://github.com/kayloehmann/tesla-powerwall-health/actions/workflows/validate.yml)

A HACS-installable custom integration that monitors **Tesla Powerwall battery
health** through the Tesla Gateway 2's local API — no cloud account, no
internet dependency, pure LAN polling.

## Why not the built-in Powerwall integration?

Home Assistant's built-in `powerwall` integration covers the same local API
but focuses on live energy dashboards. This integration is scoped narrowly
to **health monitoring**: capacity degradation over time, equivalent full
cycles, backup reserve, and fault flags — the metrics you actually want in
long-running history graphs to catch battery aging early.

## What it gives you

| Entity | What it tells you |
| --- | --- |
| State of charge | Current battery level (%) |
| Usable capacity | Current `nominal_full_pack_energy` (kWh) |
| Capacity (% of nameplate) | **The core health metric** — current usable capacity vs. the pack's nameplate rating when new. Track this over months/years to spot abnormal degradation. |
| Equivalent full cycles | Lifetime energy discharged ÷ current capacity — how hard the battery has been used relative to its age. |
| Backup reserve | Configured backup reserve (%) |
| Battery / Site / Load / Solar power | Live power flows (W) |
| Voltage / Frequency / Current | Per-pack electrical readings (disabled by default — enable if you want them) |
| Charged / Discharged (lifetime) | Cumulative energy throughput (kWh) |
| Operating mode / Grid status | e.g. `self_consumption`, `SystemGridConnected` |
| Fault | Binary sensor, on when the Gateway reports an active grid fault or a disabled reason on the battery pack |
| Grid connection | Binary sensor for grid-connected vs. islanded |

## Requirements

- A Tesla Gateway 2 (Powerwall) reachable on your LAN.
- The **local** customer login (email + password) set up in the Tesla app
  during installation — not your tesla.com account password. This is
  typically a short alphanumeric code found on the Gateway door sticker.

## Installation

### HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories → add
   `https://github.com/kayloehmann/tesla-powerwall-health` as type
   "Integration".
2. Install "Tesla Powerwall Health", restart Home Assistant.
3. Settings → Devices & Services → Add Integration → "Tesla Powerwall
   Health".

### Manual

Copy `custom_components/tesla_powerwall_health` into your Home Assistant
`custom_components` folder and restart.

## Configuration

The config flow asks for:

- **Host** — the Gateway's IP address (e.g. `10.111.0.79`)
- **Email** / **Password** — the local Gateway login
- **Nameplate capacity (Wh)** — usable capacity when new, used to compute
  the degradation percentage (Powerwall 2: `13500`)

Polling interval is fixed at 60 seconds — this is `local_polling` against a
LAN device, no cloud rate limits apply, but the interval is kept
conservative since the Gateway's web UI shares the same backend.

## Notes

- Uses the Gateway's self-signed HTTPS certificate (`verify_ssl=False`) —
  this is expected and safe on a LAN-only connection to a device you own.
- Session cookies expire after a few hours; the integration re-authenticates
  transparently on 401/403.
- Only one battery block/pack is read out per Gateway in this version
  (single-Powerwall installations). Multi-Powerwall support (summed/averaged
  across `battery_blocks[]`) is a possible future addition — PRs welcome.

## License

MIT
