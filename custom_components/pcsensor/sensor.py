"""Platform for sensor integration."""
from __future__ import annotations

from time import time

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import temper


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    TEMPerInterface.init_temper()
    add_entities(TEMPerInterface.get_sensors())


class TEMPerInterface():
    """Interface for TEMPer devices

    Limits polling rate, and generates the relevant sensors from
    the readings provided by temper-py's `temper` module.
    """
    _latest_values = None
    _next_read = 0
    _interval = 15
    _temper = None
    _sensors = {}
    
    def __init__(self):
        self.init_temper()

    @classmethod
    def init_temper(cls):
        if cls._temper is None:
            cls._temper = temper.Temper()

    @classmethod
    def read(cls):
        if time() < cls._next_read:
            return cls._latest_values
        cls._latest_values = cls._temper.read()
        cls._next_read = time() + cls._interval
        return cls._latest_values

    @classmethod
    def get_sensors(cls):
        sensor_types = [
            "internal temperature",
            "external temperature",
            "internal humidity",
            "external humidity"
            ]

        for sensor_data in cls.read():
            uid_base = f"{sensor_data['firmware']}-{sensor_data['busnum']}-{sensor_data['devnum']}-"
            uids = [uid_base + s for s in sensor_types if s in sensor_data]
            for uid in uids:
                if uid.endswith('temperature'):
                    cls._sensors[uid] = TEMPerTemperatureSensor(uid)
                elif uid.endswith('humidity'):
                    cls._sensors[uid] = TEMPerHumiditySensor(uid)
        return list(cls._sensors.values())


class TEMPerSensor(SensorEntity):
    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        sensor_data = TEMPerInterface.read()
        uid = self._attr_unique_id
        firmware, bus_num, dev_num, sensor_type = uid.rsplit('-', 3)
        bus_num, dev_num = int(bus_num), int(dev_num)
        sensor_data = [s for s in sensor_data
                       if s['busnum'] == bus_num
                       and s['devnum'] == dev_num
                       and sensor_type in s]
        if len(sensor_data) > 1:
            raise RuntimeError("Unexpected duplicate TEMPer sensor")
        if len(sensor_data) < 1:
            raise RuntimeError(f"TEMPer USB device for {uid} is missing.")
        sensor_data = sensor_data[0]
        self._attr_native_value = sensor_data[sensor_type]


class TEMPerTemperatureSensor(TEMPerSensor):
    """A temperature sensor from a TEMPer device"""
    def __init__(self, uid, **kwargs):
        self._attr_name = uid.rsplit('-', 1)[-1].title()
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = uid
        
        super().__init__(**kwargs)


class TEMPerHumididtySensor(TEMPerSensor):
    """A humidity sensor from a TEMPer device"""
    def __init__(self, uid, **kwargs):
        self._attr_name = uid.rsplit('-', 1)[-1].title()
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = uid
        
        super().__init__(**kwargs)

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = 23
