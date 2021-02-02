from pyrplidar import PyRPlidar
import time

import paho.mqtt.client as mqtt
import json


# Setup the lidar
lidar = PyRPlidar()
lidar.connect(port="/dev/ttyUSB0", baudrate=115200, timeout=3)
lidar.set_motor_pwm(500)
time.sleep(2)

# Connect to the Brain client
broker_url, broker_port = "192.168.10.103", 1883
client = mqtt.Client()
client.connect(broker_url, broker_port)

try: 
    # Run scan
    scan_generator = lidar.force_scan()
    for count, scan in enumerate(scan_generator()):
        print(count, scan)
        # Package with json and send
        message = json.dumps([scan.angle, scan.distance]).encode('utf-8')
        client.publish(topic="lidar_data", payload=message, qos=0, retain=False)

finally:
    lidar.stop()
    lidar.set_motor_pwm(0)
    lidar.disconnect()