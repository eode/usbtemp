# PCSensor TEMPer devices

| Platform | Description |
| -------- | ------------ |
| sensor   | Creates temperature and/or humidity sensor entities for each PCSensor TEMPer USB device plugged into your system |

This sensor reads PCSensor TEMPer devices, which are simple USB
temperature and humidity sensors.  There are various revisions of
the hardware, and this code supports many of them -- specifically,
those supported by the `temper-py` module.

## Caveats
There are two major caveats to using these devices.  I assure you,
I'm only coding this because I lack other convenient temperature
sensors.  I should really just spend $30 and get a different one.

### Inaccuracy
Be forewarned -- these devices have a flaw (or there is an 
implementation issue across multiple drivers in various programming 
languages) that cause the temperature to "stick" occasionally.  This 
goes beyond mere binary granularity, but seems to be an actual flaw
in the hardware, unless there is some undocumented means of interacting 
with the hardware in a way that prevents this behavior.  ..which is
totally possible, as there's no documentation for interacting with
the sensor.  Some people just want to see the world burn.

That said, for some, this hardware may just be "good enough."

### Not Unique
The devices have no unique identifier, at all.  Every TEMPer device
of one hardware revision looks like every other TEMPer device of that
hardware revision.  This means the devices have no unique id.

The workaround that this module implements is that the USB port is used 
to uniquely identify the device.  That is, if you unplug it, and plug 
it into a different port, HomeAssistant will see it as an entirely 
different device.

## Installation

Copy `custom_components/pcsensor` to `<HA config_dir>/custom_components/`.

Add the following to your `configuration.yaml` file:

```yaml
sensor:
  - platform: pcsensor
```
