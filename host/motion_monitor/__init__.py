import click
import json
import logging
import serial
import yaml

import paho.mqtt.client as mqtt


class ConfigurationError(ValueError):
    pass


def config_load(cf):
    """Loads and validates the configuration from the provided configuration file"""
    validate_keys = [
        "mqtt_host",
        "mqtt_username",
        "mqtt_password",
        "serial_port",
        "ha_device_name",
        "ha_device_class",
    ]
    with open(cf, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    if not isinstance(config, dict):
        raise ConfigurationError("Configuration must be a dictionary")
    for vk in validate_keys:
        if vk not in config:
            raise ConfigurationError(f"Configuration must contain value for item: {vk}")
    return config


def on_connect(client, userdata, flags, rc):
    """Called on (re)connection to the MQTT broker"""
    logging.info("MQTT connected with result code %s", rc)
    if userdata is not None:
        config_topic = userdata["config_topic"]
        logging.info("Registering in home assistant under %s", config_topic)
        ha_data = {k: v for k, v in userdata.items() if k != "config_topic"}
        client.publish(config_topic, json.dumps(ha_data), retain=True)


def mqtt_connect(
    host, port=1883, keepalive=60, username=None, password=None, ha_data=None
):
    """
    Opens a connection to the MQTT broker and returns the MQTT client object

    Publishes the homeassistant discovery metadata if provided as well.
    """
    mqttc = mqtt.Client()
    if (username is not None) and (password is not None):
        mqttc.username_pw_set(username, password)
    mqttc.user_data_set(ha_data)
    mqttc.on_connect = on_connect
    mqttc.connect(host=host, port=port, keepalive=keepalive)
    mqttc.loop_start()
    return mqttc


@click.command(short_help="Monitors a sensor connected to the specified port")
@click.option("-c", "--config", type=click.Path(exists=True), required=True, help="Path to the configuration file")
@click.option("--unregister", is_flag=True, help="Unregisters the binary_sensor from HA and the MQTT broker")
@click.option("--verbose", is_flag=True)
@click.option("--debug", is_flag=True)
def cli(config, unregister, verbose, debug):
    # Init logging at the correct verbosity
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Load configuration
    cf = config_load(config)

    # Open the MQTT connection
    ha_name = cf["ha_device_name"]
    uid = ha_name.replace(" ", "_").lower()
    ha_data = {
        "name": ha_name,
        "device_class": cf["ha_device_class"],
        "unique_id": uid,
        "state_topic": f"homeassistant/binary_sensor/{uid}/state",
        "config_topic": f"homeassistant/binary_sensor/{uid}/config",
    }
    mqttc = mqtt_connect(
        host=cf["mqtt_host"],
        username=cf["mqtt_username"],
        password=cf["mqtt_password"],
        ha_data=ha_data,
    )

    if unregister:
        # Unregister the HA configuration
        logging.warning("Unregistering from MQTT broker")
        mqttc.publish(ha_data["config_topic"], "")
        mqttc.disconnect()
        mqttc.loop_stop()
        raise SystemExit(0)

    # Open the serial port and read incoming characters
    try:
        with serial.Serial(cf["serial_port"], cf.get("serial_baud", 57600)) as sp:
            logging.info("Opened serial port %s", sp.port)
            while True:
                incoming = sp.read().decode("ascii")
                if incoming == "0":
                    # Sensor clear
                    logging.debug("Received sensor clear report")
                    mqttc.publish(ha_data["state_topic"], "OFF")
                elif incoming == "1":
                    # Sensor tripped
                    logging.debug("Received sensor triggered report")
                    mqttc.publish(ha_data["state_topic"], "ON")
                else:
                    logging.warning(
                        "Received invalid character from device: %s", incoming
                    )
    except serial.serialutil.SerialException:
        logging.exception("Serial port communication error:")
        raise SystemExit(1)

