import piplates.DAQCplate as DAQC
import TiltHydrometer
import base64
import datetime
import hashlib
import hmac
from gpiozero import CPUTemperature
import json
import math
import os
import re
import requests
import sys
import signal
import time

#Global Variables
RUN = True
ADDR = 0  #DAQC Plate Address
HOT = 0  #Hot Channel (DOUT/AIN)
COLD = 1 #Cold Channel (DOUT/AIN)
MAIN = 2 #Main Channel (AIN)
VOLT = 3 #Voltage (AIN)
TEMP = 0 #DS18B20 (DIN)
BEACON_MIN = 10 #minimum amount of time between beacon cycles
LOG_MIN = 10 #minimum amount of time between Log Entries
CYCLE_MIN = 10 #minimum number of seconds between hot/cold cycles

VSHIFT = -2.5
VMULT = 121.6
  #Amperage correction formula values (aX * Amps^2 - aY * Amps + aZ) when Amps > 0
AX = 0.2434
AY = 0.6855
AZ = 0.4479
TILT_PATTERN = r"^T:\ ([\d\.]*)\ G:\ ([\d\.]*)"
START_TIME = datetime.datetime.now()

Debug = False
if (len(sys.argv) > 1) and (sys.argv[1] == '--debug'):
  Debug = True

#Function Declarations
def GetAmps(channel):
  global AX, AY, AZ, ADDR, HOT, COLD, MAIN
  vMax = 0
  Amps = 0
  for x in range(0,120):
    vMeas = (DAQC.getADC(ADDR,channel) - .044)
    if vMeas > vMax:
      vMax = vMeas
  if vMax != 0:
    Amps = (AX * (vMax ** 2))- (AY * vMax) + AZ
  return round(Amps, 2)

def GetVolts():
  vMax = 0
  global VSHIFT, VMULT, ADDR, VOLT

  for x in range(0,120):
    vMeas = DAQC.getADC(ADDR, VOLT)
    if vMeas > vMax:
      vMax = vMeas

  return ((vMax + VSHIFT) * VMULT)

def GetTemp(scale):
  global ADDR, TEMP
  return DAQC.getTEMP(ADDR, TEMP, scale)

def OnKill(signum, frame):
  global RUN, ADDR, HOT, COLD
  RUN = False
  DAQC.clrDOUTbit(ADDR, HOT) #Hot Off
  DAQC.clrDOUTbit(ADDR, COLD) #Cold Off

# Build the API signature
def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash).encode('utf-8')  
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest())
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization

# Build and send a request to the POST API
def post_data(customer_id, shared_key, body, log_type):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }

    response = requests.post(uri,data=body, headers=headers)


try:
  signal.signal(signal.SIGINT, OnKill)
  signal.signal(signal.SIGTERM, OnKill)
  
  #Initial Settings Load
  f = open("/var/www/html/py/conf.json")
  Settings = json.load(f)
  f.close
  DirtySettings = False
  if Settings['CycleFrequency'] < CYCLE_MIN:
    Settings['CycleFrequency'] = CYCLE_MIN
    DirtySettings = True
  if Settings['LogFrequency'] < LOG_MIN:
    Settings['LogFrequency'] = LOG_MIN
    DirtySettings = True
  if Settings['BeaconFrequency'] < BEACON_MIN:
    Settings['BeaconFrequency'] = BEACON_MIN
    DirtySettings = True
  if DirtySettings:
    f = open('/var/www/html/py/conf.json', 'w')
    json.dump(Settings, f)
    f.close()
    DirtySettings = False

  #Initial Data Load
  f = open('/var/www/html/py/data.json')
  data = json.load(f)
  f.close()

  #Initialize loop counter
  loop = 0
  nextBeacon = loop + Settings['BeaconFrequency']
  if Settings['LogEnabled'] == True:
    nextLog = loop + Settings['LogFrequency']
  else:
    nextLog = -1
  nextCycle = loop + Settings['CycleFrequency']

  #Initialize Tilt
  tilt = TiltHydrometer.TiltHydrometerManager(False, 60, 40)
  tilt.loadSettings()
  tilt.start()
  ColdState = 0
  HotState = 0

  while RUN:
    CurrTime = datetime.datetime.now()
    #t = open('/var/www/html/py/uptime', 'w')
    #t.write(str(CurrTime - START_TIME))
    #t.close()
    d = open('/var/www/html/py/data.json')
    data = json.load(d)
    d.close()
    Uptime = CurrTime - START_TIME
    data['Uptime'] = str(Uptime)

    #reload settings if they have changed
    if os.path.isfile("/var/www/html/py/reload"):
      f = open("/var/www/html/py/conf.json")
      Settings = json.load(f)
      f.close()
      os.remove('/var/www/html/py/reload')
      if Settings['LogEnabled'] == True:
        nextLog = loop
      else:
        nextLog = -1
      
    #Refresh Metrics
    
    data['MainAmps'] = GetAmps(MAIN)
    data['HotAmps'] = GetAmps(HOT)
    data['ColdAmps'] = GetAmps(COLD)
    data['MainVolts'] = GetVolts()
    data['ProbeTemp'] = GetTemp(Settings['TempUnits'])
    data['CpuTemp'] = CPUTemperature().temperature

    #Process Beacons?
    if loop == nextBeacon:
      for color in Settings['EnabledTilts']:
        raw = str(tilt.getValue(color))
        if raw != None:
          match = re.search(TILT_PATTERN, raw)
          if match != None:
            data[color]['Temp'] = float(match.group(1))
            data[color]['Grav'] = float(match.group(2))
            if Debug:
              print("%s - %f SG at %f deg" % (color, float(match.group(2)), float(match.group(1))))
          else:
            data[color]['Temp'] = 0.0
            data[color]['Grav'] = 1.0
            if Debug:
              print("No Signal from %s tilt!" % (color))
        else:
          data[color]['Temp'] = 0.0
          data[color]['Grav'] = 1.0
      data['LastBeacon'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      #f = open('/var/www/html/py/lastbeacon', 'w')
      #f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
      #f.close()
      nextBeacon += Settings['BeaconFrequency']

    if loop == nextCycle:
      if data['ProbeTemp'] < (float(Settings['TargetTemp']) - float(Settings['Hysteresis'])):
        DAQC.clrDOUTbit(ADDR, COLD)
        DAQC.setDOUTbit(ADDR, HOT)
        data['HotState'] = 1
        data['ColdState'] = 0
      elif data['ProbeTemp'] > (float(Settings['TargetTemp']) + float(Settings['Hysteresis'])):
        DAQC.clrDOUTbit(ADDR, HOT)
        DAQC.setDOUTbit(ADDR, COLD)
        data['HotState'] = 0
        data['ColdState'] = 1
      else:
        DAQC.clrDOUTbit(ADDR, HOT)
        DAQC.clrDOUTbit(ADDR, COLD)
        data['HotState'] = 0
        data['ColdState'] = 0
      nextCycle += Settings['CycleFrequency']

    if loop == nextLog:
      for color in Settings['EnabledTilts']:
        if Debug:
          print("Logging %s to Azure:\r" % (color))
        payload = """{
          "BeerName": "%s",
          "ColdAmps": %f,
          "ColdState": %i,
          "Color": "%s",
          "ProbeTemp": %f,
          "HotAmps": %f,
          "HotState": %i,
          "MainAmps": %f,
          "Hysteresis": %f,
          "TargetTemp": %f,
          "SG": %f,
          "TiltTemp": %f,
          "Voltage": %f,
          "CpuTemp": %f,
          "Uptime": "%s",
          "LastBeacon": "%s"
        }""" % (Settings[color], data['ColdAmps'], data['ColdState'], color, data['ProbeTemp'], data['HotAmps'], data['HotState'], data['MainAmps'], Settings['Hysteresis'], Settings['TargetTemp'], data[color]['Grav'], data[color]['Temp'], data['MainVolts'], data['CpuTemp'], data['Uptime'], data['LastBeacon'])
        
        post_data(Settings['WorkspaceId'], Settings['WorkspaceKey'], payload, Settings['LogName'])
        if Debug:
          print("Logging %s to Azure: OK\r" % (color))
      nextLog += Settings['LogFrequency']

    loop += 1
    d = open('/var/www/html/py/data.json', 'w')
    json.dump(data, d)
    d.close()
    time.sleep(1)

except Exception as e:
  now = datetime.datetime.now()
  if Debug:
    print(e)
  f = open('/var/www/html/python_errors.log', 'a')
  f.write("%s - TILT [%i] - %s\n" % (now.strftime("%Y-%m-%d %H:%M:%S"), sys.exc_info()[-1].tb_lineno, e))
  f.close()

now = datetime.datetime.now()
f = open('/var/www/html/python_errors.log', 'a')
f.write("%s - TILT [0] - Exit called from interface\n" % (now.strftime("%Y-%m-%d %H:%M:%S")))
f.close()