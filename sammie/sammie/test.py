from etc import config
import nds2
import control
import numpy as np
from sammie.data import padded_ground_motion, fetch_timeseries_data
import matplotlib.pyplot as plt

conn = nds2.connection('nds.ligo-la.caltech.edu',31200)

print((config.averages*config.coherence_overlap +1)*config.coherence_fftlen)
'''
gs13_timeseries = fetch_timeseries_data("L1:ISI-HAM7_BLND_GS13X_IN1_DQ", 1386201618,1386201618  + 
                         (config.averages*config.coherence_overlap +1)*config.coherence_fftlen, conn)

print(gs13_timeseries.dt)
print(len(gs13_timeseries))
asd_a = gs13_timeseries.asd(fftlength=512,overlap=0.5)

print(asd_a.df)
print(len(asd_a.value))
print(len(asd_a.frequencies))
s = control.tf("s")
wn = 1*2*np.pi
q = 1/np.sqrt(2)
gs13_inv = (s*(s**2+wn/q*s+wn**2)) / s**3

asd_a_corrected = abs(gs13_inv(1j*2*np.pi*f)) * asd_a.value

plt.loglog(f, x*1e-9, label="motion")
plt.loglog(f, no_pad*1e-9, label="xg")
#plt.loglog(f, xg, label='padded')
plt.legend()
plt.loglog(asd_a.frequencies, asd_a_corrected, label="ISO_X output")
plt.show()
'''