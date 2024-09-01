# Prints a proxmity read from the proximity sensor
# Requires:
# pip install adafruit-circuitpython-apds9960
# pip install board

import board
from adafruit_apds9960.apds9960 import APDS9960

i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_proximity = True

print(apds.proximity)