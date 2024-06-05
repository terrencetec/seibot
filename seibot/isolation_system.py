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
        isertial_sensor : seibot.Sensor
            Inertial sensor.
        seismometer : seibot.Sensor
            Seismometer
        plant : seibot.Process
            The plant.
        transmissivity : seibot.Process.
            The seismic transmissivity.
        """
        self.relative_sensor = relative_sensor
        self.inertial_sensor = inertial_sensor
        self.seismometer = seismometer
        self.plant = plant
        self.transmissivity = transmissivity

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


class IsolationConfigurations:
    """All available isolation configurations
    
    Parameters
    ----------
    sc_pool : seibot.FilterPool
        The pool of sensor correction filters.
    lp_pool : seibot.FilterPool
        The pool of low-pass filters.
    hp_pool : seibot.FilterPool
        The pool of high-pass filters.

    Attributes
    ----------
    configuration_matrix : matrix
        Configuration matrix with elements containing
        `(seibot.Filter, (seibot.Filter, seibot.Filter))`,
        the sensor correction filter and the 2 complementary filters.
    """
    def __init__(self, sc_pool, lp_pool, hp_pool):
        """Constructor
        
        Parameters
        ----------
        sc_pool : seibot.FilterPool
            The pool of sensor correction filters.
        lp_pool : seibot.FilterPool
            The pool of low-pass filters.
        hp_pool : seibot.FilterPool
            The pool of high-pass filters.
        """
        len_sc = len(sc_pool)
        len_lp = len(lp_pool)
        configuration_matrix = np.empty(shape=(len_sc, len_lp))
        for i in range(len(configuration_matrix)):
            for j in range(len(configuration_matrix)[0]):
                configuration_matrix[i, j] = (
                    sc_pool[i], (lp_pool[j], hp_pool[j]))
        self.configuration_matrix = configuration_matrix

    @property
    def configuration_matrix(self):
        """Configuration matrix"""
        return self._configuration_matrix
    
    @configuration_matrix.setter
    def configuration_matrix(self, _configuration_matrix):
        """Configuration matrix setter"""
        self._configuration_matrix = _configuration_matrix):
