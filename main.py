import litebird_sim as lbs
import matplotlib.pyplot as plt
import numpy as np
import astropy
import healpy
import logging
import os
import sys
import math
import inspect
from modules import utils, objects, scanningstrategy as ss,errors
import astropy.time
import astropy.units as u
from astropy.coordinates import (
    ICRS,
    get_body_barycentric,
    BarycentricMeanEcliptic,
    solar_system_ephemeris,
)
from numba import jit
import time
import argparse

log = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(asctime)-15s %(process)4d:%(threadName)-11s '+utils.Colors.FAIL+'%(name)s %(message)s'+utils.Colors.ENDC
)
commandline_args = utils.parser()
if commandline_args["plot"].lower() not in ["x","y","z","d"]:
    raise errors.InputError("main.plot.commandline_args",
                            "Invalid --plot argument passed: "+str(commandline_args["plot"]))

if commandline_args["testmode"] == "True":
    toml_dir = "./parameters/real/litebird-scanning-strategy.toml"
    root = "outputs/real/"
else:
    toml_dir = str(input("Test Mode is active, please enter TOML configuration directory!\n(Press ENTER for default test file):  "))
    if len(toml_dir) == 0:
        toml_dir = "./parameters/test/test.toml"
    root = "outputs/test/"


log.info("--------  SIMULATION STARTING  --------")
#************************************  SCRIPT PARAMETERS  ************************
print("-> Toml file: ", toml_dir)
if bool(commandline_args["mpi"]):
    print("-> MPI: Enabled")
    os.environ["ENABLE_MPI"] = "1"
    comm = lbs.MPI_COMM_WORLD
else:
    print("-> MPI: Disabled")
    os.environ["ENABLE_MPI"] = "0"

utils.empty_print(1)

#Simulation
sim = objects.MySimulation(
    parameter_file=toml_dir
)

#Imo work
imo = lbs.Imo()
sim_params = sim.parameters["simulation"]
scanning_params = sim.parameters["scanning_strategy"]
planet_params = sim.parameters["planet_scanning"]
scan_params = imo.query(
    scanning_params["scanning_strategy_obj"]
)

#Instrumental variables
metadata = scan_params.metadata
strat = ss.LBScanningStrategy(metadata)
instr = lbs.Instrument(name="LiteBIRD", spin_boresight_angle_deg=sim.parameters["scanning_strategy"]["spin_boresight_angle_deg"])
det = lbs.DetectorInfo(
    name="Boresight", sampling_rate_hz=sim.parameters["planet_scanning"]["sampling_rate_hz"]
)
obs, = sim.create_observations(detectors=[det])
print(utils.Colors.WARNING+"----> Number of samples: "+utils.Colors.ENDC, obs.tod.shape[1])

utils.print_inputs(simulation=sim,detector=det,instrument=instr,strategy=strat)

#*******************************+**  CALCULATIONS  ***************+


sim.generate_spin2ecl_quaternions(
    scanning_strategy=ss.LBScanningStrategy(
        metadata = metadata
    )
) #Get quaternions responsible for rotation from spin-axis to ecliptic plane

planet = planet_params["planet_name"]
solar_system_ephemeris.set("builtin")
start = time.time()
log.warning("Calculating jupiter positions over time, might take a long while...")
times = obs.get_times(astropy_times=True)
icrs_pos = get_body_barycentric(
    planet,
    times,
utils.empty_print(1)
)#get jupiter position in barycentric coordinates

utils.sep_title("Positions")
print("Calculated "+str(planet)+" positions in Barycentric coordinates.")
print("Computation time: "+str(time.time()-start)+" seconds")
utils.empty_print(1)

#*********************  OUTPUTS  **********************
planet_dir = root+str(planet)
if not os.path.exists(planet_dir):
    os.mkdir(root+str(planet))

filename = planet_dir+"/"+str(planet)+"_barycentric.txt"
filename2 = planet_dir+"/"+str(planet)+"_detector.txt"

print("Writing outputs to file "+str(filename))
writing_start = time.time()
if bool(commandline_args["file"]):
    utils.write_to_file(filename,icrs_pos)
print("Written to file in "+str(time.time()-writing_start))

ecl_vec = (ICRS(icrs_pos)
           .transform_to(BarycentricMeanEcliptic)
           .cartesian
           .get_xyz()
           .value
            ) #Convert from Barycentric to Ecliptic, now we have everything in Ecliptic coordinates

#ecl_vec /= np.linalg.norm(ecl_vec, axis=0, ord=2) #Normalize coordinate to get position in terms of unit vector (only directions)
ecl_vec = ecl_vec.transpose()

#daprint("Vectors normalized to unit vectors and transposed.")
quats = obs.get_ecl2det_quaternions(
    sim.spin2ecliptic_quats,
    detector_quats=[det.quat],
    bore2spin_quat=instr.bore2spin_quat,
)
#Now we have the vectors in the DETECTOR frame of reference
det_vec = np.empty_like(ecl_vec)
lbs.all_rotate_vectors(det_vec, quats[0], ecl_vec)

message = "Vector size: "+str(ecl_vec.shape)
if ecl_vec.shape[0] == obs.tod.shape[1]:
    print(message+"  -- Good")
else:
    log.fatal("DimensionalError: ecl_vec & tod.shape")
utils.empty_print(1)
if bool(commandline_args["file"]):
    utils.write_to_file(filename2,ecl_vec)
log.info("Simulation completed!")
nums = [i for i in range(obs.tod.shape[1])]

det_vec_matrix = [ list(row) for row in det_vec ]
x = utils.column(det_vec_matrix,0)
y = utils.column(det_vec_matrix, 1)
z = utils.column(det_vec_matrix, 2)
distance = [ math.sqrt(x[i]**2 + y[i]**2 + z[i]**2)  for i in range(len(x))]

if commandline_args["plot"] == "x":
    plt.plot(nums,x)
elif commandline_args["plot"] == "y":
    plt.plot(nums,y)
elif commandline_args["plot"] == "z":
    plt.plot(nums, z)
elif commandline_args["plot"] == "d":
    plt.plot(nums, distance)
else:
    pass

plt.show()
