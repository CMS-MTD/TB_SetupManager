#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <string>
#include <iostream>
#include <cstring>
#include <cstdlib>
#include <vector>
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


#define THIS_IP            "131.215.112.172"
#define COMMUNICATION_PORT "10003"             // the port on ZedBoard for communicating with XDAQ
#define STREAMING_PORT     "10001"             // the port on ZedBoard for streaming to XDAQ
#define DESTINATION_IP     "131.215.112.188"  // the IP for the destination of the datastream
#define DESTINATION_PORT   10003              // the port for the destination of the datastream 47003
#define MAXBUFLEN          1492


//========================================================================================================================
// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
	if (sa->sa_family == AF_INET) {
		return &(((struct sockaddr_in*)sa)->sin_addr);
	}

	return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

//========================================================================================================================
int makeSocket(const char* ip, const char* port, struct addrinfo*& addressInfo)
{
  std::cout << __PRETTY_FUNCTION__ << "Opening socket: " << ip << " port: " << port << std::endl;
	int socketId = 0;
	struct addrinfo hints, *servinfo, *p;
	//int sendSockfd=0;
	int rv;
	//int numbytes;
	//struct sockaddr_storage their_addr;
	//char buff[MAXBUFLEN];
	//socklen_t addr_len;
	//char s[INET6_ADDRSTRLEN];

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
	//std::cout << __PRETTY_FUNCTION__ << std::endl;
	//network stuff
	struct sockaddr_in socketAddress;
	socketAddress.sin_family = AF_INET;// use IPv4 host byte order
	socketAddress.sin_port   = htons(port);// short, network byte order

	if(inet_aton(ip, &socketAddress.sin_addr) == 0)
	{
		std::cout << "FATAL: Invalid IP address " <<  ip << std::endl;
		exit(0);
	}

	memset(&(socketAddress.sin_zero), '\0', 8);// zero the rest of the struct
	return socketAddress;
}

//========================================================================================================================
int send(int toSocket, struct sockaddr_in& toAddress, const std::string& buffer)
{
	//   std::cout << "Socket Descriptor #: " << toSocket
	// 	    << " ip: " << std::hex << toAddress.sin_addr.s_addr << std::dec
	// 	    << " port: " << ntohs(toAddress.sin_port)
	// 	    << std::endl;
	if (sendto(toSocket, buffer.c_str(), buffer.size(), 0, (struct sockaddr *)&(toAddress), sizeof(sockaddr_in)) < (int)(buffer.size()))
	{
		std::cout << "Error writing buffer" << std::endl;
		return -1;
	}
	return 0;
}

//========================================================================================================================
int receiveAndAcknowledge(int fromSocket, struct sockaddr_in& fromAddress, std::string& buffer)
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
		std::string bufferS;
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

	std::cout << "Running Timing crappy stuff :)!" << std::endl;


	//LORE
	/////////////////////
	// Bind UDP socket //
	/////////////////////

	//sendSockfd = makeSocket(string("localhost").c_str(),myport,p);

	//struct addrinfo hints, *servinfo;
	struct addrinfo* p;

	int communicationSocket              = makeSocket(THIS_IP,COMMUNICATION_PORT,p);

	//int streamingSocket                  = makeSocket(THIS_IP,STREAMING_PORT,p);
	//struct sockaddr_in streamingReceiver = setupSocketAddress(DESTINATION_IP, DESTINATION_PORT);

	struct sockaddr_in messageSender;

	std::string communicationBuffer;
	//unsigned int data_buffer[32];
	//END LORE

	//LORE
	std::string currentRun;
	//bool running = false;

	std::ofstream runFile;
	while(1)
	{
		communicationBuffer = "";
		if (receiveAndAcknowledge(communicationSocket, messageSender, communicationBuffer) >= 0){
			std::cout << "Received: " << communicationBuffer << std::endl;

			if (communicationBuffer.substr(0,5) == "START")
			{
				currentRun = communicationBuffer.substr(6,communicationBuffer.length()-6);
				//	running     = true;
				runFile.open("/tmp/RunFile.txt");
				runFile << "start";
				runFile.close();
				std::string fileName = "/data/DT5742/DT5742_RAW_Run" +  currentRun + ".dat";				
				std::string command = "cd; cd Desktop/adafruit_sensors; adafruit_sensors";

				system(command.c_str());
				std::cout << "Run " << currentRun << " started!" << std::endl;
			}
			else if (communicationBuffer == "STOP")
			{
			  //running = false;
				runFile.open("/tmp/RunFile.txt");
				runFile << "stop";
				runFile.close();

				std::cout << "Run " << currentRun << " stopped!" << std::endl;
			}
			else if (communicationBuffer == "PAUSE")
			{
			  //running = false;
			}
			else if (communicationBuffer == "RESUME")
			{
			  //running = true;
			}
			else if (communicationBuffer == "CONFIGURE")
			{
			  std::cout << "Configuring...don't need to do anything.\n";
			}
		}

		// if(running)
		// {
		// 	std::cout << "I am running!" << std::endl;
		// 	usleep(1000000);

		// }
		usleep(1000);
	}

	// Clean up and exit
	close(communicationSocket);
	//close(streamingSocket);
	//LORE

	return 0;
}
