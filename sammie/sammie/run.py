import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

import configparser
# X motion
from sammie import plant_model_ham7
from sammie import plant_model_ham8 

from sammie.blend_sc_iso import sens_cor, blend, iso
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13, sensor_noise_sei
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
f, pg = function_dict[f'{ham}_{dof}_trans']()
_, xg, no_pad = padded_ground_motion(start_time,dof)


k = iso(ham, dof)
_,p = function_dict[f'{ham}_{dof}_plant']()

kp = k * p

d = abs(pg(1j*2*np.pi*f)) * xg

_, n_cps = sensor_noise_cps_xy()
_, n_seis = sensor_noise_sei()
_, n_gs13 = sensor_noise_gs13()

h_sc = sens_cor(ham, dof)
h1, h2 = blend(ham, dof)

n_sc = kontrol.core.math.quad_sum(n_cps, abs(h_sc(1j*2*np.pi*f))*n_seis, abs((1-h_sc)(1j*2*np.pi*f))*xg)

n = kontrol.core.math.quad_sum(abs(h1(1j*2*np.pi*f))*n_sc, abs(h2(1j*2*np.pi*f))*n_gs13)

x = kontrol.core.math.quad_sum(abs((1/(1+kp))(1j*2*np.pi*f))*d, abs((kp/(1+kp))(1j*2*np.pi*f))*n)



import nds2
from sammie.data import padded_ground_motion, fetch_timeseries_data
import matplotlib.pyplot as plt

conn = nds2.connection('nds.ligo-la.caltech.edu',31200)
start_time = int(config.get('current_run','gpstime'))
averages = int(config.get('current_run','averages'))
coherence_overlap = float(config.get('current_run','coherence_overlap'))
fftlen = int(config.get('current_run','coherence_fftlen'))
end_time = start_time + (averages*coherence_overlap +1)*fftlen

gs13_timeseries = fetch_timeseries_data(f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ", start_time, end_time, conn, mode='cdsutils')

gs13_resampled = gs13_timeseries.resample(512)
asd_a = gs13_resampled.asd(fftlength=fftlen,overlap=coherence_overlap)


s = control.tf("s")
wn = 1*2*np.pi
q = 1/np.sqrt(2)
gs13_inv = (s**2+wn/q*s+wn**2) / s**3
#t240_inv = 1/s


asd_a_corrected = abs(gs13_inv(1j*2*np.pi*f)) * asd_a.value

plt.loglog(f, x*1e-9, label=f"ISI {dof} motion")
plt.loglog(f, no_pad*1e-9, label="ground displacement")
#plt.loglog(f, xg, label='padded')

plt.loglog(asd_a.frequencies, asd_a_corrected *1e-9, label=f"L1:ISI-{ham}_BLND_GS13{dof}_IN1_DQ")
#plt.loglog(asd_a.frequencies, asd_a_corrected *1e-9, label=f"L1:ISI-{ham}_BLND_T240{dof}_IN1_DQ")
plt.legend()
plt.show()