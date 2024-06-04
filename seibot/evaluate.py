"""Evaluate class"""


class Evaluate:
    """Evaluate class

    Note
    ----
    This class contains internal methods that evaluate
    seismic isolation performance.

    Each method takes a pool of configurations and a system and 
    returns the best configuration.
    """
    def __init__(self):
        """Constructor"""
        pass

    def rms_displacement(self, isolation_system, isolation_configurations):
        """Returns a configuration with lowest RMS displacement.
        
        Parameters
        ----------
        isolation_system : seibot.IsolationSystem
           The isolation system with sensors and plants specified.
        isolation_configurations : seibot.IsolationConfigurations
            The isolation configurations with all possible
            seismic isolation control configurations.
        """
        pass
