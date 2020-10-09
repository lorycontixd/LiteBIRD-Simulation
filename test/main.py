import litebird_sim as lbs
import matplotlib.pyplot as plt
import numpy as np
import astropy
import healpy
import logging as log
import os
import inspect
from modules import utils, objects, scanningstrategy as ss
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

os.environ["ENABLE_MPI"] = "1"
comm = lbs.MPI_COMM_WORLD
parser = argparse.ArgumentParser(description='Parse command line arguments')
parser.add_argument()

#Simulation
sim = objects.MySimulation(
    parameter_file="litebird-scanning-strategy.toml"
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

utils.print_inputs(simulation=sim,detector=det,instrument=instr,strategy=strat)

sim.generate_spin2ecl_quaternions(
    scanning_strategy=ss.LBScanningStrategy(
        metadata = metadata
    )
) #Get quaternions responsible for rotation from spin-axis to ecliptic plane

planet = planet_params["planet_name"]
solar_system_ephemeris.set("builtin")
start = time.time()
log.warning("Calculating jupiter positions over time, might take a long while...")
icrs_pos = get_body_barycentric(
    planet,
    obs.get_times(astropy_times=True),
utils.empty_print(1)
)#get jupiter position in barycentric coordinates
utils.sep_title("Positions")
print("Calculated "+str(planet)+" positions in Barycentric coordinates.")
print("Computation time: "+str(time.time()-start)+" seconds")
utils.empty_print(1)
filename = "outputs/TEST"+str(planet)+"_barycentric"
print("Writing outputs to file "+str(filename))
utils.write_to_file(filename,icrs_pos)
print("Positions saved to file...")

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
print("Number of samples: ", ecl_vec.shape)
utils.empty_print(1)
filename2 = "outputs/TEST"+str(planet)+"_ecliptic"
utils.write_to_file(filename2,ecl_vec)
log.info("Simulation completed")

