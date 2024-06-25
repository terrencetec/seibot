"""Isolation system class"""
import control

import seibot.forecast


class Sensor:
    """A sensor class
    
    Parameters
    ----------
    f : array
        Frequency array.
    noise : array
        The amplitude spectral density of the sensor noise.

    Attributes
    ----------
    f : array
        Frequency array.
    noise : array
        The amplitude spectral density of the sensor noise.
    """
    def __init__(self, f, noise):
        """Constructor
        
        Parameters
        ----------
        f : array
            Frequency array.
        noise : array
            The amplitude spectral density of the sensor noise.
        """
        self.f = f,
        self.noise = noise

    @property
    def f(self):
        """Frequency array"""
        return self._f
    
    @f.setter
    def f(self, _f):
        """Frequency array setter"""
        self._f = _f

    @property
    def noise(self):
        """The amplitude spectral density of the sensor noises"""
        return self._noise

    @noise.setter
    def noise(self, _noise):
        """Noise setter"""
        self._noise = _noise


class Process(control.TransferFunction):
    """A control process. Dummy wrapper."""
    def __init__(self, transfer_function):
        """Constructor
        
        Parameters
        ----------
        transfer_function : control.TransferFunction
            The transfer function representing the control process.
        """
        super().__init__(transfer_function)


class IsolationSystem:
    """Isolation system class

    Note
    ----
    This isolation system class represents a physical isolation system
    and contains sensors and plant information
    of a physical seismic isolation system.
    """
    def __init__(self,
                 relative_sensor, inertial_sensor, seismometer,
                 plant, transmissivity, controller):
        """Constructor

        Parameters
        ----------
        relative_sensor : seibot.Sensor
            Relative sensor.
        isertial_sensor : seibot.Sensor
            Inertial sensor.
        seismometer : seibot.Sensor
            Seismometer
        plant : seibot.Process
            The plant.
        transmissivity : seibot.Process.
            The seismic transmissivity.
        controller : seibot.Process or seibot.Filter
            The feedback controller.
        """
        self.relative_sensor = relative_sensor
        self.inertial_sensor = inertial_sensor
        self.seismometer = seismometer
        self.plant = plant
        self.transmissivity = transmissivity
        self.controller = controller
        
        self.filter_configuration = (None, (None, None))

    def get_displacement(self, f, seismic_noise):
        """Get closed-loop displacement
        
        Parameters
        ----------
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of the seismic noise.

        Returns
        -------
        displacement : array
            The closed-loop displacement.
        """
        if (self.sensor_correction_filter is None
                or self.low_pass_filter is None
                or self.high_pass_filter is None):
            raise ValueError("sensor_correction_filter, low_pass_filter"
                             "or high_pass_filter is not set.")
        
        forecaster = seibot.forecast.Forecast()
        forecaster.relative_sensor_noise = self.relative_sensor.noise
        forecaster.inertial_sensor_noise = self.inertial_sensor.noise
        forecaster.seismometer_noise = self.seismometer.noise
        forecaster.plant = self.plant
        forecaster.transmissivity = self.transmissivity
        forecaster.controller = self.controller

        displacement = forecaster.get_displacement()
        
        return displacment
    # def __call__(self,
    #              sensor_correction_filter,
    #              low_pass_filter, high_pass_filter):
    #     """Returns forecasted displacement

    #     Parameters
    #     ----------
    #     sensor_correction_filter : control.TransferFunction
    #         Sensor correction filter
    #     low_pass_filter : control.TransferFunction
    #         Low-pass complementary filter.
    #     high_pass_filter : control.TransferFunction
    #         High-pass complementary filter.

    #     Returns
    #     -------
    #     """

    @property
    def relative_sensor(self):
        """Relative sensor"""
        return self._relative_sensor
    
    @relative_sensor.setter
    def relative_sensor(self, _relative_sensor):
        """Relative sensor setter"""
        self._relative_sensor = _relative_sensor

    @property
    def inertial_sensor(self):
        """Inertial sensor"""
        return self._inertial_sensor
    
    @inertial_sensor.setter
    def inertial_sensor(self, _inertial_sensor):
        """Inertial sensor setter"""
        self._inertial_sensor = _inertial_sensor

    @property
    def seismometer(self):
        """Seismometer"""
        return self._seismometer
    
    @seismometer.setter
    def seismometer(self, _seismometer):
        """Seismometer setter"""
        self._seismometer = _seismometer

    @property
    def plant(self):
        """Plant"""
        return self._plant
    
    @plant.setter
    def plant(self, _plant):
        """Plant setter"""
        self._plant = _plant
    
    @property
    def transmissivity(self):
        """Transmissivity"""
        return self._transmissivity
    
    @transmissivity.setter
    def transmissivity(self, _transmissivity):
        """Transmissivity setter"""
        self._transmissivity = _transmissivity

    @property
    def sensor_correction_filter(self):
        """Sensor correction filter"""
        sc, _ = self._filter_configuration
        return sc
    
    @sensor_correction_filter.setter
    def sensor_correction_filter(self, sc):
        """Sensor correction filter setter"""
        _, (lp, hp) = self.filter_configuration
        self.filter_configuration = (sc, (lp, hp))

    @property
    def low_pass_filter(self):
        """Low pass filter"""
        _, (lp, __) = self.filter_configuration
        return lp

    @low_pass_filter.setter
    def low_pass_filter(self, lp):
        """Low pass filter setter"""
        sc, (_, hp) = self.filter_configuration
        self.filter_configuration = (sc, (lp, hp))
        
    @property
    def high_pass_filter(self):
        """High pass filter"""
        _, (__, hp) = self.filter_configuration
        return hp

    @high_pass_filter.setter
    def high_pass_filter(self, hp):
        """High pass filter setter"""
        sc, (lp, _) = self.filter_configuration
        self.filter_configuration = (sc, (lp, hp))

    @property
    def filter_configuration(self):
        """Filter configuration"""
        return self._filter_configuration
    
    @filter_configuration.setter
    def filter_configuration(self, _filter_configuration):
        """Filter configuration setter"""
        self._filter_configuration = _filter_configuration
