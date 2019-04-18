import sys, os
import subprocess
import numpy as np
import time

data_dir = os.environ['HOME'] + '/data/201904_FNALTB'

active_systems = [
	'x_stage',
#	'y_stage',
	'z_rotation',
	'AdaUTH21DF', #Box temp and humidity sensor
	'VoltageSupply'
]

def write_conditions_file(conditions, run_number):
	f = open(data_dir+'/Run{}_conditions.txt'.format(run_number), 'w')
	for k, v in conditions.iteritems():
		f.write(k + ': ' + str(v) + '\n')
	f.close()



if __name__ == '__main__':
	basedir = os.path.dirname(sys.argv[0])
	msg = sys.argv[1]

	if not os.path.isdir(data_dir):
		os.system('mkdir -p '+ data_dir)

	if 'start' in msg:

		conditions = {}

		if 'x_stage' in active_systems:
			cmd = 'python {}/MotionStage/x_stage/control.py update'.format(basedir)
			os.system(cmd)
			aux = np.loadtxt(basedir+'/MotionStage/x_stage/internal_state_position.txt')
			conditions['x_stage'] = aux

		if 'y_stage' in active_systems:
			cmd = 'python {}/MotionStage/y_stage/control.py update'.format(basedir)
			os.system(cmd)
			aux = np.loadtxt(basedir+'/MotionStage/y_stage/internal_state_position.txt')
			conditions['y_stage'] = aux

		if 'z_rotation' in active_systems:
			cmd = 'python {}/MotionStage/z_rotation/control.py update'.format(basedir)
			os.system(cmd)
			aux = np.loadtxt(basedir+'/MotionStage/z_rotation/internal_state_position.txt')
			conditions['z_rotation'] = aux

		if 'AdaUTH21DF' in active_systems:
			cmd = 'python3 {}/SensorsI2C/AdaUTH21DF/ReadTempHum_AdaUTH21DF.py'.format(basedir)
			os.system(cmd)
			aux = np.loadtxt(basedir+'/SensorsI2C/AdaUTH21DF/tmp_reading.txt')
			if time.time() - aux[0] < 5:
				conditions['BoxTemp'] = aux[1]
				conditions['BoxHum'] = aux[2]

		if 'VoltageSupply' in active_systems:
			cmd = 'python {}/VoltageSupply/control.py update'.format(basedir)
			os.system(cmd)
			for k in ['Bar', 'Box']:
				conditions[k+'Voltage'] = str(np.loadtxt(basedir+'/VoltageSupply/{}_read_voltage.txt'.format(k), dtype=np.str))
				conditions[k+'Current'] = str(np.loadtxt(basedir+'/VoltageSupply/{}_read_current.txt'.format(k), dtype=np.str))


		write_conditions_file(conditions, int(msg[7:]))
