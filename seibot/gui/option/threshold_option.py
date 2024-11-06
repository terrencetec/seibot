"""Seibot GUI Threshold option"""
import tkinter

import numpy as np


class ThresholdOption(tkinter.LabelFrame):
    """Threshold option"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        """
        super().__init__(
            master,
            text="Threshold-elimination-band-optimization (TEBO) options")

        self.root = root

        self.config(font=("Helvetica", 12, "bold"))
        
        plot_all_frame = tkinter.LabelFrame(
            self, text="All within RMS thresholds")
        plot_all_frame.config(font=("Helvetica", 12, "italic"))
        plot_all_frame.grid(row=0, column=0, columnspan=3, sticky="ewns")
        self.columnconfigure(0, weight=1)
        # plot_all_frame.columnconfigure(0, weight=1)g

        self.plot_all_var = tkinter.IntVar()
        plot_all_button = tkinter.Checkbutton(
            plot_all_frame, text="Plot all",
            variable=self.plot_all_var, command=self.plot_all
        )
        plot_all_label = tkinter.Label(
            plot_all_frame, text="Select plot style: ")

        self.plot_style = tkinter.StringVar()
        self.plot_style.set("Bounds")
        plot_bounds = tkinter.Radiobutton(
            plot_all_frame, text="Bounds (fast)",
            variable=self.plot_style, value="Bounds",
            command=self.plot_all
        )
        plot_curves = tkinter.Radiobutton(
            plot_all_frame, text="Curves (slow)",
            variable=self.plot_style, value="Curves",
            command=self.plot_all
        )

        plot_all_button.grid(row=0, column=0, columnspan=2, sticky="w")
        plot_all_label.grid(row=1, column=0, sticky="w")
        plot_bounds.grid(row=1, column=1, sticky="w")
        plot_curves.grid(row=1, column=2, sticky="w")

        rms_disp_label = tkinter.Label(
            self, text="Select RMS displacement threshold: ")
        self.rms_disp_entry = tkinter.Entry(self, justify="right", width=10)
        self.rms_disp_entry.insert(0, 1000)
        self.rms_disp_entry.bind("<Return>", self.update_thresholds)
        rms_disp_unit = tkinter.Label(self, text="nm")
        rms_vel_label = tkinter.Label(
            self, text="Select RMS velocity threshold: ")

        self.rms_vel_entry = tkinter.Entry(self, justify="right", width=10)
        self.rms_vel_entry.insert(0, 300)
        self.rms_vel_entry.bind("<Return>", self.update_thresholds)
        rms_vel_unit = tkinter.Label(self, text="nm/s")

        rms_disp_label.grid(row=1, column=0, sticky="w")
        self.rms_disp_entry.grid(row=1, column=1, sticky="e")
        rms_disp_unit.grid(row=1, column=2, sticky="w")
        rms_vel_label.grid(row=2, column=0, sticky="w")
        self.rms_vel_entry.grid(row=2, column=1, sticky="e")
        rms_vel_unit.grid(row=2, column=2, sticky="w")
        
        self.plot_tebo_var = tkinter.IntVar()
        plot_tebo_button = tkinter.Checkbutton(
            self, text="Plot band optimized within RMS thresholds",
            variable=self.plot_tebo_var, command=self.plot_tebo
        )
        self.optimize_option = tkinter.StringVar()
        self.optimize_option.set("displacement")
        optimize_displacement = tkinter.Radiobutton(
            self, text="Optimize RMS displacement",
            variable=self.optimize_option, value="displacement",
            command=self.update_tebo
        )
        optimize_velocity = tkinter.Radiobutton(
            self, text="Optimize RMS velocity",
            variable=self.optimize_option, value="velocity",
            command=self.update_tebo
        )

        frequency_lower_label = tkinter.Label(
            self, text="Frequency band (lower)")
        self.frequency_lower_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_lower_entry.insert(0, 0.001)
        self.frequency_lower_entry.bind("<Return>", self.update_tebo)
        frequency_lower_unit = tkinter.Label(
            self, text="Hz")
        frequency_upper_label = tkinter.Label(
            self, text="Frequency band (upper)")
        self.frequency_upper_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_upper_entry.insert(0, 0.01)
        self.frequency_upper_entry.bind("<Return>", self.update_tebo)
        frequency_upper_unit = tkinter.Label(
            self, text="Hz")

        plot_tebo_button.grid(row=3, column=0, columnspan=2, sticky="w")
        optimize_displacement.grid(row=4, column=0, sticky="w")
        optimize_velocity.grid(row=4, column=1, sticky="w")

        frequency_lower_label.grid(row=5, column=0, sticky="w")
        self.frequency_lower_entry.grid(row=5, column=1, sticky="e")
        frequency_lower_unit.grid(row=5, column=2, sticky="w")
        frequency_upper_label.grid(row=6, column=0, sticky="w")
        self.frequency_upper_entry.grid(row=6, column=1, sticky="e")
        frequency_upper_unit.grid(row=6, column=2, sticky="w")
    
        self.buttons = [
            plot_all_button, plot_bounds, plot_curves,
            self.rms_disp_entry, self.rms_vel_entry,
            plot_tebo_button, optimize_displacement, optimize_velocity,
            self.frequency_lower_entry, self.frequency_upper_entry
        ]
        
        for button in self.buttons:
            button.config(state="disabled")

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")
        
    def initialize(self):
        """Get data from seibot instance"""
        seibot = self.root.seibot
        self.f = seibot.data.f
        self.all_displacements = self.get_all_displacement()
        self.bound_lower, self.bound_upper = self.get_bounds()
        self.tebo, self.tebo_filters = self.get_tebo()
        self.enable()

    def get_all_displacement(self):
        """Get all displacement data withint RMS thresholds.
        
        Returns
        -------
        all_displacements: array
            An array of all displacements
        """
        seibot = self.root.seibot
        f = seibot.data.f
        dm = seibot.evaluate.displacement_matrix
        disp_thres = float(self.rms_disp_entry.get())
        vel_thres = float(self.rms_vel_entry.get())
        indices = seibot.evaluate.get_threshold_indices(disp_thres, vel_thres)
        shape = (len(indices), len(f))
        all_displacements = np.empty(shape)
        for i in range(len(indices)):
            all_displacements[i] = dm[indices[i]]

        return all_displacements

    def get_bounds(self):
        """Get displacement bounds

        Returns
        -------
        bound_lower : array
            The lower bound.
        bound_upper : array
            The upper bound.
        """
        bound_lower = np.min(self.all_displacements, axis=0)
        bound_upper = np.max(self.all_displacements, axis=0)
        return bound_lower, bound_upper
    
    def get_tebo(self):
        """Get tebo displacement
        
        Returns
        -------
        displacement : array
            Displacement.
        filters : seibot.filter.FilterConfiguration
            Filter configuration.
        """
        seibot = self.root.seibot
        seismic_noise = seibot.data.seismic_noise

        disp_thres = float(self.rms_disp_entry.get())
        vel_thres = float(self.rms_vel_entry.get())
        f_lower = float(self.frequency_lower_entry.get())
        f_upper = float(self.frequency_upper_entry.get())
        optimize = self.optimize_option.get()

        filters = seibot.evaluate.threshold_optimize(
            disp_thres, vel_thres, f_lower, f_upper, optimize)

        seibot.isolation_system.filter_configuration = filters

        displacement = seibot.isolation_system.get_displacement(seismic_noise)

        return displacement, filters

    def update_thresholds(self, entry=None):
        """Update thresholds"""
        self.all_displacements = self.get_all_displacement()
        self.bound_lower, self.bound_upper = self.get_bounds()
        self.plot_all()
        self.update_tebo()

    def update_tebo(self, entry=None):
        """Update tebo"""
        self.tebo, self.tebo_filters = self.get_tebo()
        self.plot_tebo()

    def plot_all(self):
        """plot all"""
        if self.plot_all_var.get():
            if self.plot_style.get() == "Bounds":
                self.root.main_plot.update_bounds(
                    "threshold", self.f, self.bound_lower, self.bound_upper)
                self.root.main_plot.update_all_lines("threshold")
            elif self.plot_style.get() == "Curves":
                self.root.main_plot.update_all_lines(
                    "threshold", self.f, self.all_displacements
                )
                self.root.main_plot.update_bounds("threshold")
        else:
            self.root.main_plot.update_all_lines("threshold")
            self.root.main_plot.update_bounds("threshold")

    def plot_tebo(self):
        """plot tebo"""
        if self.plot_tebo_var.get():
            self.root.main_plot.update_line("tebo", self.f, self.tebo)
            sc = self.tebo_filters.sc
            lp = self.tebo_filters.lp
            hp = self.tebo_filters.hp
            self.root.sc_plot.update_line("tebo", self.f, sc.mag)
            self.root.sc_plot.update_line("tebo_comp", self.f, sc.mag_comp)
            self.root.blend_plot.update_line("tebo", self.f, lp.mag)
            self.root.blend_plot.update_line("tebo_comp", self.f, hp.mag)
        else:
            self.root.main_plot.update_line("tebo")
            self.root.sc_plot.update_line("tebo")
            self.root.sc_plot.update_line("tebo_comp")
            self.root.blend_plot.update_line("tebo")
            self.root.blend_plot.update_line("tebo_comp")
