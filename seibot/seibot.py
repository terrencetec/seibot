"""Seibot class
"""
import configparser

import numpy as np
import ezca

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

        # time spent 200ms
        # Fetch sensor noise and plant data from database/real-time.
        self.data = seibot.data.Data(config)

        # time spent 227ms
        # Construct isolation system from database
        self.isolation_system = self.get_isolation_system(self.data)
        
        # time spend 200ms ??
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
        
        # time spend 211ms
        inverse_filters = seibot.filter.InverseFilters()
        sc_inverse_filter = getattr(inverse_filters, sc_inverse)
        lp_inverse_filter = getattr(inverse_filters, lp_inverse)
        hp_inverse_filter = getattr(inverse_filters, hp_inverse)


        f = self.data.f
        # time spend 1.43s (small bottleneck here)
        # New time spent 702ms
        sc_pool = seibot.filter.FilterPool(f, sc_config, sc_inverse_filter)
        lp_pool = seibot.filter.FilterPool(f, lp_config, lp_inverse_filter)
        hp_pool = seibot.filter.FilterPool(f, hp_config, hp_inverse_filter)

        # time spend 707ms
        self.filter_configurations = seibot.filter.FilterConfigurations(
            sc_pool=sc_pool,
            lp_pool=lp_pool,
            hp_pool=hp_pool)

        # time spend 714ms
        self.isolation_system = self.get_isolation_system(self.data)

        # time spend 717ms
        self.criterion = self.config.get("Evaluate", "criterion")
        seismic_noise = self.data.seismic_noise

        # time spend 17s
        # Total times spent 3.25s.
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

        oltf = data.plant * data.controller
        sensitivity = seibot.isolation_system.Process(1/(1+oltf))
        complement = seibot.isolation_system.Process(oltf/(1+oltf))

        plant.mag = abs(plant(1j*2*np.pi*data.f))
        transmissivity.mag = abs(transmissivity(1j*2*np.pi*data.f))
        controller.mag = abs(controller(1j*2*np.pi*data.f))
        sensitivity.mag = abs(sensitivity(1j*2*np.pi*data.f))
        complement.mag = abs(complement(1j*2*np.pi*data.f))
        
        isolation_system = seibot.isolation_system.IsolationSystem(
            relative_sensor=relative_sensor,
            inertial_sensor=inertial_sensor,
            seismometer=seismometer,
            plant=plant,
            transmissivity=transmissivity,
            controller=controller,
            sensitivity=sensitivity,
            complement=complement,
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
        best_filters.export(path)

    def get_current_filters(self):
        """Get current filters"""
        # Sensor correction
        ezca_obj = ezca.Ezca(prefix="", ifo="")
        cur_chan = self.config.get("Sensor correction channels", "cur_chan")
        filter_chan = self.config.get(
            "Sensor correction channels", "filter_chan")
        try:
            cur = ezca_obj.read(cur_chan)
        except ezca.errors.EzcaConnectError:
            print("Ezca error")
            return
        
        cur = int(cur)
        print(cur)
