# Lumina Observer

Real-time aurora prediction for Australian & New Zealand aurora hunters, directly in Home Assistant.

## Features

- 🔭 **14 sensors**: solar wind, IMF, aurora probabilities, sky quality, magnetotail energy & more
- 🚗 **Worth driving** binary sensor with go/no-go recommendation
- ⚡ **Real-time streaming** via WebSocket — no polling
- 🔄 **Automatic reconnection** with exponential backoff

## Setup

1. Install via HACS
2. Add the integration in **Settings → Devices & Services**
3. Enter your latitude, longitude, and API key (starts with `lumina_`)

Get your API key at [lumina.observer](https://lumina.observer).

## Example Automations

```yaml
automation:
  - alias: "Aurora drive alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.lumina_observer_worth_driving
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "🚗 Aurora Alert!"
          message: "Probability: {{ states('sensor.lumina_observer_aurora_probability_plan') }}%"
```
