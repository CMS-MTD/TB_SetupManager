import time
import board
import busio
from adafruit_htu21d import HTU21D
import sys

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = HTU21D(i2c)
f = open('/home/pi/TB_SetupManager/SensorsI2C/AdaUTH21DF/tmp_reading.txt', 'w')
f.write('%.0f\n' % time.time())
f.write("%0.1f\n" % sensor.temperature)
f.write("%0.1f\n" % sensor.relative_humidity)
f.close()
