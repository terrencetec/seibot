"""Seibot class
"""
import seibot.data
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
        self.config = configparser.ConfigParser(allow_now_value=True)
        self.config.optionxform = str
        self.config.read(config)

        # Fetch sensor noise and plant data from database/real-time.
        self.data = seibot.data.Data(config)

        # Construct isolation system from database
        self.isolation_system = self.get_isolation_system(self.data)
        
        # Fetch all available filters from foton file.
        sc_config = self.config.get("Sensor correction filters", "config")
        lp_config = self.config.get("Low pass filters", "config")
        hp_config = self.config.get("High pass filters", "config")

        sc_pool = seibot.filter.FilterPool(sc_config)
        lp_pool = seibot.filter.FilterPool(lp_config)
        hp_pool = seibot.filter.FilterPool(hp_config)

        self.iso_config = seibot.isolation_system.IsolationConfiguraions(
            sc_pool=sc_pool, lp_pool=lp_pool, hp_pool=hp_pool)

        method = self.config.get("Evaluation", "method")
        evaulate = seibot.evaluate.Evaluate()
        self.evaluate_method = getattr(evaluate, method)
        
    def get_isolation_performance(
        self, f, seismic_noise, isolation_system, isolation_configuration):
        """Get isolation performance for a configuration
        
        Parameters
        ----------
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        isolation_system : seibot.isolation_system.IsolationSystem
            Isolation system.
        isolation_configration : (Filter, (Filter, Filter))
            A isolation configuration in the form of a tuple
            (sensor correction filter, (low-pass filter, high-pass filter)).
        """
        seismometer_noise = isolation_system.seismometer.noise
        relative_sensor_noise = isolation_system.relative_sensor.noise
        inertial_sensor_noise = isolation_system.inertial_sensor.noise
        plant = isolation_system.plant
        transmissivity = isolation_system.transmissivity
        controller = isolation_system.controller
        
        sensor_correction_filter = isolation_configuration[0]
        complementary_filters = isolation_configuration[1]
        low_pass_filter = complementary_filters[0]
        high_pass_filter = complementary_filters[1]

        forecast = seibot.forecast.Forecast()

        noise = forecast.get_noise(
            f, seismic_noise, seismometer_noise,
            relative_sensor_noise, inertial_sensor_noise
            sensor_correction_filter,
            low_pass_filter, high_pass_filter)

        disturbance = forecast.get_disturbance(
            f, seismic_noise, transmissivity)

        displacement = forecast.get_displacement(
            f, disturbance, noise, plant, controller)
        
        return displacement
        

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

        isolation_system = seibot.isolation_system.IsolationSystem(
            relative_sensor=relative_sensor,
            inertial_sensor=inertial_sensor,
            seismometer=seismoemter,
            plant=plant,
            transmissivity=transmissivity)

        return isolation_system

