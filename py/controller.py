import base64
import datetime
from gpiozero import CPUTemperature
import hashlib
import hmac
import inspect
import iot
import json
import math
import os
import piplates.DAQCplate as DAQC
import re
import requests
import sys
import signal
import tilt
import time

#Global Variables
IOT = iot.IoT()
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
TILT_COLORS = ["Black", "Blue", "Green", "Orange", "Pink", "Purple", "Red", "Yellow"]

VSHIFT = -2.5
VMULT = 121.6
  #Amperage correction formula values y = mx + b
M = 8.513513
B = 0.0
TILT_PATTERN = r"^T:\ ([\d\.]*)\ G:\ ([\d\.]*)"
START_TIME = datetime.datetime.now()
Settings = None
Data = None
CurrTime = None

#Initialize Tilt
tilt = tilt.Tilt()
tilt.Start()
#tilt = TiltHydrometer.TiltHydrometerManager(False, 60, 40)
#tilt.loadSettings()
#tilt.start()

Debug = False
if (len(sys.argv) > 1) and (sys.argv[1] == '--debug'):
  Debug = True

#Function Declarations
def GetAmps(channel):
  global M, B, ADDR, HOT, COLD, MAIN
  vMax = 0
  Amps = 0
  for x in range(0,120):
    vMeas = DAQC.getADC(ADDR,channel) - (DAQC.getADC(ADDR,8) / 2)
    if vMeas > vMax:
      vMax = vMeas
  if vMax != 0:
    Amps = M * vMax + B
  return round(Amps, 2)

def GetVolts():
  vMax = 0
  global VSHIFT, VMULT, ADDR, VOLT

  for x in range(0,120):
    vMeas = DAQC.getADC(ADDR, VOLT)
    if vMeas > vMax:
      vMax = vMeas

  return ((vMax + VSHIFT) * VMULT)

def OnKill(signum, frame):
  global RUN, ADDR, HOT, COLD
  RUN = False
  DAQC.clrDOUTbit(ADDR, HOT) #Hot Off
  DAQC.clrDOUTbit(ADDR, COLD) #Cold Off
  now = datetime.datetime.now()
  f = open('/var/www/html/python_errors.log', 'a')
  f.write("%s - TILT [0] - Exit called from interface\n" % (now.strftime("%Y-%m-%d %H:%M:%S")))
  f.close()

def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
  x_headers = 'x-ms-date:' + date
  string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
  bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
  decoded_key = base64.b64decode(shared_key)
  encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
  authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
  return authorization

def post_data(customer_id, shared_key, body, log_type):
  method = 'POST'
  content_type = 'application/json'
  resource = '/api/logs'
  rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
  content_length = len(body)
  signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
  headers = {
    'content-type': content_type,
    'Authorization': signature,
    'Log-Type': log_type,
    'x-ms-date': rfc1123date
  }
  uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'
  return requests.post(uri,data=body, headers=headers)

def WriteLog(message):
  global Debug
  now = datetime.datetime.now()
  callerFrameRecord = inspect.stack()[1]
  frame = callerFrameRecord[0]
  info = inspect.getframeinfo(frame)

  if Debug:
    print(message)
  f = open('/var/www/html/python_errors.log', 'a')
  f.write("%s - TILT [%i] - %s\n" % (now.strftime("%Y-%m-%d %H:%M:%S"), info.lineno, message))
  f.close()

#Signal handling
signal.signal(signal.SIGINT, OnKill)
signal.signal(signal.SIGTERM, OnKill)

#Initial Load
try:
  #Setup IoT
  IOT.Start()
  #Settings
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

  #Data
  f = open('/var/www/html/py/data.json')
  data = json.load(f)
  f.close()

  #Copy some settings to the data structure
  data['TargetTemp'] = Settings['TargetTemp']
  data['Hysteresis'] = Settings['Hysteresis']
  for color in TILT_COLORS:
    data[color]['Name'] = "Disabled"
    data[color]['LastBeacon'] = "Never"
    data[color]['Enabled'] = False
  for color in Settings['EnabledTilts']:
    data[color]['Name'] = Settings[color]
    data[color]['Enabled'] = True
  data['TempUnits'] = Settings['TempUnits']
  data['GravUnits'] = Settings['GravUnits']
  data['LogEnabled'] = Settings['LogEnabled']
  data['LogFrequency'] = Settings['LogFrequency']
  data['BeaconFrequency'] = Settings['BeaconFrequency']
  data['CycleFrequency'] = Settings['CycleFrequency']
  data['ColdState'] = 0  #Initialize the hot and cold state to off
  data['HotState'] = 0
  #Zero kWh
  data['kWh'] = 0
  data['kWhCost'] = Settings['kWhCost']
  #Save the new data
  d = open('/var/www/html/py/data.json', 'w')
  json.dump(data, d)
  d.close()
except Exception as e:
  WriteLog(e)

#Initialize loop counter
loop = 0
sinceLastCycle = 0
if Settings['BeaconEnabled']:
  nextBeacon = loop + Settings['BeaconFrequency']
else:
  nextBeacon = -1
if Settings['LogEnabled'] == True:
  nextLog = loop + Settings['LogFrequency']
else:
  nextLog = -1
nextCycle = loop + Settings['CycleFrequency']

while RUN:
  #Refresh Data/Settings
  try:
    CurrTime = datetime.datetime.now()
    if os.path.exists('/var/www/html/py/newdata.json'):
      d = open('/var/www/html/py/newdata.json')
      data = json.load(d)
      d.close()
      os.remove('/var/www/html/py/newdata.json')
    else:
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
      #Copy some settings to the data structure
      data['TargetTemp'] = Settings['TargetTemp']
      data['Hysteresis'] = Settings['Hysteresis']
      for color in TILT_COLORS:
        data[color]['Name'] = "Disabled"
        data[color]['Enabled'] = False
      for color in Settings['EnabledTilts']:
        data[color]['Name'] = Settings[color]
        data[color]['Enabled'] = True
      data['TempUnits'] = Settings['TempUnits']
      data['GravUnits'] = Settings['GravUnits']
      data['LogEnabled'] = Settings['LogEnabled']
      data['LogFrequency'] = Settings['LogFrequency']
      data['BeaconFrequency'] = Settings['BeaconFrequency']
      data['CycleFrequency'] = Settings['CycleFrequency']
      data['kWhCost'] = Settings['kWhCost']
      os.remove('/var/www/html/py/reload')
      if Settings['LogEnabled'] == True:
        nextLog = loop
      else:
        nextLog = -1
    

    #Refresh Metrics
    data['SinceLastCycle'] = sinceLastCycle
    data['MainAmps'] = GetAmps(MAIN)
    data['HotAmps'] = GetAmps(HOT)
    data['ColdAmps'] = GetAmps(COLD)
    data['MainVolts'] = GetVolts()
    if ((loop % 10) == 0):
      data['ProbeTemp'] = DAQC.getTEMP(ADDR, TEMP, 'c')
    data['CpuTemp'] = CPUTemperature().temperature
    kWh = (data['MainAmps'] * data['MainVolts'] * .000277) / 1000
    data['kWh'] += kWh
  except Exception as e:
    WriteLog(e)
  
  #Process Beacons
  try:
    if (loop == nextBeacon) and (Settings['BeaconEnabled']):
      for color in Settings['EnabledTilts']:
        data[color]['Temp'] = tilt.GetCalTemp(color)
        data[color]['Grav'] = tilt.GetCalGrav(color)
        data[color]['LastBeacon'] = tilt.LastBeacon[color]
  except Exception as e:
    WriteLog(e)
  finally:
    if loop == nextBeacon:
      nextBeacon += Settings['BeaconFrequency']

  #Process Heating/Cooling Cycle
  try:
    if sinceLastCycle >= Settings['CycleFrequency']:
      if data['ProbeTemp'] < (float(Settings['TargetTemp']) - float(Settings['Hysteresis'])): #Too Cold, turn on heat
        if data['HotState'] == 0:
          sinceLastCycle = 0 #Heat is off and will be toggled, reset sinceLastCycle to 0
          DAQC.clrDOUTbit(ADDR, COLD)
          DAQC.setDOUTbit(ADDR, HOT)
          data['HotState'] = 1
          data['ColdState'] = 0
      elif data['ProbeTemp'] > (float(Settings['TargetTemp']) + float(Settings['Hysteresis'])): #Too Hot, turn on cold
        if data['ColdState'] == 0:
          sinceLastCycle = 0 #Cold is off and will be toggled, reset sinceLastCycle to 0
          DAQC.clrDOUTbit(ADDR, HOT)
          DAQC.setDOUTbit(ADDR, COLD)
          data['HotState'] = 0
          data['ColdState'] = 1
      else:
        if (data['ColdState'] == 1) or (data['HotState'] == 1):
          sinceLastCycle = 0 #Cold or hot is on and we are now in the Hysteresis band.  Shut them off
          DAQC.clrDOUTbit(ADDR, HOT)
          DAQC.clrDOUTbit(ADDR, COLD)
          data['HotState'] = 0
          data['ColdState'] = 0

  except Exception as e:
    WriteLog(e)

  
  #Send Data to Log Analytics
  try:
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
          "LastBeacon": "%s",
          "TotalkWh": %f
        }""" % (Settings[color], data['ColdAmps'], data['ColdState'], color, data['ProbeTemp'], data['HotAmps'], data['HotState'], data['MainAmps'], Settings['Hysteresis'], Settings['TargetTemp'], data[color]['Grav'], data[color]['Temp'], data['MainVolts'], data['CpuTemp'], data['Uptime'], data[color]['LastBeacon'], data['kWh'])
        
        result = post_data(Settings['WorkspaceId'], Settings['WorkspaceKey'], payload, Settings['LogName'])
        if Debug:
          print("Logging %s to Azure: %i\r" % (color, result.status_code))
        if result.status_code != 200:
          WriteLog("Logging {} to Azure failed: {}".format(color, result.status_code))
        else:
          data['LastLog'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  except Exception as e:
    WriteLog(e)
  finally:
    if loop == nextLog:
      nextLog += Settings['LogFrequency']
  

  try:
    d = open('/var/www/html/py/data.json', 'w')
    json.dump(data, d)
    d.close()
  except Exception as e:
    WriteLog(e)
  finally:
    loop += 1
    sinceLastCycle += 1
  
  loopTime = (datetime.datetime.now() - CurrTime).total_seconds() * 1e3
  if loopTime < 1000:
    time.sleep((1000 - loopTime) * .001)

  try:
    if os.path.exists('/var/www/html/py/STOP'):
      RUN = False
      os.remove('/var/www/html/py/STOP')
  except Exception as e:
    WriteLog(e)

tilt.Stop()
IOT.Stop()
DAQC.clrDOUTbit(ADDR, HOT) #Hot Off
DAQC.clrDOUTbit(ADDR, COLD) #Cold Off