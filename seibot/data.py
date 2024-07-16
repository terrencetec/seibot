"""Seibot Data
"""
import configparser

import cdsutils
import numpy as np
import scipy
import scipy.optimize

import seibot.foton
import seibot.gps
import seibot.model


class Data:
    """Seibot Data class

    Parameters
    ----------
    path_config : str
        Path of the configuration file.

    Attributes
    ----------
    f : array
        Frequency array.
    seismic_noise : array
        The amplitude spectral density of the seismic noise.
    seismometer_noise : array
        The amplitude spectral density of the seismometer noise.
    inertial_sensor_noise : array
        The amplitude spectral density of the inertial sensor noise.
    relative_sensor_noise : array
        The amplitude spectral density of the relative sensor noise.
    plant : TransferFunction
        The transfer function of the plant.
    transmissivity : TransferFunction
        The transfer function of the transmissivity.
    """
    def __init__(self, path_config):
        """Constructor
        path_config : str
            Path of the configuration file.
        """
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(path_config)

        # Fetch all data.
        channel_seismometer = self.config["Channels"].get("seismometer")
        channel_seismometer_coh = self.config["Channels"].get(
            "seismometer_coh")
        channel_inertial_sensor = self.config["Channels"].get(
            "inertial_sensor")
        channel_relative_sensor = self.config["Channels"].get(
            "relative_sensor")
        channel_witness_sensor = self.config["Channels"].get("witness_sensor")

        channel_list = [
            channel_seismometer,
            channel_seismometer_coh,
            channel_inertial_sensor,
            channel_relative_sensor,
            channel_witness_sensor,
        ]
        
        duration = self.config["CDSutils"].getfloat("duration")
        start = self.config["CDSutils"].getfloat("start", fallback=None)

        # Start now if not specified
        if start is None:
            start = seibot.gps.get_gpstime_now() - duration

        # Try in case not working with LIGO workstations.
        time_series = self.fetch(channel_list, duration, start)
        
        # Unpack time series
        ts_seismometer = time_series[0].data
        ts_seismometer_coh = time_series[1].data
        ts_inertial_sensor = time_series[2].data
        ts_relative_sensor = time_series[3].data
        ts_witness_sensor = time_series[4].data

        fs_seismometer = time_series[0].sample_rate
        fs_seismometer_coh = time_series[1].sample_rate
        fs_inertial_sensor = time_series[2].sample_rate
        fs_relative_sensor = time_series[3].sample_rate
        fs_witness_sensor = time_series[4].sample_rate
        
        # Resample
        fs = fs_seismometer  # Adhere to seismometer readout.
        if fs_seismometer_coh != fs:
            q = int(fs_seismometer_coh / fs)
            ts_seismometer_coh = self.resample(ts_seismometer_coh, q)
        if fs_inertial_sensor != fs:
            q = int(fs_inertial_sensor / fs)
            ts_inertial_sensor = self.resample(ts_inertial_sensor, q)
        if fs_relative_sensor != fs:
            q = int(fs_relative_sensor / fs)
            ts_relative_sensor = self.resample(ts_relative_sensor, q)
        if fs_witness_sensor != fs:
            q = int(fs_witness_sensor / fs)
            ts_witness_sensor = self.resample(ts_witness_sensor, q)

        ## Convert to attribute and have getters access them

        self.ts_seismometer = ts_seismometer
        self.ts_seismometer_coh = ts_seismometer_coh
        self.ts_inertial_sensor = ts_inertial_sensor
        self.ts_relative_sensor = ts_relative_sensor
        self.ts_witness_sensor = ts_witness_sensor

        self.fs = fs


        # Initiallize dummy frequency axis:
        duration = self.config.getfloat("CDSutils", "duration")
        nperseg = self.config.getint("Welch", "nperseg")
        if self.fs is None:
            self.fs = self.config.getfloat("Welch", "fs")
        n_data = int(fs * duration)
        data = np.random.normal(loc=0, scale=1, size=n_data)
        f, _ = scipy.signal.welch(data, fs=fs, nperseg=nperseg)
        f = f[1:]  # Remove DC
        self.f = f

        # Initialize attributes
        # Use seismometer f array if exists.
        self.f, self.seismic_noise = self.get_seismic_noise()
        _, self.seismometer_noise = self.get_seismometer_noise()
        _, self.inertial_sensor_noise = self.get_inertial_sensor_noise()
        _, self.relative_sensor_noise = self.get_relative_sensor_noise()
        _, self.plant = self.get_plant()
        _, self.transmissivity = self.get_transmissivity()
        _, self.controller = self.get_controller()
        
    @property
    def fs(self):
        """Sample rate"""
        return self._fs

    @fs.setter
    def fs(self, _fs):
        """Sample rate setter"""
        self._fs = _fs

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
    def seismometer_noise(self):
        """Seismometer noise"""
        return self._seismometer_noise

    @seismometer_noise.setter
    def seismometer_noise(self, _seismometer_noise):
        """Seismometer noise setter"""
        self._seismometer_noise = _seismometer_noise

    @property
    def inertial_sensor_noise(self):
        """Inertial sensor noise"""
        return self._inertial_sensor_noise

    @inertial_sensor_noise.setter
    def inertial_sensor_noise(self, _inertial_sensor_noise):
        """Inertial sensor noise setter"""
        self._inertial_sensor_noise = _inertial_sensor_noise

    @property
    def relative_sensor_noise(self):
        """Relative sensor noise"""
        return self._relative_sensor_noise
    
    @relative_sensor_noise.setter
    def relative_sensor_noise(self, _relative_sensor_noise):
        """Relative sensor noise setter"""
        self._relative_sensor_noise = _relative_sensor_noise

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
        """Controller.setter"""
        self._controller = _controller

    def get_inertial_sensor_noise(self):
        """Get inertial sensor noise
        
        Returns
        -------
        f : array
            Frequency array.
        inertial_asd : array
            Amplitude spectral density of the inertial sensor noise.
        """
        dynamic = self.config["Inertial sensor"].getboolean("dynamic")

        if dynamic:
            f, inertial_asd = self.model_inertial_asd()
        else:
            f, inertial_asd = self.get_modeled("Inertial sensor")

        return f, inertial_asd

    def get_relative_sensor_noise(self):
        """Get relative sensor noise
        
        Returns
        -------
        f : array
            Frequency array.
        relative_asd : array
            Amplitude spectral density of the inertial sensor noise.
        """
        dynamic = self.config["Relative sensor"].getboolean("dynamic")
        
        if dynamic:
            f, relative_asd = self.model_relative_asd()
        else:
            f, relative_asd = self.get_modeled("Relative sensor")

        return f, relative_asd

    def get_plant(self):
        """Get plant

        Returns
        -------
        f : array
            Frequency array
        plant : TransferFunction
            The frequency response of the plant.
        """
        dynamic = self.config["Plant"].getboolean("dynamic")

        if dynamic:
            f, plant = self.model_plant()
        else:
            f, plant = self.get_modeled("Plant")

        return f, plant

    def get_transmissivity(self):
        """Get transmissivity
        
        Returns
        -------
        f : array
            Frequency array
        transmissivity : TransferFunction
            The frequency response of the transmissivity
        """
        dynamic = self.config["transmissivity"].getboolean("dynamic")
        
        if dynamic:
            f, transmissivity = self.model_transmissivity()
        else:
            f, transmissivity = self.get_modeled("Transmissivity")

        return f, transmissivity

    def get_controller(self):
        """Get controller

        Returns
        -------
        f : array
            Frequency array
        controller : TransferFunction
            The controller.
        """
        filter_file = self.config["Controller"].get("filter_file")
        module = self.config["Controller"].get("module")
        fm = self.config["Controller"].get("fm")

        fm_list = [int(fm.strip()) for fm in fm.split(",")]

        foton = seibot.foton.Foton(filter_file)
        controller = foton.get_filter_tf(module, fm_list)

        f = self.f  # Dummy

        return f, controller

    def get_seismic_noise(self):
        """Fetch and process seismometer data to get seismic noise
        
        Returns
        -------
        f : array
            Frequency array
        seismic_asd : array
            Amplitude spectral density of the seismic noise.
        """
        dynamic = self.config.getboolean("Seismic", "dynamic")
        if dynamic:
            f, seismic_asd = self.dynamic_seismic_asd()

#             # Parse config
#             seismometer_chan = self.config.get("Channels", "seismometer")
#             seismometer_coh_chan = self.config.get("Channels", "seismometer_coh")
#             f, seismic_asd = self.get_asd(channel=seismometer_chan)
#             _, seismic_coh_asd = self.get_asd(channel=seismometer_coh_chan)
#             _, coherence = self.get_coh(channel1=seismometer_chan,
#                                      channel2=seismometer_coh_chan)

#             # v TODO Warning: hardcode calibration
#             seismic_asd *= 1/(2*np.pi*f) * 1e-9  # to displacement in meters

#             seismic_asd = self.pad_seismic_noise(seismic_asd, coherence)
        else:
            f, seismic_asd = self.get_modeled("Seismic")
            seismic_asd = abs(seismic_asd(1j*2*np.pi*f))

        return f, seismic_asd

    def get_seismometer_noise(self):
        """ Fetch and process seismometer data to get seismometer noise

        Returns
        -------
        f : array
            Frequency array.
        seismometer_noise : array
            Amplitude spectral density of the seismometer noise.
        """
        dynamic = self.config.getboolean("Seismometer", "dynamic")

        if dynamic:
            f, seismometer_asd = self.dynamic_seismometer_noise()
            # seismometer_chan = self.config.get("Channels", "seismometer")
            # seismometer_coh_chan = self.config.get("Channels", "seismometer_coh")
            # f, seismic_asd = self.get_asd(channel=seismometer_chan)
            # _, seismic_coh_asd = self.get_asd(channel=seismometer_coh_chan)
            # _, coherence = self.get_coh(channel1=seismometer_chan,
            #                          channel2=seismometer_coh_chan)

            # # v TODO Warning: hardcode calibration
            # seismic_asd *= 1/(2*np.pi*f) * 1e-9  # to displacement in meters
            
            # cutoff_i = self._get_seismometer_cutoff(seismic_asd, coherence)
            # # v Hardcode 0.01 
            # f_mask = (f>0.01) * (f<f[cutoff_i])
            # seismometer_noise = seismic_asd[f_mask]
            
            # # Fit
            # param = self.fit_seismometer_noise(f[f_mask], seismometer_noise)

            # seismometer_asd = self._seismometer_noise_model(f, *param)
        else:
            f, seismometer_asd = self.get_modeled("Seismometer")        

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
        array
            The amplitude spectral density of the modeled seismometer noise.
        """
        # Parse
        model_name = self.config.get("Seismometer", "model")
        
        # Get model
        model = seibot.model.Model()
        model_method = getattr(model, model_name)

        # Fit
        param, _ = scipy.optimize.curve_fit(model_method,
                                            xdata=f,
                                            ydata=seismometer_noise)
        return model_method(f, *params)

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

    def dynamic_seismic_asd(self):
        """Estimate dynamic seismic noise asd
        
        Returns
        -------
        f : array
            Frequency array.
        seismic_asd : array
            Amplitude spectral density of the seismic noise.
        """
        nperseg = self.config["Welch"].getint("nperseg")

        f, seismic_asd = self.ts2asd(self.ts_seismometer, self.fs, nperseg)
        _, coh = self.ts2coh(
            self.ts_seismometer, self.ts_seismometer_coh, self.fs, nperseg)

        # Calibrate spectrum to displacement unit.
        calibration = self.config["Calibration"]["seismometer"]
        inv_filter = seibot.filter.InverseFilters()
        cal_filter = getattr(inv_filter, calibration)
        seismic_asd = seismic_asd * abs(cal_filter(1j*2*np.pi*f))
        seismic_asd = seismic_asd * 1e-9  # From nm to m. TODO avoid hardcode.

        seismic_asd = self.pad_seismic_noise(seismic_asd, coh)

        return f, seismic_asd

    def dynamic_seismometer_asd(self):
        """Estimate dynamic seismometer noise
        
        Returns
        -------
        f : array
            Frequency array.
        seismometer_asd : array
            Amplitude spectral density of the seismometer noise.
        """
        nperseg = self.config["Welch"].getint("nperseg")

        f, seismic_asd = self.ts2asd(self.ts_seismometer, self.fs, nperseg)
        _, coh = self.ts2coh(
            self.ts_seismometer, self.ts_seismometer_coh, self.fs, nperseg)

        # Calibrate spectrum to displacement unit.
        calibration = self.config["Calibration"].get("seismometer")
        inv_filter = seibot.filter.InverseFilters()
        cal_filter = getattr(inv_filter, calibration)
        seismic_asd = seismic_asd * abs(cal_filter(1j*2*np.pi*f))
        seismic_asd = seismic_asd * 1e-9  # From nm to m. TODO avoid hardcode.

        cutoff_i = self._get_seismometer_cutoff(seismic_asd, coherence)
        # v TODO avoid Hardcode 0.01 
        f_mask = (f>0.01) * (f<f[cutoff_i])
        seismometer_noise = seismic_asd[f_mask]
        
        # Fit
        seismometer_asd = self.fit_seismometer_noise(
            f[f_mask], seismometer_noise)

        return f, seismometer_asd

    def dynamic_inertial_asd(self):
        """Estimate dynamic inertial sensor noise.

        Returns
        -------
        f : array
            Frequency array
        inertial_asd : array
            Amplitude spectral density of the inertial sensor noise.
        """
        nperseg = self.config["Welch"].getint("nperseg")

        f, inertial_asd = self.ts2asd(
            self.ts_inertial_sensor, self.fs, nperseg)
        f, coh = self.ts2coh(
            self.ts_inertial_sensor, self,ts_seismometer_coh, self.fs, nperseg)

        # Calibrate
        calibration = self.config["Calibration"].get("inertial_sensor")
        inv_filter = seibot.filter.InverseFilters()
        cal_filter = getattr(inv_filter, calibration)
        inertial_asd = inertial_asd * abs(cal_filter(1j*2*np.pi*f))
        inertial_asd = inertial_asd * 1e-9  # From nm to m.TODO avoid hardcode.

        rounded_coh = np.round(coh, 2)
        pass
        ...
        # TODO Unfinished code 

        # v copied from Sushant's branch.
        # rounded_coh = np.round(coh, 2)
        # upper_limit = np.min(np.where(asd_ham8_gs13.frequencies.value == cutoff))
        # last_low_coh = np.max(np.where(rounded_coh[0:upper_limit] < 0.2))
        # frequency = asd_ham8_gs13.frequencies[last_low_coh]
        # freq_used =  asd_ham8_gs13.frequencies.value[1:]
        # print(freq_used)
        # upper = np.max(np.where(freq_used == frequency.value))
        # new_gs13 = np.concatenate((asd_ham8_gs13.value[0:upper], n_gs13[upper:]), axis=0)
        return f, inertial_asd

    def dynamic_relative_asd(self):
        """Estimate dynamic relative sensor.

        Returns
        -------
        f : array
            Frequency array
        relative_asd : array
            Amplitude spectral density of the relative sensor noise.
        """
        raise ValueError("Dynamic relative sensor noise is not supported.")

    def dynamic_plant(self):
        """Estimate dynamic plant.

        Returns
        -------
        f : array
            Frequency array
        plant : control.TransferFunction
            Transfer function of the plant.
        """
        raise ValueError("Dynamic plant is not supported.")

    def dynamic_transmissivity(self):
        """Estimate dynamic transmissivity

        Returns
        -------
        f : array
            Frequency array
        transmissivity : control.TransferFunction
            Transfer function of the transmissivity.
        """
        raise ValueError("Dynamic transmissivity is not supported.")


    def get_modeled(self, instrument):
        """Get modeled spectrum/frequency response
        
        Parameters
        ----------
        instrument : str
            Specify which model.
            Choose from ["Seismometer", "Inertial sensor", "Relative sensor",
            "Plant", "Transmissivity"].

        Returns
        -------
        f : array
            Frequency array.
        frequency_series : array
            The modeled frequency series.
        """
        # Parse config.
        model_name = self.config.get(instrument, "model")
        path_parameters = self.config.get(instrument, "parameters_path")
        
        # Get model
        model = seibot.model.Model()
        model_method = getattr(model, model_name)

        # Get parameters
        parameters = np.loadtxt(path_parameters)

        # Evaluate frequency series
        f = self.f
        frequency_series = model_method(f, *parameters)

        return f, frequency_series

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

    def ts2asd(self, ts, fs, nperseg=None, return_zero_frequency=False):
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
        return_zero_frequency : bool
            Return frequency spectrum at 0 Hz.
            Defaults `False`.
        
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

        if not return_zero_frequency:
            asd = asd[f>0]
            f = f[f>0]

        return f, asd

    # def get_asd(self, channel, return_zero_frequency=False):
    #     """ Get an amplitude spectral density from a readout of a given channel

    #     Parameters
    #     ----------
    #     channel : str
    #         The readout channel.
    #     return_zero_frequency : bool
    #         Return frequency spectrum at 0 Hz.
    #         Defaults `False`.

    #     Returns
    #     -------
    #     f : array
    #         Frequency array
    #     asd : array
    #         The amplitude spectral density
    #     """
    #     # CDSutils setup
    #     duration = self.config.getfloat("CDSutils", "duration")
    #     start = self.config.getfloat("CDSutils", "start", fallback=None)
        
    #     # scipy.signal.welch setup
    #     nperseg = self.config.getint("Welch", "nperseg")

    #     # Get spectrum
    #     time_series = self.fetch(channel, duration=duration, start=start)
        
    #     # TODO resampling

    #     ts = time_series.data
    #     fs = time_series.sample_rate

    #     # Welch
    #     f, asd = self.ts2asd(ts=ts, fs=fs, nperseg=nperseg)

    #     # Filters out 0 Hz
    #     if not return_zero_frequency:
    #         asd = asd[f>0]
    #         f = f[f>0]

    #     return f, asd

    def ts2coh(self, ts1, ts2, fs, nperseg=None, return_zero_frequency=False):
        """ Returns coherence function of two signals.

        Parameters
        ----------
        ts1 : array
            Time series 1.
        ts2 : array
            Time series 2
        fs : float
            Sampling frequency.
        nperseg : int, optional
            Length of each segment. Passed to ``scipy.signal.welch()''.
            Defaults to taking 1024 seconds of data.
        return_zero_frequency : bool
            Return frequency spectrum at 0 Hz.
            Defaults `False`.
        
        Returns
        -------
        f : array
            Frequency axis.
        coh : array
            Coherence function
        """
        nperseg = self.config["Welch"].getint("nperseg")

        f, coh = scipy.signal.coherence(x=ts1, y=ts2, fs=fs, nperseg=nperseg)

        # Filters out 0 Hz
        if not return_zero_frequency:
            coh = coh[f>0]
            f = f[f>0]

        return f, coh

    # def get_coh(self, channel1, channel2, return_zero_frequency=False):
    #     """ Get coherence function from two readouts

    #     Parameters
    #     ----------
    #     channel1 : str
    #         The readout channel1.
    #     channel2 : str
    #         The readout channel2.
    #     return_zero_frequency : bool
    #         Return frequency spectrum at 0 Hz.
    #         Defaults `False`.

    #     Returns
    #     -------
    #     f : array
    #         Frequency array
    #     asd : array
    #         The amplitude spectral density
    #     """
    #     # CDSutils setup
    #     # v Replace this with properties.
    #     duration = self.config.getfloat("CDSutils", "duration")
    #     start = self.config.getfloat("CDSutils", "start", fallback=None)
        
    #     # scipy.signal.welch setup
    #     nperseg = self.config.getint("Welch", "nperseg")

    #     # Get spectrum
    #     time_series1 = self.fetch(channel1, duration=duration, start=start)
    #     time_series2 = self.fetch(channel2, duration=duration, start=start)

    #     ts1 = time_series1.data
    #     ts2 = time_series2.data
    #     fs = time_series1.sample_rate
        
    #     # coherence
    #     f, coh = scipy.signal.coherence(x=ts1, y=ts2, fs=fs, nperseg=nperseg)

    #     # Filters out 0 Hz
    #     if not return_zero_frequency:
    #         coh = coh[f>0]
    #         f = f[f>0]

    #     return f, coh

    def resample(self, ts, q):
        """Down sample. scipy.signal.decimate() wrapper.

        Parameters
        ----------
        ts : array
            Time series.
        q : int
            Down sampling factor.

        Returns
        -------
        ts : array
            Downsampled time series
        """
        ts = scipy.signal.decimate(ts, ftype="fir", q=q)
        return ts
