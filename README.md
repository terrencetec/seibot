# Seibot

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

## Python scripting
### High-level usage

#### seibot.Seibot
`seibot.Seibot` is the main class interfacing the lower-level submodules
that interface the data and configuration files, produce real-time estimation
of isolation performances and inform optimal filter selections.

Construct a `Seibot` instance:
```
import seibot


config = ...
ham8_seibot = seibot.Seibot(config)
```

This initiates a `Seibot` instance that contains attributes that parse the
config compile necessary information for real-time estimation.

The simplest usage is the `get_best_filters()` method
```
best_filters = ham8_seibot.get_best_filters()
```
This returns a tuple in the form
`(sensor correction filter, (low-pass filter, high-pass filter))`.
The filters are `seibot.Filter` instances that contain the
information of the filters. See [seibot.Filter](#seibotfilter).

To export the information for further usages,
use the method `export_best_filter(path)`.
```
path = ...
ham8_seibot.export_best_filter(path)
```
This exports the filters information to a configuration file in the format
```
[Sensor correction filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 1

[Low-pass filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_BLND_Y_SUPERSENS6_DISP
fm = 1

[High-pass filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_BLND_Y_SUPERSENS6_INERT_HI
fm = 1, 10
```
This configuration file is the output of Seibot and  is meant to be further
further inferface with the Guardian state machine or other programs that
enact these changes.

### Intermediate-level usage
#### seibot.IsolationSystem
An `IsolationSystem` is initialized with 5 arguments
`relative_sensor`, `inertial_sensor`, `seisometer`,
`plant`, and `transmissivity`, which are `seibot.Sensor` and `seibot.Process`
instances.
These characterizes the hardware capability of the isolation system.
```
import seibot


relative_sensor = seibot.Sensor(f, relative_sensor_noise)
...
transmissivity = seibot.Process(tf_transmissivity)

ham8 = seibot.IsolationSystem(relative_sensor, inertial_sensor, seismometer...)
```
An alternative way to obtain an `IsolationSystem` instance is via
the `Seibot.get_isolation_system()` method.
```
import seibot


config = ...
ham8_seibot = seibot.Seibot(config)

ham8 = ham8_seibot.get_isolation_system()
```

The `IsolationSystem` can be installed with sensor correction filters
and complementary filters (blends).
```
sensor_correction_filter = ...
low_pass_filter = ...
high_pass_filter = ...

ham8.sensor_correction_filter = sensor_correction_filter
ham8.low_pass_filter = low_pass_filter
ham8.high_pass_filter = high_pass_filter
```

Alternatively, install a isolation configuration.
```
isolation_configuration = (sensor_correction_filter, (low_pass_filter, high_pass_filter))

ham8.isolation_configuration = isolation_configuration
```

With the filters installed, the closed-loop displacement can be obtained:
```
f = ...  # Frequency array
seismic_noise = ...

displacement = ham8.get_displacement(f, seismic_noise)
```



#### seibot.sensor

#### seibot.Filter


`seibot.IsolationSystem` is a class that defines an isolation platform, such
as the LIGO HAM-ISI.


# Configuration files
## Seibot configuration

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
`[Channels]`, `[CDSutils]`, and `[Welch]`.
The second group contain sections
`[Seismic]`, `[Seismometer]`, `[Inertial sensor]`, `[Relative sensor]`,
`[Plant]`, and `[Transmissivity]`.
The third group contains sections
`[Sensor correction filters]`, `[Low pass filters]`, and `[High pass filters]`.


`[Channels]` section

 - `seismometer`: The channel name of the sensor correction seismometer.
 Readout should be raw in velocity. The seismic noise and seismometer noise
 are estimated using this readout.
 - `seismometer_coh`: The channel name of a seismometer reading a coherent
ground motion to the sensor correction seisometer. This is used to determine
the frequency at which the seismometer readout is dominated by noise/signal.

`[CDSutils]` section

- `duration`: Duration of data in the past to be taken (seconds).
- `start`: The start time of the data segment (GPS time). This is optional.
- Remove this option will default to start now.

`[Welch]` section
- `nperseg`: Number of data per segment used in Welch.
- `fs`: Sampling frequency.

`[Seismic]`, `[Seismometer]`, `[Inertial sensor]`, `[Relative sensor]`,
`[Plant]`, `[Transmissivity]` sections:

- `model`: Empirical/transfer function model selected from `seibot.model`.
- `parameters_path`: Path of the model parameter file.
- `dynamic`: Dynamically modelling. If true, parameters are not used and
modeling using internal method.

`[Sensor correction filters]`, `[Low pass filters]`, `[High pass filters]`
sections:

- `config`: The path of the filter pool configuration file.
- `inverse_filter`: Optional. The inverse filter to be applied.


## Filter pool configuration file.

Shown below is an example of a configuration file defining the pool of
sensor correction filters.
The filter pool contains 9 sensor correction filters named
`[low_low]`, `[low_mid]`...

```
[low_low]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 1, 10

[low_mid]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 2, 10

[low_high]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 3, 10

[mid_low]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 4, 10

[mid_mid]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 5, 10

[mid_high]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 6, 10

[high_low]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 7, 10

[high_mid]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 8, 10

[high_high]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 9, 10
```

Each section in the configuration file correspond to one filter.
The section name, e.g. `[low_low]`, is just a label and is not referenced.

Each section contains 3 variables:

- `filter_file`: The path of the foton filter file.
- `module`: The filter module name.
- `fm`: The engaged FMs. Comma separated.


## Model parameters

The model parameter files are simple text files with model parameters listed
out space separated.

This is an example of a parameter file specifying 4 parameters for
`seibot.model.Model.noise2()`.

```
5.6234133e-11 1.3182567e-10 0.74 0
```



# Repository structure

- **data**: Fetch and process timeseries data from CDS.
- **model**: Frequency domain modeling tools for dynamic noise modeling.
- **foton**: Foton wrapper to access real-time filter modules.
- **forecast**: Real-time forecast platform motion.
- **filter**: Interface with filter pool configuration files and construct
filter pools.
- **isolation_system**: Isolation system class with defined sensor performances
.
- **evaluate**: Evaluate isolation system performances.
- **seibot**: Interface main configuration file and integrate submodules and 
	obtain best real-time isolation configuration.

Read issues: https://github.com/terrencetec/sammie/issues/1
