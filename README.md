# USBTEMP devices

| Platform | Description |
| -------- | ------------ |
| sensor   | Creates one temperature sensor entity for each [usbtemp](https://usbtemp.com) USB device plugged into your system |

This project is not affiliated with [usbtemp.com](https://usbtemp.com),
I'm simply writing it for my own utility, and sharing the resultant code.

This sensor reads USBTEMP devices, which are simple, good-quality USB
temperature sensors based on a genuine DS18B20 1–wire sensor and USB 
bridge interface, providing 9-bit to 12-bit temperature measurements.
Each thermometer has an unique 64-bit serial code stored inside ROM,
as well as a unique USB Serial code.  This is particularly useful for
Homeassistant, allowing distinct entities to be created and tracked. 
It compares favorably to sensors like the PCSensor TEMPer USB, both in
accuracy and device tracking.

## Installation

Copy `custom_components/usbtemp` to `<HA config_dir>/custom_components/`.

Add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: usbtemp
```
