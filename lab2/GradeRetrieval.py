#!/usr/bin/python3

"""
Echo Client and Server Classes

T. D. Todd
McMaster University

to create a Client: "python EchoClientServer.py -r client" 
to create a Server: "python EchoClientServer.py -r server" 

or you can import the module into another file, e.g., 
import EchoClientServer

"""

########################################################################

import socket
import argparse
import sys
import getpass
import hashlib

########################################################################
# Echo Server class
########################################################################

class Server:

    # Set the server hostname used to define the server socket address
    # binding. Note that 0.0.0.0 or "" serves as INADDR_ANY. i.e.,
    # bind to all local network interface addresses.
    HOSTNAME = "0.0.0.0"
##    HOSTNAME = "127.0.0.1"
    

    # Set the server port to bind the listen socket to.
    PORT = 50000

    RECV_BUFFER_SIZE = 1024
    MAX_CONNECTION_BACKLOG = 10
    
    MSG_ENCODING = "utf-8"

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    # AVG_COMMANDS = {"GMA":"MIDTERM","GL1A":"LAB 1","GL2A":"LAB 2","GL3A":"LAB 3","GL4A":"LAB 4"}

    def __init__(self):
        self.printData()
        self.create_listen_socket()
        self.process_connections_forever()

    def printData(self):
        self.midtermAverage = 0
        self.lab1Average = 0
        self.lab2Average = 0
        self.lab3Average = 0
        self.lab4Average = 0
        self.hashedlist = ['.']
        counter = 0
        with open("./course_grades_2021.csv","r")as file:
            print("Data read from the CSV file")
            # print(file.read())
            #[cleaned_line for cleaned_line in [line.strip() for line in file.readlines()] if cleaned_line != '']
            lines = file.readlines() #each row is an item inside one big list
            for line in lines:
                counter+=1
                line = line.split(',') #[,,,,,] become [][][]
                line = [i.strip() for i in line]
                #creation dictionary
                if counter>1:
                    self.hashedlist.append(self.hashed_ID_Pass(line[0],line[1]))
                if counter == 12:
                    self.midtermAverage = line[4]
                    self.lab1Average= line[5]
                    self.lab2Average=line[6]
                    self.lab3Average=line[7]
                    self.lab4Average=line[8]
        
    def hashed_ID_Pass(self,id_num,pwd):
        m = hashlib.sha256()
        m.update(id_num.encode('utf-8'))
        m.update(pwd.encode('utf-8'))
        return m.digest() 
            
    def getMidtermAverage(self):
        return str(self.midtermAverage)

    def getLabAverage(self,labno):
        if labno == 1:
            return self.lab1Average
        if labno == 2:
            return self.lab2Average
        if labno == 3:
            return self.lab3Average
        if labno == 4:
            return self.lab4Average

    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options. This allows us to reuse
            # the socket without waiting for any timeouts.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind(Server.SOCKET_ADDRESS)

            # Set socket to listen state.
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            
            # display output of csv file on server 
            print('\nData read from CSV File:\n')
            self.display_csv()

            print("\nListening for connections on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)
    
    def display_csv(self):
        filename = 'course_grades_2021.csv'
        file = open(filename,'r')
        data = [] 
        for line in file.readlines():
            print(line.rstrip('\n'))

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming
                # connections. When one is accepted, pass the new
                # (cloned) socket reference to the connection handler
                # function.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))

        while True:
            try:
                # Receive bytes over the TCP connection. This will block
                # until "at least 1 byte or more" is available.
                recvd_bytes = connection.recv(Server.RECV_BUFFER_SIZE)
            
                # If recv returns with zero bytes, the other end of the
                # TCP connection has closed (The other end is probably in
                # FIN WAIT 2 and we are in CLOSE WAIT.). If so, close the
                # server end of the connection and get the next client
                # connection.
                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break
                
                # Decode the received bytes back into strings. Then output
                # them.
                try:
                    recvd_str = recvd_bytes.decode(Server.MSG_ENCODING)
                except:
                    recvd_str = recvd_bytes

                print("Command received from client: ", recvd_str)

                #CALL FUNCTIONS
                if recvd_str == "GMA":
                    sentStr = self.getMidtermAverage()
                elif recvd_str == "GL1A":
                    sentStr = self.getLabAverage(1)
                elif recvd_str == "GL2A":
                    sentStr = self.getLabAverage(2)
                elif recvd_str == "GL3A":
                    sentStr = self.getLabAverage(3)
                elif recvd_str == "GL4A":
                    sentStr = self.getLabAverage(4)
                else:
                    if recvd_str in self.hashedlist:
                        #verified the identity
                        print("Correct password,record found")
                        index = self.hashedlist.index(recvd_str)
                        with open("./course_grades_2021.csv",'r')as file:
                            sentStr=list(file.readlines())[index]
                        
                    else:
                        print("Password Failure")
                        sentStr = "ID/Password Failure"



                connection.sendall(sentStr.encode(Server.MSG_ENCODING))

                # if recvd_bytes in AVG_COMMANDS.keys():
                #     print("Received command {} from client".format(recvd_bytes))

                
                # Send the received bytes back to the client.
                #connection.sendall(recvd_bytes)
                print("Sent: ", sentStr)

            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

########################################################################
# Echo Client class
########################################################################

class Client:

    # Set the server hostname to connect to. If the server and client
    # are running on the same machine, we can use the current
    # hostname.
    # SERVER_HOSTNAME = socket.gethostbyname('localhost')
#    SERVER_HOSTNAME = socket.gethostbyname('')
    # SERVER_HOSTNAME = '0.0.0.0'
##    SERVER_HOSTNAME = 'localhost'
    SERVER_HOSTNAME = '127.0.0.1'
    

    
    RECV_BUFFER_SIZE = 1024
    

    AVG_COMMANDS = {"GMA":"MIDTERM","GL1A":"LAB 1","GL2A":"LAB 2","GL3A":"LAB 3","GL4A":"LAB 4"}


    def __init__(self):
        self.get_socket()
        self.connect_to_server()
        self.send_console_input_forever()
        

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def get_console_input(self):
        self.flag = 0
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            self.input_text = input("Enter command (GMA,GL1A,GL2A,GL3A,GL4A,GG): ")
            print("Command Entered: ", self.input_text)
            # get grades input 
            if self.input_text == "GG":
                # ask for ID and password
                id_num = input("Enter ID: ")
                pwd = getpass.getpass()
                # hash ID and Passwrod
                self.input_text = self.hashed_ID_Pass(id_num, pwd)
                # print(self.flag)
                self.flag = 1
            if self.input_text != "":
                break

    def hashed_ID_Pass(self,id_num,pwd):
        m = hashlib.sha256()
        m.update(id_num.encode('utf-8'))
        m.update(pwd.encode('utf-8'))
        return m.digest()
        
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                self.connection_send()
                self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)
                
    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
            if self.flag == 1:
                self.socket.sendall(self.input_text)
            else:
                self.socket.sendall(self.input_text.encode(Server.MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            # Receive and print out text. The received bytes objects
            # must be decoded into string objects.
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            # recv will block if nothing is available. If we receive
            # zero bytes, the connection has been closed from the
            # other end. In that case, close the connection on this
            # end and exit.
            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)
            
            assignment = ""
            if self.input_text in list(Client.AVG_COMMANDS.keys()):
                assignment =  Client.AVG_COMMANDS.get(self.input_text) + " AVERAGE"
            else:
                assignment = "USER INFO"
            print("Fetching {} from Server: {}".format(assignment, recvd_bytes.decode(Server.MSG_ENCODING)))
            # print("Fetching {} average: {}".format(AVG_COMMANDS.get(self.input_text), recvd_bytes.decode(Server.MSG_ENCODING)))

        except Exception as msg:
            print(msg)
            sys.exit(1)

########################################################################
# Process command line arguments if this module is run directly.
########################################################################

# When the python interpreter runs this module directly (rather than
# importing it into another file) it sets the __name__ variable to a
# value of "__main__". If this file is imported from another module,
# then __name__ will be set to that module's name.

if __name__ == '__main__':
    roles = {'client': Client,'server': Server}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='server or client role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################






