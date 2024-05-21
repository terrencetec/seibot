# testing multiple filter

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
from scipy.signal import coherence
from sammie.blend_sc_iso import sens_cor, blend, iso
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13
from sammie.data import padded_ground_motion, fetch_timeseries_data, coherence_calculator

def get_tilt_gs13(cutoff):

    config = configparser.ConfigParser()
    config.read("../etc/config.ini")
    dof = config.get("current_run", "dof")
    ham = config.get("current_run", "ham")
    start_time = int(config.get("current_run", "gpstime"))
    averages = int(config.get("current_run", "averages"))
    coherence_overlap = float(config.get("current_run", "coherence_overlap"))
    fftlen = int(config.get("current_run", "coherence_fftlen"))
    end_time = start_time + (averages * coherence_overlap + 1) * fftlen

    f = np.arange(0.001953125, 256.0+0.001953125, 0.001953125)


    s = control.tf("s")
    wn = 1 * 2 * np.pi
    q = 1 / np.sqrt(2)
    gs13_inv = (s**2 + wn / q * s + wn**2) / s**3
    t240_inv = 1 / s

    corr_gs = abs(gs13_inv(1j * 2 * np.pi * f))
    corr_t240 = abs(t240_inv(1j * 2 * np.pi * f))


    start_time = int(config.get("current_run", "gpstime"))
    _, n_gs13 = sensor_noise_gs13(f)
    gs13_timeseries_ham8 = fetch_timeseries_data(
        f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
    )

    gs13_resampled_ham8 = gs13_timeseries_ham8.resample(512)
 
    sts_timeseries_ham7 = fetch_timeseries_data(
        f"L1:ISI-GND_STS_ITMY_{dof}_DQ", start_time, end_time, mode="cdsutils"
    )
    sts_resampled_ham7 = sts_timeseries_ham7.resample(512)

    asd_ham8_gs13 = gs13_resampled_ham8.asd(fftlength=512,overlap=0.5)[1:]
    asd_itmy_sts = sts_resampled_ham7.asd(fftlength=512,overlap=0.5)[1:]
    asd_ham8_gs13 = corr_gs * asd_ham8_gs13
    asd_itmy_sts_dis = asd_itmy_sts.value/(2*np.pi*asd_itmy_sts.frequencies)
    nperseg = 512*512
    f,coh = coherence(gs13_resampled_ham8.value, sts_resampled_ham7.value, fs=512, nperseg=nperseg, noverlap=nperseg/2)

    fig, (ax1,ax2) = plt.subplots(2,1, sharex=True, figsize=(15,6))
    ax1.plot(asd_ham8_gs13.frequencies, asd_ham8_gs13, label="HAM8 GS13")
    ax1.plot(asd_itmy_sts.frequencies, asd_itmy_sts, label="ITMY STS")
    ax1.set_xlim(0.001,100)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title("ASD")
    ax1.legend()
    ax2.plot(f,coh)
    ax2.set_title("Coherence")
    plt.show()

    rounded_coh = np.round(coh, 2)
    upper_limit = np.min(np.where(asd_ham8_gs13.frequencies.value == cutoff))
    last_low_coh = np.max(np.where(rounded_coh[0:upper_limit] < 0.2))
    frequency = asd_ham8_gs13.frequencies[last_low_coh]
    freq_used =  asd_ham8_gs13.frequencies.value[1:]
    print(freq_used)
    upper = np.max(np.where(freq_used == frequency.value))
    new_gs13 = np.concatenate((asd_ham8_gs13.value[0:upper], n_gs13[upper:]), axis=0)

    return new_gs13