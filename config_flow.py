"""Defines config flow for setup of AAP alarm integration."""

import voluptuous as vol

from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import DOMAIN
from .credentials import host, port


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate that the user input allows us to connect."""
    return {"title": f"AAP Integration - {data['host']}"}


class AAPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """AAP Config Flow."""

    VERSION = 1

    def __init__(self):
        """Initialize temporary flow data storage."""
        self._flow_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Ask for host, port and number of sensors."""
        if user_input is not None:
            # Store host/port and nymber of sensors in _flow_data
            self._flow_data["host"] = user_input["host"]
            self._flow_data["port"] = user_input["port"]
            self._flow_data["num_sensors"] = int(user_input["num_sensors"])
            self._flow_data["sensor_names"] = []

            # Go to next step to ask for each sensor name
            return await self.async_step_sensor_names()

        # Step 1 form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host", default=host): str,
                    vol.Required("port", default=port): int,
                    vol.Required("num_sensors", default=7): selector.NumberSelector(
                        config={"min": 0, "max": 32, "mode": "box"}
                    ),
                    # vol.Required("num_sensors", default=7): vol.All(
                    #     vol.Coerce(int), vol.Range(min=1, max=32)
                    # ),
                }
            ),
        )

    async def async_step_sensor_names(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: ask for each sensor name."""

        index = self._flow_data.get("current_index", 0)
        num_sensors = self._flow_data["num_sensors"]

        if user_input is not None:
            self._flow_data["sensor_names"].append(user_input["name"])
            index += 1
            self._flow_data["current_index"] = index

        if index >= num_sensors:
            # Skip sensor name collection and create entry immediately
            data = {
                "host": self._flow_data["host"],
                "port": self._flow_data["port"],
                "sensors": self._flow_data["sensor_names"],
            }
            return self.async_create_entry(
                title=f"AAP Alarm @ {data['host']}:{data['port']}", data=data
            )

        # Ask for the next sensor name
        return self.async_show_form(
            step_id="sensor_names",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=f"Sensor {index + 1}"): str,
                }
            ),
            description_placeholders={"current": f"{index + 1}", "total": num_sensors},
        )
