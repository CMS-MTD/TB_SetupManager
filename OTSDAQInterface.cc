#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <string>
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <regex>
#include <map>
#include <fstream>


//LORE
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <fcntl.h>
#include <ctype.h>

using namespace std;


#define THIS_IP            "131.215.112.172"
#define COMMUNICATION_PORT "10001"             // the port for communicating with XDAQ
#define MAXBUFLEN          1492


//========================================================================================================================
// get sockaddr, IPv4 or IPv6:
// void *get_in_addr(struct sockaddr *sa)
// {
// 	if (sa->sa_family == AF_INET) {
// 		return &(((struct sockaddr_in*)sa)->sin_addr);
// 	}
//
// 	return &(((struct sockaddr_in6*)sa)->sin6_addr);
// }

string getIPAddress(){
	system("ifconfig | grep -A 1 eth0 | grep ine > .tmp_IP.txt");
	string line;
  ifstream myfile (".tmp_IP.txt");
  if ( !getline (myfile,line) ) {
		cout << "ifconfig error\n";
		exit(0);
	}
  myfile.close();

	string result;
  regex re("inet [0-9\\.]+");
  smatch match;
  if (regex_search(line, match, re)) {
    result = match.str(0);
		result = result.substr(5, result.length()-5);
  }
	else {
    cout << "IP adress not found" << endl;
		exit(0);
  }

	return result;
}

//========================================================================================================================
int makeSocket(const char* ip, const char* port, struct addrinfo*& addressInfo)
{
  cout << "Opening socket: " << ip << " port: " << port << endl;
	int socketId = 0;
	struct addrinfo hints, *servinfo, *p;
	int rv;

	memset(&hints, 0, sizeof hints);
	//    hints.ai_family   = AF_UNSPEC; // set to AF_INET to force IPv4
	hints.ai_family   = AF_INET; // set to AF_INET to force IPv4
	hints.ai_socktype = SOCK_DGRAM;
	if(ip == NULL)
		hints.ai_flags    = AI_PASSIVE; // use my IP

	if ((rv = getaddrinfo(ip, port, &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	// loop through all the results and bind to the first we can
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((socketId = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) {
			perror("listener: socket");
			continue;
		}

		if (bind(socketId, p->ai_addr, p->ai_addrlen) == -1) {
			close(socketId);
			perror("listener: bind");
			continue;
		}

		break;
	}

	if (p == NULL) {
		fprintf(stderr, "listener: failed to bind socket\n");
		return 2;
	}
	freeaddrinfo(servinfo);
	return socketId;
}

//========================================================================================================================
struct sockaddr_in setupSocketAddress(const char* ip, unsigned int port)
{
	//cout << __PRETTY_FUNCTION__ << endl;
	//network stuff
	struct sockaddr_in socketAddress;
	socketAddress.sin_family = AF_INET;// use IPv4 host byte order
	socketAddress.sin_port   = htons(port);// short, network byte order

	if(inet_aton(ip, &socketAddress.sin_addr) == 0)
	{
		cout << "FATAL: Invalid IP address " <<  ip << endl;
		exit(0);
	}

	memset(&(socketAddress.sin_zero), '\0', 8);// zero the rest of the struct
	return socketAddress;
}

//========================================================================================================================
int send(int toSocket, struct sockaddr_in& toAddress, const string& buffer)
{
	//   cout << "Socket Descriptor #: " << toSocket
	// 	    << " ip: " << hex << toAddress.sin_addr.s_addr << dec
	// 	    << " port: " << ntohs(toAddress.sin_port)
	// 	    << endl;
	if (sendto(toSocket, buffer.c_str(), buffer.size(), 0, (struct sockaddr *)&(toAddress), sizeof(sockaddr_in)) < (int)(buffer.size()))
	{
		cout << "Error writing buffer" << endl;
		return -1;
	}
	return 0;
}

//========================================================================================================================
int receiveAndAcknowledge(int fromSocket, struct sockaddr_in& fromAddress, string& buffer)
{
	struct timeval tv;
	tv.tv_sec = 0;
	tv.tv_usec = 10; //set timeout period for select()
	fd_set fileDescriptor;  //setup set for select()
	FD_ZERO(&fileDescriptor);
	FD_SET(fromSocket,&fileDescriptor);
	select(fromSocket+1, &fileDescriptor, 0, 0, &tv);

	if(FD_ISSET(fromSocket,&fileDescriptor))
	{
		string bufferS;
		//struct sockaddr_in fromAddress;
		socklen_t addressLength = sizeof(fromAddress);
		int nOfBytes;
		buffer.resize(MAXBUFLEN);
		if ((nOfBytes=recvfrom(fromSocket, &buffer[0], MAXBUFLEN, 0, (struct sockaddr *)&fromAddress, &addressLength)) == -1)
			return -1;

		// Confirm you've received the message by returning message to sender
		send(fromSocket, fromAddress, buffer);
		buffer.resize(nOfBytes);
		//char address[INET_ADDRSTRLEN];
		//inet_ntop(AF_INET, &(fromAddress.sin_addr), address, INET_ADDRSTRLEN);
		//unsigned long  fromIPAddress = fromAddress.sin_addr.s_addr;
		//unsigned short fromPort      = fromAddress.sin_port;

	}
	else
		return -1;

	return 0;
}

/////////////////////////////////////////////////////////////////////////
int main(int argc, char **argv){
	string this_IP = getIPAddress();

	cout << "Listening for connections" << endl;

	struct addrinfo* p;
	int communicationSocket = makeSocket(this_IP.c_str(),COMMUNICATION_PORT,p);
	struct sockaddr_in messageSender;

	string communicationBuffer;
	string currentRun;

	ofstream runFile;
	while(1)
	{
		communicationBuffer = "";
		if (receiveAndAcknowledge(communicationSocket, messageSender, communicationBuffer) >= 0){
			cout << "Received: " << communicationBuffer << endl;
			string cmd = "python /home/pi/TB_SetupManager/OTSDAQInterface.py \"";
			cmd = cmd + communicationBuffer + "\"";
			system(cmd.c_str());
		}

		usleep(1000);
	}

	close(communicationSocket);

	return 0;
}
