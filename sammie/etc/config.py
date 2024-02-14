# Channels to be used

channel_list = [
    "L1:ISI-GND_STS_ETMX_X_DQ"
    "L1:ISI-GND_STS_ETMX_Y_DQ"
    "L1:ISI-GND_STS_ETMX_Z_DQ"
    "L1:ISI-GND_STS_ETMY_X_DQ"
    "L1:ISI-GND_STS_ETMY_Y_DQ"
    "L1:ISI-GND_STS_ETMY_Z_DQ"
    "L1:ISI-GND_STS_HAM5_X_DQ"
    "L1:ISI-GND_STS_HAM5_Y_DQ"
    "L1:ISI-GND_STS_HAM5_Z_DQ"
    "L1:ISI-GND_STS_ITMX_X_DQ"
    "L1:ISI-GND_STS_ITMX_Y_DQ"
    "L1:ISI-GND_STS_ITMX_Z_DQ"
    "L1:ISI-GND_STS_ITMY_X_DQ"
    "L1:ISI-GND_STS_ITMY_Y_DQ"
    "L1:ISI-GND_STS_ITMY_Z_DQ"]

# Coherence calculation settings
sample_rate = 512
coherence_fftlen = 512
coherence_overlap = 0.5
averages = 50


# Sample gps times from threshold exercise
gps_sample_list = [
    1386201618,
    1385596818,
    1385164818,
    1385078418,
    1384732818,
    1384473618,
    1383264018,
    1383091218,
    1382745618,
    1382486218,
    1382313618,
    1381536018,
    1381363218
]

# frequency binnning for finding cutoff
bin_width = 10
coherence_diff = 0.5