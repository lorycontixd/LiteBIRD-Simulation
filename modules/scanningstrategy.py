import litebird_sim as lbs
from modules import utils
import numpy as np
import logging as log
import numba
import time

class LBScanningStrategy(lbs.ScanningStrategy):
    def __init__(self,metadata):
        self.metadata = metadata
        for item in self.metadata:
            setattr(self, item, metadata[item])
    
    def __repr__(self):
        string = """- Spin-Sun Angle (deg): {}
- Precession Period (min): {}
- Spin rate (rpm): {}
- Mission duration (yrs): {}
- Observation duty cycle: {}
- Cosmic ray loss: {}
- Margin: {}
- Detector yield: {}"""
        return string.format(
            self.spin_sun_angle_deg,
            self.precession_period_min,
            self.spin_rate_rpm,
            self.mission_duration_year,
            self.observation_duty_cycle,
            self.cosmic_ray_loss,
            self.margin,
            self.detector_yield
        )

    def generate_spin2ecl_quaternions(self,start_time,time_span_s,delta_time_s):
        # Compute how many quaternions are needed to cover
        # the time interval specified by "time_span_s"
        num_of_quaternions = (
            lbs.ScanningStrategy.optimal_num_of_quaternions(
                time_span_s=time_span_s,
                delta_time_s=delta_time_s,
            )
        )
        print("(SS) Number of quats: ",num_of_quaternions)
        # Make room for the quaternions
        spin2ecliptic_quats = np.zeros((num_of_quaternions, 4))

        # We compute the times when the quaternions need to be
        # calculated. Note that ScanningStrategy returns two
        # arrays ("time" and "time_s"), but we neglect the second
        # because we don't need it in this very simple case
        utils.sep_title("Time")
        log.warning("Calculating time array, might take a while...")
        start = time.time()
        (times, times_s) = lbs.ScanningStrategy.get_times(
            start_time=start_time,
            delta_time_s=delta_time_s,
            num_of_quaternions=num_of_quaternions,
        )
        print("Time array: ")
        print(str(times[0])+" --> "+str(times[-1]))
        print("Computation time: "+str(time.time()-start)+" seconds")
        utils.empty_print(1)
        # Compute the angle on the Ecliptic plane between the x
        # axis and the Sun-Earth axis, possibly using AstroPy
        utils.sep_title("Sun-Earth Angles")
        log.warning("Calculating angles Sun-Earth, might take a while...")
        start2 = time.time()
        sun_earth_angles_rad = lbs.calculate_sun_earth_angles_rad(times)
        print("Sun earth angles : ")
        print(sun_earth_angles_rad)
        print("Computation time: "+str(time.time()-start2)+" seconds")
        utils.empty_print(1)
        assert times.shape == sun_earth_angles_rad.shape,"DimensionalError: Time and Angles must have same sizee"
        # This code is *not* optimized: in a real-world case,
        # you'll probably want to use Numba instead of the
        # following "for" loop
        for i in range(num_of_quaternions):
            # Rotate by 90° around the y axis (move the boresight
            # to the Ecliptic xy plane)
            spin2ecliptic_quats[i, :] = lbs.quat_rotation_y(np.pi / 2)

            # Simulate the revolution of the spacecraft around
            # the Sun using the angles computed above
            lbs.quat_left_multiply(
                spin2ecliptic_quats[i, :],
                *lbs.quat_rotation_z(sun_earth_angles_rad[i]),
            )

        # Return the quaternions wrapped in an instance of
        # "Spin2EclipticQuaternions"
        return lbs.Spin2EclipticQuaternions(
            start_time=start_time,
            pointing_freq_hz=1.0 / delta_time_s,
            quats=spin2ecliptic_quats,
        )
