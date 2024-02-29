import control
import numpy as np
import matplotlib.pyplot as plt


def sensor_noise_sei():
    # measurements T240meas
    freq_data   = [ .01, .03,    .1,    0.3,    1,     3,     10,   100]
    noise_data  = [ 2*1.4e-7, 2e-8, 1.5e-9, 2e-10, 4e-11, 5e-12, 1.5e-12, 1e-13]

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    n_sei = noise_model(f_, a=2, b=1.1, na=10**-11, nb=10**-10.9)
    return f_, n_sei

def noise_model(f, a, b, na, nb):
    """Noise model"""

    noise = 1.5*((na/f**a)**2 + (nb/f**b)**2)**.5
    return noise

def sensor_noise_gs13():
    # measurements GS13 March 2007
    noise_data = [ 670, 6.32e-5, 2.138e-8, 1.958e-9, 1.892e-10, 1.732e-11,
                    7.262e-12, 3.887e-12, 2.449e-12, 1.462e-12, 9.725e-13, 
                    4.423e-13, 3.280e-13, 1.137e-13, 5.610e-14, 2.053e-14,
                    2e-15]   
    freq_data = [1e-4, 0.01, 0.101, 0.201, 0.400, 0.792, 0.994, 1.258, 1.655, 2.588, 
                 3.954, 8.202, 10.710, 24.796, 46.087, 91.208, 1e3]
    
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    n_gs13 = noise_model(f_, a=3.5, b=1.25, na=10**-11.5, nb=10**-11.5)
    return f_, n_gs13


def sensor_noise_cps_z():
	# ADE_p25 
    freq_data   = [0.001,   0.002,    0.01,      0.1,    0.7,    100]
    noise_data  = [1.5e-08, 2.7e-09, 7.5e-10, 1.5e-10, 6e-11, 6e-11]
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    n_cpsz = noise_model(f_, a=0.75, b=0, na=10**-10.8, nb=10**-10.4)

    return f_, n_cpsz


def sensor_noise_cps_xy():
	# ADE_1mm 
    freq_data   = [.001,  .002,  .01,    .1,    .7,    100]
    noise_data  = [ 5e-8, 9e-9, 2.5e-9, 5e-10, 2e-10, 2e-10]
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    n_cpsxy = noise_model(f_, a=0.74, b=0, na=10**-10.25, nb=10**-9.88)
    return f_, n_cpsxy
