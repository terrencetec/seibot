from gwpy.timeseries import TimeSeries
from etc import config
import numpy as np
from scipy.signal import coherence
import matplotlib.pyplot as plt



def fetch_timeseries_data(channel, gps_start, gps_end):
    data = TimeSeries.fetch(channel, gps_start, gps_end, allow_tape=True)
    return data


def coherence_calculator(data_A, data_B):
    rate = data_A.sample_rate.value
    f,coh = coherence(data_A.value,data_B.value, fs=rate, nperseg=rate*512, noverlap=rate*512/2)
    return f,coh


def plot_asd_coherence(data_A, data_B, start_times, cutoff_freq=None):

    f,coh = coherence_calculator(data_A, data_B)
    fig, (ax1,ax2) = plt.subplots(2,1, sharex=True, figsize=(15,6))
    asd_a = ITMX_data.asd(fftlength=512,overlap=0.5)
    asd_b = ITMY_data.asd(fftlength=512,overlap=0.5)
    ax1.plot(asd_a.frequencies, asd_a.value, label="ITMX")
    ax1.plot(asd_b.frequencies, asd_b.value, label="ITMY")
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




def frequency_minima_calculator(data_A, data_B):

    f,coh = coherence_calculator(data_A, data_B)

    # find the point where there is max coherence
    rounded_coh = np.round(coh, 2)
    first_one_coh = np.min(np.where(rounded_coh == 1.00))
    corresponding_f = f[first_one_coh]

    # from that frequency position to 0 make freq-bins of given width and check for 
    # coherence difference in each bin
    check_array = np.arange(first_one_coh, 0, -config.bin_width)

    for i in range(len(check_array)):
        try:
            sub_array = rounded_coh[check_array[i+1]:check_array[i]]
            min_sub_array = np.min(sub_array)
            max_sub_array = np.max(sub_array)
            diff = max_sub_array - min_sub_array
            if diff > config.coherence_diff:
                location_within_subarray = np.where(sub_array == min_sub_array)[0]
                indices_in_superarray = np.arange(check_array[i+1],check_array[i])
                frequency = f[indices_in_superarray[location_within_subarray[0]]]
                break
        except:
            print("reached the end. Substituting default check")
            min_coh = np.min(rounded_coh[0:first_one_coh])
            last_one_coh = np.max(np.where(rounded_coh[0:first_one_coh] == min_coh))
            frequency = f[last_one_coh]

    return frequency


for start_times in config.gps_sample_list:
    # Checking coherence between ETMX and ITMX ground sensors
    print(start_times)

    ITMX_data = fetch_timeseries_data('L1:ISI-GND_STS_ITMX_X_DQ',
                                    start_times, start_times + 
                                    (config.averages*config.coherence_overlap +1)*config.coherence_fftlen )
    ITMY_data = fetch_timeseries_data('L1:ISI-GND_STS_ITMY_X_DQ',
                                    start_times, start_times + 
                                    (config.averages*config.coherence_overlap +1)*config.coherence_fftlen )
    print("done")
    cutoff_freq = frequency_minima_calculator(ITMX_data, ITMY_data)
    plot_asd_coherence(ITMX_data, ITMY_data, start_times, cutoff_freq)