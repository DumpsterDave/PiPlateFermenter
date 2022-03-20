from azure.iot.device import IoTHubDeviceClient
from datetime import datetime
import json
import threading
import time


class IoT:
    Config = None
    Client = None
    Data = None
    DoSend = False
    DoReceive = False
    ErrorCount = 0
    
    Sender = None

    def SendData(self):
        while self.DoSend:
            try:
                f = open('/var/www/html/py/data.json')
                self.Data = json.load(f)
                f.close()
                self.Client.send_message(json.dumps(self.Data))
            except Exception as e:
                f = open('/var/www/html/iot.log', 'a')
                f.write("IoT[{}]: {} {}\n".format(24,datetime.now().isoformat(timespec='seconds'),e))
                f.close()
                self.ErrorCount += 1
            finally:
                time.sleep(self.Config['LogFrequency'])
    
    def ReceiveData(self, message):
        if self.DoReceive:
            try:
                props = message.custom_properties
                for key in props.keys():
                    self.Config[key] = props.get(key)
                d = open('/var/www/html/py/conf.json', 'w')
                json.dump(self.Config, d)
                d.close()
                r = open('/var/www/html/py/reload', 'w')
                r.close()
            except Exception as e:
                f = open('/var/www/html/iot.log', 'a')
                f.write("IoT[{}]: {} {}\n".format(24,datetime.now().isoformat(timespec='seconds'),e))
                f.close()
                self.ErrorCount += 1

    def __init__(self):
        f = open('/var/www/html/py/conf.json')
        self.Config = json.load(f)
        f.close()

        self.Client = IoTHubDeviceClient.create_from_connection_string(self.Config['IoTHubConnectionString'])
        self.Sender = threading.Thread(target=self.SendData)
        self.Client.on_message_received = self.ReceiveData

    def Start(self):
        self.DoSend = True
        self.DoReceive = True
        self.Sender.start()

    def Stop(self):
        self.DoSend = False
        self.DoReceive = False
    