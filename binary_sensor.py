"""AAP Binary Sensors for PIR and Reed devices."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AAPCoordinator
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):

    coordinator: AAPCoordinator = entry.runtime_data

    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    sensors_cfg: list[dict] = entry.data.get("sensors", [])

    entities = []
    for sensors in sensors_cfg:
        name = str(sensors["name"])
        zone = int(sensors["zone"])
        entities.append(AAPBinarySensor(coordinator, name, zone))

    async_add_entities(entities)


class AAPBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor representing a PIR or Reed zone."""

    def __init__(self, coordinator: AAPCoordinator, name: str, zone: int) -> None:
        super().__init__(coordinator)
        self.zone = zone
        self._attr_name = name

        self._attr_unique_id = f"aap_sensor_{zone}"

    @property
    def is_on(self) -> bool:
        """Return whether this zone is active."""
        # Default to False if not yet seen
        return self.coordinator.data.get(self.zone, False) # type: ignore

    @property
    def available(self) -> bool:
        """Sensors are availble once coordinator has any data."""
        return True
