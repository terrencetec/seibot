from gwpy.timeseries import TimeSeries
from gwpy.frequencyseries import FrequencySeries
import numpy as np
from scipy.signal import coherence
from scipy.signal import argrelextrema
from scipy import optimize
import matplotlib.pyplot as plt
import configparser
import cdsutils
from scipy.optimize import curve_fit
import nds2

def noise_model(f, a, na):
    """Noise model for STS noise"""

    noise = ((na/f**a)**2)**.5
    return noise

def fetch_timeseries_data(channel, gps_start, gps_end, mode):
    if mode == 'gwpy':
        data = TimeSeries.fetch(channel, gps_start, gps_end)
    elif mode == 'cdsutils':
        target_data =  cdsutils.getdata(channel, gps_end-gps_start, gps_start)
        data = TimeSeries(data=target_data.data*1e-9, t0=gps_start, dt=1/target_data.sample_rate,name=channel)
    return data


def coherence_calculator(data_A, data_B):
    rate = data_A.sample_rate.value
    f,coh = coherence(data_A.value,data_B.value, fs=rate, nperseg=rate*512, noverlap=rate*512/2)
    return f,coh


def plot_asd_coherence(data_A, data_B, start_times, cutoff_freq=None):

    f,coh = coherence_calculator(data_A, data_B)
    fig, (ax1,ax2) = plt.subplots(2,1, sharex=True, figsize=(15,6))
    asd_a = data_A.asd(fftlength=512,overlap=0.5)
    asd_b = data_B.asd(fftlength=512,overlap=0.5)
    asd_a_dis = asd_a.value/(2*np.pi*asd_a.frequencies)
    asd_b_dis = asd_b.value/(2*np.pi*asd_b.frequencies)
    ax1.plot(asd_a.frequencies, asd_a_dis, label="ITMX")
    ax1.plot(asd_b.frequencies, asd_b_dis, label="ITMY")
    ax1.set_xlim(0.001,100)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title("ASD")
    if cutoff_freq:
        ax1.axvline(cutoff_freq, c='r')
    ax1.legend()
    ax2.plot(f,coh)
    ax2.set_title("Coherence")
    if cutoff_freq:
        ax2.axvline(cutoff_freq, c='r')
    plt.savefig(f"../temp_analysis/asd_coh_cutoff_{str(start_times)}.png", dpi=300)


def plot_padded_asd(asd_a, asd_b, cutoff_freq):
    fig, ax = plt.subplots(figsize=(15,6))
    ax.plot(asd_a.frequencies, asd_a.value, label="ITMX")
    ax.plot(asd_b.frequencies, asd_b.value, label="ITMY")
    ax.set_xlim(0.001,100)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title("ASD")
    ax.legend()
    ax.axvline(cutoff_freq, c='r')
    plt.savefig(f"../temp_analysis/padded_asd_{str(int(asd_a.epoch.value))}.png", dpi=300)

def frequency_minima_scipy_groundmotion(data_A, data_B, asd_dis_a, asd_dis_b):

    f,coh = coherence_calculator(data_A, data_B)
    # find the point where there is max coherence
    rounded_coh = np.round(coh, 2)
    first_one_coh = np.min(np.where(rounded_coh == 1.00))

    # from that frequency position to 0 make freq-bins of given width and check for 
    # coherence difference in each bin
    check_array = np.arange(first_one_coh, 0, -5)
    min_asd = np.min(asd_dis_a.value[0:first_one_coh])
    last_one_coh = np.max(np.where(asd_dis_a.value[0:first_one_coh] == min_asd))
    frequency = asd_dis_a.frequencies[last_one_coh]
    return frequency.value


def pad_asd(asd_a, asd_b, cutoff_freq):
    loc_cutoff = np.where((asd_a.frequencies.value == cutoff_freq))[0][0]
    pad_value_a = asd_a.value[loc_cutoff]
    pad_value_b = asd_b.value[loc_cutoff]
    data_a = asd_a.value
    data_a[0:loc_cutoff] = pad_value_a 
    data_b = asd_b.value
    data_b[0:loc_cutoff] = pad_value_b 
    asd_a.append(data_a, resize=False)
    asd_b.append(data_b, resize=False)
    asd_a.f0 = 0 
    asd_b.f0 = 0

    return asd_a, asd_b

def padded_ground_motion(gpstime, dof):
    config = configparser.ConfigParser()
    config.read("../etc/config.ini")
    #conn = nds2.connection('nds.ligo-la.caltech.edu',31200)
    # Checking coherence between ETMX and ITMX ground sensors
    start_time = int(config.get('current_run','gpstime'))
    averages = int(config.get('current_run','averages'))
    coherence_overlap = float(config.get('current_run','coherence_overlap'))
    fftlen = int(config.get('current_run','coherence_fftlen'))
    end_time = start_time + (averages*coherence_overlap +1)*fftlen
    ITMX_data = fetch_timeseries_data(f'L1:ISI-GND_STS_ITMX_{dof}_DQ',
                                    start_time, end_time, mode='cdsutils')
    ITMY_data = fetch_timeseries_data(f'L1:ISI-GND_STS_ITMY_{dof}_DQ',
                                    start_time, end_time, mode='cdsutils')

    asd_a = ITMX_data.asd(fftlength=fftlen,overlap=coherence_overlap)
    asd_b = ITMY_data.asd(fftlength=fftlen,overlap=coherence_overlap)

    asd_dis_a = FrequencySeries(data=asd_a.value/(2*np.pi*asd_a.frequencies), 
                                f0=asd_a.f0, 
                                df=asd_a.df, 
                                name=asd_a.name, 
                                epoch=asd_a.epoch, 
                                channel=asd_a.channel)

    asd_dis_b = FrequencySeries(data=asd_b.value/(2*np.pi*asd_b.frequencies), 
                                f0=asd_b.f0, 
                                df=asd_b.df, 
                                name=asd_b.name, 
                                epoch=asd_b.epoch, 
                                channel=asd_b.channel)

    displacement_asd = asd_dis_a.copy()
    cutoff_freq= frequency_minima_scipy_groundmotion(ITMX_data, ITMY_data, asd_dis_a, asd_dis_b)
    _,n_sei = conditional_n_sei(cutoff_freq, noise_model, asd_dis_a)
    padded_asd_a, padded_asd_b = pad_asd(asd_dis_a, asd_dis_b, cutoff_freq)

    

    return padded_asd_a.frequencies.value, padded_asd_a.value, displacement_asd.value, n_sei

def conditional_n_sei(cutoff, noise_model, disp_asd):
    upper = np.max(np.where(disp_asd.frequencies.value == cutoff))
    lower = np.max(np.where((disp_asd.frequencies.value - 1e-2) <0.001))
    x = disp_asd.frequencies.value[lower:upper]
    y = disp_asd.value[lower:upper]
    param, _ = curve_fit(noise_model, x, y)
    n_sei = noise_model(disp_asd.frequencies.value[1:], a=param[0], na=param[1])

    return disp_asd.frequencies.value[1:], n_sei

def conditional_n_sei_vishack(f, cutoff, noise_model, disp_asd):
    upper = cutoff
    lower = np.max(np.where((f - 1e-2) <0.001))
    x = f[lower:upper]
    y = disp_asd[lower:upper]
    param, _ = curve_fit(noise_model, x, y)
    print(f'parameters : {param}')
    n_sei = noise_model(f[1:], a=param[0], na=param[1])

    return f[1:], n_sei