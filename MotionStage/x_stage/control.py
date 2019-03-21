import numpy as np
import serial
import argparse
import os
import sys

def parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, help="Move right")
    args = parser.parse_args()
    return args

# dir = os.environ['HOME'] + '/TB_SetupManager/MotionStage/x_stage/'
dir = os.path.dirname(sys.argv[0]) + '/'
calibration_data = dir+'calibration_data.txt'
calibration = dir+'calibration.txt'
USB_port = '/dev/ttyUSB0'
max_play = 210. #mm

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

def MoveSteps(N):
    ser = serial.Serial(port=USB_port, baudrate=9600)
    ser.flush()
    ser.write('MR {}\r\n'.format(N))
    ser.close()

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
            print 'Maximum position is ', max_play
            print 'Moving stage to it.'
            Move_mm(max_play - i_pos)
            write_number(dir+'internal_state_position.txt', max_play)
            write_number(dir+'user_set_position.txt', max_play)
        else:
            dx = u_pos - i_pos
            if dx != 0:
                Move_mm(dx)
                write_number(dir+'internal_state_position.txt', u_pos)
