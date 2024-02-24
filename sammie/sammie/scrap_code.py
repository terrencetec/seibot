
from gwpy.timeseries import TimeSeries
from etc import config
import numpy as np
from scipy.signal import coherence
from scipy.signal import argrelextrema
from scipy import optimize
import matplotlib.pyplot as plt
import nds2


def coherence_calculator(data_A, data_B):
    rate = data_A.sample_rate.value
    f,coh = coherence(data_A.value,data_B.value, fs=rate, nperseg=rate*512, noverlap=rate*512/2)
    return f,coh


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

def frequency_minima_withscipy(data_A, data_B):

    f,coh = coherence_calculator(data_A, data_B)

    # find the point where there is max coherence
    rounded_coh = np.round(coh, 2)
    first_one_coh = np.min(np.where(rounded_coh == 1.00))

    # from that frequency position to 0 make freq-bins of given width and check for 
    # coherence difference in each bin
    check_array = np.arange(first_one_coh, 0, -1)

    for i in range(len(check_array)):
        
        try:
            sub_array = rounded_coh[check_array[i+config.bin_width]:check_array[i]]     
            min = argrelextrema(sub_array, np.less)
            min_pos_ar = min[0]
            if len(min_pos_ar) != 0:
                print(sub_array[min[0]])
                print(np.max(np.where(rounded_coh[0:first_one_coh] == sub_array[min_pos_ar[0]])))
                frequency = f[np.max(np.where(rounded_coh[0:first_one_coh] == sub_array[min_pos_ar[0]]))]
                
                if sub_array[min[0][0]] < 0.4:
                    return frequency
                    break
        except:
            print("reached the end. Substituting default check")
            min_coh = np.min(rounded_coh[0:first_one_coh])
            last_one_coh = np.max(np.where(rounded_coh[0:first_one_coh] == min_coh))
            frequency = f[last_one_coh]

    return frequency