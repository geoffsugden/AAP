"""Bare bones coordinator."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AAPCoordinator(DataUpdateCoordinator):
    """Minimal coordinator for AAP."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=None,  # no auto-updates yet
        )

        self.hass = hass
        self.entry = entry
        self.host = entry.data["host"]
        self.port = entry.data["port"]

        self.data: dict[int, bool] = {}  # zone_id -> True / False

        # Start TCP Listener Class
        self._tcp_task = None

    async def async_start(self):
        """Start TCP listener after HA has loaded entities."""
        if self._tcp_task is None:
            self._tcp_task = asyncio.create_task(self._tcp_listener())

    async def _async_update_data(self):
        """Return current data (push-based, so nothing to fetch)."""
        return self.data

    async def _tcp_listener(self):
        """Connect to the alarm system and read push messages."""
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            _LOGGER.info("Connected to AAP alarm at %s:%s", self.host, self.port)

            while True:
                data = await reader.read(512)
                if not data:
                    _LOGGER.warning("TCP Connection Closed")
                    break

                line = data.decode("utf-8").strip()
                await self._handle_tcp_message(line)

        except asyncio.CancelledError:
            _LOGGER.info("AAP TCP Listener Cancelled")
        except Exception as e:
            _LOGGER.error("Error in TCP Listener: %s", e)

    async def _handle_tcp_message(self, message: str):
        """Parse zone messages and update data."""
        if message.startswith("ZO"):
            zone = int(message[2:])
            state = True
        elif message.startswith("ZC"):
            zone = int(message[2:])
            state = False
        else:
            _LOGGER.debug("Unknown message: %s", message)
            return

        new_state = dict(self.data)
        new_state[zone] = state

        self.data = new_state
        self.async_update_listeners()

    async def async_request_status(self):
        """Send Status request to alarm system (future implementation)."""
        pass

    async def async_stop(self):
        """Cancel TCP Listener task."""
        if self._tcp_task:
            self._tcp_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._tcp_task
