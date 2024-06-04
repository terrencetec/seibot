"""Seibot class
"""
import seibot.data
import seibot.forecast
import seibot.filter


class Seibot:
    """Seibot class

    Parameters
    ----------
    config : str
        Path of the Seibot configuration file

    Attribute
    ---------
    data : seibot.data.Data
    forecaster :
    """
    def __init__(self, config):
        """Constructor

        Parameters
        ----------
        config : str
            Path of the Seibot configuration file.
        """
        self.config = configparser.ConfigParser(allow_now_value=True)
        self.config.optionxform = str
        self.config.read(config)

        # Fetch sensor noise and plant data from database/real-time.
        self.data = seibot.data.Data(config)
        
        # Fetch all available filters from foton file.
        sc_config = self.config.get("Sensor correction filters", "config")
        lp_config = self.config.get("Low pass filters", "config")
        hp_config = self.config.get("High pass filters", "config")

        self.sc_pool = seibot.filter.FilterPool(sc_config)
        self.lp_pool = seibot.filter.FilterPool(lp_config)
        self.hp_pool = seibot.filter.FilterPool(hp_config)
        

        
