import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control
ff = foton.FilterFile("L1ISIHAM7.txt")

# Sensor Correction X

def ham7_sens_cor_x():
    s = control.tf("s")
    hsc_x_1 = ff["HAM7_SENSCOR_X_UNCOR_FILT1"][1]
    hsc_x_2 = ff["HAM7_SENSCOR_X_UNCOR_FILT1"][2]
    
    zpk_1 = hsc_x_1.get_zpk()
    zpk_2 = hsc_x_2.get_zpk()
    h_sc_tf_1 = kontrol.core.foton.get_zpk2tf(zpk_1)
    h_sc_tf_2 = kontrol.core.foton.get_zpk2tf(zpk_2)
    h_sc = s*h_sc_tf_1 * h_sc_tf_2
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)

    return f_, h_sc


def ham7_sens_cor_y():
    s = control.tf("s")
    hsc_y_1 = ff["HAM7_SENSCOR_Y_UNCOR_FILT1"][1]
    hsc_y_2 = ff["HAM7_SENSCOR_Y_UNCOR_FILT1"][2]
    
    zpk_1 = hsc_y_1.get_zpk()
    zpk_2 = hsc_y_2.get_zpk()
    h_sc_tf_1 = kontrol.core.foton.get_zpk2tf(zpk_1)
    h_sc_tf_2 = kontrol.core.foton.get_zpk2tf(zpk_2)
    h_sc = s*h_sc_tf_1 * h_sc_tf_2
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)

    return f_, h_sc



def ham7_sens_cor_z():
    s = control.tf("s")
    hsc_z_1 = ff["HAM7_SENSCOR_Z_NORM_FILT1"][0]
    
    zpk_1 = hsc_z_1.get_zpk()
    h_sc_tf_1 = kontrol.core.foton.get_zpk2tf(zpk_1)
    h_sc = s*h_sc_tf_1
    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)

    return f_, h_sc


def ham7_blend_x():
    s = control.tf("s")
    blend_1_a = ff["HAM7_BLND_X_SUPERSENS1_DISP"][0]
    blend_1_b = ff["HAM7_BLND_X_SUPERSENS1_DISP"][2]

    blend_1_a_zpk = blend_1_a.get_zpk()
    blend_1_b_zpk = blend_1_b.get_zpk()
    blnd_1 = kontrol.core.foton.get_zpk2tf(blend_1_a_zpk)*\
             kontrol.core.foton.get_zpk2tf(blend_1_b_zpk)
    

    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    blend_2 = ff["HAM7_BLND_X_SUPERSENS1_INERT_HI"][0]

    blend_2_zpk = blend_2.get_zpk()
    blnd_2 = kontrol.core.foton.get_zpk2tf(blend_2_zpk) / gs13_inv

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)

    return f_, blnd_1, blnd_2

def ham7_blend_y():
    s = control.tf("s")
    blend_1_a = ff["HAM7_BLND_Y_SUPERSENS1_DISP"][0]
    blend_1_b = ff["HAM7_BLND_Y_SUPERSENS1_DISP"][2]

    blend_1_a_zpk = blend_1_a.get_zpk()
    blend_1_b_zpk = blend_1_b.get_zpk()
    blnd_1 = kontrol.core.foton.get_zpk2tf(blend_1_a_zpk)*\
             kontrol.core.foton.get_zpk2tf(blend_1_b_zpk)
    

    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    blend_2 = ff["HAM7_BLND_Y_SUPERSENS1_INERT_HI"][0]

    blend_2_zpk = blend_2.get_zpk()
    blnd_2 = kontrol.core.foton.get_zpk2tf(blend_2_zpk) / gs13_inv

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)

    return f_, blnd_1, blnd_2


def ham_7_blend_z():
    s = control.tf("s")
    blend_1_a = ff["HAM7_BLND_Z_SUPERSENS1_DISP"][0]
    blend_1_b = ff["HAM7_BLND_Z_SUPERSENS1_DISP"][1]

    blend_1_a_zpk = blend_1_a.get_zpk()
    blend_1_b_zpk = blend_1_b.get_zpk()
    blnd_1 = kontrol.core.foton.get_zpk2tf(blend_1_a_zpk)*\
             kontrol.core.foton.get_zpk2tf(blend_1_b_zpk)
    

    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    blend_2 = ff["HAM7_BLND_Z_SUPERSENS1_INERT_HI"][0]

    blend_2_zpk = blend_2.get_zpk()
    blnd_2 = kontrol.core.foton.get_zpk2tf(blend_2_zpk) / gs13_inv

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    return f_, blnd_1, blnd_2


def ham7_iso_x():
    s = control.tf("s")
    cont3 = ff["HAM7_ISO_X"][3]
    boost3 = ff["HAM7_ISO_X"][7]

    cont3_zpk = cont3.get_zpk()
    boost3_zpk= boost3.get_zpk()
    iso_x = kontrol.core.foton.get_zpk2tf(cont3_zpk)*\
             kontrol.core.foton.get_zpk2tf(boost3_zpk)

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    return f_, iso_x

def ham7_iso_y():
    s = control.tf("s")
    cont3 = ff["HAM7_ISO_Y"][3]
    boost3 = ff["HAM7_ISO_Y"][7]

    cont3_zpk = cont3.get_zpk()
    boost3_zpk= boost3.get_zpk()
    iso_y = kontrol.core.foton.get_zpk2tf(cont3_zpk)*\
             kontrol.core.foton.get_zpk2tf(boost3_zpk)

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    return f_, iso_y

def ham7_iso_z():
    s = control.tf("s")
    cont3 = ff["HAM7_ISO_Z"][3]
    boost3 = ff["HAM7_ISO_Z"][7]

    cont3_zpk = cont3.get_zpk()
    boost3_zpk= boost3.get_zpk()
    iso_z = kontrol.core.foton.get_zpk2tf(cont3_zpk)*\
             kontrol.core.foton.get_zpk2tf(boost3_zpk)

    f_ = np.arange(0.0,256.0+0.001953125 , 0.001953125)
    return f_, iso_z

'''
    plt.loglog(f_, abs(h_sc(1j*2*np.pi*f_)))
    plt.grid(which="both")
    plt.show()

    plt.loglog(f_, abs(blnd_1(1j*2*np.pi*f_)))
    plt.loglog(f_, abs(blnd_2(1j*2*np.pi*f_)))
    plt.grid(which="both")
    plt.show()
'''