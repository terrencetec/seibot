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

from sammie.blend_sc_iso import sens_cor, blend, iso
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13
from sammie.data import padded_ground_motion, fetch_timeseries_data, frequency_minima_scipy_groundmotion

def get_tilt_gs13():

    config = configparser.ConfigParser()
    config.read("../etc/config.ini")
    dof = config.get("current_run", "dof")
    ham = config.get("current_run", "ham")
    ham = 'HAM8'
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


    _, n_cps = sensor_noise_cps_xy(f)
    _, n_gs13 = sensor_noise_gs13(f)

    plt.loglog(f, no_pad)
    plt.loglog(f, n_gs13)

    plt.legend(prop={"size": 12})
    plt.show()


    gs13_timeseries_ham8 = fetch_timeseries_data(
        f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, mode="cdsutils"
    )
    gs13_resampled_ham8 = gs13_timeseries_ham8.resample(512)
    gs13_timeseries_ham7 = fetch_timeseries_data(
        f"L1:ISI-GND_STS_ITMY_{dof}_DQ", start_time, end_time, mode="cdsutils"
    )
    gs13_resampled_ham7 = gs13_timeseries_ham7.resample(512)

    asd_ham8 = gs13_resampled_ham8.asd(fftlength=512,overlap=0.5)
    asd_ham7 = gs13_resampled_ham7.asd(fftlength=512,overlap=0.5)
    from scipy.signal import coherence
    f,coh = coherence(gs13_resampled_ham7.value, gs13_resampled_ham8.value, fs=512, nperseg=512*512, noverlap=512*512/2)
    '''
    s = control.tf("s")
    wn = 1 * 2 * np.pi
    q = 1 / np.sqrt(2)
    gs13_inv = (s**2 + wn / q * s + wn**2) / s**3
    t240_inv = 1 / s

    corr_gs = abs(gs13_inv(1j * 2 * np.pi * f))

    asd_ham8 = corr_gs * asd_ham8
    asd_ham7 = corr_gs * asd_ham7
    '''


    fig, (ax1,ax2) = plt.subplots(2,1, sharex=True, figsize=(15,6))
    ax1.plot(asd_ham8.frequencies, asd_ham8.value/(2*np.pi*asd_ham8.frequencies), label="HAM8 GS13")
    ax1.plot(asd_ham7.frequencies, asd_ham7.value/(2*np.pi*asd_ham7.frequencies), label="ITMY STS")
    ax1.set_xlim(0.001,100)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title("ASD")
    ax1.legend()
    ax2.plot(f,coh)
    ax2.set_title("Coherence")
    plt.show()


    asd_ham8_dis = asd_ham8.value/(2*np.pi*asd_ham8.frequencies)
    rounded_coh = np.round(coh, 2)
    first_one_coh = np.min(np.where(rounded_coh == 1.00))
    # from that frequency position to 0 make freq-bins of given width and check for 
    # coherence difference in each bin
    check_array = np.arange(first_one_coh, 0, -5)
    min_asd = np.min(asd_ham8_dis.value[0:first_one_coh])
    last_one_coh = np.max(np.where(asd_ham8_dis.value[0:first_one_coh] == min_asd))
    frequency = asd_ham8.frequencies[last_one_coh]
    print(frequency)

    noise_data = [ 2.138e-8, 1.958e-9, 1.892e-10, 1.732e-11,
                    7.262e-12, 3.887e-12, 2.449e-12, 1.462e-12, 9.725e-13, 
                    4.423e-13, 3.280e-13, 1.137e-13, 5.610e-14, 2.053e-14,
                    2e-15]   
    freq_data = [0.101, 0.201, 0.400, 0.792, 0.994, 1.258, 1.655, 2.588, 
                    3.954, 8.202, 10.710, 24.796, 46.087, 91.208, 1e3]

    def noise_model_gs13(f, a):
        """Noise model"""
        b= 1.25
        nb = 10**-11.5   
        na = 10**-11.5 
        noise = np.log10(1.5*((na/f**a)**2 + (nb/f**b)**2)**.5)
        return noise

    freq_used =  asd_gs13.frequencies.value[1:]
    print(freq_used)
    upper = np.max(np.where(freq_used == frequency.value))
    lower = np.max(np.where((freq_used - 1e-2) <0.001))
    x = np.concatenate((freq_used[lower:upper], np.array(freq_data)))
    y = np.concatenate((asd_gs13_corrected[lower:upper], np.array(noise_data)))
    '''
    param, _ = curve_fit(noise_model_gs13, x, np.log10(y))
    print(param)
    n_gs13_new = noise_model_gs13(freq_used, a=param[0]) 

    '''
    new_gs13 = np.concatenate((asd_gs13_corrected[0:upper], n_gs13[upper:]), axis=0)

    '''
    plt.loglog(freq_used,n_gs13, label="old")
    plt.loglog(freq_used, new_gs13, label="new")
    plt.loglog(
        asd_gs13.frequencies[1:],
        asd_gs13_corrected,
        label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ",
    )
    plt.legend()
    plt.show()
    '''
    return new_gs13
