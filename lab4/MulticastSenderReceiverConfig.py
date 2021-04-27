#!/usr/bin/env python3

########################################################################

import socket
import argparse
import sys
import time
import struct
import threading
import json
#from pynput import keyboard
# global end_t
# end_t = 0



########################################################################

# Read in the config.py file to set various addresses and ports.
#from config import *
CMD_FIELD_LEN = 1
FILE_SIZE_FIELD_LEN = 8

CMD = {
    "getdir":1,
    "makeroom":2,
    "deleteroom":3,
    "bye":4,
}


########################################################################
# Broadcast Server class
########################################################################

class Sender:

    # HOSTNAME = socket.gethostbyname('')
    HOSTNAME = 'localhost'
    CDP_PORT = 50000
    BACKLOG = 5

    TIMEOUT = 2
    RECV_SIZE = 256
    
    MSG_ENCODING = "utf-8"
    # MESSAGE =  HOSTNAME + "multicast beacon: "
    MESSAGE = "Hello from " 
    MESSAGE_ENCODED = MESSAGE.encode('utf-8')

    # TTL = 1 # Hops
    # TTL_SIZE = 1 # Bytes
    # TTL_BYTE = TTL.to_bytes(TTL_SIZE, byteorder='big')
    # OR: TTL_BYTE = struct.pack('B', TTL)

    #chatroomDict = {}

    def __init__(self):
        self.connected = 0
        self.chatroomDict = {}
        self.thread_list = []
        self.create_listen_socket()
        self.process_connections_forever()
        #self.send_messages_forever()

    # def getDict(self,dic):
    #     print(dic.items())
    #     return dic.items()


    def create_listen_socket(self):
        try:
            #create TCP server listen socket

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Sender.HOSTNAME, Sender.CDP_PORT))
            # tcp_thread = thread.Thread(target=self.socket.listen(Server.BACKLOG))
            self.socket.listen(Sender.BACKLOG)
            print("WELCOME TO THE CRDS \nListening for TCP connections on CDP Port {} ...".format(Sender.CDP_PORT))
            print('-'*72)

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_handler(self,client):
        connection,address = client
        while True:
            #read the command sent from client to server
             cmd = int.from_bytes(connection.recv(CMD_FIELD_LEN), byteorder='big')
             #print(cmd)
             if (cmd not in CMD.values()):
                 print('Incorrect command received')
                 break
                
             if (cmd==CMD['bye']):
                 print('Closing {} client connection...'.format(address))
                 print('-'*72)
                 connection.close()
                 break

             elif(cmd == CMD['getdir']):
                 try:
                     #print("in the server")
                     dicttoSend = json.dumps(self.chatroomDict)
                     chatroomDict = dicttoSend.encode(Sender.MSG_ENCODING)
                     connection.sendall(chatroomDict)
                     print("Sending dictionary")
                 except socket.error:
                     print("Closing client connection...")
                     connection.close()
                     return

             elif(cmd == CMD['makeroom']):
                #decode message from client
                 #print("decoding message")
                 room_bytes = connection.recv(Sender.RECV_SIZE)
                 room_str = room_bytes.decode(Sender.MSG_ENCODING)
                 #print(room_str)
                


                 #check address/port combination is unique
                 
               
                 #print(list(self.chatroomDict.values()))
                 #print("this ist the length",len(self.chatroomDict))
                 if len(self.chatroomDict)>0:
                     for value in list(self.chatroomDict.values()):
                         #print("inside for loop")
                         if value!= (room_str.split(",")[1],room_str.split(",")[2]):
                             self.chatroomDict[room_str.split(",")[0]] = (room_str.split(",")[1],room_str.split(",")[2])
                         else:
                             print("address/port already exits")
                 else:
                     self.chatroomDict[room_str.split(",")[0]] = (room_str.split(",")[1],room_str.split(",")[2])

                 

             elif(cmd==CMD['deleteroom']):
                 #print("Inside delete function")
                 deleteroom_bytes = connection.recv(Sender.RECV_SIZE)
                 deleteroom_str = deleteroom_bytes.decode(Sender.MSG_ENCODING)
                 print(deleteroom_str)
                 print(self.chatroomDict)
                 self.chatroomDict.pop(deleteroom_str)
                 #print("POPPED OFF")
                 print(self.chatroomDict)
                 



             elif (cmd==CMD['bye']):
                 print("CLOSING CONNECTION")
                 #closing client connection to server but not server socket as its still listening
                 connection.close()
                 break



    def process_connections_forever(self):
        try:
            while True:
                new_client = self.socket.accept()
                new_thread = threading.Thread(target=self.connection_handler,args=(new_client,))
                self.thread_list.append(new_thread)
                #print("Starting serving thread:", new_thread.name)
                print("Connected to the client")

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


########################################################################
# Echo Receiver class
########################################################################

class Receiver:

    RECV_SIZE = 256
    MSG_ENCODING = 'utf-8'
    TTL = 1 # Hops
    TTL_SIZE = 1 # Bytes
    TTL_BYTE = TTL.to_bytes(TTL_SIZE, byteorder='big')
    TIMEOUT = 2

    def __init__(self):
        self.userName = ""
        self.chatroomName = ""
        self.flag = 0
        self.chatroomInfo = {}
        self.thread_list = []
        self.get_console_input()
        


    def tcp_connection(self):
        if self.connected ==1:
            self.get_socket()
            self.connect_to_server()
            #self.send_console_input_forever()

    def get_socket(self):
        try:
            #create TCP socket
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except Exception as msg:
            print(msg)
            exit()

    def connect_to_server(self):
        try:
            #create TCP connection
            self.socket.connect((Sender.HOSTNAME, Sender.CDP_PORT))
        except Exception as msg:
            print(msg)
            exit()


    def getdir(self):
        #print("inside getdir")
        #create packet and send to server
        getdir_field = CMD["getdir"].to_bytes(CMD_FIELD_LEN,byteorder='big')
        self.socket.sendall(getdir_field)
        try:
            recvd_bytes = self.socket.recv(Receiver.RECV_SIZE)
            json_str = recvd_bytes.decode(Receiver.MSG_ENCODING)
            #print(json.loads(json_str))
            #print(type(json.loads(json_str)))
            test_dict = json.loads(json_str)
            self.chatroomInfo = dict(list(test_dict.items()))
            print(self.chatroomInfo)
            
            
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def makeroom(self,roomName,address,port):
        makeroom_field = CMD["makeroom"].to_bytes(CMD_FIELD_LEN,byteorder='big')
        roomName = roomName + ","
        roomNameField = roomName.encode(Receiver.MSG_ENCODING)
        address = address + ","
        addressField = address.encode(Receiver.MSG_ENCODING)
        portField = port.encode(Receiver.MSG_ENCODING)
        pkt = makeroom_field + roomNameField + addressField + portField
        #print("sending packet")
        self.socket.sendall(pkt)


    def send_messages_forever(self,MULTICAST_ADDRESS,MULTICAST_PORT):
        try:
            while True:
                self.chat_text = input()
                MULTICAST_PORT = int(MULTICAST_PORT)
                MULTICAST_ADDRESS_PORT = (MULTICAST_ADDRESS, MULTICAST_PORT)
                if self.chat_text == "~]" :
                    #send message to receive socket to signal it to finish
                    killMsg = "Sender thread closing".encode(Receiver.MSG_ENCODING)
                    self.socket_udp.sendto(killMsg,MULTICAST_ADDRESS_PORT)
                    return
                nameField = self.userName.encode(Receiver.MSG_ENCODING)
                dashField = ":".encode(Receiver.MSG_ENCODING)
                textField = self.chat_text.encode(Receiver.MSG_ENCODING)
                pkt = nameField + dashField + textField
                self.socket_udp.sendto(pkt,MULTICAST_ADDRESS_PORT)
                time.sleep(Sender.TIMEOUT)
        except KeyboardInterrupt:
            #print("There has been an error",msg)
            print("exiting")
            return


    def receive_forever(self):
        while True:
            try:
                data, address_port = self.socket_r.recvfrom(Receiver.RECV_SIZE)
                address, port = address_port
                if data.decode('utf-8') == "Sender thread closing":
                    #print("Closing receive thread")
                    return
                print("\n")
                print(data.decode('utf-8'))
            # except Exception as msg:
            #     print("There has been an error",msg)
            #     #sys.exit(1)
            except KeyboardInterrupt:
                print("exiting")
                return
    
    def deleteroomFunc(self,room):
        delete_field = CMD['deleteroom'].to_bytes(CMD_FIELD_LEN,byteorder='big')
        room_field = room.encode(Receiver.MSG_ENCODING)
        pkt = delete_field + room_field
        self.socket.sendall(pkt)
          

    def bye(self):
        bye_field = CMD['bye'].to_bytes(CMD_FIELD_LEN,byteorder='big')
        self.socket.sendall(bye_field)
        print("Closing connection to the CRDS")
        self.connected = 0
        #closing TCP socket and cannot do self.socket functions
        self.socket.close()
        #sys.exit(1)

    def chat(self):
        #print("Inside chat function")
        #find multicast ip address and port from local dictionary 
        MULTICAST_ADDRESS,MULTICAST_PORT = self.chatroomInfo[self.chatroomName]
        #create udp send socket
        try:
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, Receiver.TTL_BYTE)
            #print("Create the first socket")
        except Exception as msg:
            print(msg)

    #create udp receive socket and multicast group request
        try:
            self.socket_r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            MULTICAST_PORT = int(MULTICAST_PORT)
            self.socket_r.bind((MULTICAST_ADDRESS,MULTICAST_PORT))
            multicast_group_bytes = socket.inet_aton(MULTICAST_ADDRESS)
            RX_IFACE_ADDRESS = "0.0.0.0"
            multicast_if_bytes = socket.inet_aton(RX_IFACE_ADDRESS)
            print("before multicast request")
            multicast_request = multicast_group_bytes + multicast_if_bytes
            self.socket_r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
            print("created the second socket")
        except Exception as msg:
            print (msg)

        #change command prompt
        print('\n'+'*'*50)
        print("Entering chatroom")

        # #Create listener thread to listen for ctrl key
        # def pass_to_thread(self,key):
        #     print(key.char)

        # def dummyFunction(self):
        #     return False

        # h = keyboard.Listener(on_press = pass_to_thread, on_release = dummyFunction)
        # #h.daemon = True
        # self.thread_list.append(h)
        # h.start()





        #Create UDP thread 
        udp_thread_send = threading.Thread(target=self.send_messages_forever,args=(MULTICAST_ADDRESS,MULTICAST_PORT))
        self.thread_list.append(udp_thread_send)
        #udp_thread_send.daemon = True
        udp_thread_send.start()
    

        #create UDP thread 
        udp_thread_receive = threading.Thread(target=self.receive_forever)
        self.thread_list.append(udp_thread_receive)
        #udp_thread_receive.daemon = True
        udp_thread_receive.start()

        #set flag back to zero and go back to console_input
        udp_thread_send.join()
        udp_thread_receive.join()
        self.socket_udp.close()
        self.socket_r.close()
        self.flag = 0
        self.get_console_input()
       




    def get_console_input(self):
        while self.flag!=1:
            print('\n'+'*'*50)
            self.input_text = input("--(connect,getdir, makeroom, deleteroom, name , chat)--\n Enter Command: ")
            try:
                if (self.input_text == "connect"):
                    self.connected = 1
                    self.tcp_connection()
                    print("Connected to the CRDS")

            except Exception as msg:
                print(msg)

            try:
                if(self.input_text == "getdir"):
                    #print("detected")
                    self.getdir()
            except Exception as msg:
                print(msg)

            try:
                if(self.input_text.split()[0] == "makeroom"):
                    if(len(self.input_text.split())<2):
                        print('ENTER FORMAT: makeroom <chat room name> <address> <port>')
                        break

                    chatRoomName = self.input_text.split()[1]
                    address = self.input_text.split()[2]
                    port = self.input_text.split()[3]

                    self.makeroom(chatRoomName,address,port)

            except Exception as msg:
                print(msg)

            try:
                if(self.input_text.split()[0] == "deleteroom"):
                    deleteroomName = self.input_text.split()[1]
                    self.deleteroomFunc(deleteroomName)
            except Exception as msg:
                print(msg)


            try:
                if(self.input_text.split()[0] == "chat"):
                    # chatRoomName = self.input_text.split()[1]
                    # print("This si the name of the chatroom",chatRoomName)
                    # self.chat(chatRoomName)
                    self.chatroomName = self.input_text.split()[1]
                    self.flag = 1
            except Exception as msg:
                print(msg)

            try:
                if(self.input_text.split()[0] == "name"):
                    self.userName = self.input_text.split()[1]
                    print("This is the name entered",self.userName)
            except Exception as msg:
                print(msg)

            try:
                if(self.input_text.split()[0] == "bye"):
                    self.bye()
            except Exception as msg:
                print(msg)

        print("proceeding to chat function")
        self.chat()




########################################################################
# Process command line arguments if run directly.
########################################################################

if __name__ == '__main__':
    roles = {'receiver': Receiver,'sender': Sender}
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--role',
                        choices=roles, 
                        help='sender or receiver role',
                        required=True, type=str)

    args = parser.parse_args()
    roles[args.role]()

########################################################################






