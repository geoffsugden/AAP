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

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Step 1: Ask for host, port and sensor / button data."""

        if user_input is not None:
            # Store host/port and nymber of sensors in _flow_data
            self._flow_data["host"] = user_input["host"]
            self._flow_data["port"] = user_input["port"]

            # High level sensor data
            self._flow_data["num_sensors"] = int(user_input["num_sensors"])
            self._flow_data["sensor_data"] = []

            # High level button data
            self._flow_data["num_buttons"] = int(user_input.get("num_buttons", 0))
            self._flow_data["button_data"] = []

            self._flow_data["current_sensor_index"] = 0
            self._flow_data["current_button_index"] = 0

            # Go to next step to ask for each sensor name if we have more than 0 sensors
            if self._flow_data["num_sensors"] > 0:
                return await self.async_step_sensor_data()
            if self._flow_data["num_buttons"] > 0:
                return await self.async_step_button_data()

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
                    vol.Required("num_buttons", default=0): selector.NumberSelector(
                        config={"min":  0, "max": 4, "mode": "box"}
                    ),
                }
            ),
        )

    async def async_step_sensor_data(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Step 2. Ask for each sensor name and zone number."""

        index = self._flow_data.get("current_sensor_index", 0)
        num_sensors = self._flow_data["num_sensors"]

        # Check if we have any sensors
        if user_input is not None:
            self._flow_data.setdefault("sensor_data", [])
            self._flow_data["sensor_data"].append({
                "name": str(user_input["name"]).strip(),
                "zone": int(user_input["zone"])
            })
            index += 1
            self._flow_data["current_sensor_index"] = index

        if index >= num_sensors:
            if self._flow_data["num_buttons"] > 0:
                return await self.async_step_button_data()
            # Skip sensor name collection and create entry immediately
            data = {
                "host": self._flow_data["host"],
                "port": self._flow_data["port"],
                "sensors": self._flow_data["sensor_data"],
                "buttons": self._flow_data.get("button_data", [])
            }
            return self.async_create_entry(
                title=f"AAP Alarm @ {data['host']}:{data['port']}", data=data
            )

        existing_zones = {int(s["zone"]) for s in self._flow_data.get("sensor_data", [])}

        suggested_zone = 1
        while suggested_zone in existing_zones:
            suggested_zone += 1

        suggested_zone = max(1,min(32,suggested_zone))

        # Ask for the next sensor name
        return self.async_show_form(
            step_id="sensor_data",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=f"Sensor {index + 1}"): str,
                    vol.Required("zone", default=(index + 1)): int,
                }
            ),
            description_placeholders={"current": f"{index + 1}", "total": num_sensors},
        )

    async def async_step_button_data(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Step 3. Ask for each button name and control number."""

        index = self._flow_data.get("current_button_index", 0)
        num_buttons = self._flow_data["num_buttons"]

        if user_input is not None:
            self._flow_data.setdefault("button_data", [])
            self._flow_data["button_data"].append({
                "name": user_input["name"],
                "output": user_input["output"]
            })
            index += 1
            self._flow_data["current_button_index"] = index

        if index >= num_buttons:
            #All buttons done, create the final entry
            data = {
                "host": self._flow_data["host"],
                "port": self._flow_data["port"],
                "sensors": self._flow_data.get("sensor_data", []),
                "buttons": self._flow_data.get("button_data", []),
            }
            return self.async_create_entry(
                title=f"AAP Alarm @ {data['host']}:{data['port']}",
                data=data
            )

        # Ask for next button
        return self.async_show_form(
            step_id="button_data",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=f"Button {index + 1}"): str,
                    vol.Required("output", default=index + 1): selector.NumberSelector(
                        config={"min": 1, "max": 4}
                    ),
                }
            ),
        )
