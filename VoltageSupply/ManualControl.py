from SCPI_socket import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('cmd', type=str, help='Command to send via SCPI')
parser.add_argument('--ip', type=str, default='192.168.133.200', help='IP adress of the device to control')
parser.add_argument('--port', type=int, default=5025, help='Port used to communication')
args = parser.parse_args()

s = SCPI_sock_connect(args.ip, args.port)

cmd = args.cmd
if '?' == cmd[-1]:
	r = SCPI_sock_query(s,cmd)
	print r
else:
	SCPI_sock_send(s, cmd)

SCPI_sock_close(s)
