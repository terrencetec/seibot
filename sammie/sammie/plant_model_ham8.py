import control
import numpy as np
import matplotlib.pyplot as plt

def ham8_plant_x():
    data = np.loadtxt("l1_ham8_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3
    z_tf *= gs13_inv(1j*2*np.pi*f)

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    s = control.tf("s")
    w1 = 1.25*2*np.pi
    q1 = 1/0.9
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 12.5

    return f_, model

def ham8_plant_y():
    data = np.loadtxt("l1_ham8_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 3]
    z_imag = data[:, 4]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    
    s = control.tf("s")
    w1 = 1.25*2*np.pi
    q1 = 1/0.9
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 12.5

    return f_, model

def ham8_plant_z():
    data = np.loadtxt("l1_ham8_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 5]
    z_imag = data[:, 6]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    s = control.tf("s")
    w1 = 1.9*2*np.pi
    q1 = 1/0.7
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 6.5

    return f_, model


def noise_model_trans(f, a, b, q, na, nb):
    """Noise model"""

    noise =q*(((na/f**a)**2 + (nb/f**b)**2)**.5)
    return noise

def ham8_trans_x():
    data = np.loadtxt("l1_ham8_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    w1 = 1.25*2*np.pi
    q1 = 1/1.1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 0.95

    return f_, model

def ham8_trans_y():
    data = np.loadtxt("l1_ham8_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 3]
    z_imag = data[:, 4]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    w1 = 1.25*2*np.pi
    q1 = 1/1.1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 0.95

    return f_, model


def ham8_trans_z():
    data = np.loadtxt("l1_ham8_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 5]
    z_imag = data[:, 6]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    w1 = 1.825*2*np.pi
    q1 = 1/1.
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 1.05

    return f_, model


ham8_plant_x()
ham8_plant_y()
ham8_plant_z()
ham8_trans_x()
ham8_trans_y()
ham8_trans_z()