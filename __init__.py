"""AAP Integration entry point."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .coordinator import AAPCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up your integration from a config entry."""

    coordinator = AAPCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload AAP config entry."""
    coordinator: AAPCoordinator = entry.runtime_data

    # Cancel TCP listener
    await coordinator.async_stop()

    # Unload platforms
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
