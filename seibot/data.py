"""SeiBot Data
"""
import configparser

import cdsutils
import numpy as np
import scipy
import scipy.optimize


class Data:
    """SeiBot Data class

    Parameters
    ----------
    path_config : str
        Path of the configuration file.
    """
    def __init__(self, path_config):
        """Constructor
        path_config : str
            Path of the configuration file.
        """
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(path_config)

        # CDSutils options
        # start = config.read("CDSutils", "start")
        # duration = config.read("CDSutils", "duration")

    def get_seismic_noise(self):
        """Fetch and process seismometer data to get seismic noise
        
        Returns
        -------
        f : array
            Frequency array
        seismic_asd : array
            Amplitude spectral density of the seismic noise.
        """
        # Parse config
        seismometer_chan = self.config.get("Channels", "seismometer")
        seismometer_coh_chan = self.config.get("Channels", "seismometer_coh")
        f, seismic_asd = self.get_asd(channel=seismometer_chan)
        _, seismic_coh_asd = self.get_asd(channel=seismometer_coh_chan)
        _, coherence = self.get_coh(channel1=seismometer_chan,
                                 channel2=seismometer_coh_chan)

        # v TODO Warning: hardcode calibration
        seismic_asd *= 1/(2*np.pi*f) * 1e-9  # to displacement in meters

        seismic_asd = self.pad_seismic_noise(seismic_asd, coherence)

        return f, seismic_asd

    def get_seismometer_noise(self, dynamic=True):
        """ Fetch and process seismometer data to get seismometer noise

        Parameters
        ----------
        dynamic : bool, optional 
            Estimate real-time seismometer noise.
            If false, Or get it from the data base.
            Defaults True.

        Returns
        -------
        f : array
            Frequency array.
        seismometer_noise : array
            Amplitude spectral density of the seismometer noise.
        """
        seismometer_chan = self.config.get("Channels", "seismometer")
        seismometer_coh_chan = self.config.get("Channels", "seismometer_coh")
        f, seismic_asd = self.get_asd(channel=seismometer_chan)
        _, seismic_coh_asd = self.get_asd(channel=seismometer_coh_chan)
        _, coherence = self.get_coh(channel1=seismometer_chan,
                                 channel2=seismometer_coh_chan)

        # v TODO Warning: hardcode calibration
        seismic_asd *= 1/(2*np.pi*f) * 1e-9  # to displacement in meters
        
        cutoff_i = self._get_seismometer_cutoff(seismic_asd, coherence)
        # v Hardcode 0.01 
        f_mask = (f>0.01) * (f<f[cutoff_i])
        seismometer_noise = seismic_asd[f_mask]
        
        # Fit
        param = self.fit_seismometer_noise(f[f_mask], seismometer_noise)

        seismometer_asd = self._seismometer_noise_model(f, *param)
        
        return f, seismometer_asd

    def _get_seismometer_cutoff(self, seismic_asd, coherence):
        """Get the index in seismic_asd that divides noise and signal

        Parameters
        ----------
        seismic_asd : array
            Amplitude spectral density of the seismic noise readout
        coherence : array
            The coherence between the seismic noise readout and another
            seismic noise readout.

        Returns
        -------
        cutoff_i : int
            The cutoff index.
        """
        # v This is effectively setting a coherence threshold
        rounded_coh = np.round(coherence, 2)
        coh_one_i = np.min(np.where(rounded_coh == 1.00))  # When coh becomes 1
        # ^ This is effectively settting a coherence threshold

        min_asd_i = np.max(np.argmin(seismic_asd[:coh_one_i]))
        cutoff_i = min_asd_i

        return cutoff_i

    def fit_seismometer_noise(self, f, seismometer_noise):
        """Fit seismometer noise using an internal model.
        
        Parameters
        ----------
        f : array
            Frequency array.
        seismometer_noise : array
            The amplitude spectral density of the seismometer noise.

        Returns
        -------
        param : array
            The parameters for the model.
        """
        model = self._seismometer_noise_model
        param, _ = scipy.optimize.curve_fit(model,
                                            xdata=f,
                                            ydata=seismometer_noise)
        return param

    def pad_seismic_noise(self, seismic_asd, coherence):
        """Edge-pad seismometer noise from seismic noise readout
        
        Parameters
        ----------
        seismic_asd : array
            Amplitude spectral density of the seismic noise readout
        coherence : array
            The coherence between the seismic noise readout and another
            seismic noise readout.

        Returns
        -------
        seismic_asd : array
            The padded seismic noise amplitude spectral density
        """
        cutoff_i = self._get_seismometer_cutoff(seismic_asd, coherence)
        seismic_asd[:cutoff_i] = seismic_asd[cutoff_i]  # Edge-pad noises.
        
        return seismic_asd

    def _seismometer_noise_model(self, f, a, na):
        """Seismometer noise model
        
        Parameters
        ----------
        f : array
            Frequency array.
        a : float
            Frequency exponent.
        na : float
            Noise level at 1 Hz.
        """
        noise = na / f**a
        
        return noise

    def fetch(self, channel, duration, start=None):
        """ Fetch data given channel names

        Parameters
        ----------
        channel : str
            Channel name.
        duration : float
            Length of the data segment in seconds.
        start : float, optional
            Start time of the data, in GPS time.
            If not specified, start now.
            Defaults None.

        Returns
        -------
        time_series : cdsutils.TimeSeries
            The time series.
        """
        time_series = cdsutils.getdata(channel, duration=duration, start=start)

        return time_series

    def ts2asd(self, ts, fs, nperseg=None):
        """Time series to amplitude spectral density
        
        Parameters
        ----------
        ts : array
            Time series.
        fs : float
            Sampling frequency.
        nperseg : int, optional
            Length of each segment. Passed to ``scipy.signal.welch()''.
            Defaults to taking 1024 seconds of data.
        
        Returns
        -------
        f : array
            Frequency axis.
        asd : array
            Amplitude spectral density.
        """
        if nperseg is None:
            nperseg = int(fs*1024)  # Defaults to 1024 seconds ~0.001 Hz

        f, psd = scipy.signal.welch(ts, fs=fs, nperseg=nperseg)
        asd = psd**.5

        return f, asd

    def get_asd(self, channel, return_zero_frequency=False):
        """ Get an amplitude spectral density from a readout of a given channel

        Parameters
        ----------
        channel : str
            The readout channel.
        return_zero_frequency : bool
            Return frequency spectrum at 0 Hz.
            Defaults `False`.

        Returns
        -------
        f : array
            Frequency array
        asd : array
            The amplitude spectral density
        """
        # CDSutils setup
        duration = self.config.getfloat("CDSutils", "duration")
        start = self.config.getfloat("CDSutils", "start", fallback=None)
        
        # scipy.signal.welch setup
        nperseg = self.config.getint("Welch", "nperseg")

        # Get spectrum
        time_series = self.fetch(channel, duration=duration, start=start)

        ts = time_series.data
        fs = time_series.sample_rate

        # Welch
        f, asd = self.ts2asd(ts=ts, fs=fs, nperseg=nperseg)

        # Filters out 0 Hz
        if not return_zero_frequency:
            asd = asd[f>0]
            f = f[f>0]

        return f, asd

    def get_coh(self, channel1, channel2, return_zero_frequency=False):
        """ Get coherence function from two readouts

        Parameters
        ----------
        channel1 : str
            The readout channel1.
        channel2 : str
            The readout channel2.
        return_zero_frequency : bool
            Return frequency spectrum at 0 Hz.
            Defaults `False`.

        Returns
        -------
        f : array
            Frequency array
        asd : array
            The amplitude spectral density
        """
        # CDSutils setup
        # v Replace this with properties.
        duration = self.config.getfloat("CDSutils", "duration")
        start = self.config.getfloat("CDSutils", "start", fallback=None)
        
        # scipy.signal.welch setup
        nperseg = self.config.getint("Welch", "nperseg")

        # Get spectrum
        time_series1 = self.fetch(channel1, duration=duration, start=start)
        time_series2 = self.fetch(channel2, duration=duration, start=start)

        ts1 = time_series1.data
        ts2 = time_series2.data
        fs = time_series1.sample_rate
        
        # coherence
        f, coh = scipy.signal.coherence(x=ts1, y=ts2, fs=fs, nperseg=nperseg)

        # Filters out 0 Hz
        if not return_zero_frequency:
            coh = coh[f>0]
            f = f[f>0]

        return f, coh
