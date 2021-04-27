import getpass
import hashlib

# 5 commands for the user to input from client 
# TCP connection created upon one of these get average commands -> printed on cmd
GET_MIDTERM_AVG_CMD = "GMA"
GET_LAB_1_AVG_CMD = "GL1A"
GET_LAB_2_AVG_CMD = "GL2A"
GET_LAB_3_AVG_CMD = "GL3A"
GET_LAB_4_AVG_CMD = "GL4A"

# if not one of 5 commands --> interpreted as HASHED ID/password 

# GET GRADES COMMAND - receive a specific student's grades  
GET_GRADES = "GG"
# input id/pass from client 
id_num = input("ID Number: ")
pwd = getpass.getpass() # automatically prints password 
# TCP CONNECTION TO SERVER !!! 
# send message to server with secure hash of entered ID & pass 
# hashedID = hashlib.sha256(id_num.encode('utf-8')).digest()
# hashedPass = hashlib.sha256(password.encode('utf-8')).digest()
# hashboth = hashedID+hashedPass
# print(hashedID)
# print(hashedPass)
# print(hashboth)
m = hashlib.sha256()
m.update(id_num.encode('utf-8'))
m.update(pwd.encode('utf-8'))
print(m.digest())
