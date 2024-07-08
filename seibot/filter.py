"""Seibot filter class"""
import configparser

import control
import numpy as np

import seibot.foton


class Filter(control.TransferFunction):
    """Filter class
    
    Attribute
    ---------
    filter_file : str
        The path of the foton file.
    module : str
        The filter module the filter is in.
    fm : list of int
        The engaged FMs of this filter
    """
    def __init__(self, *args):
        """Constructor"""
        super().__init__(*args)
        
    @property
    def module(self):
        """Foton module name"""
        return self._module

    @module.setter
    def module(self, _module):
        """Foton module setter
        
        Parameters
        ----------
        _module : str
            The foton module.
        """
        self._module = _module

    @property
    def fm(self):
        """Foton FM list"""
        return self._fm

    @fm.setter
    def fm(self, _fm):
        """Foton FM list setter
        
        Parameters
        ----------
        _fm : list of int
            The foton FM list.
        """
        self._fm = _fm


class FilterPool(list):
    """Filter pool"""
    def __init__(self, filter_config, inverse_filter=None):
        """Constructor
        
        Parameters
        ----------
        filter_config : str
            Path of the filter config.
        inverse_filter : control.TransferFunction, optional
            Filter representing the inverse response of a sensor.
            The inverse of this filter is applied to get rid of the
            calibration component of the filter, the filter is divided
            by the inverse_filter before putting it into the pool.
            Defaults None.
        """
        super().__init__()
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(filter_config)

        self.construct_filter_pool(inverse_filter)

    def construct_filter_pool(self, inverse_filter=None):
        """Construct the filter pool
        
        Parameters
        ----------
        inverse_filter : control.TransferFunction, optional
            Filter representing the inverse response of a sensor.
            The inverse of this filter is applied to get rid of the
            calibration component of the filter, the filter is divided
            by the inverse_filter before putting it into the pool.
            Defaults None.
        """
        if inverse_filter is None:
            inverse_filter = control.tf([1], [1])

        for filter_ in self.config.sections():
            filter_file = self.config[filter_].get("filter_file")
            module = self.config[filter_].get("module")
            fm = self.config[filter_].get("fm")

            # Convert fm str to list.
            fm_list = [int(fm.strip()) for fm in fm.split(",")]

            foton = seibot.foton.Foton(filter_file)
            tf = foton.get_filter_tf(module, fm_list)
            tf = tf / inverse_filter

            # Construct a filter instance
            filter_obj = Filter(tf)
            filter_obj.filter_file = filter_file
            filter_obj.module = module
            filter_obj.fm = fm

            # Append the instance to the pool
            self.append(filter_obj)


class FilterConfigurations:
    """Function class for all available filter configurations
    
    Parameters
    ----------
    sc_pool : seibot.FilterPool
        The pool of sensor correction filters.
    lp_pool : seibot.FilterPool
        The pool of low-pass filters.
    hp_pool : seibot.FilterPool
        The pool of high-pass filters.

    Returns
    -------
    filter_configuration : Dict
        Dictionary with key words ["sensor correction filter",
        "low pass filter", "high pass filter"].
    """
    def __init__(self,
                 sc_pool=None, lp_pool=None, hp_pool=None,
                 sc_config=None, lp_config=None, hp_config=None):
        """Constructor
        
        Parameters
        ----------
        sc_pool : seibot.FilterPool, optional
            The pool of sensor correction filters.
            If `sc_pool` is `None`, `sc_config` must be specified.
            Defaults `None`.
        lp_pool : seibot.FilterPool, optional
            The pool of low-pass filters.
            If `lp_pool` is `None`, `lp_config` must be specified.
            Defaults `None`.
        hp_pool : seibot.FilterPool, optional
            The pool of high-pass filters.
            If `hp_pool` is `None`, `hp_config` must be specified.
            Defaults `None`.
        sc_config : str, optional
            Path of the sensor correction filter config.
            Defaults `None`.
        lp_config : str, optional
            Path of the low-pass filter config.
            Defaults `None`
        hp_config : str, optional
            Path of the high-pass filter config.
            Defaults `None.
        """
        if sc_pool is None and sc_config is not None:
            sc_pool = FilterPool(sc_config)
        elif sc_pool is None and sc_config is None:
            raise ValueError("sc_pool or sc_config must be provided.")
        if lp_pool is None and sc_config is not None:
            lp_pool = FilterPool(sc_config)
        elif lp_pool is None and sc_config is None:
            raise ValueError("lp_pool or sc_config must be provided.")
        if hp_pool is None and sc_config is not None:
            hp_pool = FilterPool(sc_config)
        elif hp_pool is None and sc_config is None:
            raise ValueError("hp_pool or sc_config must be provided.")
        self.sc_pool = sc_pool
        self.lp_pool = lp_pool
        self.hp_pool = hp_pool

    def __call__(self, i, j):
        """ Returns a filter configuration tuple.
        
        Parameters
        ----------
        i : int
            Sensor correction index
        j : int
            Complementary filter index

        Returns
        -------
        filter_configuration : Dict
            Dictionary with key words ["sensor correction filter",
            "low pass filter", "high pass filter"].
        """
        sc = self.sc_pool[i]
        lp = self.lp_pool[j]
        hp = self.hp_pool[j]
        filter_configuration = {
            "sensor correction filter": sc,
            "low pass filter": lp,
            "high pass filter": hp
        }

        return filter_configuration


class InverseFilters:
    """Inverse response filters"""
    def __init__(self):
        """Constructor"""
        pass

    @property
    def gs13(self):
        """GS13 sensor inverse response filter"""
        s = control.tf("s")
        wn = 1*2*np.pi  # resonance at 1 Hz
        q = 1/np.sqrt(2)  # q at 0.707
        inverse = 1/s**3 * (s**2 + wn/q*s + wn**2)

        return inverse

    @property
    def sts(self):
        """STS sensor inverse response filter"""
        s = control.tf("s")
        inverse = 1/s

        return inverse

    @property
    def none(self):
        """Returns 1"""
        return control.tf([1], [1])
