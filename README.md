# everHome EcoTracker — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HACS Action](https://github.com/Tenosiey/everHome-Integration/actions/workflows/hacs.yml/badge.svg)](https://github.com/Tenosiey/everHome-Integration/actions/workflows/hacs.yml)

A custom [Home Assistant](https://www.home-assistant.io/) integration that reads
live power and energy values from an [everHome EcoTracker](https://everhome.de/)
IR meter via its **local REST API** — no cloud account and no internet
connection required.

## Features

- 🔌 100 % local polling (`local_polling`) — values are read directly from the
  device on your network.
- ⚡ Live power readings (total, 1-minute average and per phase).
- 📈 Energy import/export counters, ready for the Home Assistant **Energy
  Dashboard**.
- 🧭 Guided onboarding — just enter the device IP, the rest is automatic.
- 🌍 English and German translations.
- ⚙️ Configurable update interval.

## Provided sensors

| Sensor | API field | Unit | Notes |
| --- | --- | --- | --- |
| Power | `power` | W | Negative = feed-in, positive = consumption |
| Power (1 min average) | `powerAvg` | W | Average of `power` over the last minute |
| Power phase 1–3 | `powerPhase1` … `powerPhase3` | W | Only if the meter reports per-phase data |
| Energy import | `energyCounterIn` | Wh | Total energy drawn from the grid |
| Energy import (tariff 1) | `energyCounterInT1` | Wh | High tariff, only if reported |
| Energy import (tariff 2) | `energyCounterInT2` | Wh | Low tariff, only if reported |
| Energy export | `energyCounterOut` | Wh | Total energy fed into the grid |

> Optional sensors (per-phase power and the tariff counters) are created only
> when the device actually reports those values.

## Prerequisites

1. The EcoTracker and your Home Assistant instance must be on the **same local
   network**.
2. Enable the **Local HTTP server** in the everHome app
   (*Settings → EcoTracker*). It is enabled by default.
3. Note the device's IP address (visible in the everHome app or your router).

You can verify the API works from any computer on the network:

```bash
curl http://<EcoTrackerIP>/v1/json
```

## Installation

### Via HACS (recommended)

1. In Home Assistant, go to **HACS → Integrations**.
2. Open the three-dot menu → **Custom repositories**.
3. Add `https://github.com/Tenosiey/everHome-Integration` with category
   **Integration**.
4. Search for **everHome EcoTracker**, install it, and restart Home Assistant.

[![Open your Home Assistant instance and open a repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Tenosiey&repository=everHome-Integration&category=integration)

### Manual

1. Copy the `custom_components/everhome_ecotracker` folder into your Home
   Assistant `config/custom_components` directory.
2. Restart Home Assistant.

## Onboarding / Setup

After installation, add the integration:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **everHome EcoTracker**.
3. Enter the **IP address** of your EcoTracker (for example `192.168.1.50`).
4. The integration verifies that the device is reachable and then creates one
   device with all available sensors.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=everhome_ecotracker)

If the connection fails, double-check the IP address and that the *Local HTTP
server* option is enabled in the everHome app.

### Changing the update interval

Go to **Settings → Devices & Services → everHome EcoTracker → Configure** to
change how often the device is polled (default: every 10 seconds).

## Energy Dashboard

The `Energy import` and `Energy export` sensors use the `total_increasing`
state class and can be added directly to the Home Assistant **Energy
Dashboard**:

- *Grid consumption* → **Energy import**
- *Return to grid* → **Energy export**

## The local REST API

The EcoTracker exposes a single JSON endpoint:

```http
GET http://<EcoTrackerIP>/v1/json
```

```json
{
  "power": 125,
  "powerAvg": 100,
  "powerPhase1": 50,
  "powerPhase2": 50,
  "powerPhase3": 25,
  "energyCounterIn": 145000,
  "energyCounterInT1": 100000,
  "energyCounterInT2": 45000,
  "energyCounterOut": 4500
}
```

| Field | Meaning |
| --- | --- |
| `power` | Current power in W (negative = feed-in, positive = consumption) |
| `powerAvg` | Average `power` in W over the last minute |
| `powerPhase1`–`3` | Current power in W per phase (not provided by every meter) |
| `energyCounterIn` | Grid import meter reading in Wh |
| `energyCounterInT1` | High-tariff import reading (not always present) |
| `energyCounterInT2` | Low-tariff import reading (not always present) |
| `energyCounterOut` | Grid export (feed-in) meter reading in Wh |

## Troubleshooting

- **"Could not reach the EcoTracker"** — confirm the IP, that both devices share
  the network, and that the *Local HTTP server* is enabled.
- **Sensors show *unavailable*** — the device became unreachable; the
  integration retries automatically on the next update.
- Enable debug logging by adding the following to `configuration.yaml`:

  ```yaml
  logger:
    logs:
      custom_components.everhome_ecotracker: debug
  ```

## Contributing

Issues and pull requests are welcome. This is an unofficial, community-built
integration and is not affiliated with everHome.

## License

Released under the [MIT License](LICENSE).
