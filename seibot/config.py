"""Configuration files"""
import configparser


def get_seibot_config(path):
    """Write a seibot config to path
    
    Parameters
    ----------
    path : str
        The path to be written to.
    """
    config = configparser.ConfigParser()
    config["Channels"] = {
        "seismometer": "L1:ISI-GND_STS_HAM8_Y_DQ",
        "seismometer_coh": "L1:ISI-GND_STS_ITMY_Y_DQ",
    }
    config["CDSutils"] = {
        "duration": "4096",
    }
    config["Welch"] = {
        "nperseg": "524288",
        "fs": "512",
    }

    config["Seismic"] = {
        "model": "second_order_plant",
        "parameters_path": "../model_parameters/seismic.txt",
        "dynamic": "False"
    }
    config["Seismometer"] = {
        "model": "noise1",
        "parameters_path": "../model_parameters/sts.txt",
        "dynamic": "False"
    }
    config["Inertial sensor"] = {
        "model": "noise2",
        "parameters_path": "../model_parameters/gs13.txt",
        "dynamic": "False"
    }
    config["Relative sensor"] = {
        "model": "noise2",
        "parameters_path": "../model_parameters/cps.txt",
        "dynamic": "False"
    }
    config["Plant"] = {
        "model": "second_order_plant",
        "parameters_path": "../model_parameters/plant.txt",
        "dynamic": "False"
    }
    config["Transmissivity"] = {
        "model": "second_order_plant",
        "parameters_path": "../model_parameters/transmissivity.txt",
        "dynamic": "False"
    }

    config["Controller"] = {
        "filter_file": "../foton_files/L1ISIHAM8.txt",
        "module": "HAM8_ISO_Y",
        "fm": "4, 8"
    }

    config["Sensor correction filters"] = {
        "config": "../config/sensor_correction_filters.ini",
        "inverse_filter": "sts"
    }
    config["Low pass filters"] = {
        "config": "../config/low_pass_filters.ini"
    }
    config["High pass filters"] = {
        "config": "../config/high_pass_filters.ini",
        "inverse_filter": "gs13"
    }

    config["Evaluate"] = {
        "criterion": "min_rms_displacement"
    }

    with open(path, "w") as file:
        config.write(file)


def get_filter_config(path):
    """Write a filter configuration file to path
    
    Parameters
    ----------
    path : str
        The path to be written to.
    """
    config = configparser.ConfigParser()
    config["Filter 1"] = {
        "filter_file": "../foton_files/L1ISIHAM8.txt",
        "module": "HAM8_SENSCOR_Y_UNCOR_FILT2",
        "fm": "1, 10"
    }
    config["Filter 2"] = {
        "filter_file": "../foton_files/L1ISIHAM8.txt",
        "module": "HAM8_SENSCOR_Y_UNCOR_FILT2",
        "fm": "2, 10"
    }
    config["Filter 3"] = {
        "filter_file": "../foton_files/L1ISIHAM8.txt",
        "module": "HAM8_SENSCOR_Y_UNCOR_FILT2",
        "fm": "3, 10"
    }

    with open(path, "w") as file:
        config.write(file)
