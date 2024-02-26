import control
import numpy as np
import matplotlib.pyplot as plt

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
    s = control.tf("s")
    w1 = 1.3*2*np.pi
    q1 = 1/1.1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 15
    plt.clf()
    plt.loglog(f, abs(z_tf))

    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 Plant X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_x.png", dpi=300)
    return f_, model

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
    s = control.tf("s")
    w1 = 1.3*2*np.pi
    q1 = 1/1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 14
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 Plant Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_y.png", dpi=300)
    return f_, model

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
    s = control.tf("s")
    w1 = 1.9*2*np.pi
    q1 = 1/0.7
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 6.5
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 Plant Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/plant_ham7_z.png", dpi=300)
    return f_, model

def ham7_trans_x():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,200.0, 0.001953125)
    w1 = 1.3*2*np.pi
    q1 = 1/1.1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 1.03
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 trans X Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_x.png", dpi=300)
    return f_, model

def ham7_trans_y():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 3]
    z_imag = data[:, 4]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,200.0, 0.001953125)
    w1 = 1.3*2*np.pi
    q1 = 1/1.1
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 1.05
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 trans Y Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_y.png", dpi=300)
    return f_, model


def ham7_trans_z():
    data = np.loadtxt("l1_ham7_trans_xyz.txt")
    f = data[:, 0]
    z_real = data[:, 5]
    z_imag = data[:, 6]
    z_tf = z_real + 1j*z_imag

    s = control.tf("s")
    f_ = np.arange(0.0,200.0, 0.001953125)
    w1 = 1.825*2*np.pi
    q1 = 1/1.
    model = w1**2 / (s**2+w1/q1*s+w1**2) * 1.05
    plt.clf()
    plt.loglog(f, abs(z_tf))
    plt.loglog(f_, abs(model(1j*2*np.pi*f_)), label="model")
    plt.title("ham7 trans Z Dof")
    plt.grid(which="both")
    plt.legend()
    plt.savefig("../temp_analysis/trans_ham7_z.png", dpi=300)
    return f_, model


ham7_plant_x()
ham7_plant_y()
ham7_plant_z()
ham7_trans_x()
ham7_trans_y()
ham7_trans_z()