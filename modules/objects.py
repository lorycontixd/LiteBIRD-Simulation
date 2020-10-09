import litebird_sim as lbs
from tabulate import tabulate
import json

class MySimulation(lbs.Simulation):
    def __repr__(self):
        string = ""
        for par in self.parameters:
            string += "-"+str(par)+"\n"
            for item in self.parameters[par]:
                string += "+-----"+str(item)+" = "+str(self.parameters[par][item])+"\n"
            string += "\n"
        return string