from datetime import datetime
import json
import requests
import sys
import threading
import time

class BrewFather:
  GravUnits = None
  Config = None
  DoSend = False
  ErrorCount = 0
  Sender = None
  Payload = None

  def __init__(self):
    self.RefreshConfig()
    self.Payload = {
      'name': self.Config['BeerName'],
      'temp': 0,
      'temp_unit': self.Config['TempUnits'].upper(),
      'temp_target': 0,
      'gravity': 0,
      'gravity_unit': self.GravUnits.upper(),
      'pressure': 0,
      'pressure_unit': 'PSI',
      'device_state': 'off',
      'report_source': 'SSB Fermenter'
    }
    self.Sender = threading.Thread(target=self.SendData)

  def RefreshConfig(self):
    f = open('/var/www/html/py/conf.json')
    self.Config = json.load(f)
    f.close()
    if (self.Config['GravUnits'] == 'brix' or self.Config['GravUnits'] == 'plato'):
      gravUnits = 'P'
    else:
      gravUnits = 'G'
    self.GravUnits = gravUnits

  def SendData(self):
    while True:
      try:
        self.RefreshConfig()
        f = open('/var/www/html/py/data.json')
        Data = json.load(f)
        f.close()

        if (self.Config['TempUnits'] == 'F'):
          self.Payload['temp'] = self.CtoF(Data['ProbeTemp'])
          self.Payload['temp_target'] = self.CtoF(Data['TargetTemp'])
        else:
          self.Payload['temp'] = Data['ProbeTemp']
          self.Payload['temp_target'] = Data['TargetTemp']
        if (self.GravUnits == 'P'):
          self.Payload['gravity'] = self.SGtoPlato(Data['TiltGrav'])
        else:
          self.Payload['gravity'] = Data['TiltGrav']
        self.Payload['pressure'] = Data['Pressure']
        if (Data['ColdState'] == 1):
          self.Payload['device_state'] = 'cooling'
        elif (Data['HotState'] == 1):
          self.Payload['device_state'] = 'heating'
        elif(Data['Status'] == 'OFF'):
          self.Payload['device_state'] = 'off'
        else:
          self.Payload['device_state'] = 'on'

        req = requests.post(self.Config['BrewfatherEndpoint'], json=self.Payload)
        if (req.status_code != 200):
          raise ConnectionError('Brewfather POST did not return 20')
        
        if (self.DoSend != True):
          break
      except Exception as e:
        f = open('/var/www/html/iot.log', 'a')
        f.write("BF[{}]: {} {}\n".format(sys.exc_info()[-1].tb_lineno,datetime.now().isoformat(timespec='seconds'),e))
        f.close()
        self.ErrorCount += 1
      finally:
        time.sleep(self.Config['LogFrequency'])

  def CtoF(temp):
    return ((temp * 9 / 5) + 32)

  def SGtoPlato(grav):
    return ((-616.868) + (1111.14 * grav) - (630.272 * grav^2) + (135.997 * grav^3))

  def Start(self):
    self.DoSend = True
    self.Sender.start()

  def Stop(self):
    self.DoSend = False