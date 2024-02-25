import control
import numpy as np
import matplotlib.pyplot as plt

def noise_model(f, a, b,q,  na, nb):
    """Noise model"""

    noise =q*1/ (((na/f**a)**2 + (nb/f**b)**2)**.5)
    return noise

def ham7_plant_x():
    data = np.loadtxt("l1_ham7_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 165
    plant_ham7_x = noise_model(f_, a=0.0, b=-2.25,q=q, na=10, nb=4)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham7_x , label="model")
    plt.title("ham7 Plant X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_x.png", dpi=300)
    return f_, plant_ham7_x

def ham7_plant_y():
    data = np.loadtxt("l1_ham7_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 3]
    z_imag = data[:, 4]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 165
    plant_ham7_y = noise_model(f_, a=0.1, b=-2.2,q=q, na=10, nb=5)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham7_y , label="model")
    plt.title("ham7 Plant Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_y.png", dpi=300)
    return f_, plant_ham7_y

def ham7_plant_z():
    data = np.loadtxt("l1_ham7_plant_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 5]
    z_imag = data[:, 6]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 90
    plant_ham7_z = noise_model(f_, a=0.25, b=-2.2,q=q, na=10, nb=2)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham7_z , label="model")
    plt.title("ham7 Plant Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_z.png", dpi=300)
    return f_, plant_ham7_z

def noise_model_trans(f, a, b, q, na, nb):
    """Noise model"""

    noise =q*(((na/f**a)**2 + (nb/f**b)**2)**.5)
    return noise

def ham7_trans_x():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    q = 0.25
    f_ = np.arange(0.0,200.0, 0.001953125)
    trans_ham7_x = noise_model_trans(f_, a=2.9, b=0,q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham7_x , label="model")
    plt.title("ham7 trans X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_x.png", dpi=300)
    return f_, trans_ham7_x

def ham7_trans_y():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 3]
    z_imag = data[:, 4]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 0.25
    trans_ham7_y = noise_model_trans(f_, a=2.9, b=0,q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham7_y , label="model")
    plt.title("ham7 trans Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_y.png", dpi=300)
    return f_, trans_ham7_y

def ham7_trans_z():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 5]
    z_imag = data[:, 6]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 0.30
    trans_ham7_z = noise_model_trans(f_, a=2.6, b=0, q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham7_z , label="model")
    plt.title("ham7 trans Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_z.png", dpi=300)
    return f_, trans_ham7_z

ham7_plant_x()
ham7_plant_y()
ham7_plant_z()
ham7_trans_x()
ham7_trans_y()
ham7_trans_z()