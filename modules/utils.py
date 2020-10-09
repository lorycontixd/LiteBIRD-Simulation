import litebird_sim as lbs
import logging
import argparse
from datetime import datetime

class Colors():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

col_dict = {
        "warn": "WARNING",
        "fail": "FAIL",
        "end": "ENDC",
        "pass": "OKGREEN",
        "blue": "OKBLUE"
    }

def load_parameters(parameters,title):
    return parameters[title]

def log(level,message):
    stream = open("outputs/logs.log")
    m2 = str(datetime.now())+" -- "+str(level)+" -- "+str(message)
    stream.write(m2)

def print_inputs(*args,**kwargs):
    accepted = ["simulation","observation","instrument","detector","strategy"]
    for kw in kwargs:
        assert kw in accepted, "Invalid keyword argument: "+str(kw)
        logging.info("Displaying "+str(kw)+" information")
        print(str(kwargs[kw]))
        if kw != "simulation":
            print(" ")

def sep():
    print("***********************************************************************")

def sep_title(title):
    print("***********************************  "+str(title)+"  **********************************")

def write_to_file(filename,iterable):
    file = open(filename,"w+")
    for item in iterable:
        file.write(str(item)+"\n")
    return file

def empty_print(myint):
    for i in range(myint):
        print(" ")


def column(matrix, i):
    return [row[i] for row in matrix]

def parser():
    parser = argparse.ArgumentParser(
        description='Parse command line arguments')

    parser.add_argument(
        "-testmode","--testmode",
        action = "store_true",
        help = "Set test mode to script"
    )

    parser.add_argument(
        "-mpi", "--mpi",
        help="Use MPI for execution",
        action = "store_true"
    )
    parser.add_argument(
        "-file","--file",
        help = "Write output to file",
        action = "store_true"
    )

    parser.add_argument(
        "-plot","--plot",
        help="Plot graph",
        default = "x",
        nargs = "?"
    )
    args = parser.parse_args()
    commandline_args = vars(args)
    return commandline_args


