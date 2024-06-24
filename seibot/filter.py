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
    def __init__(self, filter_config):
        """Constructor
        
        Parameters
        ----------
        filter_config : str
            Path of the filter config.
        """
        super().__init__()
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(filter_config)

        self.construct_filter_pool()


    def construct_filter_pool(self):
        """Construct the filter pool"""
        for filter_ in self.config.sections():
            filter_file = self.config[filter_].get("filter_file")
            module = self.config[filter_].get("module")
            fm = self.config[filter_].get("fm")

            # Convert fm str to list.
            fm_list = [int(fm.strip()) for fm in fm.split(",")]

            foton = seibot.foton.Foton(filter_file)
            tf = foton.get_filter_tf(module, fm_list)

            # Construct a filter instance
            filter_obj = Filter(tf)
            filter_obj.filter_file = filter_file
            filter_obj.module = module
            filter_obj.fm = fm

            # Append the instance to the pool
            self.append(filter_obj)


class FilterConfigurations:
    """All available filter configurations
    
    Parameters
    ----------
    sc_pool : seibot.FilterPool
        The pool of sensor correction filters.
    lp_pool : seibot.FilterPool
        The pool of low-pass filters.
    hp_pool : seibot.FilterPool
        The pool of high-pass filters.

    Attributes
    ----------
    matrix : array of shape(len(sc_pool), len(lp_pool))
        Configuration matrix with elements containing
        `(seibot.Filter, (seibot.Filter, seibot.Filter))`,
        the sensor correction filter and the 2 complementary filters.
    """
    def __init__(self, sc_pool, lp_pool, hp_pool):
        """Constructor
        
        Parameters
        ----------
        sc_pool : seibot.FilterPool
            The pool of sensor correction filters.
        lp_pool : seibot.FilterPool
            The pool of low-pass filters.
        hp_pool : seibot.FilterPool
            The pool of high-pass filters.
        """
        len_sc = len(sc_pool)
        len_lp = len(lp_pool)
        matrix = np.empty(shape=(len_sc, len_lp))
        for i in range(len(matrix)):
            for j in range(len(matrix)[0]):
                matrix[i, j] = (sc_pool[i], (lp_pool[j], hp_pool[j]))
        self.matrix = matrix

    @property
    def matrix(self):
        """Configuration matrix"""
        return self._matrix
    
    @matrix.setter
    def matrix(self, _matrix):
        """Configuration matrix setter"""
        self._matrix = _matrix
    

class InverseFilters:
    """Inverse response filters"""
    def __init__(self):
        """Constructor"""
        pass

    def gs13(self):
        """GS13 sensor inverse response filter"""
        s = control.tf("s")
        wn = 1*2*np.pi  # resonance at 1 Hz
        q = 1/np.sqrt(2)  # q at 0.707
        invese = 1/s**3 * (s**2 + wn/q*s + wn**2)

        return inverse

    def sts(self):
        """STS sensor inverse response filter"""
        s = control.tf("s")
        inverse = 1/s

        return inverse
