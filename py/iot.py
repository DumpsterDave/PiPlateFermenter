from azure.iot.device import IoTHubDeviceClient
import json
import threading
import time

class IoT:
    Config = None
    Client = None
    Data = None
    DoSend = False
    DoReceive = False
    
    Sender = None

    def SendData(self):
        try:
            while self.DoSend:
                f = open('/var/www/html/py/data.json')
                self.Data = json.load(f)
                f.close()
                self.Client.send_message(json.dumps(self.Data))
                time.sleep(self.Config['LogFrequency'])
        except Exception as e:
            print("IoT: {}".format(e))
    
    def ReceiveData(self, message):
        
        if self.DoReceive:
            props = message.custom_properties
            for key in props.keys():
                self.Config[key] = props.get(key)
            d = open('/var/www/html/py/conf.json', 'w')
            json.dump(self.Config, d)
            d.close()
            r = open('/var/www/html/py/reload', 'w')
            r.close()
            

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
    