# testing multiple filter

import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control
import glob
import warnings
import json

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

import configparser

# X motion
from sammie import plant_model_ham7
from sammie import plant_model_ham8

from sammie.blend_sc_iso import sens_cor, blend, iso
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13
from sammie.data import padded_ground_motion, fetch_timeseries_data

config = configparser.ConfigParser()
config.read("../etc/config.ini")
dof = config.get("current_run", "dof")
ham = config.get("current_run", "ham")

function_dict = {
    "HAM7_X_plant": plant_model_ham7.ham7_plant_x,
    "HAM7_Y_plant": plant_model_ham7.ham7_plant_y,
    "HAM7_Z_plant": plant_model_ham7.ham7_plant_z,
    "HAM7_X_trans": plant_model_ham7.ham7_trans_x,
    "HAM7_Y_trans": plant_model_ham7.ham7_trans_y,
    "HAM7_Z_trans": plant_model_ham7.ham7_trans_z,
    "HAM8_X_plant": plant_model_ham8.ham8_plant_x,
    "HAM8_Y_plant": plant_model_ham8.ham8_plant_y,
    "HAM8_Z_plant": plant_model_ham8.ham8_plant_z,
    "HAM8_X_trans": plant_model_ham8.ham8_trans_x,
    "HAM8_Y_trans": plant_model_ham8.ham8_trans_y,
    "HAM8_Z_trans": plant_model_ham8.ham8_trans_z,
}


start_time = int(config.get("current_run", "gpstime"))
averages = int(config.get("current_run", "averages"))
coherence_overlap = float(config.get("current_run", "coherence_overlap"))
fftlen = int(config.get("current_run", "coherence_fftlen"))
end_time = start_time + (averages * coherence_overlap + 1) * fftlen

f, xg, no_pad, n_seis = padded_ground_motion(start_time, dof)
gs13_timeseries = fetch_timeseries_data(
    f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
)
t240_timeseries = fetch_timeseries_data(
    f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
)

gs13_resampled = gs13_timeseries.resample(512)
t240_resampled = t240_timeseries.resample(512)

asd_gs13 = gs13_resampled.asd(fftlength=fftlen, overlap=coherence_overlap)
asd_t240 = t240_resampled.asd(fftlength=fftlen, overlap=coherence_overlap)

s = control.tf("s")
wn = 1 * 2 * np.pi
q = 1 / np.sqrt(2)
gs13_inv = (s**2 + wn / q * s + wn**2) / s**3
t240_inv = 1 / s

corr_gs = abs(gs13_inv(1j * 2 * np.pi * f))
corr_t240 = abs(t240_inv(1j * 2 * np.pi * f))
asd_gs13_corrected = corr_gs * asd_gs13.value[1:]
asd_t240_corrected = corr_t240 * asd_t240.value[1:]

# plt.loglog(asd_a.frequencies, asd_a_corrected, label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ")
plt.loglog(
    asd_gs13.frequencies[1:],
    asd_gs13_corrected,
    label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ",
)
plt.loglog(
    asd_t240.frequencies[1:],
    asd_t240_corrected,
    label=f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ",
)


start_time = int(config.get("current_run", "gpstime"))

start_time = int(config.get("current_run", "gpstime"))
_, pg = function_dict[f"{ham}_{dof}_trans"]()
f, xg, no_pad, n_seis = padded_ground_motion(start_time, dof)


_, n_cps = sensor_noise_cps_xy(f)
_, n_gs13 = sensor_noise_gs13(f)


plt.loglog(f, n_gs13)
plt.legend(prop={"size": 6})
plt.show()