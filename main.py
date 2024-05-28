import time
import pycom
import machine
from network import WLAN
from pycoproc import Pycoproc 
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE
from umqtt.simple import MQTTClient
 
# Initialize Pycoproc and sensors
py = Pycoproc(Pycoproc.PYSENSE)
DEVICE_ID = "stavros"


# Wi-Fi credentials
WIFI_SSID = "asyrmata"
WIFI_PASS = "pasiphae"
 
# MQTT settings
MQTT_BROKER = "192.168.1.101"
MQTT_PORT = 1883
 
# Turn off heartbeat LED and set it to white
pycom.heartbeat(False)
pycom.rgbled(0x0A0A08)  # white
 
# Initialize sensors
acc = LIS2HH12(py)
li = LTR329ALS01(py)
alt = MPL3115A2(py, mode=ALTITUDE)  # Returns height in meters
dht = SI7006A20(py)
press = MPL3115A2(py, mode=PRESSURE)  # Returns pressure in Pa
 
# Connect to Wi-Fi with a timeout and error handling
wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid=WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS))
 
timeout = 10  # seconds
start_time = time.time()
while not wlan.isconnected():
    if time.time() - start_time > timeout:
        print("Failed to connect to WiFi")
        machine.reset()
    machine.idle()
 
print("Connected to WiFi\n")
 
# MQTT client setup
client = MQTTClient(DEVICE_ID, MQTT_BROKER, port=MQTT_PORT)
 
# Function to send sensor metrics
def sendMetrics():
    try:
        client.publish("sensors/temperature/"+DEVICE_ID, str(alt.temperature()))
        client.publish("sensors/altitude/"+DEVICE_ID, str(alt.altitude()))
        client.publish("sensors/pressure/"+DEVICE_ID, str(press.pressure()))
        client.publish("sensors/humidity/"+DEVICE_ID, str(dht.humidity()))
        client.publish("sensors/light/"+DEVICE_ID, str(li.light()))
        client.publish("sensors/acceleration/"+DEVICE_ID, str(acc.acceleration()))
        client.publish("sensors/roll/"+DEVICE_ID, str(acc.roll()))
        client.publish("sensors/pitch/"+DEVICE_ID, str(acc.pitch()))
        client.publish("sensors/battery/"+DEVICE_ID, str(py.read_battery_voltage()))
    except Exception as e:
        print("Failed to send metrics:", e)
 
# Callback function for received MQTT messages
def sub_cb(topic, msg):
    topic = topic.decode()
    msg = msg.decode()

    #if topic ends with device id, then skip
    if topic.endswith(DEVICE_ID):
        return
    
    print("Received:", topic.decode(), msg.decode())
 
# Function to receive metrics
def receiveMetrics():
    try:
        client.set_callback(sub_cb)
        client.subscribe("sensors/#")
        client.check_msg()
    except Exception as e:
        print("Failed to receive metrics:", e)
 
# Connect to MQTT broker with error handling
try:
    client.connect()
    print("Connected to MQTT Broker\n")
except Exception as e:
    print("Failed to connect to MQTT Broker:", e)
    machine.reset()
 
# Main loop
while True:
    sendMetrics()
    receiveMetrics()
    time.sleep(5)