from gwpy.timeseries import TimeSeries
from etc import config
import numpy as np
from scipy.signal import coherence
from scipy.signal import argrelextrema
from scipy import optimize
import matplotlib.pyplot as plt
import nds2


def fetch_timeseries_data(channel, gps_start, gps_end, conn):
    
    data = TimeSeries.fetch(channel, gps_start, gps_end,connection=conn, allow_tape=True)
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




def frequency_minima_scipy_groundmotion(data_A, data_B):

    f,coh = coherence_calculator(data_A, data_B)
    asd_a = data_A.asd(fftlength=512,overlap=0.5)
    asd_b = data_B.asd(fftlength=512,overlap=0.5)
    asd_a_dis = asd_a.value/(2*np.pi*asd_a.frequencies)
    asd_b_dis = asd_b.value/(2*np.pi*asd_b.frequencies)
    # find the point where there is max coherence
    rounded_coh = np.round(coh, 2)
    first_one_coh = np.min(np.where(rounded_coh == 1.00))

    # from that frequency position to 0 make freq-bins of given width and check for 
    # coherence difference in each bin
    check_array = np.arange(first_one_coh, 0, -config.bin_width)
    min_asd = np.min(asd_a_dis[0:first_one_coh])
    last_one_coh = np.max(np.where(asd_a_dis[0:first_one_coh] == min_asd))
    frequency = asd_a.frequencies[last_one_coh]
    return frequency.value


conn = nds2.connection('nds.ligo-la.caltech.edu',31200)
for start_times in config.gps_sample_list:
    # Checking coherence between ETMX and ITMX ground sensors
    print(start_times)

    ITMX_data = fetch_timeseries_data('L1:ISI-GND_STS_ITMX_X_DQ',
                                    start_times, start_times + 
                                    (config.averages*config.coherence_overlap +1)*config.coherence_fftlen, conn )
    ITMY_data = fetch_timeseries_data('L1:ISI-GND_STS_ITMY_X_DQ',
                                    start_times, start_times + 
                                    (config.averages*config.coherence_overlap +1)*config.coherence_fftlen, conn )
    print("done")
    cutoff_freq = frequency_minima_scipy_groundmotion(ITMX_data, ITMY_data)
    plot_asd_coherence(ITMX_data, ITMY_data, start_times, cutoff_freq)
