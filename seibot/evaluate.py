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
                    self.seismic_noise)
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

    def min_rms_displacement(self, f_lower=None, f_upper=None):
        """Returns a configuration with lowest RMS displacement. 

        Parameters
        ----------
        f_lower : float, default None
            Lower bound of the frequency band.
        f_upper : float, default None
            Upper bound of the frequency band.
        """
        if f_lower is None:
            f_lower = 0
        if f_upper is None:
            f_upper = np.inf
        mask = (self.f > f_lower) * (self.f < f_upper)
        rms_displacement_matrix = np.empty(
            np.shape(self.displacement_matrix[:, :, 0]))
        for i in range(len(rms_displacement_matrix)):
            for j in range(len(rms_displacement_matrix[0])):
                f = self.f[mask]
                displacement = self.displacement_matrix[i, j][mask]
                rms_displacement_matrix[i, j] = self.get_rms(f, displacement)

        argmin = np.argmin(rms_displacement_matrix)
        min_i, min_j = np.unravel_index(argmin, rms_displacement_matrix.shape)
        
        return self.filter_configurations(min_i, min_j)

    def min_rms_velocity(self, f_lower=None, f_upper=None):
        """Returns a configuration with lowest RMS velocity. 

        Parameters
        ----------
        f_lower : float, default None
            Lower bound of the frequency band.
        f_upper : float, default None
            Upper bound of the frequency band.
        """
        if f_lower is None:
            f_lower = 0
        if f_upper is None:
            f_upper = np.inf
        mask = (self.f > f_lower) * (self.f < f_upper)
        rms_velocity_matrix = np.empty(
            np.shape(self.displacement_matrix[:, :, 0]))
        for i in range(len(rms_velocity_matrix)):
            for j in range(len(rms_velocity_matrix[0])):
                f = self.f[mask]
                velocity = 2*np.pi*f*self.displacement_matrix[i, j][mask] 
                rms_velocity_matrix[i, j] = self.get_rms(f, velocity)

        argmin = np.argmin(rms_velocity_matrix)
        min_i, min_j = np.unravel_index(argmin, rms_velocity_matrix.shape)
        
        return self.filter_configurations(min_i, min_j)

    def get_threshold_indices(self, disp_thres, vel_thres):
        """Returns a list of indices of displacements within thresholds.
        
        Parameters
        ----------
        disp_thres : float
            RMS displacement threshold (nm).
        vel_thres : float
            RMS velocity threshold (nm/s).
        
        Returns
        -------
        List of Tuples
            A list of indices of the displacement matrix.
        """
        list_indices = []
        for i in range(len(self.displacement_matrix)):
            for j in range(len(self.displacement_matrix[0])):
                # Test RMS displacement
                displacement = self.displacement_matrix[i, j]
                rms_displacement = self.get_rms(self.f, displacement)
                rms_displacement *= 1e9  # m to nm
                if rms_displacement > disp_thres:
                    continue
                # Test RMS velocity
                velocity = 2*np.pi*self.f*displacement
                rms_velocity = self.get_rms(self.f, velocity)
                rms_velocity *= 1e9
                if rms_velocity > vel_thres:
                    continue
                # Passes two tests
                list_indices.append((i, j))
        return list_indices

    def threshold_optimize(
            self, disp_thres, vel_thres, f_lower, f_upper, optimize):
        """Eliminate and then optimize within frequency band
        
        Parameters
        ----------
        disp_thres : float
            RMS displacement threshold (nm).
        vel_thres : float
            RMS velocity threshold (nm/s).
        f_lower : float
            Lower bound of the frequency band.
        f_upper : float
            Upper bound of the frequency band.
        optimize : str
            Optimize RMS displacement or velocity within the frequency band.
            Choose from "displacement" or "velocity"

        Returns
        -------
        Dict
            A filter configuration within displacement and velocity
            thresholds that gives optimized band-limited
            displacement/velocity RMS.
        """
        list_indices = self.get_threshold_indices(disp_thres, vel_thres)
        list_rms = []

        mask = (self.f > f_lower) * (self.f < f_upper)
        f = self.f[mask]

        for index in list_indices:
            displacement = self.displacement_matrix[index][mask]
            if optimize == "velocity":
                asd = 2*np.pi*f*displacement
            else:
                asd = displacement
            rms = self.get_rms(f, asd)
            list_rms.append(rms)

        min_index = np.argmin(list_rms)
        min_i, min_j = list_indices[min_index]

        return self.filter_configurations(min_i, min_j)
