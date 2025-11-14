"""Initialize the AAP integration"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ConfigEntryNotReady

from .api import API, APIConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AAP from a config entry."""
    api = API(entry.data["host"], entry.data["port"])
    try:
        await hass.async_add_executor_job(api.connect)
    except APIConnectionError as err:
        raise ConfigEntryNotReady from err

    # Store the API instance for later use
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload AAP config entry."""
    api: API = hass.data[DOMAIN].pop(entry.entry_id)
    await hass.async_add_executor_job(api.disconnect)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
