import foton
import kontrol
import matplotlib.pyplot as plt
import numpy as np
import control
from configparser import ConfigParser

config = ConfigParser()
config.read("../etc/config.ini")
ham = config.get('current_run','ham')
ff = foton.FilterFile(f"../etc/data/L1ISI{ham}.txt")

# Sensor Correction X

def sens_cor(ham,dof):
    s = control.tf("s")
    h_sc = s
    filter_fms = np.asarray((config.get(ham,f'SC_{dof}').split(',')), dtype='int')
    for fm in filter_fms:
        hsc_foton = ff[config.get( ham,f'SC_{dof}_filter_name')][fm-1]
        zpk = hsc_foton.get_zpk()
        print(zpk)
        h_sc_tf = kontrol.core.foton.get_zpk2tf(zpk)
        h_sc = h_sc * h_sc_tf
    return h_sc

def blend(ham, dof):
    s = control.tf("s")
    wn = 1*2*np.pi
    q = 1/np.sqrt(2)
    gs13_inv = (s**2+wn/q*s+wn**2) / s**3

    filter_fms_1 = np.asarray((config.get(ham,f'BLND_{dof}_1').split(',')), dtype='int')
    blnd_1 = 1
    for fm in filter_fms_1:
        hsc_foton = ff[config.get(ham,f'BLND_{dof}_1_filter_name')][fm-1]
        zpk = hsc_foton.get_zpk()
        h_blnd_1_tf = kontrol.core.foton.get_zpk2tf(zpk)
        blnd_1 = blnd_1 * h_blnd_1_tf
    
    filter_fms_2 = np.asarray((config.get(ham,f'BLND_{dof}_2').split(',')), dtype='int')
    blnd_2 = 1
    for fm in filter_fms_2:
        hsc_foton = ff[config.get(ham,f'BLND_{dof}_2_filter_name')][fm-1]
        zpk = hsc_foton.get_zpk()
        h_blnd_2_tf = kontrol.core.foton.get_zpk2tf(zpk)/ gs13_inv
        blnd_2 = blnd_2 * h_blnd_2_tf

    return blnd_1, blnd_2


def iso(ham,dof):
    iso = 1
    filter_fms = np.asarray((config.get(ham,f'ISO_{dof}').split(',')), dtype='int')
    for fm in filter_fms:
        iso_foton = ff[config.get(ham,f'ISO_{dof}_filter_name')][fm-1]
        zpk = iso_foton.get_zpk()
        iso_tf = kontrol.core.foton.get_zpk2tf(zpk)
        iso = iso * iso_tf
    return iso
