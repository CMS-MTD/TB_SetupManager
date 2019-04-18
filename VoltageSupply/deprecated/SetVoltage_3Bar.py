from SCPI_socket import *
import argparse

#parser = argparse.ArgumentParser()
#parser.add_argument('cmd', type=str, help='Command to send via SCPI')
#parser.add_argument('--ip', type=str, default='192.168.133.200', help='IP adress of the device to control')
#parser.add_argument('--port', type=int, default=5025, help='Port used to communication')
#args = parser.parse_args()

parser = argparse.ArgumentParser()
parser.add_argument('--v', type=str, default=1, help='desired voltage')
args = parser.parse_args()

s = SCPI_sock_connect("192.168.133.200", 5025)

r = SCPI_sock_query(s,"VOLT?")
print "query result: voltage ",r

SCPI_sock_send(s, "VOLT "+args.v)

i = SCPI_sock_query(s,"CURR?")
print "query result: current ", i

SCPI_sock_send(s, "CURR 0.001")

SCPI_sock_send(s, "OUTPut ON")

r = SCPI_sock_query(s,"VOLT?")
i = SCPI_sock_query(s,"CURR?")
print "voltage: ", r
print "current limit: ", i


#set to desired voltage
#set to desired current limit (0.001A) : "CURR 0.001"
#Turn on bias : "OUTPut ON"
#print out voltage, and current limit

#3-bar assembly has ip address 192.168.133.200
# 1bar assembly has ip address 192.168.133.201


