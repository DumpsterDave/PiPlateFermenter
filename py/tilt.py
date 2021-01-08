import bluetooth._bluetooth as bluez
import json
import queue

f = open('tilt.json')
Config = json.load(f)
f.close()

for color in Config['Colors']:
  