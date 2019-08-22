#coding: utf-8

import bme280
import tsl2561
import requests
import json
import time
import csv
import ipget
import os

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

def postData(infoList):
    temperature, pressure, humidity = bme280.getBME280All()
    dataList = [temperature, humidity, pressure]
    
    """
    print("temp = %f" % temperature)
    print("humi = %f" % humidity)
    print("pres = %f" % pressure)
    """

    url = SERVER + "/api/koshizuka-lab/raspberrypi/sensorstate/"
        
    count = 0
    for data in infoList:
        data["value"] = dataList[count]
        
        try:
            conn = requests.post(url=url, data=json.dumps(data), headers=HEADERS, timeout=30.0)
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

