"""Seibot filter class"""
import configparser

import control

import seibot.foton


class Filter(control.TransferFunction):
    """Filter class
    
    Attribute
    ---------
    foton_file : str
        The path of the foton file.
    foton_module : str
        The filter module the filter is in.
    foton_fm : list of int
        The engaged FMs of this filter
    """
    def __init__(self, *args):
        """Constructor"""
        super().__init__(*args)
        
    @property
    def foton_module(self):
        """Foton module name"""
        return self._foton_module

    @foton_module.setter
    def foton_module(self, _foton_module):
        """Foton module setter
        
        Parameters
        ----------
        _foton_module : str
            The foton module.
        """
        self._foton_module = _foton_module

    @property
    def foton_fm(self):
        """Foton FM list"""
        return self._foton_fm

    @foton_fm.setter
    def foton_fm(self, _foton_fm):
        """Foton FM list setter
        
        Parameters
        ----------
        _foton_fm : list of int
            The foton FM list.
        """
        self._foton_fm = _foton_fm


class FilterPool:
    """Filter pool"""
    def __init__(self, filter_config):
        """Constructor
        
        Parameters
        ----------
        filter_config : str
            Path of the filter config.
        """
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.optionxform = str
        self.config.read(filter_config)

        self.construct_filter_pool()

    def __call__(self):
        """Returns a list of filters"""
        return self.filter_pool

    def construct_filter_pool(self):
        """Construct the filter pool"""
        self.filter_pool = []

        for filter_ in self.config.sections():
            foton_file = self.config[filter_].get("foton_file")
            foton_module = self.config[filter_].get("foton_module")
            foton_fm = self.config[filter_].get("foton_fm")

            # Convert foton_fm str to list.
            fm_list = [int(fm.strip()) for fm in foton_fm.split(",")]

            foton = seibot.foton.Foton(foton_file)
            tf = foton.get_filter_tf(foton_module, fm_list)

            # Construct a filter instance
            filter_obj = Filter(tf)
            filter_obj.foton_file = foton_file
            filter_obj.foton_module = foton_module
            filter_obj.foton_fm = foton_fm

            # Append the instance to the pool
            self.filter_pool.append(filter_obj)
