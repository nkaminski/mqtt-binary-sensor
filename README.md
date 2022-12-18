# mqtt-binary-sensor
Program to read a PIR sensor connected to a Pi Pico and publish the status over MQTT (w/ HA discovery)


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
