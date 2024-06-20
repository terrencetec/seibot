# SeiBot

Semi-adaptive seismic isolation control framework for LIGO

# Installation

## Create conda environment and install dependencies
```
conda create -n [environment] -c conda-forge python=3.9 cdsutils control numpy
matplotlib python-foton scipy
```
Only `python<=3.9` works for now due to LIGO dependencies.

## Install seibot

Clone repository
```
git clone https://github.com/terrencetec/seibot.git
```

Change directory
```
cd seibot
```

Install using `pip`
```
pip install .
```

# Usage

## Quick start
Seibot supports command line usages

## Command line usage
Get sample configuration files.
```
seibot --get-seibot-config -p [path]
```

Get filter configuration files.
```
seibot --get-filter-config -p [path]
```

Get model parameters.
```
seibot --get-model-parameters -p [path]
```

Run Seibot.
```
seibot --config [config]
```
This outputs a configuration file that states the best
seismic isolation configuration.

## Configuration files
### Seibot configuration
Here is an example configuration file.
```
[Channels]
seismometer = L1:ISI-GND_STS_HAM8_Y_DQ
seismometer_coh = L1:ISI-GND_STS_ITMY_Y_DQ

[CDSutils]
duration = 4096
start = 1399680018

[Welch]
nperseg = 524288
fs = 512


[Seismic]
model = second_order_plant
parameters_path = ../model_parameters/seismic.txt
dynamic = False

[Seismometer]
model = noise2
parameters_path = ../model_parameters/sts.txt
dynamic = False

[Inertial sensor]
model = noise2
parameters_path = ../model_parameters/gs13.txt
dynamic = False

[Relative sensor]
model = noise2
parameters_path = ../model_parameters/cps.txt
dynamic = False

[Plant]
model = second_order_plant
parameters_path = ../model_parameters/plant.txt
dynamic = False

[Transmissivity]
model = second_order_plant
parameters_path = ../model_parameters/transmissivity.txt
dynamic = False


[Sensor correction filters]
config = ../config/sesnor_correction_filters.ini
inverse_filter = sts

[Low pass filters]
config = ../config/low_pass_filters.ini

[High pass filters]
config = ../config/high_pass_filters.ini
inverse_filter = gs13
```

The seibot configuration file contains 3 groups of sections.
The first group contains sections
`[Channels]`, `[CDSutils]`, and ``[Welch]`.
The second group contain sections
`[Seismic]`, `[Seismometer]`, `[Inertial sensor]`, `[Relative sensor]`,
`[Plant]`, and `[Transmissivity]`.
The third group contains sections
`[Sensor correction filters]`, `[Low pass filters]`, and `[High pass filters]`.

In the `[Channels]` section, two parameters are required.

 - `seismometer`: The channel name of the sensor correction seismometer.
 Readout should be raw in velocity. The seismic noise and seismometer noise
 are estimated using this readout
 - `seismometer_coh`: The channel name of a seismometer reading a coherent
ground motion to the sensor correction seisometer. This is used to determine
frequency at which the seismometer readout is dominated by noise/signal.


# Repository structure

- **data**: Fetch and process timeseries data from CDS.
- **model**: Frequency domain modeling tools for dynamic noise modeling.
- **foton**: Foton wrapper to access real-time filter modules.
- **forecast**: Real-time forecast platform motion

Read issues: https://github.com/terrencetec/sammie/issues/1
