# testing multiple filter 

import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control
import glob
import warnings
import vishack
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
dof = config.get('current_run','dof')
ham = config.get('current_run','ham')

function_dict = {
    "HAM7_X_plant" : plant_model_ham7.ham7_plant_x,
    "HAM7_Y_plant" : plant_model_ham7.ham7_plant_y,
    "HAM7_Z_plant" : plant_model_ham7.ham7_plant_z,
    "HAM7_X_trans" : plant_model_ham7.ham7_trans_x,
    "HAM7_Y_trans" : plant_model_ham7.ham7_trans_y,
    "HAM7_Z_trans" : plant_model_ham7.ham7_trans_z,    
    "HAM8_X_plant" : plant_model_ham8.ham8_plant_x,
    "HAM8_Y_plant" : plant_model_ham8.ham8_plant_y,
    "HAM8_Z_plant" : plant_model_ham8.ham8_plant_z,
    "HAM8_X_trans" : plant_model_ham8.ham8_trans_x,
    "HAM8_Y_trans" : plant_model_ham8.ham8_trans_y,
    "HAM8_Z_trans" : plant_model_ham8.ham8_trans_z, 

}

start_time = int(config.get('current_run','gpstime'))

start_time = int(config.get('current_run','gpstime'))
_, pg = function_dict[f'{ham}_{dof}_trans']()
f, xg, no_pad, n_seis = padded_ground_motion(start_time,dof)

def predict_motion(ham, dof, h_sc, h1, h2, f):
    _, pg = function_dict[f'{ham}_{dof}_trans']()
    k = -iso(ham, dof)
    _,p = function_dict[f'{ham}_{dof}_plant']()

    kp = k * p
    d = abs(pg(1j*2*np.pi*f)) * xg

    _, n_cps = sensor_noise_cps_xy(f)
    _, n_gs13 = sensor_noise_gs13(f)


    n_sc = kontrol.core.math.quad_sum(n_cps, abs(h_sc(1j*2*np.pi*f))*n_seis, abs((1-h_sc)(1j*2*np.pi*f))*xg)
    n = kontrol.core.math.quad_sum(abs(h1(1j*2*np.pi*f))*n_sc, abs(h2(1j*2*np.pi*f))*n_gs13)
    x = kontrol.core.math.quad_sum(abs((1/(1+kp))(1j*2*np.pi*f))*d, abs((kp/(1+kp))(1j*2*np.pi*f))*n)
    return f, x

h_sc = sens_cor(ham, dof)
h1, h2 = blend(ham, dof)
f, x = predict_motion(ham, dof, h_sc, h1, h2, f)
rms_dict = {}

bandwidth  = float(config.get('current_run','bandwidth'))
rms_val = kontrol.core.spectral.asd2rms(x[1:]*2*np.pi*f[1:], df=bandwidth, return_series=False)
rms_dict['current'] = rms_val 
plt.loglog(f, x, label=f"ISI {dof} motion default rms = {rms_val} nm/s")
rms_val =kontrol.core.spectral.asd2rms(xg[1:]*2*np.pi*f[1:], df=bandwidth, return_series=False)
rms_dict['ground_motion'] = rms_val 
plt.loglog(f, no_pad, label=f"ground displacement rms = {rms_val} nm/s")

hsc_prefilt = kontrol.load_transfer_function("../etc/data/h_sc_prefilt.pkl")
h2_prefilt = kontrol.load_transfer_function("../etc/data/h2_prefilter.pkl")
sc_files = glob.glob("../etc/data/filter_bank/sensor_correction_bank/*.*")
h1_files = glob.glob("../etc/data/filter_bank/h1_bank/*.*")
h2_files = glob.glob("../etc/data/filter_bank/h2_bank/*.*")


for i in range(len(sc_files)): 
    h_sc_hinf1 = kontrol.load_transfer_function(sc_files[i])
    for j in range(len(h1_files)):
        h1_hinf1 = kontrol.load_transfer_function(h1_files[j])
        h2_hinf1 = kontrol.load_transfer_function(h2_files[j])

        f_1,x_1 = predict_motion(ham, dof, h_sc_hinf1*hsc_prefilt, (1- h2_hinf1*h2_prefilt), h2_hinf1*h2_prefilt, f)
        new = 1- h_sc_hinf1*hsc_prefilt
        rms_val = kontrol.core.spectral.asd2rms(x_1*2*np.pi*f_1, df=bandwidth, return_series=False)
        print(rms_val)
        plt.loglog(f_1, x_1, label=f"ISI {dof} motion filter {sc_files[i].split('/')[-1]} + {h1_files[j].split('/')[-1]}  rms = {rms_val} nm")

        print(f"{sc_files[i].split('/')[-1]} + {h1_files[j].split('/')[-1]}")
        rms_dict[f"{sc_files[i].split('/')[-1]} + {h1_files[j].split('/')[-1]}"] = rms_val 

temp = min(rms_dict.values())
res = [key for key in rms_dict if rms_dict[key] == temp]
print("Keys with minimum values are : " + str(res))


import nds2
from sammie.data import padded_ground_motion, fetch_timeseries_data
import matplotlib.pyplot as plt

start_time = int(config.get('current_run','gpstime'))
averages = int(config.get('current_run','averages'))
coherence_overlap = float(config.get('current_run','coherence_overlap'))
fftlen = int(config.get('current_run','coherence_fftlen'))
end_time = start_time + (averages*coherence_overlap +1)*fftlen

gs13_timeseries = fetch_timeseries_data(f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, mode='cdsutils')
t240_timeseries = fetch_timeseries_data(f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ", start_time, end_time, mode='cdsutils')

gs13_resampled = gs13_timeseries.resample(512)
t240_resampled = t240_timeseries.resample(512)

asd_gs13 = gs13_resampled.asd(fftlength=fftlen,overlap=coherence_overlap)
asd_t240 = t240_resampled.asd(fftlength=fftlen,overlap=coherence_overlap)

s = control.tf("s")
wn = 1*2*np.pi
q = 1/np.sqrt(2)
gs13_inv = (s**2+wn/q*s+wn**2) / s**3
t240_inv = 1/s


asd_gs13_corrected = abs(gs13_inv(1j*2*np.pi*f))*asd_gs13.value[1:]
asd_t240_corrected = abs(t240_inv(1j*2*np.pi*f))*asd_t240.value[1:]

h2 = kontrol.load_transfer_function(h2_files[0])

_, n_gs13 = sensor_noise_gs13(f)
new = abs(h2(1j*2*np.pi*f))*n_gs13
plt.loglog(f,n_seis, label="Seismometer noise")
plt.loglog(f,n_gs13, label="GS13 noise")
plt.loglog(f,new, label="product")

#plt.loglog(asd_a.frequencies, asd_a_corrected, label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ")
plt.loglog(asd_gs13.frequencies[1:], asd_gs13_corrected, label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ")
plt.loglog(asd_t240.frequencies[1:], asd_t240_corrected, label=f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ")

plt.legend(prop={'size': 6})
plt.show()

