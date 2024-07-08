"""Evaluate class"""


class Evaluate:
    """Evaluate class

    Note
    ----
    This class contains internal methods that evaluate
    seismic isolation performance.

    Each method takes a pool of configurations and a system and 
    returns the best configuration.
    """
    def __init__(self, isolation_system, filter_configurations):
        """Constructor

        Parameters
        ----------
        isolation_system : seibot.isolation_system.IsolationSystem
           The isolation system with sensors and plants specified.
        filter_configurations : seibot.filter.FilterConfigurations
            The Filter configurations with all possible
            seismic isolation control configurations.
        """
        self.isolation_system = isolation_system
        self.filter_configuration = filter_configurations
        pass

    @property
    def isolation_system(self):
        """Isolation system"""
        return self._isolation_system

    @isolation_system.setter
    def isolation_system(self, _isolation_system):
        """Isolation system setter"""
        self._isolation_system = _isolation_system

    @property
    def filter_configurations(self):
        """Filter configurations"""
        return filter_configurations

    @filter_configurations.setter
    def filter_configurations(self, _filter_configurations):
        """Filter configurations setter"""
        self._filter_configurations = _filter_configurations

    @property
    def n_sc(self):
        """Number of sensor correction filters"""
        return len(self.filter_configurations.sc_pool)

    @property
    def n_blend(self):
        """Number of blends"""
        return len(self.filter_configurations.lp_pool)

    def _displacement_matrix(self):
        """Put all possible displacements spectrums in a matrix"""
        pass

    def min_rms_displacement(self):
        """Returns a configuration with lowest RMS displacement.
        
        Parameters
        ----------
        isolation_system : seibot.IsolationSystem
           The isolation system with sensors and plants specified.
        isolation_configurations : seibot.IsolationConfigurations
            The isolation configurations with all possible
            seismic isolation control configurations.
        """
        pass
