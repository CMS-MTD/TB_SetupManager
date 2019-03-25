import RPi.GPIO as GPIO
import argparse
import time
import numpy as np

def parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("MR", type=int, help="Move up")

    args = parser.parse_args()
    return args

def MoveStep(step):
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(5, GPIO.OUT) #step
    GPIO.setup(6, GPIO.OUT) # Direction
    GPIO.setup(4, GPIO.OUT)  #enable
    GPIO.setup(17, GPIO.OUT)  #ms1
    GPIO.setup(27, GPIO.OUT)  #ms2
    GPIO.setup(22, GPIO.OUT)  #ms3

    #End of line switches
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.output(4, 0)
    if step > 0:
        GPIO.output(6, 0)
    else:
        GPIO.output(6, 1)

    GPIO.output(17, 0)
    GPIO.output(27, 0)
    GPIO.output(22, 0)

    for x in range (0, np.abs(step)):
        dwn_guard = GPIO.input(20)
        up_guard = GPIO.input(16)
        if (not dwn_guard and step<0) or (not up_guard and step>0):
            # print '{} {}'.format(dwn_guard, up_guard)
            break

        GPIO.output(5, 1)
        time.sleep(0.001)
        GPIO.output(5, 0)
        time.sleep(0.001)
    # print 'Done'
    GPIO.cleanup()


if __name__ == '__main__':
    args = parsing()
    MoveStep(args.MR)
