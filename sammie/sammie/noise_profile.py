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
from sammie.data import padded_ground_motion, fetch_timeseries_data, conditional_n_sei
from sammie.gs13_noise import get_tilt_gs13
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
f = f[1:]
_, xg, no_pad, n_seis = padded_ground_motion(start_time,dof)


k = -iso(ham, dof)
_,p = function_dict[f'{ham}_{dof}_plant']()

kp = k * p

pg = p/p.dcgain()
d = abs(pg(1j*2*np.pi*f)) * xg

_, n_cps = sensor_noise_cps_xy(f)
#_, n_seis = sensor_noise_sei()
_, n_gs13 = sensor_noise_gs13(f)
#n_gs13 = get_tilt_gs13()
h_sc = sens_cor(ham, dof)
h1, h2 = blend(ham, dof)

n_sc = kontrol.core.math.quad_sum(n_cps, abs(h_sc(1j*2*np.pi*f))*n_seis, abs((1-h_sc)(1j*2*np.pi*f))*xg)

n = kontrol.core.math.quad_sum(abs(h1(1j*2*np.pi*f))*n_sc, abs(h2(1j*2*np.pi*f))*n_gs13)

x = kontrol.core.math.quad_sum(abs((1/(1+kp))(1j*2*np.pi*f))*d, abs((kp/(1+kp))(1j*2*np.pi*f))*n)

plt.loglog(f, no_pad, label="ground displacement")
plt.loglog(f,n_seis, label="Seismometer noise")
plt.loglog(f,n_gs13, label="gs13 noise")
#plt.loglog(f,n_cps, label="cps noise")
plt.loglog(f,n_sc, label="n_sc")
plt.loglog(f,abs(h_sc(1j*2*np.pi*f))*n_seis, label="hsc * seis noise")
#plt.loglog(f,abs((1-h_sc)(1j*2*np.pi*f))*xg, label="1- hsc * ground motion")
plt.loglog(f,abs(h1(1j*2*np.pi*f))*n_sc, label=" h1 * n_sc")
plt.loglog(f,abs(h2(1j*2*np.pi*f))*n_gs13, label=" h2 * gs13")
plt.loglog(f,n, label="n blend")
plt.loglog(f,abs((1/(1+kp))(1j*2*np.pi*f))*d, label="first term")
plt.loglog(f,abs((kp/(1+kp))(1j*2*np.pi*f))*n, label="second term")
plt.legend()
plt.show()