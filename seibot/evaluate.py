"""Evaluate class"""
import numpy as np


class Evaluate:
    """Evaluate class

    Note
    ----
    This class contains internal methods that evaluate
    seismic isolation performance.

    Each method takes a pool of configurations and a system and 
    returns the best configuration.
    """
    def __init__(self, isolation_system, filter_configurations,
                 f, seismic_noise):
        """Constructor

        Parameters
        ----------
        isolation_system : seibot.isolation_system.IsolationSystem
           The isolation system with sensors and plants specified.
        filter_configurations : seibot.filter.FilterConfigurations
            The Filter configurations with all possible
            seismic isolation control configurations.
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        """
        self.isolation_system = isolation_system
        self.filter_configurations = filter_configurations
        self.f = f
        self.seismic_noise = seismic_noise
        
        self.displacement_matrix = self.get_displacement_matrix()

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
        return self._filter_configurations

    @filter_configurations.setter
    def filter_configurations(self, _filter_configurations):
        """Filter configurations setter"""
        self._filter_configurations = _filter_configurations

    @property
    def f(self):
        """Frequency array"""
        return self._f
    
    @f.setter
    def f(self, _f):
        """Frequency array setter"""
        self._f = _f

    @property
    def seismic_noise(self):
        """Seismic noise"""
        return self._seismic_noise

    @seismic_noise.setter
    def seismic_noise(self, _seismic_noise):
        """Seismic noise setter"""
        self._seismic_noise = _seismic_noise

    @property
    def n_sc(self):
        """Number of sensor correction filters"""
        return len(self.filter_configurations.sc_pool)

    @property
    def n_blend(self):
        """Number of blends"""
        return len(self.filter_configurations.lp_pool)

    @property
    def displacement_matrix(self):
        """Put all possible displacements spectrums in a matrix"""
        return self._displacement_matrix

    @displacement_matrix.setter
    def displacement_matrix(self, _displacement_matrix):
        """Displacement matrix setter"""
        self._displacement_matrix = _displacement_matrix

    def get_displacement_matrix(self):
        """Set the displacement matrix.
        
        Returns
        -------
        displacement_matrix : ndarray
            The matrix with elements as spectrum of the
            possible displacements.
        """
        shape = (self.n_sc, self.n_blend, len(self.f))
        displacement_matrix = np.empty(shape)

        for i in range(self.n_sc):
            for j in range(self.n_blend):
                filter_config = self.filter_configurations(i, j)
                self.isolation_system.filter_configuration = filter_config
                displacement = self.isolation_system.get_displacement(
                    self.f, self.seismic_noise)
                displacement_matrix[i, j] = displacement

        return displacement_matrix

    def get_rms(self, f, asd):
        """Get RMS value of from ASD
        
        Parameters
        ----------
        f : array
            Frequency array
        asd : array
            The amplitude spectral density.

        Returns
        -------
        rms : array
            The RMS value.
        """
        rms = np.sqrt(np.trapz(y=asd**2, x=f))
        return rms

    def min_rms_displacement(self):
        """Returns a configuration with lowest RMS displacement.
        
        """
        rms_displacement_matrix = np.empty(
            np.shape(self.displacement_matrix[:, :, 0]))
        for i in range(len(rms_displacement_matrix)):
            for j in range(len(rms_displacement_matrix[0])):
                rms_displacement_matrix[i, j] = self.get_rms(
                    self.f, self.displacement_matrix[i, j])

        argmin = np.argmin(rms_displacement_matrix)
        min_i, min_j = np.unravel_index(argmin, rms_displacement_matrix.shape)
        
        return self.filter_configurations(min_i, min_j)


