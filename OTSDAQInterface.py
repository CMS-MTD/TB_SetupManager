import sys, os
import numpy as np

data_dir = os.environ['HOME'] + '/data/test'

active_systems = [
	'x_stage',
	'y_stage'
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

	if 'START' in msg:

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

		write_conditions_file(conditions, int(msg[6:]))
