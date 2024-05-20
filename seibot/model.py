"""Model Library
"""
import numpy as np


class Model:
    """Model class
    """
    def __init__(self):
        """Constructor"""
        pass

    def noise1(self, f, na, a):
        """Noise model with one frequency dependency

        Parameters
        ----------
        f : array
            Frequency axis
        na : float
            Noise level at 1 Hz.
        a : float
            Frequency dependency (reciprocal).

        Returns
        -------
        noise : array
            The amplitude spectral density of the noise.
        """
        noise = na/f**a

        return noise

    def noise2(self, f, na, nb, a, b):
        """Quadrature sum noise model

        Parameters
        ----------
        f : array
            Frequency axis
        na : float
            Noise level at 1 Hz for frequency dependency `a`.
        nb : float
            Noise level at 1 Hz for frequency dependency `b`.
        a : float
            Frequency dependency 1 (reciprocal).
        b : float
            Frequency depencency 2 (reciprocal).

        Returns
        -------
        noise : array
            The amplitude spectral density of the noise.
        """
        noise = ((na/f**a)**2 + (nb/f**b)**2)**.5

        return noise

    def second_order_plant(self, f, wn, q, dcgain):
        """Second order transfer function

        Parameters
        ----------
        f : array
            Frequency axis.
        wn : float
            Resonance frequency in rad/s.
        q : float
            Q factor.
        dcgain : float
            The DC gain of the transfer function.

        Returns
        -------
        freq_resp : array
            Frequency response of the plant
        """
        s = 1j*2*np.pi*f
        freq_resp = dcgain * wn**2 / (s**2 + wn/q*s + wn**2)

        return freq_resp
