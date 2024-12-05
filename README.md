# mqtt-binary-sensor
Program to read a PIR sensor connected to a Pi Pico and publish the status over MQTT (w/ HA discovery).

Presently used to report the status of a motion sensor attached to a Falcon Player instance for holiday light show control purposes.

## CLI Usage
```
Usage: motion-monitor [OPTIONS]

Options:
  -c, --config PATH  Path to the configuration file  [required]
  --unregister       Unregisters the binary_sensor from HA and the MQTT broker
  --verbose
  --debug
  --help             Show this message and exit.
```

## Configuration example
```
---
mqtt_host: homeassistant.home
mqtt_username: your_mqtt_user
mqtt_password: REDACTED
serial_port: /dev/ttyACM0
ha_device_name: "Test Motion Sensor"
ha_device_class: motion
```
