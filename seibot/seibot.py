"""Seibot class
"""
import configparser

import seibot.data
import seibot.evaluate
import seibot.forecast
import seibot.filter
import seibot.isolation_system


class Seibot:
    """Seibot class

    Parameters
    ----------
    config : str
        Path of the Seibot configuration file.

    Attribute
    ---------
    data : seibot.data.Data
    forecaster :
    """
    def __init__(self, config):
        """Constructor

        Parameters
        ----------
        config : str
            Path of the Seibot configuration file.
        """
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(config)

        # Fetch sensor noise and plant data from database/real-time.
        self.data = seibot.data.Data(config)

        # Construct isolation system from database
        self.isolation_system = self.get_isolation_system(self.data)
        
        # Fetch all available filters from foton file.
        sc_config = self.config.get("Sensor correction filters", "config")
        sc_inverse = self.config.get("Sensor correction filters",
                                     "inverse_filter", fallback="none")
        lp_config = self.config.get("Low pass filters", "config")
        lp_inverse = self.config.get("Low pass filters",
                                     "inverse_filter", fallback="none")
        hp_config = self.config.get("High pass filters", "config")
        hp_inverse = self.config.get("High pass filters",
                                     "inverse_filter", fallback="none")
        
        inverse_filters = seibot.filter.InverseFilters()
        sc_inverse_filter = getattr(inverse_filters, sc_inverse)
        lp_inverse_filter = getattr(inverse_filters, lp_inverse)
        hp_inverse_filter = getattr(inverse_filters, hp_inverse)

        sc_pool = seibot.filter.FilterPool(sc_config, sc_inverse_filter)
        lp_pool = seibot.filter.FilterPool(lp_config, lp_inverse_filter)
        hp_pool = seibot.filter.FilterPool(hp_config, hp_inverse_filter)

        self.filter_configurations = seibot.filter.FilterConfigurations(
            sc_pool=sc_pool,
            lp_pool=lp_pool,
            hp_pool=hp_pool)

        self.isolation_system = self.get_isolation_system(self.data)

        self.criterion = self.config.get("Evaluate", "criterion")
        f = self.data.f
        seismic_noise = self.data.seismic_noise
        self.evaluate = seibot.evaluate.Evaluate(
            self.isolation_system, self.filter_configurations,
            f, seismic_noise)
        self.evaluate_method = getattr(self.evaluate, self.criterion)
        
    def get_isolation_system(self, data):
        """Construct an isolation system instance from a data instance
        
        Parameters
        ----------
        data : seibot.data.Data
            Seibot data instance.

        Returns
        -------
        isolation_system : seibot.isolation_system.IsolationSystem
            The isolation system.
        """
        relative_sensor = seibot.isolation_system.Sensor(
            data.f, data.relative_sensor_noise)
        inertial_sensor = seibot.isolation_system.Sensor(
            data.f, data.inertial_sensor_noise)
        seismometer = seibot.isolation_system.Sensor(
            data.f, data.seismometer_noise)
        plant = seibot.isolation_system.Process(data.plant)
        transmissivity = seibot.isolation_system.Process(data.transmissivity)
        controller = seibot.isolation_system.Process(data.controller)

        isolation_system = seibot.isolation_system.IsolationSystem(
            relative_sensor=relative_sensor,
            inertial_sensor=inertial_sensor,
            seismometer=seismometer,
            plant=plant,
            transmissivity=transmissivity,
            controller=controller,
        )

        return isolation_system
    
    def get_best_filters(self):
        """Get best filters
        
        Returns
        -------
        best_filters : dict
            Dictionary with keys
            ["sensor correction filter", "low pass filter", "high pass filter"]
        """
        best_filters = self.evaluate_method()
        return best_filters

    def export_best_filters(self, path):
        """Export best filters into path
        
        Parameters
        ----------
        path : str
            The path of the output configuration file.
        """
        best_filters = self.get_best_filters()
        self.export_configuration(best_filters, path)

    def export_configuration(self, filter_configuration, path):
        """Export a filter configuration to path

        Parameters
        ----------
        filter_configuration : dict
            The filter configuration with keys
            ["sensor correction filter", "low pass filter", "high pass filter"]
        path : str
            The path of the output configuration file.
        """
        sc = filter_configuration["sensor correction filter"]
        lp = filter_configuration["low pass filter"]
        hp = filter_configuration["high pass filter"]

        config = configparser.ConfigParser()
        config["Sensor correction filter"] = {
            "filter_file": sc.filter_file,
            "module": sc.module,
            "fm": sc.fm
        }
        config["Low pass filter"] = {
            "filter_file": lp.filter_file,
            "module": lp.module,
            "fm": lp.fm
        }
        config["High pass filter"] = {
            "filter_file": hp.filter_file,
            "module": hp.module,
            "fm": hp.fm
        }

        with open(path, "w") as file:
            config.write(file)
