import logging
import uuid

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify
from . import AlertsDataUpdateCoordinator

from .const import (
    ATTRIBUTION,
    CONF_API_KEY,
    CONF_TEAM_ID,
    COORDINATOR,
    DEFAULT_ICON,
    DEFAULT_API_KEY,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TEAM_ID): cv.positive_int,
        vol.Required(CONF_API_KEY, default=DEFAULT_API_KEY): str,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configuration from yaml"""
    if DOMAIN not in hass.data.keys():
        hass.data.setdefault(DOMAIN, {})
        config.entry_id = slugify(f"{config.get(CONF_TEAM_ID)}")
        config.data = config
    else:
        config.entry_id = slugify(f"{config.get(CONF_TEAM_ID)}")
        config.data = config

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        config,
        config[CONF_API_KEY],
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][config.entry_id] = {
        COORDINATOR: coordinator,
    }
    async_add_entities([PALLONEsensorSensor(hass, config)], True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the sensor platform."""
    async_add_entities([PALLONEsensorSensor(hass, entry)], True)


class PALLONEsensorSensor(CoordinatorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass.data[DOMAIN][entry.entry_id][COORDINATOR])
        self._config = entry
        self._name = entry.data[CONF_NAME]
        self._icon = DEFAULT_ICON
        self.referee = None
        self.home_team_name = None
        self.away_team_name = None
        self.match_day = None
        self.venue = None
        self.league = None
        self.venue_location = None
        self._last_update = None
        self._team_id = entry.data[CONF_TEAM_ID]
        self.coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    @property
    def unique_id(self):
        """
        Return a unique, Home Assistant friendly identifier for this entity.
        """
        return f"{slugify(self._name)}_{self._config.entry_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        elif "state" in self.coordinator.data.keys():
            return self.coordinator.data["state"]
        else:
            return None

    @property
    def device_state_attributes(self):
        """Return the state message."""
        attrs = {}

        if self.coordinator.data is None:
            return attrs

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        attrs["home_team_name"] = self.coordinator.data["home_team_name"]
        attrs["home_team_logo"] = self.coordinator.data["home_team_logo"]
        attrs["away_team_name"] = self.coordinator.data["away_team_name"]
        attrs["away_team_logo"] = self.coordinator.data["away_team_logo"]
        attrs["match_day"] = self.coordinator.data["match_day"]
        attrs["referee"] = self.coordinator.data["referee"]
        attrs["venue"] = self.coordinator.data["venue"]
        attrs["venue_location"] = self.coordinator.data["venue_location"]
        attrs["league"] = self.coordinator.data["league"]
        attrs["league_round"] = self.coordinator.data["league_round"]
        attrs["league_logo"] = self.coordinator.data["league_logo"]       
        attrs["team_id"] = self.coordinator.data["team_id"]
        attrs["today_match"] = self.coordinator.data["today_match"]
        attrs["last_update"] = self.coordinator.data["last_update"]
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
