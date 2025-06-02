"""Forecaster"""
import numpy as np


class Forecast:
    """Forecaster"""
    def __init__(self):
        """Constructor"""
        pass

    @property
    def relative_sensor_noise(self):
        """Relative sensor noise"""
        return self._relative_sensor_noise

    @relative_sensor_noise.setter
    def relative_sensor_noise(self, _relative_sensor_noise):
        """Relative sensor noise setter"""
        self._relative_sensor_noise = _relative_sensor_noise

    @property
    def inertial_sensor_noise(self):
        """Inertial sensor noise"""
        return self._inertial_sensor_noise
    
    @inertial_sensor_noise.setter
    def inertial_sensor_noise(self, _inertial_sensor_noise):
        """Inertial sensor noise setter"""
        self._inertial_sensor_noise = _inertial_sensor_noise

    @property
    def seismometer_noise(self):
        """Seismometer noise"""
        return self._seismometer_noise

    @seismometer_noise.setter
    def seismometer_noise(self, _seismometer_noise):
        """Seismometer noise setter"""
        self._seismometer_noise = _seismometer_noise

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
    def controller(self):
        """Controller"""
        return self._controller

    @controller.setter
    def controller(self, _controller):
        """Controller setter"""
        self._controller = _controller

    @property
    def f(self):
        """Frequency array"""
        return self._f
    
    @f.setter
    def f(self, _f):
        """Frequency array setter"""
        self._f = _f

    def get_sensor_correction_noise(self,
                                    seismic_noise, seismometer_noise,
                                    sensor_correction_filter,
                                    sensor_correction_comp):
        """Evaluate the sensor correction noise

        Parameters
        ----------
        seismic_noise : array
            The amplitude spectral density of seismic noise.
        seismometer_noise : array
            The amplitude spectral density of seismometer noise.
        sensor_correction_filter : array
            The magnitude response of the sensor correction filter.
        sensor_correction_comp : array
            The magnitude response of the sensor correction complementary.

        Returns
        -------
        noise : array
            The estimated sensor correction noise
        """
        h_sc = sensor_correction_filter
        h_trans = sensor_correction_comp.copy()
        # filtered_seismometer = abs(h_sc(1j*2*np.pi*f)) * seismometer_noise
        # filtered_seismic = abs(h_trans(1j*2*np.pi*f)) * seismic_noise
        filtered_seismometer = h_sc * seismometer_noise

        # Update 2025-06-02 Limit transmissivity
        band = (self.f > 0.1) * (self.f < 0.5)
        mask = h_trans < 0.1
        h_trans[band*mask] = 0.1

        filtered_seismic = h_trans * seismic_noise
        noise = (filtered_seismometer**2 + filtered_seismic**2)**.5
        
        return noise
        
    def get_corrected_relative_noise(self,
                                   relative_sensor_noise,
                                   sensor_correction_noise):
        """Evaluate the sensor-corrected relative sensor noise
        
        Parameters
        ----------
        relative_sensor_noise : array
            The amplitude spectral density of relative sensor noise.
        sensor_correction_noise : array
            The amplitude spectral density of the sensor correction noise.

        Returns
        -------
        noise : array
            The estimated sensor-corrected relative sensor noise
        """
        noise = (relative_sensor_noise**2 + sensor_correction_noise**2)**.5

        return noise

    def get_super_sensor_noise(self,
                               sensor_noise1, sensor_noise2,
                               h1, h2):
        """Evaluate the super sensor noise
        
        Parameters
        ----------
        sensor_noise1 : array
            The amplitude spectral density of sensor noise 1.
        sensor_noise2 : array
            The amplitude spectral density of sensor noise 2.
        h1 : array
            The magnitude response of the complementary filter 1.
        h2 : array
            The magnitude response of the complementary filter 2.

        Returns
        -------
        noise : array
            The estimated super sensor noise.
        """
        # filtered_noise1 = abs(h1(1j*2*np.pi*f)) * sensor_noise1
        # filtered_noise2 = abs(h2(1j*2*np.pi*f)) * sensor_noise2
        filtered_noise1 = h1 * sensor_noise1
        filtered_noise2 = h2 * sensor_noise2
        noise = (filtered_noise1**2 + filtered_noise2**2)**.5
        
        return noise
    
    def get_disturbance(self, seismic_noise, transmissivity):
        """Evaluate seismic disturbance

        Parameters
        ----------
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        transmissivity : array
            The magnitude response of the seismic transmissivity.
        
        Returns
        -------
        disturbance : array
            The estimated seismic disturbance
        """
        # disturbance = abs(transmissivity(1j*2*np.pi*f)) * seismic_noise
        disturbance =  transmissivity * seismic_noise

        return disturbance

    def get_noise(self, seismic_noise, seismometer_noise,
                  relative_sensor_noise, inertial_sensor_noise,
                  sensor_correction_filter, sensor_correction_comp,
                  h1, h2):
        """Evaluate sensing noise of the isolation platform
        
        Parameters
        ----------
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        seismoemter_noise : array
            The amplitude spectral density of the seismometer noise.
        relative_sensor_noise : array
            The amplitude spectral density of the relative sensor noise.
        inertial_sensor_noise : array
            The amplitude spectral density of the inertial sensor noise.
        sensor_correction_filter : array
            The magnitude response of the sensor correction filter.
        sensor_correction_comp : array
            The magnitude response of the sensor correction complementary.
        h1 : array
            The magnitude response of the
            complementary filter filtering the corrected relative sensor.
        h2 : array
            The magnitude response of the
            complementary filter filtering the inertial sensor.

        Returns
        -------
        noise : array
            The estimated sensing noise of the isolation platform.
        """
        sensor_correction_noise = self.get_sensor_correction_noise(
            seismic_noise, seismometer_noise,
            sensor_correction_filter, sensor_correction_comp)
        corrected_relative_noise = self.get_corrected_relative_noise(
            relative_sensor_noise, sensor_correction_noise)
        noise = self.get_super_sensor_noise(
            corrected_relative_noise, inertial_sensor_noise,
            h1, h2)

        return noise

    def get_displacement(self, disturbance, noise, sensitivity, complement):
        """Evaluate the feedback controlled displacement

        Parameters
        ----------
        disturbance : array
            The amplitude spectral density of the disturbance.
        noise : array
            The amplitude spectral density of the sensing noise.
        sensitivity : array
            Magnitude response of the sensitivity function.
        complement : array
            Magnitude response of the complementary sensitivity function.

        Returns
        -------
        displacement : array
            The estimated feedback controlled displacement.
        """
        # filtered_disturbance = abs(sensitivity(1j*2*np.pi*f)i) * disturbance
        # filtered_noise = abs(complement(1j*2*np.pi*f)) * noise
        filtered_disturbance = sensitivity * disturbance
        filtered_noise = complement * noise
        displacement = (filtered_disturbance**2 + filtered_noise**2)**.5

        return displacement

    @property
    def relative_sensor_noise(self):
        """Relative sensor noise"""
        return self._relative_sensor_noise
    
    @relative_sensor_noise.setter
    def relative_sensor_noise(self, _relative_sensor_noise):
        """Relative sensor noise setter"""
        self._relative_sensor_noise = _relative_sensor_noise
# continues.
