import sys
import litebird_sim
import string
import logging as log
import matplotlib.pyplot as plt
import re
import math

def au_to_km(au):
    return au*1.496e+08

def km_to_au(km):
    return km/(1.496e+08)

def read_barycentric(filename):
    file = open(filename,"r+")
    content = file.read()
    lines = content.split("\n")
    matrix = []
    print("Parsing file")
    i = 0
    j = 1
    for line in lines[:-1]:
        for char in line:
            if char in list(string.ascii_lowercase) or char in list(string.ascii_uppercase) or char == "(" or char == ")":
                line = line.replace(char, "")
        temp = line.split(",")
        temp = [float(item.replace(" ","")) for item in temp]
        row = [temp[0],temp[1],temp[2]]
        #print(row)
        matrix.append(row)
        if i%1500 == 0:
            log.warning("Checkpoint "+str(j)+" reached --> ("+str(j)+"/"+str( (len(lines)//1500)+1 )+") ")
            j+=1
        i+=1
    print("Asserting dimensions")
    assert len(matrix[0]) == 3, "DimensionError: Matrix columns must be 3"
    return matrix

def read_ecliptic(filename):
    file = open(filename,"r+")
    content = file.read()
    lines = content.split("\n")
    matrix = []
    for line in lines[:-1]:
        line = line.replace("[","")
        line = line.replace("]", "")
        line = re.sub(' +', ' ',line)
        if len(line)>3:
            line = line[:-1]
        temp = line.split(" ")
        temp = [float(i) for i in temp]
        matrix.append(temp)
    return matrix
#positions = read_barymetric("jupiter_barycentric.txt")


def column(matrix, i):
    return [row[i] for row in matrix]

pos_au = read_barycentric("../outputs/jupiter_barycentric")
pos_km = [[au_to_km(elem) for elem in row] for row in pos_au]
print("Total points: ",len(pos_km))

time = [i for i in range(len(pos_km))]

x = column(pos_au,0)
y = column(pos_au,1)
z = column(pos_au,2)
assert len(x) == len(y) == len(z)
distance = [float(math.sqrt( x[i]**2 + y[i]**2 + z[i]**2 )) for i in range(len(x))]
log.info("Printing distances")
j = 0


plt.plot(time,distance)
plt.show()
