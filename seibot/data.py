"""SeiBot Data
"""
import configparser

import cdsutils


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
        seismic_noise : array
            Amplitude spectral density of the seismic noise.
        """
        ## vv Replace with a common function vv
        # Parse config
        chan = self.config.get("Channels", "seismometer")
        duration = self.config.get("CDSutils", "duration")
        start = self.config.get("CDSutils", "start")
        
        nperseg = self.config.get("Spectral", "nperseg")

        # Get spectrum
        time_series = self.fetch(channel, duration=duration, start=start)

        ts = time_series.data
        fs = time_series.sample_rate

        f, psd = self.ts2asd(ts=ts, fs=fs, nperseg=nperseg)
        asd = psd**.5
        ## ^^ Replace with a common function ^^

        asd *= 1/(2*np.pi*f) * 1e-9  # to displacement in meters.
        seismic_noise = self.pad_seismic_noise(asd)  # Do some magic
        return f, seismic_noise

    def get_seismometer_noise(self, adaptive=True):
        """ Fetch and process seismometer data to get seismometer noise

        Parameters
        ----------
        adaptive : Bool
            Estimate real-time seismometer noise
        
        Returns
        -------
        f : array
            Frequency array.
        seismometer_noise : array
            Amplitude spectral density of the seismometer noise.
        """
        pass

    def pad_seismic_noise(self, asd):
        """Pad seismic noise amplitude spectral density"""
        # Sushant help.
        return asd

    def fetch(self, channel, duration):
        """ Fetch data given channel names

        Parameters
        ----------
        channel : str
            Channel name.

        Returns
        -------
        time_series : cdsutils.TimeSeries
            The time series.
        """
        time_series = cdsutils.getdata(channel, duration=duration)
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
