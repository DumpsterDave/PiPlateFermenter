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
import megaind
import librtd
import re
import requests
import sys
import signal
import tilt
import time

#Global Variables
IOT = iot.IoT()
RUN = True
RTDADDR = 0
INDADDR = 1
#0-10v Outs
VOLT_OUT = 1
MAIN_OUT = 2
COLD_OUT = 3
HOT_OUT = 4
#Open Drain Outputs
COLD_OD = 1
PUMP_OD = 2
HOT_OD = 3 
ERR_OD = 4
#0-10v Inputs
VOLT_IN = 1
MAIN_IN = 2
COLD_IN = 3
HOT_IN = 4
#RTD Probes
TEMP = 1
HS = 8

BEACON_MIN = 10 #minimum amount of time between beacon cycles
LOG_MIN = 10 #minimum amount of time between Log Entries
CYCLE_MIN = 30 #minimum number of seconds between hot/cold cycles
TILT_COLORS = ["Black", "Blue", "Green", "Orange", "Pink", "Purple", "Red", "Yellow"]
VDIV = 2.5
VMUL = 111
ERRCOUNT = 0
TOTERRORS = 0

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

#Power on sensors
megaind.set0_10Out(INDADDR, VOLT_OUT, 5)
megaind.set0_10Out(INDADDR, MAIN_OUT, 5)
megaind.set0_10Out(INDADDR, COLD_OUT, 5)
megaind.set0_10Out(INDADDR, HOT_OUT, 5)

#Rest Error Indicator
megaind.setOdPWM(INDADDR, ERR_OD, 0)

Debug = False
if (len(sys.argv) > 1) and (sys.argv[1] == '--debug'):
  Debug = True

megaind.set0_10Out(1, 1, 5)
megaind.set0_10Out(1, 2, 5)
megaind.set0_10Out(1, 3, 5)
megaind.set0_10Out(1, 4, 5)

#Function Declarations
def GetAmps(channel):
  global INDADDR
  vMax = 0
  vMin = 10
  for x in range(0,120):
    vMeas = megaind.get0_10In(INDADDR, channel)
    if vMeas > vMax:
      vMax = vMeas
    elif vMeas < vMin:
      vMin = vMeas
  p2p = vMax - vMin
  Amps = 26 * p2p
  return round(Amps, 3)

def GetVolts():
  vMax = 0
  global VDIV, VMUL, INDADDR, VOLT_IN

  for x in range(0,120):
    vMeas = megaind.get0_10In(INDADDR, VOLT_IN)
    if vMeas > vMax:
      vMax = vMeas

  return vMax / VDIV * VMUL

def OnKill(signum, frame):
  global RUN, INDADDR, HOT_OD, COLD
  RUN = False
  megaind.setOdPWM(INDADDR, HOT_OD, 0) #Hot Off
  megaind.setOdPWM(INDADDR, COLD_OD, 0) #Cold Off
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
  data['TiltName'] = Settings['BeerName']
  data['TiltColor'] = Settings['TiltColor']
  data['TiltEnabled'] = Settings['BeaconEnabled']
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
  ERRCOUNT += 1
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
  TOTERRORS = ERRCOUNT + IOT.ErrorCount
  try:
    if TOTERRORS > 0:
      megaind.setOdPWM(INDADDR, ERR_OD, 100)
    else:
      megaind.setOdPWM(INDADDR, ERR_OD, 0)

    CurrTime = datetime.datetime.now()
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
      data['TiltName'] = Settings['BeerName']
      data['TiltColor'] = Settings['TiltColor']
      data['TiltEnabled'] = Settings['BeaconEnabled']
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
    data['MainAmps'] = GetAmps(MAIN_IN)
    data['HotAmps'] = GetAmps(HOT_IN)
    data['ColdAmps'] = GetAmps(COLD_IN)
    data['MainVolts'] = GetVolts()
    #if ((loop % 10) == 0):
    data['ProbeTemp'] = librtd.get(RTDADDR, TEMP)
    data['CpuTemp'] = CPUTemperature().temperature
    data['HSTemp'] = librtd.get(RTDADDR, HS)
    kWh = (data['MainAmps'] * data['MainVolts'] * .000277) / 1000
    data['kWh'] += kWh
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1

  #Get IoT Hub Info
  if IOT.DoSend == True:
    data['IoTSending'] = True
  else:
    data['IoTSending'] = False
  data['LastLog'] = IOT.LastLog

  #Process Beacons
  try:
    if (loop == nextBeacon) and (Settings['BeaconEnabled']):
      color = data['TiltColor']
      data['TiltTemp'] = tilt.GetCalTemp(color)
      data['TiltGrav'] = tilt.GetCalGrav(color)
      #data['TiltTemp'] = tilt.GetTemp(color)
      #data['TiltGrav'] = tilt.GetGrav(color)
      data['LastBeacon'] = tilt.LastBeacon[color]
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1
  finally:
    if loop == nextBeacon:
      nextBeacon += Settings['BeaconFrequency']

  #Process Heating/Cooling Cycle
  try:
    if sinceLastCycle >= Settings['CycleFrequency']:
      if data['ProbeTemp'] < (float(Settings['TargetTemp']) - float(Settings['Hysteresis'])): #Too COLD_OD, turn on heat
        if data['HotState'] == 0:
          sinceLastCycle = 0 #Heat is off and will be toggled, reset sinceLastCycle to 0
          megaind.setOdPWM(INDADDR, COLD_OD, 0)
          megaind.setOdPWM(INDADDR, HOT_OD, 100)
          data['HotState'] = 1
          data['ColdState'] = 0
      elif data['ProbeTemp'] > (float(Settings['TargetTemp']) + float(Settings['Hysteresis'])): #Too HOT_OD, turn on cold
        if data['ColdState'] == 0:
          sinceLastCycle = 0 #Cold is off and will be toggled, reset sinceLastCycle to 0
          megaind.setOdPWM(INDADDR, COLD_OD, 100)
          megaind.setOdPWM(INDADDR, HOT_OD, 0)
          data['HotState'] = 0
          data['ColdState'] = 1
      else:
        if (data['ColdState'] == 1) or (data['HotState'] == 1):
          sinceLastCycle = 0 #Cold or hot is on and we are now in the Hysteresis band.  Shut them off
          megaind.setOdPWM(INDADDR, COLD_OD, 0)
          megaind.setOdPWM(INDADDR, HOT_OD, 0)
          data['HotState'] = 0
          data['ColdState'] = 0

  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1

  
  #Send Data to Log Analytics
  try:
    if loop == nextLog:
      if Debug:
        print("Logging %s to Azure:\r" % (color))
      payload = json.dumps(data)
      result = post_data(Settings['WorkspaceId'], Settings['WorkspaceKey'], payload, Settings['LogName'])
      if Debug:
        print("Logging %s to Azure: %i\r" % (color, result.status_code))
      if result.status_code != 200:
        WriteLog("Logging {} to Azure failed: {}".format(color, result.status_code))
      else:
        data['LastLog'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1
  finally:
    if loop == nextLog:
      nextLog += Settings['LogFrequency']
  
  #Reset Errors if instructed to
  try:
    if os.path.exists('/var/www/html/py/clear_logs'):
      ERRCOUNT = 0
      IOT.ErrorCount = 0
      TOTERRORS = 0
      if os.path.exists('/var/www/html/python_errors.log'):
        os.remove('/var/www/html/python_errors.log')
      if os.path.exists('/var/www/html/iot.log'):
        os.remove('/var/www/html/iot.log')
      os.remove('/var/www/html/py/clear_logs')
    if os.path.exists('/var/www/html/py/reset_error_counts'):
      ERRCOUNT = 0
      IOT.ErrorCount = 0
      TOTERRORS = 0
      os.remove('/var/www/html/py/reset_error_counts')
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1

  #Set Error Counts
  data['ControllerErrors'] = ERRCOUNT
  data['IoTErrors'] = IOT.ErrorCount
  data['TotalErrors'] = TOTERRORS

  #Write Data
  try:
    d = open('/var/www/html/py/data.json', 'w')
    json.dump(data, d)
    d.close()
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1
  finally:
    loop += 1
    sinceLastCycle += 1
  
  loopTime = (datetime.datetime.now() - CurrTime).total_seconds() * 1e3
  if loopTime < 1000:
    time.sleep((1000 - loopTime) * .001)

  try:
    if os.path.exists('/var/www/html/py/STOP'):
      WriteLog("STOP called from interface")
      RUN = False
      os.remove('/var/www/html/py/STOP')
  except Exception as e:
    WriteLog(e)
    ERRCOUNT += 1

tilt.Stop()
IOT.Stop()
megaind.setOdPWM(INDADDR, COLD_OD, 0)
megaind.setOdPWM(INDADDR, HOT_OD, 0)
megaind.setOdPWM(INDADDR, ERR_OD, 0)
megaind.setOdPWM(INDADDR, PUMP_OD, 0)
megaind.set0_10Out(INDADDR, VOLT_OUT, 0)
megaind.set0_10Out(INDADDR, MAIN_OUT, 0)
megaind.set0_10Out(INDADDR, COLD_OUT, 0)
megaind.set0_10Out(INDADDR, HOT_OUT, 0)

os._exit(ERRCOUNT)