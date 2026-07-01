"""Constants for the Lumina Observer integration."""

DOMAIN = "lumina_observer"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

WS_URL = "wss://lumina.observer/api/v1/stream"

# WebSocket reconnection
INITIAL_BACKOFF = 1  # seconds
MAX_BACKOFF = 30  # seconds
BACKOFF_MULTIPLIER = 2

# Heartbeat interval (server sends every 30s, we allow 60s before considering stale)
HEARTBEAT_TIMEOUT = 60

ATTR_SOLAR_WIND_SPEED = "solar_wind_speed"
ATTR_SOLAR_WIND_DENSITY = "solar_wind_density"
ATTR_IMF_BZ = "imf_bz"
ATTR_IMF_BT = "imf_bt"
ATTR_HEMISPHERIC_POWER = "hemispheric_power"
ATTR_SCORE = "score"
ATTR_AURORA_PROB_FIELD = "aurora_probability_field"
ATTR_AURORA_PROB_PLAN = "aurora_probability_plan"
ATTR_CONFIDENCE = "confidence"
ATTR_INTENSITY_COLOUR = "intensity_colour"
ATTR_WORTH_DRIVING = "worth_driving"
ATTR_MAGNETOTAIL_ENERGY_RATIO = "magnetotail_energy_ratio"
ATTR_MAGNETOTAIL_ENERGY_STATE = "magnetotail_energy_state"
ATTR_UPCOMING_CME_COUNT = "upcoming_cme_count"
ATTR_SQM = "sqm"
ATTR_LAST_UPDATE = "last_update"
