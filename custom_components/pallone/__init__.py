""" PALLONE Team Status """
from .const import (
    API_ENDPOINT_SOCCER,
    CONF_API_KEY,
    CONF_TEAM_ID,
    COORDINATOR,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    USER_AGENT,
    VERSION,
)
import logging
from datetime import timedelta, datetime
from xmlrpc.client import boolean
import arrow

import aiohttp
from dateutil.parser import parse
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

TIME_INTERVAL = 60


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the saved entities."""
    # Print startup message
    _LOGGER.info(
        "PALLONE version %s is starting, if you have any issues please report them here: %s",
        VERSION,
        ISSUE_URL,
    )
    hass.data.setdefault(DOMAIN, {})

    if entry.unique_id is not None:
        hass.config_entries.async_update_entry(entry, unique_id=None)

        ent_reg = async_get(hass)
        for entity in async_entries_for_config_entry(ent_reg, entry.entry_id):
            ent_reg.async_update_entity(
                entity.entity_id, new_unique_id=entry.entry_id)

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        entry.data,
        TIME_INTERVAL
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the " +
                     DOMAIN + " integration")
    except ValueError:
        pass
    return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))


class AlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching PALLONE data."""

    def __init__(self, hass, config, the_timeout: int):
        """Initialize."""
        self.interval = timedelta(minutes=TIME_INTERVAL)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config
        self.hass = hass

        _LOGGER.debug("Data will be updated every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Fetch data"""
        async with timeout(self.timeout):
            try:
                data = await update_game(self.config)
                self.update_interval = timedelta(minutes=TIME_INTERVAL)
            except Exception as error:
                raise UpdateFailed(error) from error
            return data


async def update_game(config) -> dict:
    """Fetch new state data for the sensor.
    This is the only method that should fetch new data for Home Assistant.
    """

    data = await async_get_state(config)
    return data


def generateMatch(matchFound, isTodayMatch, teamId):
    values = {}
    values["home_team_name"] = matchFound['teams']['home']['name']
    values["home_team_logo"] = matchFound['teams']['home']['logo']
    values["away_team_name"] = matchFound['teams']['away']['name']
    values["away_team_logo"] = matchFound['teams']['away']['logo']
    values["match_day"] = matchFound['fixture']['date']
    values["referee"] = matchFound["fixture"]["referee"]
    values["venue"] = matchFound['fixture']['venue']['name']
    values["venue_location"] = matchFound['fixture']['venue']['city']
    values["league"] = matchFound['league']['name']
    values["league_round"] = matchFound['league']['round']
    values["league_logo"] = matchFound['league']['logo']
    values["team_id"] = teamId
    values["today_match"] = isTodayMatch
    values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
    values["state"] = values["match_day"] or 'off'

    return values


async def async_get_state(config) -> dict:
    """Query API for status."""
    api_key = config[CONF_API_KEY]

    headers = {"User-Agent": USER_AGENT,
               "Accept": "application/ld+json", "X-apisports-Key": api_key}
    data = None
    url = API_ENDPOINT_SOCCER
    team_id = config[CONF_TEAM_ID]
    async with aiohttp.ClientSession() as session:
        async with session.get(url.format(team=team_id, season=2021), headers=headers) as r:
            _LOGGER.debug("Getting state for %s from %s" % (team_id, url))
            if r.status == 200:
                data = await r.json()

    if data is not None:
        today = datetime.now().date()
        todayMatch = next(filter(lambda match: parse(
            match['fixture']['date']).date() == today, data['response']), None)
        if todayMatch is not None:
            return generateMatch(todayMatch, True, team_id)
        else:
            sortedResult = sorted(
                data["response"], key=lambda x: x['fixture']['timestamp'])
            nextMatch = next(filter(
                lambda match: (match['fixture']['status']['short'] == "NS" or match['fixture']['status']['short'] == "TBD"), sortedResult), None)
            return generateMatch(nextMatch, False, team_id)
