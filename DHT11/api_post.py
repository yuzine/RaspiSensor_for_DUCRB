import RPi.GPIO as GPIO
import dht11
import tsl2561
import requests
import json
import time
import csv
import ipget
import os

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

instance = dht11.DHT11(pin=4)

SERVER = ""
DEV_UCODE = ""
HEADERS = {'Content-type': 'application/json'}

RETRY_COUNT = 0

def getRaspiInfo():
    url = SERVER + "/api/" + DEV_UCODE + "/raspberrypi/info/"
    r = requests.get(url=url)
    return r.json()

def postRaspiIpaddress():
    global RETRY_COUNT
    url = SERVER + "/api/raspberrypi/ipaddress/"
    ip = ipget.ipget()
    ipaddress = ip.ipaddr("wlan0")

    data = {
        "dev_ucode": DEV_UCODE,
        "ip": ipaddress
    }

    try:
        conn = requests.post(url=url, data=json.dumps(data), headers=HEADERS, timeout=30.0)
        RETRY_COUNT = 0
    except:
        time.sleep(10)
        if (RETRY_COUNT == 10):
            os.system("sudo ifconfig wlan0 down")
            os.system("sudo ifconfig wlan0 up")
        else:
            RETRY_COUNT += 1
            postRaspiIpaddress()

def readDHT11All():
    while True:
        result = instance.read()
        if result.is_valid():
            return result.temperature, result.humidity
        else :
            continue;

def postData(infoList):
    temperature, humidity = readDHT11All()
    lux = tsl2561.getCalcLux()
    dataList = [temperature, humidity, lux]
    
    """
    print("temperature: %f" % temperature)
    print("humidity: %f" % humidity)
    print("lux: %f" % lux)
    """

    url = SERVER + "/api/koshizuka-lab/raspberrypi/sensorstate/"
    headers = {'Content-type': 'application/json'}
    
    count=0
    for data in infoList:
        data["value"] = dataList[count]
        
        try:
            conn = requests.post(url, data=json.dumps(data), headers=HEADERS, timeout=30.0)
            #print(conn.status_code)
            count+=1
        except TimeoutError:
            #print("TimeoutError")
            return False
        except requests.exceptions.ConnectionError:
            #print("Connection_Error")
            return False
    return True

if __name__ == '__main__':
    try:
        infoList = getRaspiInfo()
        postRaspiIpaddress()
        while True:
            if postData(infoList):
                time.sleep(60)
            else:
                postRaspiIpaddress()
                continue
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
