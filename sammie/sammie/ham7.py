import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

# X motion
from sammie.plant_model_ham7 import ham7_plant_x, ham7_trans_x
from sammie.blend_sc_iso_ham7 import ham7_sens_cor_x, ham7_blend_x, ham7_iso_x
from sammie.sensor_noise_model import sensor_noise_cps_xy, sensor_noise_gs13, sensor_noise_sei
from sammie.data import padded_ground_motion


f, pg = ham7_trans_x()
print(f)
_, xg, _ = padded_ground_motion(1386201618)



_,k = ham7_iso_x()
_,p = ham7_plant_x()

kp = k * p

d = abs(pg(1j*2*np.pi*f)) * xg

_, n_cps = sensor_noise_cps_xy()
_, n_seis = sensor_noise_sei()
_, n_gs13 = sensor_noise_gs13()

_, h_sc = ham7_sens_cor_x()
_, h1, h2 = ham7_blend_x()

n_sc = kontrol.core.math.quad_sum(n_cps, abs(h_sc(1j*2*np.pi*f))*n_seis, abs((1-h_sc)(1j*2*np.pi*f))*xg)

n = kontrol.core.math.quad_sum(abs(h1(1j*2*np.pi*f))*n_sc, abs(h2(1j*2*np.pi*f))*n_gs13)

x = kontrol.core.math.quad_sum(abs((1/(1+kp))(1j*2*np.pi*f))*d, abs((kp/(1+kp))(1j*2*np.pi*f))*n)

plt.loglog(f, x)
plt.show()