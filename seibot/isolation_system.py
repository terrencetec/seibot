"""Isolation system class"""
import control


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
    This isolation system class contains sensors and plant information
    of a physical seismic isolation system.
    """
    def __init__(self,
                 relative_sensor, inertial_sensor, seismometer,
                 plant, transmissivity):
        """Constructor

        Parameters
        ----------
        relative_sensor : seibot.Sensor
            Relative sensor.
        inertial_sensor : seibot.Sensor
            Inertial sensor.
        seismometer : seibot.Sensor
            Seismometer
        plant : seibot.Process
            The plant.
        transmissivity : seibot.Process.
            The seismic transmissivity.
        """
        pass
