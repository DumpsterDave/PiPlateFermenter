from datetime import datetime
import json
import requests
import sys
import threading
import time

class BrewFather:
  Config = None
  DoSend = False
  ErrorCount = 0
  Sender = None
  Payload = None

  def __init__(self):
    self.RefreshConfig()
    self.Payload = {
      'name': 'SSBFermenter',
      'beer': self.Config['BeerName'],
      'temp': 0,
      'temp_unit': 'C',
      'temp_target': 0,
      'gravity': 0,
      'gravity_unit': 'G',
      'pressure': 0,
      'pressure_unit': 'PSI',
      'device_state': 'off'
    }
    self.Sender = threading.Thread(target=self.SendData)

  def RefreshConfig(self):
    f = open('/var/www/html/py/conf.json')
    self.Config = json.load(f)
    f.close()

  def SendData(self):
    while True:
      try:
        self.RefreshConfig()
        f = open('/var/www/html/py/data.json')
        Data = json.load(f)
        f.close()
        self.Payload['temp'] = Data['ProbeTemp']
        self.Payload['temp_target'] = Data['TargetTemp']
        self.Payload['gravity'] = Data['TiltGrav']
        self.Payload['pressure'] = Data['Pressure']
        self.Payload['beer'] = self.Config['BeerName']
        if (Data['ColdState'] == 1):
          self.Payload['device_state'] = 'cooling'
        elif (Data['HotState'] == 1):
          self.Payload['device_state'] = 'heating'
        elif(Data['Status'] == 'OFF'):
          self.Payload['device_state'] = 'off'
        else:
          self.Payload['device_state'] = 'on'

        header = {'Content-Type': 'application/json'}

        req = requests.post(self.Config['BrewfatherEndpoint'], headers=header, json=self.Payload)
        if (req.status_code != 200):
          raise ConnectionError('Brewfather POST did not return 200')
        
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