"""Forecaster"""
import numpy as np


class Forecast:
    """Forecaster"""
    def __init__(self):
        """Constructor"""
        pass

    def get_sensor_correction_noise(self, f,
                                    seismic_noise, seismometer_noise
                                    sensor_correction_filter):
        """Evaluate the sensor correction noise

        Parameters
        ----------
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of seismic noise.
        seismometer_noise : array
            The amplitude spectral density of seismometer noise.
        sensor_correction_filter : TransferFunction
            The transfer function of the sensor correction filter.

        Returns
        -------
        noise : array
            The estimated sensor correction noise
        """
        h_sc = sensor_correction_filter
        h_trans = 1 - sensor_correction_filter
        filtered_seismometer = abs(h_sc(1j*2*np.pi*f)) * seismometer_noise
        filtered_seismic = abs(h_trans(1j*2*np.pi*f)) * seismic_noise
        noise = (filtered_seismometer**2 + filtered_seismimc**2)**.5
        
        return noise
        
    def get_corrected_relative_noise(self, f,
                                   relative_sensor_noise,
                                   sensor_correction_noise):
        """Evaluate the sensor-corrected relative sensor noise
        
        Parameters
        ----------
        f : array
            Frequency array
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

    def get_super_sensor_noise(self, f,
                               sensor_noise1, sensor_noise2,
                               h1, h2=None):
        """Evaluate the super sensor noise
        
        Parameters
        ----------
        f : array
            Frequency array
        sensor_noise1 : array
            The amplitude spectral density of sensor noise 1.
        sensor_noise2 : array
            The amplitude spectral density of sensor noise 2.
        h1 : TransferFunction
            The complementary filter 1.
        h2 : TransferFunction, optional
            The complementary filter 2.
            Defaults ``1-h1``.

        Returns
        -------
        noise : array
            The estimated super sensor noise.
        """
        filtered_noise1 = abs(h1(1j*2*np.pi*f)) * sensor_noise1
        filtered_noise2 = abs(h2(1j*2*np.pi*f)) * sensor_noise2
        noise = (filtered_noise1**2 + filtered_noise2**2)**.5
        
        return noise
    
    def get_disturbance(self, f, seismic_noise, transmissivity):
        """Evaluate seismic disturbance

        Parameters
        ----------
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        transmissivity : TransferFunction
            The seismic transmissivity.
        
        Returns
        -------
        disturbance : array
            The estimated seismic disturbance
        """
        disturbance = abs(transmissivity(1j*2*np.pi*f)) * seismic_noise

        return disturbance

    def get_noise(self, f, seismic_noise, seismometer_noise,
                  relative_sensor_noise, inertial_sensor_noise,
                  sensor_correction_filter, h1, h2=None):
        """Evaluate sensing noise of the isolation platform
        
        Parameters
        ----------
        f : array
            Frequency array.
        seismic_noise : array
            The amplitude spectral density of the seismic noise.
        seismoemter_noise : array
            The amplitude spectral density of the seismometer noise.
        relative_sensor_noise : array
            The amplitude spectral density of the relative sensor noise.
        inertial_sensor_noise : array
            The amplitude spectral density of the inertial sensor noise.
        sensor_correction_filter : TransferFunction
            The sensor correction filter.
        h1 : TransferFunction
            The complementary filter filtering the corrected relative sensor.
        h2 : TransferFunction, optional
            The complementary filter filtering the inertial sensor.
            Defaults ``1-h1``.

        Returns
        -------
        noise : array
            The estimated sensing noise of the isolation platform.
        """
        sensor_correction_noise = self.get_sensor_correction_noise(
            f, seismic_noise, seismometer_noise)
        corrected_relative_noise = self.get_corrected_relative_noise(
            f, relative_sensor_noise, sensor_correction_noise)
        noise = self.get_super_sensor_noise(
            f, corrected_relative_noise, inertial_sensor_noise,
            h1, h2)

        return noise

    def get_displacement(self, f, disturbance, noise, plant, controller):
        """Evaluate the feedback controlled displacement

        Parameters
        ----------
        f : array
            Frequency array
        disturbance : array
            The amplitude spectral density of the disturbance.
        noise : array
            The amplitude spectral density of the sensing noise.
        plant : TransferFunction
            The plant to be controlled.
        controller : TransferFunction
            The feedback controller.

        Returns
        -------
        displacement : array
            The estimated feedback controlled displacement.
        """
        oltf = plant * controller
        sensitivity = 1 / (1+oltf)
        complement = 1 - sensitivity
        filtered_disturbance = abs(sensitivity(1j*2*np.pi*f)) * disturbance
        filtered_noise = abs(complement(1j*2*np.pi*f)) * noise
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
