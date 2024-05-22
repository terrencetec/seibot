"""Seibot foton"""
import control
import foton
import numpy as np


class Foton:
    """Foton class"""
    def __init__(self, path_foton_file):
        """Constructor
        
        Parameters
        ----------
        path_foton_file : str
            Path of the foton file.
        """
        self.path_foton_file = path_foton_file
        self.foton = foton.Filterfile(path_foton_file)

    def get_filter_tf(module, fm_list):
        """Get transfer function from a foton filter file
        Parameters
        ----------
        module : str
            Specify which filter module in the foton file.
        fm_list : list of int
            Specify list of engaged filter modules.

        Returns
        -------
        tf : TransferFunction
            The transfer function of the filter.
        """
        index_list = np.array(fm_list) - 1  # Compensate for foton offset
        tf_list = []
        
        for i in index_list:
            get_zpk = self.foton[module][i].get_zpk()
            _tf = self.get_zpk2tf(get_zpk)
            tf_list.append(_tf)

        tf = np.prod(tf_list)

        return tf
        
    
    def get_zpk2tf(self, get_zpk, plant="s"):
        """Convert output from foton get_zpk() into a transfer function
        
        Parameters
        ----------
        get_zpk : str
            The get_zpk() output.

        Returns
        -------
        tf : TransferFunction
            The converted transfer function.
        """
        zeros = get_zpk[0]
        poles = get_zpk[1]
        gain = get_zpk[2]

        if plane in "nf":
            # zeros poles are in Hz. Gain is DC.
            zeros *= 2*np.pi  # Convert to rad/s
            poles *= 2*np.pi
            raise ValueError('plane="n" or "f" not supported in this version.')
        #     print("nf")

        if plane in "sf":
            # Negate for (s+z), (s+p) convention.
            zeros = -zeros
            poles = -poles

        tf = control.tf([1], [1])
        s = control.tf("s")

        for zero in zeros:
            if zero == 0:
                tf *= (s+zero)/(2*np.pi)
            elif zero.imag > 0 and zero.real != 0:
                wn = np.sqrt(zero.real**2 + zero.imag**2)
                q = wn / (2*zero.real)
                tf *= (s**2 + wn/q*s + wn**2) / wn**2
            elif zero.imag > 0 and zero.real == 0:
                wn = zero.imag
                tf *= (s**2 + wn**2)/wn**2
            elif zero.imag == 0 and zero.real != 0:
                tf *= (s+zero.real)/zero.real

        for pole in poles:
            if pole == 0:
                tf /= (s+pole)/(2*np.pi)
            elif pole.imag > 0 and pole.real != 0:
                wn = np.sqrt(pole.real**2 + pole.imag**2)
                q = wn / (2*pole.real)
                tf /= (s**2 + wn/q*s + wn**2) / wn**2
            elif pole.imag > 0 and pole.real == 0:
                wn = pole.imag
                tf /= (s**2 + wn**2)/wn**2
            elif pole.imag == 0 and pole.real != 0:
                tf /= (s+pole.real)/pole.real

        if plane == "n":
            tf *= gain
        elif plane in "sf":
            tf *= gain / (tf.num[0][0][0]/tf.den[0][0][0])

        return tf
