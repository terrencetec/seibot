import control
import numpy as np
import matplotlib.pyplot as plt

def noise_model(f, a, b,q,  na, nb):
    """Noise model"""

    noise =q*1/ (((na/f**a)**2 + (nb/f**b)**2)**.5)
    return noise

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
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 160
    plant_ham8_x = noise_model(f_, a=0.1, b=-2.2,q=q, na=10, nb=5)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham8_x , label="model")
    plt.title("HAM8 Plant X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham8_x.png", dpi=300)
    return f_, plant_ham8_x

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
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 160
    plant_ham8_y = noise_model(f_, a=0.1, b=-2.2,q=q, na=10, nb=5)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham8_y , label="model")
    plt.title("HAM8 Plant Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham8_y.png", dpi=300)
    return f_, plant_ham8_y

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
    f_ = np.arange(0.0,200.0, 0.001953125)
    q = 110
    plant_ham8_z = noise_model(f_, a=0.3, b=-2.2,q=q, na=11, nb=3)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,plant_ham8_z , label="model")
    plt.title("HAM8 Plant Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham8_z.png", dpi=300)
    return f_, plant_ham8_z


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
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    z_tf *= gs13_inv(1j*2*np.pi*f)
    q = 0.22
    f_ = np.arange(0.0,200.0, 0.001953125)
    trans_ham8_x = noise_model_trans(f_, a=2.9, b=0,q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham8_x , label="model")
    plt.title("ham8 trans X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham8_x.png", dpi=300)
    return f_, trans_ham8_x

def ham8_trans_y():
    data = np.loadtxt("l1_ham8_trans_xyz.txt")
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
    q = 0.22
    trans_ham8_y = noise_model_trans(f_, a=2.9, b=0,q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham8_y , label="model")
    plt.title("ham8 trans Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham8_y.png", dpi=300)
    return f_, trans_ham8_y

def ham8_trans_z():
    data = np.loadtxt("l1_ham8_trans_xyz.txt")
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
    q = 0.27
    trans_ham8_z = noise_model_trans(f_, a=2.6, b=0, q=q, na=1, nb=0)
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_,trans_ham8_z , label="model")
    plt.title("ham8 trans Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham8_z.png", dpi=300)
    return f_, trans_ham8_z

ham8_plant_x()
ham8_plant_y()
ham8_plant_z()
ham8_trans_x()
ham8_trans_y()
ham8_trans_z()