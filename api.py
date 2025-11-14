"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from dataclasses import dataclass
from enum import StrEnum
import logging

# import credentials
from random import choice, randrange

_LOGGER = logging.getLogger(__name__)


class DeviceType(StrEnum):
    """Device Types."""

    BINARY_SENSOR = "binary_sensor"
    OTHER = "other"


DEVICES = [
    {"id": 1, type: DeviceType.BINARY_SENSOR},
    {"id": 2, type: DeviceType.BINARY_SENSOR},
    {"id": 3, type: DeviceType.BINARY_SENSOR},
]


@dataclass
class Device:
    """API Device."""

    device_id: int
    device_unique_id: str
    device_type: DeviceType
    name: str
    state: int | bool


class API:
    """Class for example API."""

    def __init__(self, host: str, port: str) -> None:  # noqa: D107
        self.host = host
        self.port = port
        self.connected: bool = False

    @property
    def controller_name(self) -> str:
        """Return the name of the controller."""
        return self.host.replace(".", "_")

    def connect(self) -> bool:
        """Connect to api."""
        self.connected = True
        return True

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True

    def get_device_unique_id(self, device_id: str, device_type: DeviceType) -> str:
        """Return a unique device id."""
        return f"{self.controller_name}_Z{device_id}"

    def get_device_name(self, device_id: str, device_type: DeviceType) -> str:
        """Return the device name."""
        return f"BinarySensor{device_id}"

    def get_device_value(self, device_id: str, device_type: DeviceType) -> int | bool:
        """Get device random value."""
        return choice([True, False])


class APIAuthError(Exception):
    """Exception class for auth error."""


class APIConnectionError(Exception):
    """Exception class for connection error."""
