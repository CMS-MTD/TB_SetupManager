import numpy as np
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
max_play = 60.0 #mm

def write_number(fname, x):
    f = open(fname, 'w')
    f.write('{}\n'.format(x))
    f.close()

def calibrate(data_loc=calibration_data):
    print 'Reading calibration data from:', data_loc
    d = np.loadtxt(data_loc)
    out = np.polyfit(d[:,0], d[:,1],1)
    print 'Calibration result: {:1.2e} mm/step'.format(out[0])
    write_number(calibration, out[0])

def MoveSteps(step):
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

def Move_mm(x):
    mm_per_step = np.loadtxt(calibration)
    steps = int(float(x)/mm_per_step)
    MoveSteps(steps)

if __name__ == '__main__':
    args = parsing()

    if args.action == 'calibrate':
        calibrate()
    elif args.action == 'reset':
        Move_mm(-230)
        write_number(dir+'internal_state_position.txt', 0.0)
    elif args.action == 'update':
        i_pos = float(np.loadtxt(dir+'internal_state_position.txt'))
        if i_pos < 0:
            Move_mm(-max_play-1.0)
            write_number(dir+'internal_state_position.txt', 0.0)


        u_pos = float(np.loadtxt(dir+'user_set_position.txt'))
        if u_pos < 0:
            print 'Minimum position is 0. Moving the stave to 0.'
            Move_mm(-i_pos)
            write_number(dir+'user_set_position.txt', 0.0)
        elif u_pos > max_play:
            print 'Maximum position is', max_play, 'mm'
            print 'Moving stage to it.'
            Move_mm(max_play - i_pos)
            write_number(dir+'internal_state_position.txt', max_play)
            write_number(dir+'user_set_position.txt', max_play)
        else:
            dx = u_pos - i_pos
            if dx != 0:
                print 'Moving y-stage of {:.1f} mm'.format(dx)
                Move_mm(dx)
                print 'Done'
                write_number(dir+'internal_state_position.txt', u_pos)
