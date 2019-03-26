import serial
import argparse
import RPi.GPIO as GPIO
import time
import numpy as np


#x direction /dev/ttyUSB0
#z angle /dev/ttyUSB1

def parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("MR", type=int, help="Rotate")
    parser.add_argument("-P", "--port", type=str, default='/dev/ttyUSB1', help='port')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parsing()

    tot_mov = args.MR
    steps = 2000

    ser = serial.Serial(port=args.port, baudrate=9600)
    # ser.flush()
    # ser.write('MR {}\r\n'.format(tot_mov))
    # ser.flush()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    dwn_guard = GPIO.input(12)
    moved = 0
    while (tot_mov > 0 and moved < tot_mov and dwn_guard) or (tot_mov < 0 and tot_mov < moved):

        ser.flush()
        ser.write('MR {}\r\n'.format(np.sign(tot_mov)*steps))
        ser.flush()

        moved += np.sign(tot_mov)*steps

        dwn_guard = GPIO.input(12)
        time.sleep(0.01)

    print("stage moved")
    ser.close()
