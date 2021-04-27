
# try:
#     file = open(filename,'r')
# # except FileNotFoundError:
# #     print("Creating database:{}".format(filename))
# #     # file = open(filename, 'w')


filename = 'course_grades_2021.csv'

file = open(filename,'r')

data = [] 
for line in file.readlines():
    # values = line.rstrip('\n').split(",")
    # data.append(values)
    print(line.rstrip('\n'))

idNum = [] 
password = [] 
lastName = [] 
firstName = [] 
midterm = []
lab1 = []
lab2 = []
lab3 = []
lab4 = []

for record in data[1:]:
    idNum.append(record[0]) 
    password.append(record[1])
    lastName.append(record[2]) 
    firstName.append(record[3]) 
    midterm.append(record[4])
    lab1.append(record[5])
    lab2.append(record[6])
    lab3.append(record[7])
    lab4.append(record[8])

keys = data[0]
values = [idNum, password, lastName, firstName, midterm, lab1, lab2, lab3, lab4]

records = dict(zip(keys,values))
print(records)