# Lumina Observer for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Real-time aurora metrics & prediction data from [lumina.observer](https://lumina.observer) in Home Assistant. Built for Australian and New Zealand aurora hunters.

## Features

- **Real-time streaming** via WebSocket — no polling, data arrives the moment it's available
- **14 sensors** covering solar wind, IMF, hemispheric power, aurora probabilities, sky quality, magnetotail energy, and more
- **Worth driving** binary sensor — a go/no-go recommendation for aurora chasing
- **Automatic reconnection** with exponential backoff (1s → 2s → 4s → max 30s)
- **Heartbeat monitoring** — forces reconnect if connection goes stale

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.lumina_observer_score` | Sensor | Lumina's space weather score (0–100) |
| `sensor.lumina_observer_aurora_probability_field` | Sensor | Field mode (short-horizon) aurora probability (0–100%) |
| `sensor.lumina_observer_aurora_probability_plan` | Sensor | Plan mode (drive-horizon) aurora probability (0–100%) |
| `sensor.lumina_observer_solar_wind_speed` | Sensor | Solar wind speed (km/s) |
| `sensor.lumina_observer_solar_wind_density` | Sensor | Solar wind density (p/cm³) |
| `sensor.lumina_observer_imf_bz` | Sensor | IMF Bz component (nT) |
| `sensor.lumina_observer_imf_bt` | Sensor | IMF Bt total field (nT) |
| `sensor.lumina_observer_hemispheric_power` | Sensor | Hemispheric power (GW) |
| `sensor.lumina_observer_sky_quality` | Sensor | Sky quality meter (mag/arcsec²) |
| `sensor.lumina_observer_data_confidence` | Sensor | Data quality: Stable / Volatile / Uncertain |
| `sensor.lumina_observer_magnetotail_state` | Sensor | Substorm energy loading state |
| `sensor.lumina_observer_magnetotail_energy_ratio` | Sensor | Magnetotail energy ratio |
| `sensor.lumina_observer_incoming_cmes` | Sensor | Count of active Earth-directed CMEs |
| `binary_sensor.lumina_observer_worth_driving` | Binary | Go/no-go drive recommendation |

## Installation

### HACS (recommended)

1. Open HACS → Integrations → ⋮ → **Custom repositories**
2. Paste `https://github.com/gregdev/lumina-home-assistant` and select **Integration**
3. Click **Add**, then find **Lumina Observer** and click **Download**
4. Restart Home Assistant

### Manual

Copy the `custom_components/lumina_observer/` folder into your Home Assistant `custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration → Lumina Observer**
2. Enter your:
   - **Latitude** (e.g. `-35.0` for Canberra)
   - **Longitude** (e.g. `149.0`)
   - **API Key** (starts with `lumina_`)

## Automations

```yaml
# Notify when it's worth driving
automation:
  - alias: "Aurora drive alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.lumina_observer_worth_driving
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Aurora Alert!"
          message: >-
            Aurora probability is {{ states('sensor.lumina_observer_aurora_probability_field') }}%.
            Score: {{ states('sensor.lumina_observer_score') }}.
```

```yaml
# Dashboard gauge for space weather score
type: gauge
entity: sensor.lumina_observer_score
min: 0
max: 100
severity:
  green: 0
  yellow: 40
  red: 70
```

## Requirements

- Home Assistant 2024.1.0+
- A [Lumina Observer](https://lumina.observer) API key
