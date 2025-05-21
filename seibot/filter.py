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
    def __init__(
            self, tf=None,
            filter_file=None, module=None, fm=None,
            f=None, inverse_filter=None):
        """Constructor"""
        if inverse_filter is None:
            inverse_filter = control.tf([1], [1])
        
        if tf is not None:
            pass
        elif (filter_file is not None
                and module is not None
                and fm is not None):
            foton = seibot.foton.Foton(filter_file)
            tf = foton.get_filter_tf(module, fm)
            self.filter_file = filter_file
            self.module = module
            self.fm = fm
        else:
            raise ValueError(
                "Either tf or (filter_file, module, fm) must be specified")
        tf = tf / inverse_filter
        super().__init__(tf)

        if f is not None:
            self.mag = abs(tf(1j*2*np.pi*f))
            self.mag_comp = abs((1-tf)(1j*2*np.pi*f))
            self.f = f
        
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

    @property
    def mag(self):
        """Magnitude response"""
        return self._mag
    
    @mag.setter
    def mag(self, _mag):
        """Magnitude response"""
        self._mag = _mag

    @property
    def mag_comp(self):
        """Magnitude response of the complement filter"""
        return self._mag_comp
    
    @mag_comp.setter
    def mag_comp(self, _mag_comp):
        """mag_comp.setter"""
        self._mag_comp = _mag_comp

    @property
    def f(self):
        """Frequency"""
        return self._f

    @f.setter
    def f(self, _f):
        """f.setter"""
        self._f = _f

# def make_filter(filter_file, module
class FilterPool(list):
    """Filter pool"""
    def __init__(self, f, filter_config, inverse_filter=None):
        """Constructor
        
        Parameters
        ----------
        f : array
            Frequency array
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

        self.construct_filter_pool(f, inverse_filter)

    def construct_filter_pool(self, f, inverse_filter=None):
        """Construct the filter pool
        
        Parameters
        ----------
        f : array
            Frequency array.
        inverse_filter : control.TransferFunction, optional
            Filter representing the inverse response of a sensor.
            The inverse of this filter is applied to get rid of the
            calibration component of the filter, the filter is divided
            by the inverse_filter before putting it into the pool.
            Defaults None.
        """
        if inverse_filter is None:
            inverse_filter = control.tf([1], [1])

        filter_file = ""
        for filter_ in self.config.sections():
            # This if-else statement avoids unnecssary calls
            # of the python-foton module, which is slow.
            if filter_file == self.config[filter_].get("filter_file"):
                pass
            else:
                filter_file = self.config[filter_].get("filter_file")
                foton = seibot.foton.Foton(filter_file)

            module = self.config[filter_].get("module")
            fm = self.config[filter_].get("fm")

            # Convert fm str to list.
            fm_list = [int(fm.strip()) for fm in fm.split(",")]

            filter_obj = Filter(
                filter_file=filter_file,
                module=module,
                fm=fm_list,
                f=f,
                inverse_filter=inverse_filter)
            # # get_filter_tf is slow.
            # tf = foton.get_filter_tf(module, fm_list)
            # tf = tf / inverse_filter

            # # Construct a filter instance
            # filter_obj = Filter(tf)
            # filter_obj.filter_file = filter_file
            # filter_obj.module = module
            # filter_obj.fm = fm
            # # Storing the magnitude response makes future calculations
            # # faster.
            # filter_obj.mag = abs(tf(1j*2*np.pi*f))
            # filter_obj.mag_comp = abs((1-tf)(1j*2*np.pi*f))

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
            raise ValueError("lp_pool or lp_config must be provided.")
        if hp_pool is None and sc_config is not None:
            hp_pool = FilterPool(sc_config)
        elif hp_pool is None and sc_config is None:
            raise ValueError("hp_pool or hp_config must be provided.")
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

        filter_configuration = FilterConfiguration(sc, lp, hp)
        # filter_configuration = {
        #     "sensor correction filter": sc,
        #     "low pass filter": lp,
        #     "high pass filter": hp
        # }

        return filter_configuration


class FilterConfiguration(dict):
    """Filter Configuration"""
    def __init__(self, sc, lp, hp):
        """Constructor"""
        super().__init__()
        self.sc = sc
        self.lp = lp
        self.hp = hp

    @property
    def sc(self):
        """Sensor correction filter"""
        return self._sc
    
    @sc.setter
    def sc(self, _sc):
        """Sensor correction filter setter"""
        self._sc = _sc
        self["sensor correction filter"] = _sc

    @property
    def lp(self):
        """Low pass filter"""
        return self._lp
    
    @lp.setter
    def lp(self, _lp):
        """Low pass filter setter"""
        self._lp = _lp
        self["low pass filter"] = _lp

    @property
    def hp(self):
        """High pass filter"""
        return self._hp
    
    @hp.setter
    def hp(self, _hp):
        """High pass filter setter"""
        self._hp = _hp
        self["high pass filter"] = _hp
    
    def export(self, path):
        """Export filter configuration to path"""
        sc = self.sc
        lp = self.lp
        hp = self.hp

        config = configparser.ConfigParser()
        config["Sensor correction filter"] = {
            "filter_file": sc.filter_file,
            "module": sc.module,
            "fm": str(sc.fm)[1:-1]
        }
        config["Low pass filter"] = {
            "filter_file": lp.filter_file,
            "module": lp.module,
            "fm": str(lp.fm)[1:-1]
        }
        config["High pass filter"] = {
            "filter_file": hp.filter_file,
            "module": hp.module,
            "fm": str(hp.fm)[1:-1]
        }

        with open(path, "w") as file:
            config.write(file)


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
        inverse = (s**2 + wn/q*s + wn**2) / s**3

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
