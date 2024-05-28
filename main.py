import time
import pycom
import machine
from network import WLAN
from pycoproc import Pycoproc 
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
from umqtt.simple import MQTTClient
py = Pycoproc(1)

# connect to wifi using ldap
WIFI_SSID = "asyrmata"
WIFI_PASS = "pasiphae"

MQTT_BROKER = "192.168.1.101"
MQTT_PORT = 1883

DEVICE_ID = "stavros"
OTHER_DEVICES = ["antonis", "giorgos"]
pycom.heartbeat(False)
pycom.rgbled(0x0A0A08) # white
acc = LIS2HH12(py)
li = LTR329ALS01(py)
alt = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
dht = SI7006A20(py)
t_ambient = 24.4
li = LTR329ALS01(py)
press = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters


def sendMetrics():

    # send to mqtt
    client.publish("sensors/"+DEVICE_ID+"/temperature", str(alt.temperature()))


# receive same data above from other devices in mqtt but not from self
def receiveMetrics():
    client.set_callback(sub_cb)
    for device in OTHER_DEVICES:
        client.subscribe("sensors/"+device+"/temperature")
        client.wait_msg()



def sub_cb(topic, msg):
    print("Received: ", topic, msg)

# Connect to WiFi using WPA2 
wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid=WIFI_SSID, auth=(WLAN.WPA2, WIFI_PASS))
while not wlan.isconnected():
    machine.idle()


print("Connected to Wifi\n")

# connect to mqtt broker 
client = MQTTClient("stavros", MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("Connected to MQTT Broker\n")


while True:
    sendMetrics()
    receiveMetrics()
    time.sleep(5)