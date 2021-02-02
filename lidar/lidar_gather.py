from pyrplidar import PyRPlidar
import time

import paho.mqtt.client as mqtt
import json

def run_scan(client, userdata, message):

    print(message)
    print(message.payload.decode())
    request = json.loads(message.payload.decode())
    print(request)

    # Storage for scan data
    SAMPLE_BATCH = []

    # Run scan
    scan_generator = lidar.start_scan()
    for count, scan in enumerate(scan_generator()):
        print(count, len(SAMPLE_BATCH), scan)

        # If scan meets quality standard, add to BATCH
        if scan.quality > 10:
            SAMPLE_BATCH.append([scan.angle, scan.distance])

        # Break if reached the maximum number of samples
        if len(SAMPLE_BATCH) > MAX_SAMPLES:
            break

    # Package with json and send
    message = json.dumps(SAMPLE_BATCH).encode('utf-8')
    client.publish(topic="lidar_batch", payload=message, qos=0, retain=False)

    # Stop the lidar
    lidar.stop()
    lidar.set_motor_pwm(0)
    lidar.disconnect()


MAX_SAMPLES = 2000

# Setup the lidar
lidar = PyRPlidar()
lidar.connect(port="/dev/ttyUSB0", baudrate=115200, timeout=3)
lidar.set_motor_pwm(500)
time.sleep(2)

# Connect to the Brain client
broker_url, broker_port = "192.168.10.103", 1883
client = mqtt.Client()
client.connect(broker_url, broker_port)

# Subscribe to request topic
client.subscribe("lidar_request", qos=0)
client.message_callback_add("lidar_request", run_scan)

client.loop_forever()

