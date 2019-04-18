import numpy as np
import argparse
import os, sys, time
from SCPI_socket import *

def parsing():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, help="Action to be performed")
    args = parser.parse_args()
    return args

dir = os.path.dirname(sys.argv[0]) + '/'
if dir == '/':
    dir = ''

ip = {}
ip['Box'] = '192.168.133.200'
ip['Bar'] = '192.168.133.201'

def write_number(fname, x):
    f = open(fname, 'w')
    f.write('{}\n'.format(x))
    f.close()

def communicate(cmd, rec_ip):
    s = SCPI_sock_connect(rec_ip)
    r = None
    if '?' == cmd[-1]:
    	r = SCPI_sock_query(s,cmd)
    else:
    	SCPI_sock_send(s, cmd)
    SCPI_sock_close(s)
    return r

if __name__ == '__main__':
    args = parsing()

    if args.action == 'halt':
        communicate('OUTP OFF', ip['Box'])
	communicate('OUTP OFF', ip['Bar'])
    elif args.action == 'light':
        communicate('OUTP ON', ip['Box'])
        communicate('OUTP ON', ip['Bar'])
    elif args.action == 'update':
	for k in ip.keys():
        	Vset = str(np.loadtxt(dir+k+'_user_set_voltage.txt', dtype=np.str))
		if Vset == 'OFF':
			communicate('OUTP OFF', ip[k])
			write_number(dir+k+'_read_voltage.txt', 'OFF')
			write_number(dir+k+'_read_current.txt', 'OFF')
		else:
        		Vread = float(communicate('VOLT?', ip[k]))

		        if float(Vset) != Vread:
		            	communicate('VOLT '+str(Vset), ip[k])
		            	time.sleep(0.1)
            			Vread = float(communicate('VOLT?', ip[k]))
            			if float(Vset) != Vread:
                			f = open(dir+'control.log', 'a+')
                			ln = time.asctime( time.localtime(time.time()) ) + '\n'
                			ln += k + ' voltage set failed. Vset={} Vread={}\n'.format(Vset, Vread)
                			f.write(ln)
                			f.close()

        		write_number(dir+k+'_read_voltage.txt', Vread)
			write_number(dir+k+'_read_current.txt', float(communicate('CURR?', ip[k])))
