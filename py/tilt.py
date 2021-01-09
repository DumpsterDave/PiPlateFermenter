import blescan
import bluetooth._bluetooth as bluez
import json
import threading
import time


class Tilt:
    #Variables
    DEV_ID = 0
    UUIDS = {
        'a495bb10c5b14b44b5121370f02d74de' : 'Red',
        'a495bb20c5b14b44b5121370f02d74de' : 'Green',
        'a495bb30c5b14b44b5121370f02d74de' : 'Black',
        'a495bb40c5b14b44b5121370f02d74de' : 'Purple',
        'a495bb50c5b14b44b5121370f02d74de' : 'Orange',
        'a495bb60c5b14b44b5121370f02d74de' : 'Blue',
        'a495bb70c5b14b44b5121370f02d74de' : 'Yellow',
        'a495bb80c5b14b44b5121370f02d74de' : 'Pink'
    }
    Temp = {
        "Black" : 0.0,
        "Blue" : 0.0,
        "Green": 0.0,
        "Orange" : 0.0,
        "Pink" : 0.0,
        "Purple" : 0.0,
        "Red" : 0.0,
        "Yellow" : 0.0
    }
    Grav = {
        "Black" : 0.0,
        "Blue" : 0.0,
        "Green": 0.0,
        "Orange" : 0.0,
        "Pink" : 0.0,
        "Purple" : 0.0,
        "Red" : 0.0,
        "Yellow" : 0.0
    }
    Config = None
    Scanner = None
    Debug = False
    DoScan = True

    def __init__(self, Debug=False):
        #Load Settings
        f = open('tilt.json')
        self.Config = json.load(f)
        f.close()
        self.Debug = Debug
        self.Scanner = threading.Thread(target=self.BleScan)

    def BleScan(self):
        try:
            sock = bluez.hci_open_dev(self.DEV_ID)

            blescan.hci_le_set_scan_parameters(sock)
            blescan.hci_enable_le_scan(sock)
            while self.DoScan:
                returnedList = blescan.parse_events(sock, 10)
                for beacon in returnedList:
                    parts = beacon.split(",")
                    color = self.UUIDS.get(parts[1])
                    if color != None:
                        self.Temp[color] = (float(parts[2]) - 32) / 1.8
                        self.Grav[color] = float(parts[3]) / 1000
                    time.sleep(1)
        except Exception as e:
            print("BleScan: {}".format(e))

    def GetCalTemp(self, Color):
        m = (float(self.Config[Color]["TempHighRef"]) - float(self.Config[Color]["TempLowRef"]))/(float(self.Config[Color]["TempHigh"]) - float(self.Config[Color]["TempLow"]))
        b = float(self.Config[Color]["TempHighRef"]) - m * float(self.Config[Color]["TempHigh"])
        return m * self.Temp[Color] + b

    def GetCalGrav(self, Color):
        m = (float(self.Config[Color]["GravHighRef"]) - float(self.Config[Color]["GravLowRef"]))/(float(self.Config[Color]["GravHigh"]) - float(self.Config[Color]["GravLow"]))
        b = float(self.Config[Color]["GravHighRef"]) - m * float(self.Config[Color]["GravHigh"])
        return m * self.Grav[Color] + b

    def GetTemp(self, Color):
        return self.Temp[Color]

    def GetGrav(self, Color):
        return self.Grav[Color]

    def Start(self):
        self.DoScan = True
        self.Scanner.start()

    def Stop(self):
        self.DoScan = False