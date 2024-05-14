
import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control
import glob
import warnings
import json
from scipy.optimize import curve_fit
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

import configparser

# X motion
from sammie import plant_model_ham7
from sammie import plant_model_ham8

from sammie.blend_sc_iso import sens_cor, blend, iso
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13
from sammie.data import padded_ground_motion, fetch_timeseries_data, frequency_minima_scipy_groundmotion

config = configparser.ConfigParser()
config.read("../etc/config.ini")
dof = config.get("current_run", "dof")
ham = config.get("current_run", "ham")

start_time = int(config.get("current_run", "gpstime"))
averages = int(config.get("current_run", "averages"))
coherence_overlap = float(config.get("current_run", "coherence_overlap"))
fftlen = int(config.get("current_run", "coherence_fftlen"))
end_time = start_time + (averages * coherence_overlap + 1) * fftlen
f = np.arange(0.001953125,256.0+0.001953125 , 0.001953125)

gs13_timeseries = fetch_timeseries_data(
    f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
)
t240_timeseries = fetch_timeseries_data(
    f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
)
gs13_timeseries_ham8 = fetch_timeseries_data(
    f"L1:ISI-GND_STS_HAM8_{dof}_DQ", start_time, end_time, mode="cdsutils"
)

gs13_resampled = gs13_timeseries.resample(512)
t240_resampled = t240_timeseries.resample(512)
gs13_resampled_ham8 = gs13_timeseries_ham8.resample(512)
asd_ham8 = gs13_resampled_ham8.asd(fftlength=512,overlap=0.5)
asd_gs13 = gs13_resampled.asd(fftlength=fftlen, overlap=coherence_overlap)
asd_t240 = t240_resampled.asd(fftlength=fftlen, overlap=coherence_overlap)


_, n_gs13 = sensor_noise_gs13(f)
s = control.tf("s")
wn = 1 * 2 * np.pi
q = 1 / np.sqrt(2)
gs13_inv = (s**2 + wn / q * s + wn**2) / s**2
t240_inv = 1 / s

corr_gs = abs(gs13_inv(1j * 2 * np.pi * f))
corr_t240 = abs(t240_inv(1j * 2 * np.pi * f))
asd_gs13_corrected = corr_gs * asd_gs13.value[1:]
asd_t240_corrected = corr_t240 * asd_t240.value[1:]

gs13_RX_timeseries = fetch_timeseries_data(
    f"L1:ISI-{ham}_BLND_GS13RX_IN1_DQ", start_time, end_time, mode="cdsutils"
)
gs13_RX_resampled = gs13_RX_timeseries.resample(512)
asd_gs13_RX = gs13_RX_resampled.asd(fftlength=fftlen, overlap=coherence_overlap)
asd_gs13_RX_corrected = asd_gs13_RX[1:] * corr_gs
a = 1
tilt = a*9.8/s**2

plt.loglog(
    asd_gs13.frequencies[1:],
    asd_gs13_corrected,
    label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ",
)
'''
plt.loglog(
    asd_gs13.frequencies[1:],
    abs(tilt(1j * 2 * np.pi * f)),
    label=f"g/s^2",
)
'''
plt.loglog(
    asd_gs13.frequencies[1:],
    abs(tilt(1j * 2 * np.pi * f)) * asd_gs13_RX_corrected,
    label=f"g/s^2 * RX",
)

plt.loglog(
    asd_ham8.frequencies,
    asd_ham8.value/(2*np.pi*asd_ham8.frequencies),
    label=f"HAM8 STS",
)
plt.loglog(f,n_gs13, label="GS13")
plt.legend()
plt.show()