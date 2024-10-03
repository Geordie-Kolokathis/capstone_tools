import argparse
import board
import time
import digitalio
from adafruit_apds9960.apds9960 import APDS9960

# Set up argparse to take output_dir as an input argument
parser = argparse.ArgumentParser(description='Read sensor data and save to file.')
parser.add_argument('--output_dir', type=str, default='output', help='Directory to save the sensor data files.')
args = parser.parse_args()

# Initialize the sensor
i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_proximity = True
start_time = time.gmtime()
current_time = time.strftime("%H:%M:%S", start_time)
sensor_name = 'adps9960'

# Open the file for writing sensor data
with open(f"{args.output_dir}/{sensor_name}_{current_time}.txt", 'a') as file:
    print(f"Writing sensor data to {args.output_dir}/{sensor_name}_{current_time}.txt")
    while True:
        time.sleep(0.01)
        file.write(str(apds.proximity) + ';' + time.strftime("%D %T", time.gmtime()) + '\n')
