"""AAP Buttons for controlling outputs."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AAPCoordinator
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up buttons for the AAP integration."""

    coordinator: AAPCoordinator = entry.runtime_data

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Create one button per configured button in config flow
    buttons = [
        AAPButton(coordinator, button["name"], button["output"])
        for button in entry.data.get("buttons", [])
    ]
    async_add_entities(buttons)


class AAPButton(CoordinatorEntity, ButtonEntity):
    """Representation of a single AAP output button."""

    def __init__(self, coordinator: AAPCoordinator, name: str, output: int):
        super().__init__(coordinator)
        self._attr_name = name
        self.output = output
        self._attr_unique_id = f"aap_button_{output}"

    async def async_press(self) -> None:
        """Send OUTPUTON command to the alarm panel."""
        # You can implement actual sending via the coordinator here
        if hasattr(self.coordinator, "async_send_command"):
            await self.coordinator.async_send_command(f"OUTPUTON {self.output}")  # type: ignore
        else:
            # fallback: just log
            _LOGGER.info(f"Would send: OUTPUTON {self.output}")
