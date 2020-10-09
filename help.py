import multiprocessing as mp
import time
import inspect
import astropy.coordinates as c
import astropy
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
#from modules import animate_healpix_maps
import litebird_sim as lbs

print(inspect.getsource(lbs.Simulation))