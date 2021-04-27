#!/usr/bin/env python3

########################################################################
#
# GET File Transfer
#
# When the client connects to the server, it immediately sends a
# 1-byte GET command followed by the requested filename. The server
# checks for the GET and then transmits the file. The file transfer
# from the server is prepended by an 8 byte file size field. These
# formats are shown below.
#
# The server needs to have REMOTE_FILE_NAME defined as a text file
# that the client can request. The client will store the downloaded
# file using the filename LOCAL_FILE_NAME. This is so that you can run
# a server and client from the same directory without overwriting
# files.
#
########################################################################

import socket
import argparse
import threading
import sys
import time
import datetime
import os

########################################################################

# Define all of the packet protocol field lengths. See the
# corresponding packet formats below.
CMD_FIELD_LEN = 1 # 1 byte commands sent from the client.
FILE_SIZE_FIELD_LEN  = 8 # 8 byte file size field.

# Packet format when a GET command is sent from a client, asking for a
# file download:

# -------------------------------------------
# | 1 byte GET command  | ... file name ... |
# -------------------------------------------

# When a GET command is received by the server, it reads the file name
# then replies with the following response:

# -----------------------------------
# | 8 byte file size | ... file ... |
# -----------------------------------

# Define a dictionary of commands. The actual command field value must
# be a 1-byte integer. For now, we only define the "GET" command,
# which tells the server to send a file.

CMD = { 
    "get" : 1,
    "put" : 2,
    "list": 3,
    "bye": 4
 }

MSG_ENCODING = "utf-8"
    
########################################################################
# SERVER
########################################################################

class Server:

    HOSTNAME = "127.0.0.1"
    ALL_IF_HOSTNAME = "0.0.0.0"

    SDP_PORT = 30000 # file sharing service discovery port 
    PORT = 50000 # FSP
    RECV_SIZE = 1024
    BACKLOG = 5

    FILE_NOT_FOUND_MSG = "Error: Requested file is not available!"

    # This is the file that the client will request using a GET.
    # REMOTE_FILE_NAMES = ['remotefile.txt']
    # REMOTE_FILE_NAMES = os.listdir('remotefiles') # gets array of files in RFILE directory
    REMOTE_FILE_NAMES = os.listdir('C:/Users/sahaj/Desktop/lab3-dn files/remotefiles')
    # REMOTE_FILE_PATH = os.getcwd() +'\\remotefiles\\' # path to files 
    REMOTE_FILE_PATH = 'C:/Users/sahaj/Desktop/lab3-dn files/remotefiles/'

    MSG = "SID-ABI-SAHAJ's File Sharing Service"
    MSG_ENCODED = MSG.encode(MSG_ENCODING)


    def __init__(self):
        self.thread_list = []
        self.create_listen_socket()
        self.process_connections_forever()
        # tcp_thread = threading.Thread(target=self.process_connections_forever)
        # print("Starting serving thread: ", tcp_thread.name)
        # self.thread_list.append(tcp_thread)
        # tcp_thread.daemon = True
        # tcp_thread.start()
        # print("-" * 72)

    # Service discovery
    def service_announcement(self):
        self.create_socket_sd()
        self.receive_forever_sd()

    def create_socket_sd(self):
        try:
            # Create an IPv4 UDP socket.
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Get socket layer socket options.
            self.socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket_udp.bind( (Server.ALL_IF_HOSTNAME, Server.SDP_PORT) )
        except Exception as msg:
            print(msg)
            sys.exit(1)
    
    def receive_forever_sd(self):
        while True:
            try:                
                print(Server.MSG, "listening on SDP port {} ...".format(Server.SDP_PORT))
                recvd_bytes, address = self.socket_udp.recvfrom(Server.RECV_SIZE)

                print("Received: ", recvd_bytes.decode('utf-8'), " Address:", address)
            
                # Decode the received bytes back into strings.
                recvd_str = recvd_bytes.decode(MSG_ENCODING)

                # Check if the received packet contains a service scan
                # command.
                # if Server.SCAN_CMD in recvd_str:
                #     # Send the service advertisement message back to
                #     # the client.
                self.socket_udp.sendto(Server.MSG_ENCODED, address)
            except KeyboardInterrupt:
                print()
                sys.exit(1)

    def printFiles(self):
        print('Files stored in remote directory: ')
        for files in Server.REMOTE_FILE_NAMES:
            print(files)

    def create_listen_socket(self):
        try:
            # forever running UDP socket for service annoucement
            # self.service_announcement()
            # print('Listening on service discovery messages on SDP port {}'.format(Server.SDP_PORT))
            sdp_thread = threading.Thread(target=self.service_announcement)
            print("\nStarting serving thread: ", sdp_thread.name)
            self.thread_list.append(sdp_thread)
            sdp_thread.daemon = True
            sdp_thread.start()
            print("-" * 72)


            # Create the TCP server listen socket in the usual way.
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            # tcp_thread = thread.Thread(target=self.socket.listen(Server.BACKLOG))
            self.socket.listen(Server.BACKLOG)
            print("Listening for file sharing connections on port {} ...".format(Server.PORT))
            print('-'*72)

        except Exception as msg:
            print(msg)
            exit()

    def process_connections_forever(self):
        try:
            # sdp_thread = threading.Thread(target=self.service_announcement())
            # self.thread_list.append(sdp_thread)
            # sdp_thread.start()
            while True:               

                # self.connection_handler(self.socket.accept())
                new_client = self.socket.accept()

                # new client connected. Create new thread to process
                new_thread = threading.Thread(target=self.connection_handler,
                                              args=(new_client,))
                
                # Record the new thread.
                self.thread_list.append(new_thread)

                # Start the new thread running.
                print("Starting serving thread: ", new_thread.name)
                new_thread.daemon = True
                new_thread.start()
        
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            print("Closing server socket...")
            self.socket.close()
            sys.exit(1)

    def connection_handler(self, client):
        connection, address = client
        print("-" * 72)
        print("Connection received from {}.".format(address))


        while True:

            # recvd_bytes = connection.recv(Server.RECV_SIZE)

            # Read the command and see if it is a GET.
            cmd = int.from_bytes(connection.recv(CMD_FIELD_LEN), byteorder='big')
            print(cmd)

            if (cmd not in CMD.values()):
                # print("Closing {} client connection ... ".format(address))
                # connection.close()
                print('Incorrect command received!')
                # Break will exit the connection_handler and cause the
                # thread to finish.clear
                break


            if(cmd == CMD['bye']):
                print('Closing {} client connection ...'.format(address))
                print('-'*72)
                connection.close()
                break



            # if cmd != CMD["GET"]:
            #     print("GET command not received!")
            #     return


            elif (cmd == CMD['list']):
                # recvd_bytes = connection.recv(Server.RECV_SIZE)
                # recvd_str = recvd_bytes.decode(MSG_ENCODING)
                remoteFiles = Server.REMOTE_FILE_NAMES
                print(remoteFiles)
                remoteFiles_str = ''
                for rfile in remoteFiles:
                    remoteFiles_str += rfile + ' '
                remoteFiles_bytes = remoteFiles_str.encode(MSG_ENCODING)

                # list_bytes = [remoteFile.encode(MSG_ENCODING) for remoteFile in remoteFiles]
                # list_size_bytes = len(list_bytes)
                # list_size_field = list_size_bytes.to_bytes(FILE_SIZE_FIELD_LEN, byteorder='big')

                    # Create the packet to be sent with the header field.
                # pkt = file_size_field + file_bytes
                # print('Sending RLIST directory to client...')
                try:
                        # Send the packet to the connected client.
                    # for rfile in list_bytes:
                    #     connection.sendall(rfile)
                    connection.sendall(remoteFiles_bytes)
                        # print("Sent packet bytes: \n", pkt)
                    print("Sending FSD to client ... ")
                except socket.error:
                        # If the client has closed the connection, close the
                        # socket on this end.
                    print("Closing client connection ...")
                    connection.close()
                    return

            elif(cmd == CMD['put']):

                # filename_bytes = connection.recv(Server.RECV_SIZE)
                filename_size_bytes = connection.recv(FILE_SIZE_FIELD_LEN)
                filename_size = int.from_bytes(filename_size_bytes,byteorder='big')
                filename_bytes = connection.recv(filename_size)
                # filename_bytes = connection.recv(FILE_SIZE_FIELD_LEN)
                filename_str = filename_bytes.decode(MSG_ENCODING)
                print('filename size: ', filename_size)
                print('filename: {} received'.format(filename_str))
                
                file_type = filename_str.split('.')[1]
                

                # Read the file size field.
                file_size_bytes = connection.recv(FILE_SIZE_FIELD_LEN)
                if len(file_size_bytes) == 0:
                    connection.close()
                    return

                # Make sure that you interpret it in host byte order.
                file_size = int.from_bytes(file_size_bytes, byteorder='big')
                print('file size:', file_size)


                # Receive the file itself.
                recvd_bytes_total = bytearray()
                try:
                    # Keep doing recv until the entire file is downloaded. 
                    while len(recvd_bytes_total) < file_size:
                        recvd_bytes_total += connection.recv(Server.RECV_SIZE)

                    # Create a file using the received filename and store the
                    # data.
                    print("Received {} bytes. Creating file: {}" \
                        .format(len(recvd_bytes_total), filename_str)) 
                    
                    new_file_path = Server.REMOTE_FILE_PATH + filename_str
                    # print(new_file_path)

                    if (file_type == 'txt'):
                        with open(new_file_path, 'w') as f:
                            f.write(recvd_bytes_total.decode(MSG_ENCODING))
                    else:
                        with open(new_file_path, 'wb') as f:
                            f.write(recvd_bytes_total)
                    print('File successfully uploaded!\n')
                    # uploaded = 'complete'
                except KeyboardInterrupt:
                    print()
                    exit(1)
                # If the socket has been closed by the server, break out
                # and close it on this end.
                except socket.error:
                    print('SOCKET ERROR')
                    connection.close()


            elif (cmd == CMD['get']):
                    # The command is good. Now read and decode the requested
                    # filename.
                filename_bytes = connection.recv(Server.RECV_SIZE)
                filename_str = filename_bytes.decode(MSG_ENCODING)
                print(filename_str)
                file_path = Server.REMOTE_FILE_PATH + filename_str
                # print(file_path)


                    # Open the requested file and get set to send it to the
                    # client.
                file_type = filename_str.split('.')[1]
                print(file_type)
                print(file_path)
                try:
                    if(file_type == 'txt'):
                        file = open(file_path, 'r').read()
                        file_bytes = file.encode(MSG_ENCODING)
                    else:
                        file = open(file_path,'rb').read()
                        file_bytes = file
                except FileNotFoundError:
                    print(Server.FILE_NOT_FOUND_MSG)
                    connection.close()                   
                    return

                    # Encode the file contents into bytes, record its size and
                    # generate the file size field used for transmission.
                # file_bytes = file.encode(MSG_ENCODING)
                file_size_bytes = len(file_bytes)
                file_size_field = file_size_bytes.to_bytes(FILE_SIZE_FIELD_LEN, byteorder='big')

                    # Create the packet to be sent with the header field.
                pkt = file_size_field + file_bytes
                    
                try:
                        # Send the packet to the connected client.
                    connection.sendall(pkt)
                        # print("Sent packet bytes: \n", pkt)
                    print("Sending file: ", filename_str)
                except socket.error:
                        # If the client has closed the connection, close the
                        # socket on this end.
                    print("Closing client connection ...")
                    connection.close()
                    return

########################################################################
# CLIENT
########################################################################

class Client:

    RECV_SIZE = 10
    RECV_SIZE_SD = 1024
    # Define the local file name where the downloaded file will be
    # saved.

    # LOCAL_FILE_NAMES = os.listdir('localfiles') # array of all files in localfiles
    # LOCAL_FILE_PATH = os.getcwd() +'\\localfiles\\'

    LOCAL_FILE_NAMES = os.listdir('C:/Users/sahaj/Desktop/lab3-dn files/localfiles')
    # REMOTE_FILE_PATH = os.getcwd() +'\\remotefiles\\' # path to files 
    LOCAL_FILE_PATH = 'C:/Users/sahaj/Desktop/lab3-dn files/localfiles/'

    # Service discovery 
    BROADCAST_ADDRESS = "255.255.255.255"
    BROADCAST_PORT = 30000
    BROADCAST_ADDRESS_PORT = (BROADCAST_ADDRESS,BROADCAST_PORT)
    SCAN_CYCLES = 3
    SCAN_TIMEOUT = 3


    def __init__(self):
        # self.printLocalFiles()
        # self.get_console_input()
        self.send_console_input_forever()
        self.connected = 0
        # self.get_socket()
        # self.connect_to_server()
        # self.get_file()

    def tcp_connection(self):
        while self.connected ==1:
            self.get_socket()
            self.connect_to_server()
            self.send_console_input_forever()


    def get_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            exit()

    def connect_to_server(self):
        try:
            self.socket.connect((Server.HOSTNAME, Server.PORT))
        except Exception as msg:
            print(msg)
            exit()

    def socket_recv_size(self, length):
        bytes = self.socket.recv(length)
        if len(bytes) < length:
            self.socket.close()
            exit()
        return(bytes)
    
    def get_console_input(self):
        # In this version we keep prompting the user until a non-blank
        # line is entered.
        while True:
            print('\n'+'*'*50)
            self.input_text = input("--(scan, connect, llist, rlist, put, get)--\n Enter Command: ")
            try:
                    
                if (self.input_text == "scan"):
                    self.service_discovery()
                    
                elif (self.input_text.split()[0] == "get"):
                    if(len(self.input_text.split())<2):
                        print('ENTER FORMAT: get <filename>')
                        break

                    fetch_text = self.input_text.split()[1] 
                    if (fetch_text not in Server.REMOTE_FILE_NAMES):
                        print('File not in remote FSD!')
                        break
                    self.get_file(fetch_text)

                elif(self.input_text.split()[0] == "connect"):

                    # if(len(self.input_text.split())<3):
                    #     print('ENTER FORMAT: connect <IPADDR> <PORT>')
                    #     break
                    # elif (self.input_text.split()[1] != Server.HOSTNAME):
                    #     print('INVALID IP ADDRESS ENTERED')
                    #     break
                    # elif (int(self.input_text.split()[2])  != Server.PORT):
                    #     print('INVALID PORT ENTERED')
                    #     break
                    self.connected = 1
                    self.tcp_connection()
                
                elif (self.input_text.split()[0] == "put"):
                    if(len(self.input_text.split())<2):
                        print('ENTER FORMAT: put <filename>')
                        break

                    upload_text = self.input_text.split()[1] 
                    if (upload_text not in Client.LOCAL_FILE_NAMES):
                        print('File not in local directory!')
                        break
                    self.put_file(upload_text)
                
                elif(self.input_text == "llist"):
                    self.printLocalFiles()

                elif(self.input_text == "rlist"):
                    self.remote_list()
                
                elif(self.input_text =='bye'):
                    self.bye()
                
                elif(self.input_text not in CMD.keys()):
                    print('COMMAND NOT RECOGNIZED')
                    break

                if self.input_text != "":
                    break

            except IndexError: # no command entered
                break

    def bye(self):
        # convert bye in commands to bytes and send to server
        bye_field = CMD["bye"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        self.socket.sendall(bye_field)

        print('CLOSING CONNECTION')
        self.connected = 0
        # close client socket
        self.socket.close()
        sys.exit(1)
    


    # SERVICE DISCOVERY
    def service_discovery(self):
        self.get_socket_udp()
        self.scan_for_service()

    def get_socket_udp(self):
        try:
            # Service discovery done using UDP packets.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Arrange to send a broadcast service discovery packet.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Set the socket for a socket.timeout if a scanning recv
            # fails.
            self.socket.settimeout(Client.SCAN_TIMEOUT);
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def scan_for_service(self):
        # Collect our scan results in a list.
        scan_results = []
        SCAN_CMD = "SCAN"
        SCAN_CMD_ENCODED = SCAN_CMD.encode(MSG_ENCODING)
        # Repeat the scan procedure a preset number of times.
        for i in range(Client.SCAN_CYCLES):

            # Send a service discovery broadcast.
            print("Sending broadcast scan {}".format(i))            
            self.socket.sendto(SCAN_CMD_ENCODED, Client.BROADCAST_ADDRESS_PORT)
        
            while True:
                # Listen for service responses. So long as we keep
                # receiving responses, keep going. Timeout if none are
                # received and terminate the listening for this scan
                # cycle.
                try:
                    recvd_bytes, address = self.socket.recvfrom(Client.RECV_SIZE_SD)
                    recvd_msg = recvd_bytes.decode(MSG_ENCODING)

                    # Record only unique services that are found.
                    if (recvd_msg, address) not in scan_results:
                        scan_results.append((recvd_msg, address))
                        continue
                # If we timeout listening for a new response, we are
                # finished.
                except socket.timeout:
                    break

        # Output all of our scan results, if any.
        if scan_results:
            for result in scan_results:
                print(result)
        else:
            print("No services found.")


    
    def send_console_input_forever(self):
        while True:
            try:
                self.get_console_input()
                # self.connection_send()
                # self.connection_receive()
            except (KeyboardInterrupt, EOFError):
                print()
                print("Closing server connection ...")
                self.socket.close()
                sys.exit(1)

    def connection_send(self):
        try:
            # Send string objects over the connection. The string must
            # be encoded into bytes objects first.
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

            print("Received: ", recvd_bytes.decode(Server.MSG_ENCODING))

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def printLocalFiles(self):
        for files in Client.LOCAL_FILE_NAMES:
            print(files)

    def remote_list(self):
        
        # Create packet LIST field 
        rlist_field = CMD["list"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        # print(rlist_field)
        
        # send packet to server 
        self.socket.sendall(rlist_field)

        try:
            recvd_bytes = self.socket.recv(Client.RECV_SIZE_SD)

            # if len(recvd_bytes) == 0:
            #     print('Closing server connection ...')
            #     self.socket.close()
            #     sys.exit(1)
            # if len(file_size_bytes) == 0:
            #     self.socket.close()
            #     return
            
            print("FILES STORED IN FSD: ", recvd_bytes.decode(MSG_ENCODING))
        except Exception as msg:
            print(msg)
            sys.exit(1)

            
    def get_file(self, filename):

        # Create the packet GET field.
        get_field = CMD["get"].to_bytes(CMD_FIELD_LEN, byteorder='big')

        # Create the packet filename field.
        # filename_field = Server.REMOTE_FILE_NAME.encode(MSG_ENCODING)
        filename_field = filename.encode(MSG_ENCODING)

        # Create the packet.
        pkt = get_field + filename_field

        # Send the request packet to the server.
        self.socket.sendall(pkt)

        file_type = filename.split('.')[1]

        # Read the file size field.
        file_size_bytes = self.socket_recv_size(FILE_SIZE_FIELD_LEN)
        if len(file_size_bytes) == 0:
               self.socket.close()
               return

        # Make sure that you interpret it in host byte order.
        file_size = int.from_bytes(file_size_bytes, byteorder='big')
        print(file_size)

        # Receive the file itself. Initalize byte object
        recvd_bytes_total = bytearray()
        try:
            # Keep doing recv until the entire file is downloaded. 
            while len(recvd_bytes_total) < file_size:
                recvd_bytes_total += self.socket.recv(Client.RECV_SIZE)

            # Create a file using the received filename and store the
            # data.
            print("Received {} bytes. Creating file: {}" \
                  .format(len(recvd_bytes_total), filename)) #Client.LOCAL_FILE_NAME))

            # with open(Client.LOCAL_FILE_NAME, 'w') as f:
            #     f.write(recvd_bytes_total.decode(MSG_ENCODING))
            
            new_file_path = Client.LOCAL_FILE_PATH + filename
            print(new_file_path)
            if (file_type == 'txt'):
                with open(new_file_path, 'w') as f:
                    f.write(recvd_bytes_total.decode(MSG_ENCODING))
            else:
                with open(new_file_path, 'wb') as f:
                    f.write(recvd_bytes_total)
        except KeyboardInterrupt:
            print()
            exit(1)
        # If the socket has been closed by the server, break out
        # and close it on this end.
        except socket.error:
            self.socket.close()
    
    def put_file(self, filename):
    
                # The command is good. Now read and decode the requested
            # filename.
        put_field = CMD["put"].to_bytes(CMD_FIELD_LEN, byteorder='big')
        # encode filename
        filename_field = filename.encode(MSG_ENCODING)
        filename_size = len(filename_field)
        filename_size_field = filename_size.to_bytes(FILE_SIZE_FIELD_LEN,byteorder='big')

        # packet to send with put, size of filename, filename
        pkt = put_field + filename_size_field + filename_field
        #     3  + 13 + localfile.txt
        # self.socket.sendall(pkt)           

        # path of file in localfiles to be sent to FSD 
        file_path = Client.LOCAL_FILE_PATH + filename
        file_type = filename.split('.')[1]

        # open requested file and read contents 
        try: 
            if (file_type == 'txt'):
                file = open(file_path, 'r').read()
                file_bytes = file.encode(MSG_ENCODING)
            else:
                file = open(file_path,'rb').read()
                file_bytes = file

        except FileNotFoundError:
            print('LOCAL FILE NOT FOUND')
            return
        
        # size of file to bytes - 8 in len
        # file_bytes = file.encode(MSG_ENCODING)
        file_size_bytes = len(file_bytes)
        file_size_field = file_size_bytes.to_bytes(FILE_SIZE_FIELD_LEN, byteorder='big')
        
        send_total_bytes = bytearray()
        print('file_size_fiekd: ', len(file_size_field))
        # print('file_bytes: ', file_bytes)
        

        # pkt2 = put_field + file_size_field + file_bytes
        pkt2 = pkt + file_size_field + file_bytes

        # put_command + 13 + localfile.txt + 20 + 'this is a localfile'
        try:
                # Send the packet to the connected client.
            self.socket.sendall(pkt2)
                # print("Sent packet bytes: \n", pkt)
            print("Sending file: ", filename)
        # if keyboard interrupt --> cancel file upload
        except KeyboardInterrupt:
            print('FILE WAS NOT UPLOADED - CONNECTION CLOSE')
            connection.close()
        except socket.error:
                # If the client has closed the connection, close the
                # socket on this end.
            print("Closing client connection ...")
            connection.close()
            return
            
########################################################################

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






