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
        self.foton = foton.FilterFile(path_foton_file)

    def get_filter_tf(self, module, fm_list):
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
        
    
    def get_zpk2tf(self, get_zpk, plane="s"):
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

        # put all zeros and poles into a list to avoid *=
        tf_list = []

        for zero in zeros:
            zero_real = zero.real
            zero_imag = zero.imag
            if zero == 0:
                # tf *= (s+zero)/(2*np.pi)
                tf_list.append((s+zero)/2*np.pi)
            elif zero_imag > 0 and zero_real != 0:
                wn = np.sqrt(zero_real**2 + zero_imag**2)
                q = wn / (2*zero_real)
                # tf *= (s**2 + wn/q*s + wn**2) / wn**2
                tf_list.append((s**2+wn/q*s+wn**2)/wn**2)
            elif zero_imag > 0 and zero_real == 0:
                wn = zero.imag
                # tf *= (s**2 + wn**2)/wn**2
                tf_list.append((s**2+wn**2)/wn**2)
            elif zero_imag == 0 and zero_real != 0:
                # tf *= (s+zero.real)/zero.real
                tf_list.append((s+zero_real)/zero_real)

        for pole in poles:
            pole_real = pole.real
            pole_imag = pole.imag
            if pole == 0:
                # tf /= (s+pole)/(2*np.pi)
                tf_list.append((2*np.pi)/(s+pole))
            elif pole_imag > 0 and pole_real != 0:
                wn = np.sqrt(pole_real**2 + pole_imag**2)
                q = wn / (2*pole_real)
                # tf /= (s**2 + wn/q*s + wn**2) / wn**2
                tf_list.append(wn**2/(s**2+wn/q*s+wn**2))
            elif pole_imag > 0 and pole_real == 0:
                wn = pole_imag
                # tf /= (s**2 + wn**2)/wn**2
                tf_list.append(wn**2/(s**2+wn**2))
            elif pole_imag == 0 and pole_real != 0:
                # tf /= (s+pole.real)/pole.real
                tf_list.append(pole_real/(s+pole_real))

        tf = np.prod(tf_list)

        if plane == "n":
            tf *= gain
        elif plane in "sf":
            tf *= gain / (tf.num[0][0][0]/tf.den[0][0][0])

        return tf
