"""Seibot GUI Plot"""
import tkinter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as mplstyle


mplstyle.use('fast')
plt.rcParams["font.size"] = 14


class Plot(tkinter.Frame):
    """Plot frame"""
    def __init__(self, master, figsize):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent
        figsize : tuple
            pyplot figure size.
        """
        super().__init__(master)
        fig, ax = plt.subplots(figsize=figsize)
        self.fig = fig
        self.ax = ax
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().pack()


class MainPlot(Plot):
    """Main Plot"""
    def __init__(self, master, figsize=(16*2/3, 9*2/3)):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent
        figsize : tuple, optional
            pyplot figure size.
            Defaults (16*2/3, 9*2/3).
        """
        super().__init__(master, figsize)
        self.selected_ln, = self.ax.loglog([], [], "C1", zorder=2)
        self.min_disp_ln, = self.ax.loglog([], [], "C2", zorder=3)
        self.min_vel_ln, = self.ax.loglog([], [], "C3", zorder=4)
        self.tebo_ln, = self.ax.loglog([], [], "C4", zorder=5)

        self.seismic_ln, = self.ax.loglog([], [], "C0--", alpha=.5, zorder=0)
        self.seismometer_ln, = self.ax.loglog(
            [], [], "C1--", alpha=.5, zorder=0)
        self.relative_ln, = self.ax.loglog([], [], "C2--", alpha=.5, zorder=0)
        self.inertial_ln, = self.ax.loglog([], [], "C3--", alpha=.5, zorder=0)

        self.all_ln = []
        self.all_ln_label, = self.ax.loglog([], [], "k", alpha=.5, zorder=0)
        self.threshold_ln = []
        self.threshold_ln_label, = self.ax.loglog(
            [], [], "C0", alpha=.5, zorder=1)

        self.all_bound_ln = self.ax.fill_between([], [], [])
        self.threshold_bound_ln = self.ax.fill_between([], [], [])

        self.witness_ln, = self.ax.loglog([], [], "C5", zorder=0)

        self.ax.set_title("Isolation table motion")
        self.ax.set_ylabel(
            r"Displacement $\left(\mathrm{m}/\sqrt{\mathrm{Hz}}\right)$")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.grid(which="both")

    def update_line(self, line, xdata=None, ydata=None):
        """Update line

        Parameters
        ----------
        line : str
            Line to be updated.
            Select from ["selected", "min_disp", "min_vel", "tebo",
            "seismic", "seismometer", "relative", "inertial", "witness"]
        xdata : array, optional
            Updated x data.
            Defaults None.
        ydata : array, optional
            Updated y data.
            Defaults None.
        """
        if line == "selected":
            ln = self.selected_ln
            label = "Selected"
        elif line == "min_disp":
            ln = self.min_disp_ln
            label = "Min. RMS displacement"
        elif line == "min_vel":
            ln = self.min_vel_ln
            label = "Min. RMS velocity"
        elif line == "tebo":
            ln = self.tebo_ln
            label = "Threshold-elmination-band-optimization"
        elif line == "seismic":
            ln = self.seismic_ln
            label = "Seismic noise"
        elif line == "seismometer":
            ln = self.seismometer_ln
            label = "Seismometer noise"
        elif line == "relative":
            ln = self.relative_ln
            label = "Relative sensor noise"
        elif line == "inertial":
            ln = self.inertial_ln
            label = "Inertial sensor noise"
        elif line == "witness":
            ln = self.witness_ln
            label = "Witness measurement"
        else:
            raise ValueError(f"{line} line does not exist.")

        zorder = ln.zorder
        color = ln.get_color()
        ls = ln.get_ls()

        # This is faster than set_data()
        if ln in self.ax.lines: ln.remove()

        if xdata is None or ydata is None:
            ln, = self.ax.loglog([], [], color=color, ls=ls, zorder=zorder)
        else:
            ln, = self.ax.loglog(
                xdata, ydata, color=color, ls=ls, zorder=zorder, label=label
            )

        if line == "selected":
            self.selected_ln = ln
        elif line == "min_disp":
            self.min_disp_ln = ln
        elif line == "min_vel":
            self.min_vel_ln = ln
        elif line == "tebo":
            self.tebo_ln = ln
        elif line == "seismic":
            self.seismic_ln = ln
        elif line == "seismometer":
            self.seismometer_ln = ln
        elif line == "relative":
            self.relative_ln = ln
        elif line == "inertial":
            self.inertial_ln = ln
        elif line == "witness":
            self.witness_ln = ln
        
        self.update_legend()
        self.canvas.draw()

    def update_all_lines(self, line, xdata=None, ydatas=None):
        """Update a collection of lines
        
        Parameters
        ----------
        line : str
            Lines to be updated.
            Select from ["all", "threshold"].
        xdata : array, optional
            Updated x data.
            Defaults None.
        ydata : array, optional
            Updated y data collection.
            Defaults None.
        """
        if line == "all":
            all_ln = self.all_ln
            all_ln_label = self.all_ln_label
            label = "All estimated displacements"
            color = "k"
            zorder = 0
            try:
                alpha = .1 * len(ydatas)/10
            except:
                pass
        elif line == "threshold":
            all_ln = self.threshold_ln
            all_ln_label = self.threshold_ln_label
            label = "All within RMS thresholds"
            color = "C0"
            zorder = 1
            try:
                alpha = .1 * len(ydatas)/10
            except:
                pass

        for ln in all_ln:
            if ln in self.ax.lines: ln.remove()

        all_ln = []

        if xdata is None or ydatas is None:
            all_ln_label.set_label("_nolegend_")
        else:
            for ydata in ydatas:
                ln, = self.ax.loglog(
                    xdata, ydata, color=color, alpha=alpha, zorder=zorder)
                all_ln.append(ln)
            all_ln_label.set_label(label)
        
        if line == "all":
            self.all_ln = all_ln
        elif line == "threshold":
            self.threshold_ln = all_ln

        self.update_legend()
        self.canvas.draw()
    
    def update_bounds(
            self, bounds, xdata=None, bound_lower=None, bound_upper=None):
        """Update fill between bounds
        
        Parameters
        ----------
        bounds : str
            Fill to be updated.
            Select from ["all", "threshold"].
        xdata : array, optional
            Updated x data.
            Defaults None.
        bound_lower : array, optional
            Update lower bound.
            Defaults None.
        bound_upper : array, optional
            Updated upper bound.
            Defaults None.
        """
        if bounds == "all":
            ln = self.all_bound_ln
            label = "All estimated displacements (bounds)"
            color = "k"
            alpha = .1
            zorder = 0
        elif bounds == "threshold":
            ln = self.threshold_bound_ln
            label = "All within RMS threshold (bounds)"
            color = "C0"
            alpha = .2
            zorder = 1

        if ln in self.ax.collections: ln.remove()

        if xdata is None or bound_lower is None or bound_upper is None:
            ln.set_label("_nolegend_")
        else:    
            ln = self.ax.fill_between(
                xdata, bound_lower, bound_upper,
                color=color, label=label, alpha=alpha, zorder=zorder
            )
        
        if bounds == "all":
            self.all_bound_ln = ln
        elif bounds == "threshold":
            self.threshold_bound_ln = ln

        self.update_legend()
        # self.ax.relim()
        # self.ax.autoscale_view()
        self.canvas.draw()
        
    def update_legend(self):
        """Update legend"""
        disp_handles = [
            self.selected_ln,
            self.min_disp_ln,
            self.min_vel_ln,
            self.tebo_ln,
            self.all_ln_label,
            self.all_bound_ln,
            self.threshold_ln_label,
            self.threshold_bound_ln,
            self.witness_ln
        ]
        noise_handles = [
            self.seismic_ln,
            self.seismometer_ln,
            self.relative_ln,
            self.inertial_ln
        ]

        for artist in self.ax.artists:
            artist.remove()
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

        disp_legend = self.ax.legend(handles=disp_handles, loc="lower left")
        noise_legend = self.ax.legend(handles=noise_handles, loc="upper right")
        self.ax.add_artist(disp_legend)


class SensorCorrectionPlot(Plot):
    """Filter Plot"""
    def __init__(self, master, figsize=(16*1/3, 9*1/3)):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent
        figsize : tuple, optional
            pyplot figure size.
            Defaults (16*1/3, 9*1/3).
        """
        super().__init__(master, figsize)
        self.selected_ln, = self.ax.loglog([], [], "C1", zorder=2)
        self.min_disp_ln, = self.ax.loglog([], [], "C2", zorder=3)
        self.min_vel_ln, = self.ax.loglog([], [], "C3", zorder=4)
        self.tebo_ln, = self.ax.loglog([], [], "C4", zorder=5)

        self.selected_comp_ln, = self.ax.loglog([], [], "C1--", zorder=2)
        self.min_disp_comp_ln, = self.ax.loglog([], [], "C2--", zorder=3)
        self.min_vel_comp_ln, = self.ax.loglog([], [], "C3--", zorder=4)
        self.tebo_comp_ln, = self.ax.loglog([], [], "C4--", zorder=5)

        self.ax.set_title("Sensor correction filters")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.grid(which="both")

    def update_line(self, line, xdata=None, ydata=None):
        """Update line

        Parameters
        ----------
        line : str
            Line to be updated.
            Select from ["selected", "min_disp", "min_vel", "tebo",
            "selected_comp", "min_disp_comp", "min_vel_comp", "tebo_comp"]
        xdata : array, optional
            Updated x data.
            Defaults None.
        ydata : array, optional
            Updated y data.
            Defaults None.
        """
        if line == "selected":
            ln = self.selected_ln
            label = "Selected sensor correction"
        elif line == "min_disp":
            ln = self.min_disp_ln
            label = "Min. disp. sensor correction"
        elif line == "min_vel":
            ln = self.min_vel_ln
            label = "Min. vel. sensor correction"
        elif line == "tebo":
            ln = self.tebo_ln
            label = "TEBO sensor correction"
        elif line == "selected_comp":
            ln = self.selected_comp_ln
            label = "Selected transmissivity"
        elif line == "min_disp_comp":
            ln = self.min_disp_comp_ln
            label = "Min. disp. transmissivity"
        elif line == "min_vel_comp":
            ln = self.min_vel_comp_ln
            label = "Min. vel. transmissivity"
        elif line == "tebo_comp":
            ln = self.tebo_comp_ln
            label = "TEBO transmissivity"
        else:
            raise ValueError(f"{line} line does not exist.")

        color = ln.get_color()
        ls = ln.get_ls()
        zorder = ln.zorder

        if ln in self.ax.lines: ln.remove()

        if xdata is None or ydata is None:
            ln, = self.ax.loglog([], [], color=color, ls=ls, zorder=zorder)
        else:
            ln, = self.ax.loglog(
                xdata, ydata, color=color, ls=ls, zorder=zorder, label=label
            )

        if line == "selected":
            self.selected_ln = ln
        elif line == "min_disp":
            self.min_disp_ln = ln
        elif line == "min_vel":
            self.min_vel_ln = ln
        elif line == "tebo":
            self.tebo_ln = ln
        elif line == "selected_comp":
            self.selected_comp_ln = ln
        elif line == "min_disp_comp":
            self.min_disp_comp_ln = ln
        elif line == "min_vel_comp":
            self.min_vel_comp_ln = ln
        elif line == "tebo_comp":
            self.tebo_comp_ln = ln

        self.update_legend()
        self.canvas.draw()

    def update_legend(self):
        """Update legend"""
        filter1_handles = [
            self.selected_ln,
            self.min_disp_ln,
            self.min_vel_ln,
            self.tebo_ln
        ]
        filter2_handles = [
            self.selected_comp_ln,
            self.min_disp_comp_ln,
            self.min_vel_comp_ln,
            self.tebo_comp_ln
        ]

        for artist in self.ax.artists:
            artist.remove()
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

        filter1_legend = self.ax.legend(
            handles=filter1_handles, loc="lower left", prop={"size": 9})
        filter2_legend = self.ax.legend(
            handles=filter2_handles, loc="lower right", prop={"size": 9})
        self.ax.add_artist(filter1_legend)


class BlendPlot(Plot):
    """Filter Plot"""
    def __init__(self, master, figsize=(16*1/3, 9*1/3)):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent
        figsize : tuple, optional
            pyplot figure size.
            Defaults (16*1/3, 9*1/3).
        """
        super().__init__(master, figsize)
        self.selected_ln, = self.ax.loglog([], [], "C1", zorder=2)
        self.min_disp_ln, = self.ax.loglog([], [], "C2", zorder=3)
        self.min_vel_ln, = self.ax.loglog([], [], "C3", zorder=4)
        self.tebo_ln, = self.ax.loglog([], [], "C4", zorder=5)

        self.selected_comp_ln, = self.ax.loglog([], [], "C1--", zorder=2)
        self.min_disp_comp_ln, = self.ax.loglog([], [], "C2--", zorder=3)
        self.min_vel_comp_ln, = self.ax.loglog([], [], "C3--", zorder=4)
        self.tebo_comp_ln, = self.ax.loglog([], [], "C4--", zorder=5)

        self.ax.set_title("Complementary filters (blends)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_xlabel("Frequency (Hz)")
        self.ax.grid(which="both")

    def update_line(self, line, xdata=None, ydata=None):
        """Update line

        Parameters
        ----------
        line : str
            Line to be updated.
            Select from ["selected", "min_disp", "min_vel", "tebo",
            "selected_comp", "min_disp_comp", "min_vel_comp", "tebo_comp"]
        xdata : array, optional
            Updated x data.
            Defaults None.
        ydata : array, optional
            Updated y data.
            Defaults None.
        """
        if line == "selected":
            ln = self.selected_ln
            label = "Selected low-pass"
        elif line == "min_disp":
            ln = self.min_disp_ln
            label = "Min. disp. low-pass"
        elif line == "min_vel":
            ln = self.min_vel_ln
            label = "Min. vel. low-pass"
        elif line == "tebo":
            ln = self.tebo_ln
            label = "TEBO low-pass"
        elif line == "selected_comp":
            ln = self.selected_comp_ln
            label = "Selected high-pass"
        elif line == "min_disp_comp":
            ln = self.min_disp_comp_ln
            label = "Min. disp. high-pass"
        elif line == "min_vel_comp":
            ln = self.min_vel_comp_ln
            label = "Min. vel. high-pass"
        elif line == "tebo_comp":
            ln = self.tebo_comp_ln
            label = "TEBO high-pass"
        else:
            raise ValueError(f"{line} line does not exist.")
        
        color = ln.get_color()
        ls = ln.get_ls()
        zorder = ln.zorder
        
        if ln in self.ax.lines: ln.remove()

        if xdata is None or ydata is None:
            ln, = self.ax.loglog([], [], color=color, ls=ls, zorder=zorder)
        else:
            ln, = self.ax.loglog(
                xdata, ydata, color=color, ls=ls, zorder=zorder, label=label)

        if line == "selected":
            self.selected_ln = ln
        elif line == "min_disp":
            self.min_disp_ln = ln
        elif line == "min_vel":
            self.min_vel_ln = ln
        elif line == "tebo":
            self.tebo_ln = ln
        elif line == "selected_comp":
            self.selected_comp_ln = ln
        elif line == "min_disp_comp":
            self.min_disp_comp_ln = ln
        elif line == "min_vel_comp":
            self.min_vel_comp_ln = ln
        elif line == "tebo_comp":
            self.tebo_comp_ln = ln

        self.update_legend()
        self.canvas.draw()

    def update_legend(self):
        """Update legend"""
        filter1_handles = [
            self.selected_ln,
            self.min_disp_ln,
            self.min_vel_ln,
            self.tebo_ln
        ]
        filter2_handles = [
            self.selected_comp_ln,
            self.min_disp_comp_ln,
            self.min_vel_comp_ln,
            self.tebo_comp_ln
        ]

        for artist in self.ax.artists:
            artist.remove()
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

        filter1_legend = self.ax.legend(
            handles=filter1_handles, loc="lower left", prop={"size": 10})
        filter2_legend = self.ax.legend(
            handles=filter2_handles, loc="lower right", prop={"size": 10})
        self.ax.add_artist(filter1_legend)
