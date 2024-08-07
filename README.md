# Seibot

Semi-adaptive seismic isolation control framework for LIGO

**Table of content**
- [Introduction](#introduction)
- [Installation](#installation)
- [Step-by-step tutorial](#step-by-step-tutorial)
- [Usage](#usage)
	- [Command line](#command-line)
	- [Python scripting](#python-scripting)
		- [High-level usage](#high-level-usage)
		- [Intermediate-level usage](#intermediate-level-usage)
		- [Low-level usage](#low-level-usage)
- [Configuration files](#configuration-files)
	- [Seibot configuration](#seibot-configuration)
	- [Filter pool configuration](#filter-pool-configuration)
	- [Model parameters configuration](#model-parameters-configuration)
- [Seibot output file](#seibot-output-file)
- [Repository structure](#repository-structure)

# Introduction
`Seibot` is a Python package that defines a real-time optimal control
filter selection framework, i.e. semi-adaptive control,
for seismic isolation systems at LIGO.
In a nutshell, `Seibot` does the followings

1. Fetch real-time seismic and isolation system data using CDSutils.
2. Model seismic noises, sensor noises, and system dynamics.
3. Compile all available sensor correction and sensor fusion
   complementary filters, i.e. blends, from Foton.
4. Predict the all possible real-time seismic isolation performances
   using all combinations of sensor correction and blends.
5. Select the best combination of filters base on some optimal criteria.
6. Inform the best filters by outputing a configuration file.

These functionalities are supported by the main classes of `seibot`, namely

1. `seibot.Data`
2. `seibot.Filter`
3. `seibot.IsolationSystem`
4. `seibot.Evaluate`
5. `seibot.Seibot`

![](https://github.com/terrencetec/seibot/blob/0c3cca83396ed06fdb766438cb6953c8fdadb1e1/images/flowchart.png)
The `seibot.Data` class interfaces the CDS environment and local database to
obtain estimates or models of seismic noise, sensor noises, and plant models
using real-time signals.
These information can be used to initialize `seibot.Sensor`
and `seibot.Process` instances.
These are attributes of a `seibot.IsolationSystem` instance defining
an isolation system's dynamics and hardware capabilities.

A `seibot.FilterConfigurations` instance is initialized with
three `seibot.FilterPool` instances, corresponding to the pools of
sensor correction filters, complementary low-pass filters, and complementary
high-pass filters, which are `seibot.Filter` instances that has
attributes identifying their whereabouts in a Foton file.

The `seibot.IsolationSystem` can be installed with filter configurations,
by calling `seibot.FilterConfigurations(i, j)`, which fully defines
the active isolation performance of the system.
The `seibot.IsolationSystem.get_displacement()` method can then be called
to obtain an estimate of the amplitude spectral density of the isolation
platform given an amplitude spectral density of the seismic noise.

The `seibot.Evaluate` class is initialized with a pair of
`seibot.IsolationSystem` and `seibot.FilterConfigurations` instances.
And it contains internal methods that automatically select the
best filter configurations at the real-time seismic condition according
to some pre-defined criteria.

Finally, the `seibot.Seibot` is a high-level class that wraps around
all the above basic functionalities and makes `seibot` extremely easy to use.
The `seibot.Seibot` is initialized by a
[Seibot configuration](#seibot-configuration), and
the best filters can be obtained by the method
`seibot.Seibot.get_best_filters()`.
Alternatively, `seibot.Seibot.export_best_filters()` exports
an [Seibot output file](#seibot-output-file) that and external program, such
as Guardian, can parse and make real-time changes to achieve
semi-adaptive seismic isolation control.

To setup `seibot` properly, be sure to check out the
[Step-by-step tutorial](#step-by-step-tutorial) and the [Usage](#usage)
sections.

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


# Step-by-step tutorial

## Install Seibot
Follow [Installation](#installation) on how to install `Seibot` in a conda
environment.

## Set up configuration files.
config, filter config, model parameters.


# Usage

## Command line
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
seismic isolation configuration. See [Seibot output file](#seibot-output-file).

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
This returns a dictionary with in the form
```
{
"sensor correction filter": ...,
"low pass filter": ...,
"high pass filter": ...
}
```
where ... are [seibot.Filter](#seibotfilter) instances.
The filters are `seibot.Filter` instances that contain the
information of the filters. See [seibot.Filter](#seibotfilter).

To export the information for further usages,
use the method `export_best_filter(path)`.
```
path = ...
ham8_seibot.export_best_filter(path)
```
This exports the filters information to a configuration file.
See [Seibot output file](#seibot-output-file)

### Intermediate-level usage
#### seibot.IsolationSystem
An `IsolationSystem` is initialized with 5 arguments
`relative_sensor`, `inertial_sensor`, `seisometer`,
`plant`, `transmissivity`, and `controller`
which are `seibot.Sensor` and `seibot.Process`
instances.
See [seibot.Sensor](#seibotsensor) and [seibot.Process](#seibotprocess).
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

Alternatively, install a filter configuration.
```
sensor_correction_filter = seibot.Filter(...)
low_pass_filter = seibot.Filter(...)
high_pass_filter = seibot.Filter(...)

filter_configuration = {
	"sensor correction filter": ...,
	"low pass filter": ...,
	"high_pass_filter": ...
}

ham8.filter_configuration = filter_configuration
```

With the filters installed, the closed-loop displacement can be obtained:
```
f = ...  # Frequency array
seismic_noise = ...

displacement = ham8.get_displacement(f, seismic_noise)
```

#### seibot.Evaluate
`seibot.Evaluate` instances contain internal methods to evaluate
filter configurations using different criteria.
A `seibot.Evaluate` instance is initiated by an `IsolationSystem`
(See [seibot.IsolationSystem](#seibotisolationsystem)) and
a `FilterConfigurations` instances
(see [seibot.FilterConfigurations](#seibotfilterconfigurations)).
```
import seibot

...
seismic_noise = ...
ham8 = seibot.IsolationSystem(...)
filter_configurations = siebot.FilterConfigurations(...)

evalutate = seibot.Evaluate(ham8, filter_configurations, seismic noise)
```

The internal methods each iterates through all possible filter configurations
for the specified isolation system and returns the best filter configuration
for the given seismic condition.
For example, the `rms_displacement()` method gives the best set of
sensor correction and complementary filters that gives the least
isolation platform RMS displacement.
```
best_filters = evaluate.rms_displacement()
```
 
### Low-level usage

#### seibot.filter module
`seibot.filter` module contain classes `Filter`, `FilterPool`, and
`FilterConfiguration`.

The `seibot.filter.Filter` class inherits `control.TransferFunction` class
and has additional attributes `filter_file`, `module` and `fm` that
identify the origin of the filter in Foton.
To construct a `seibot.filter.Filter` instance:
```
import control

import seibot.filter


tf = control.tf(...)

filter = seibot.filter.Filter(tf)
```

Access filter information
```
print(filter.filter_file)
print(filter.module)
print(filter.fm)
```

The `seibot.filter.FilterPool` class inherits the `list` class
and is a list of `seibot.filter.Filter` instances.
This class is used to construct a pool of filters for sensor correction and
complementary filters.
To construct a `seibot.filter.FilterPool` instance, use a
[Filter pool configuration](#filter-pool-configuration).
```
filter_config = ...

filter_pool = seibot.filter.FilterPool(filter_config)
```
Some filter contains compensation filters that inverse the responses
of the sensors. To get rid of them, specify an `inverse_filter`.
```
inverse_filter = ...

filter_pool = seibot.filter.FilterPool(filter_config, inverse_filter)
```
Preset `inverse_filter` can be found as methods
in `seibot.filter.InverseFilters`.
```
seibot.filter.InverseFilters().gs13()
seibot.filter.InverseFilters().sts()
```
Then, simply use it as a `list` instance. For example,
```
best_filter = filter_pool[1]

fm = best_filter.fm
```

The `seibot.filter.FilterConfigurations` class is a function class for all
available filter configurations of sensor correction and complementary filters.
It can be constructed using a pool of sensor correction filters,
a pool of low-pass filters, and a pool of high-pass filters.
Alternatively, it can be constructed using the paths of
the filter configuration files.
```
# Paths of the configuration files.
sc_config = ...
lp_config = ...
hp_config = ...

# Sensor correction and complementary filter pools.
sc_pool = seibot.filter.FilterPool(sc_config)
lp_pool = ...
hp_pool = ...

filter_config = seibot.filter.FilterConfigurations(sc_pool, lp_pool, hp_pool)
```
or
```
filter_config = seibot.filter.FilterConfigurations(
	sc_config=sc_config, lp_config=lp_config, hp_config=hp_config)
```
or in any combination
```
filter_config = seibot.filter.FilterConfigurations(
	sc_pool, lp_config=lp_config, hp_pool=hp_pool)
```
The `seibot.filter.FilterConfigurations` is a callable with 2 integer
parameters, indicating the index of the sensor correction filters and the
index of the complementary filters.
It returns a configuration in the form of
(sensor_correction, (low_pass_filter, high_pass_filter)).
```
sc, (lp, hp) = filter_config(1, 2)
```

#### seibot.Data
#### seibot.Forecast
#### seibot.Model
#### seibot.Sensor
#### seibot.Process
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

[Controller]
filter_file = ../foton_files/L1ISIHAM8.txt
module = HAM8_ISO_Y
fm = 4, 8


[Sensor correction filters]
config = ../config/sesnor_correction_filters.ini
inverse_filter = sts

[Low pass filters]
config = ../config/low_pass_filters.ini

[High pass filters]
config = ../config/high_pass_filters.ini
inverse_filter = gs13


[Evaluate]
criterion = min_rms_displacement
```

The seibot configuration file contains 4 groups of sections.
The first group contains sections
`[Channels]`, `[CDSutils]`, and `[Welch]`.
The second group contain sections
`[Seismic]`, `[Seismometer]`, `[Inertial sensor]`, `[Relative sensor]`,
`[Plant]`, `[Transmissivity]`, `[Controller]`.
The third group contains sections
`[Sensor correction filters]`, `[Low pass filters]`, and `[High pass filters]`.
The fourth group contains sections
`[Evaluate]`.


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
	Remove this option will default to start now.

`[Welch]` section
- `nperseg`: Number of data per segment used in Welch.
- `fs`: Sampling frequency.

`[Seismic]`, `[Seismometer]`, `[Inertial sensor]`, `[Relative sensor]`,
`[Plant]`, `[Transmissivity]` sections:

- `model`: Empirical/transfer function model selected from `seibot.model`.
- `parameters_path`: Path of the model parameter file.
- `dynamic`: Dynamically modelling. If true, parameters are not used and
	modeling using internal method.

`[Controller]` setion:
- `filter_file`: The path of the foton file
- `module`: The foton module that the controller is in.
- `fm`: The list of engaged FMs for the controllers.

`[Sensor correction filters]`, `[Low pass filters]`, `[High pass filters]`
sections:

- `config`: The path of the filter pool configuration file.
- `inverse_filter`: Optional. The inverse filter to be applied.

The `[Evaluation]` section has one variable.

- `criterion`: The filter selection criterion.
  Available options: `min_rms_displacement`.


## Filter pool configuration

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


## Model parameters configuration

The model parameter files are simple text files with model parameters listed
out space separated.

This is an example of a parameter file specifying 4 parameters for
`seibot.model.Model.noise2()`.

```
5.6234133e-11 1.3182567e-10 0.74 0
```

# Seibot output file

Seibot evaluates the isolation performance and inform the users the best filter configurations using a configuration file as follows.

```
[Sensor correction filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_SENSCOR_Y_UNCOR_FILT2
fm = 1

[Low pass filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_BLND_Y_SUPERSENS6_DISP
fm = 1

[High pass filter]
filter_file = /opt/rtcds/chans/llo/L1ISIHAM8.txt
module = HAM8_BLND_Y_SUPERSENS6_INERT_HI
fm = 1, 10
```

This configuration file is the output of Seibot and is meant to be further
further inferface with the Guardian state machine or other programs that
enact these changes.

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
