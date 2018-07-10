
# For HTTP requests
import urequests

import pycom
import machine
import time

# WLAN support
from network import WLAN

from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
#from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE


wlan = WLAN(mode=WLAN.STA)
py = Pysense()
mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
si = SI7006A20(py)
#lt = LTR329ALS01(py)
li = LIS2HH12(py)

# Replace <teamSecret> in this url with your SIGNL4 team secret.
# You can find your secret in the SIGNL4 mobile app under Settings (gear) -> APIs.
# It is the alias part of your SIGNL4 team email address, e.g. dsd29x2
s4teamURL = "https://api.signl4.com/webhook/<teamSecret>/"


while True:
    pycom.heartbeat(False)

    print("MPL3115A2 temperature: " + str(mp.temperature()))
    print("Altitude: " + str(mp.altitude()))
    print("Pressure: " + str(mpp.pressure()))

    print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
    print("Dew point: "+ str(si.dew_point()) + " deg C")
    t_ambient = 24.4
    print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")

    # print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))

    print("Acceleration: " + str(li.acceleration()))
    print("Roll: " + str(li.roll()))
    print("Pitch: " + str(li.pitch()))

    print("Battery voltage: " + str(py.read_battery_voltage()))

    # Check WLAN first, replace SSID and password with appropriate values in your environment
    if wlan.isconnected() == False:
        print('Trying to connect to WIFI...')
        #Now the device may proceed to scan for networks:
        nets = wlan.scan()
        for net in nets:
            if net.ssid == '<yourSSID>':
                print('Network found!')
                wlan.connect(net.ssid, auth=(net.sec, 'yourWIFIPassword'), timeout=5000)
                while not wlan.isconnected():
                    machine.idle() # save power while waiting
                print("WLAN connection succeeded! IP Config: " + str(wlan.ifconfig()))

                pycom.rgbled(0x000014) #blue
                time.sleep(0.1)
                pycom.heartbeat(False)
                time.sleep(0.1)
                pycom.rgbled(0x000014) #blue
                time.sleep(0.1)
                pycom.heartbeat(False)

                break
    else:
        print("WLAN is connected. IP Config: " + str(wlan.ifconfig()))

        pycom.rgbled(0x001400) #green
        time.sleep(0.1)
        pycom.heartbeat(False)
        time.sleep(0.1)
        pycom.rgbled(0x001400) #green    
        time.sleep(0.1)
        pycom.heartbeat(False)


    # Send telemetry to SIGNL4
    if wlan.isconnected() == True:
        print("WLAN connected, sending sensor data to SIGNL4...")

        strJSONData = '{"IoT Sensor Device": "Pycom Pysense", "Temperature": "' + str(si.temperature()) + ' deg C", "Humidity": "' + str(si.humidity()) + ' %RH", "Pressure": "' + str(mpp.pressure()) + '", "Altitude": "' + str(mp.altitude()) + '", "Dew point": "' + str(si.dew_point()) + '", "Acceleration": "' + str(li.acceleration()) + '", "Roll": "' + str(li.roll()) + '", "Pitch": "' + str(li.pitch()) + '"}'

        urequests.request("POST",s4teamURL, strJSONData, None, {"Content-Type" : "application/json"}).text
        
        pycom.rgbled(0x001400) #green

        print("Sensor data sent to SIGNL4.")
    else:
        print("No WLAN connection, cannot send sensor data to SIGNL4.")
        pycom.rgbled(0x140000) # red

    # Let led keep color for 0.5 secs
    time.sleep(0.5) 
    pycom.heartbeat(False)

    time.sleep(3600)