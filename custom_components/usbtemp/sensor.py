"""Platform for sensor integration."""
from __future__ import annotations

# stdlib
from pathlib import Path
import re
import termios
from time import time

# 3rd party
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# project imports
from . import usbtemp


KNOWN_DEVICES = (
    ('067b', '23a3'),
    )


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities(find_devices())


def find_devices():
    # Look up devices by idVendor and idProduct using sysfs
    def _is_usb(path):
        return any(re.match(r'usb\d+', x) for x in path.parts)

    devices = Path('/sys/devices').glob('**/idVendor')
    devices = [dev.parent for dev in devices if _is_usb(dev)]

    uids = set()
    for vendor, product in KNOWN_DEVICES:
        for dev in devices:
            if vendor != (dev / 'idVendor').read_text().strip():
                continue
            if product != (dev / 'idProduct').read_text().strip():
                continue
            # get the serial number
            serial = dev / 'serial'
            assert serial.exists()  # no serial number present for this device
            serial = serial.read_text().strip()
            assert serial           # blank serial number on this device
            # we only need the serial number.
            uids.add(serial)

    # Look up a link to the specific ttyusbXX file
    uid_path_map = {}
    for path in Path("/dev/serial/by-id").glob('*'):
        for uid in uids:
            if uid in path.name:
                uid_path_map[uid] = path
    return [USBTempSensor(dev, uid) for uid, dev in uid_path_map.items()]


class USBTempSensor(SensorEntity):
    def __init__(self, device, uid, **kwargs):
        self._attr_name = "USBTemp Thermometer"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = uid

        self.linux_device = device
        self.read_interval = 15
        self._usbtemp_next_read = 0
        self._usbtemp_thermometer = usbtemp.Thermometer(str(device))
        self._usbtemp_thermometer.Open()

        super().__init__(**kwargs)

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        if time() > self._usbtemp_next_read:
            thermometer = self._usbtemp_thermometer
            try:
                if not thermometer.uart:
                    thermometer.Open()
                self._attr_native_value = round(float(self._usbtemp_thermometer.Temperature()), 1)
                self._usbtemp_next_read = time() + self.read_interval
            except (IOError, termios.error):
                self._usbtemp_thermometer.Close()
