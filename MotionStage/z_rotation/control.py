import numpy as np
import serial
import argparse
import os
import sys
import time
import RPi.GPIO as GPIO


def parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, help="Action to be performed")
    args = parser.parse_args()
    return args

# dir = os.environ['HOME'] + '/TB_SetupManager/MotionStage/x_stage/'
dir = os.path.dirname(sys.argv[0]) + '/'
if dir == '/':
    dir = ''

calibration_data = dir+'calibration_data.txt'
calibration = dir+'calibration.txt'
USB_port = '/dev/ttyUSB1'
min_play = -60. #deg
max_play = 90. #deg

def write_number(fname, x):
    f = open(fname, 'w')
    f.write('{}\n'.format(x))
    f.close()

def calibrate(data_loc=calibration_data):
    print 'Reading calibration data from:', data_loc
    d = np.loadtxt(data_loc)
    out = np.polyfit(d[:,0], d[:,1],1)
    print 'Calibration result: {:1.2e} deg/step'.format(out[0])
    write_number(calibration, out[0])

def MoveSteps(N, carefull = False):
    if not carefull:
        ser = serial.Serial(port=USB_port, baudrate=9600)
        ser.flush()
        ser.write('MR {}\r\n'.format(N))
        ser.close()
        time.sleep(0.2+abs(N)*16e-7)
    else:
        tot_mov = N
        steps = 2000

        ser = serial.Serial(port=USB_port, baudrate=9600)
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
            time.sleep(0.02)

        print("stage moved")
        if tot_mov > 0 and not dwn_guard:
            print "of a total of {} steps".format(moved)
        ser.close()

def Move_deg(x, carefull = False):
    deg_per_step = np.loadtxt(calibration)
    steps = -1*int(float(x)/deg_per_step)
    MoveSteps(steps, carefull)

def reset():
    Move_deg(-360, carefull=True)
    MoveSteps(-566000, False)
    write_number(dir+'internal_state_position.txt', 0.0)

if __name__ == '__main__':
    args = parsing()

    if args.action == 'calibrate':
        calibrate()
    elif args.action == 'reset':
        reset()
    elif args.action == 'update':
        i_pos = float(np.loadtxt(dir+'internal_state_position.txt'))
        if i_pos < min_play:
            reset()

        u_pos = float(np.loadtxt(dir+'user_set_position.txt'))
        if u_pos < min_play:
            print 'Minimum position is {} deg, moving the stage there.'.format(min_play)
            u_pos = min_play
            write_number(dir+'user_set_position.txt', min_play)
        elif u_pos > max_play:
            print 'Maximum position is {} deg, moving the stage there.'.format(max_play)
            u_pos = max_play
            write_number(dir+'user_set_position.txt', max_play)

        ddeg = u_pos - i_pos
        if ddeg != 0:
            print 'Rotating z-axis of {:.1f} deg'.format(ddeg)
            Move_deg(ddeg)
            print 'Done'
            write_number(dir+'internal_state_position.txt', u_pos)
