"""Seibot GUI Plot Options"""
import tkinter

import numpy as np

from . import noise_option

class PlotOption(tkinter.LabelFrame):
    """Plot option"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        root : Tkinter.Tk
            Tkinter root.
        """
        super().__init__(master, text="Plot options")

        self.master = master # Master is OptionPanel
        self.root = root # Root is main.Root

        self.config(font=("Helvetica", 12, "bold"))

        plot_all_frame = tkinter.LabelFrame(
            self, text="All forcasted displacements")
        plot_all_frame.config(font=("Helvetica", 12, "italic"))

        plot_all_frame.grid(row=0, column=0, sticky="ewns")
        plot_all_frame.columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.plot_all_var = tkinter.IntVar()
        plot_all_button = tkinter.Checkbutton(
            plot_all_frame, text="Plot all",
            variable=self.plot_all_var, command=self.plot_all)

        self.plot_style = tkinter.StringVar()
        self.plot_style.set("Bounds")

        plot_all_label = tkinter.Label(
            plot_all_frame, text="Select plot style: ")
        plot_bounds = tkinter.Radiobutton(
            plot_all_frame, text="Bounds (fast)",
            variable=self.plot_style, value="Bounds", command=self.plot_all
        )
        plot_curves = tkinter.Radiobutton(
            plot_all_frame, text="Curves (slow)",
            variable=self.plot_style, value="Curves", command=self.plot_all
        )

        self.plot_witness_var = tkinter.IntVar()
        self.plot_witness_var.set(0)
        plot_witness_button = tkinter.Checkbutton(
            self, text="Plot witness sensor measurement",
            variable=self.plot_witness_var, command=self.plot_witness
        )

        self.plot_selected_var = tkinter.IntVar()
        self.plot_selected_var.set(0)
        plot_selected_button = tkinter.Checkbutton(
            self, text="Plot selected",
            variable=self.plot_selected_var, command=self.plot_selected
        )

        self.noise = noise_option.NoiseOption(self, root)

        plot_all_button.grid(row=0, column=0, columnspan=2, sticky="w")
        plot_all_label.grid(row=1, column=0, sticky="w")
        plot_bounds.grid(row=1, column=1, sticky="w")
        plot_curves.grid(row=1, column=2, sticky="w")
        self.noise.grid(row=2, column=0, columnspan=2, sticky="ensw")

        plot_witness_button.grid(row=3, column=0, sticky="w")
        plot_selected_button.grid(row=4, column=0, sticky="w")

        self.buttons = [
            plot_all_button, plot_bounds, plot_curves,
            # plot_min_disp_button, plot_min_vel_button,
            plot_witness_button, plot_selected_button]

        for button in self.buttons:
            button.config(state="disabled")

    def enable(self):
        """Enable"""
        for button in self.buttons:
            button.config(state="normal")

    def initialize(self):
        """Get data from seibot instance"""
        # Get frequency
        seibot = self.root.seibot
        self.f = seibot.data.f
        self.all_displacements = self.get_all_displacement()
        self.bound_lower, self.bound_upper = self.get_bounds()
        self.min_disp, self.min_disp_filters = self.get_min_disp()
        self.min_vel, self.min_vel_filters = self.get_min_vel()
        self.witness = self.get_witness()

        self.enable()
        self.noise.initialize()

    def get_all_displacement(self):
        """Get all displacement data
        
        Returns
        -------
        all_displacements: array
            An array of all displacements
        """
        seibot = self.root.seibot
        f = seibot.data.f
        dm = seibot.evaluate.displacement_matrix
        all_displacements = dm.reshape(-1, len(f))
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

    def get_min_disp(self):
        """Get minimum RMS displacement
            
        Returns
        -------
        displacement : array
            Displacement.
        filters : seibot.filter.FilterConfiguration
            Filter configuration.
        """
        seibot = self.root.seibot
        seismic_noise = seibot.data.seismic_noise
        filters = seibot.evaluate.min_rms_displacement()
        seibot.isolation_system.filter_configuration = filters
        displacement = seibot.isolation_system.get_displacement(seismic_noise)
        return displacement, filters
        
    def get_min_vel(self):
        """Get minimum RMS velocity
            
        Returns
        -------
        displacement : array
            Displacement.
        sc : seibot.filter.Filter
            Sensor correction filter.
        lp : seibot.filter.Filter
            Low-pass filter.
        hp : seibot.filter.Filter
            High-pass filter
        """
        seibot = self.root.seibot
        seismic_noise = seibot.data.seismic_noise
        filters = seibot.evaluate.min_rms_velocity()
        seibot.isolation_system.filter_configuration = filters
        displacement = seibot.isolation_system.get_displacement(seismic_noise)
        return displacement, filters

    def get_witness(self):
        """Get witness measurement
        
        Returns
        -------
        witness : array or None
            The witness measurement spectrum
        """
        seibot = self.root.seibot
        witness = seibot.data.witness_sensor  # This could be a None object.
        return witness

    def plot_all(self):
        """Plot all"""
        if self.plot_all_var.get():
            if self.plot_style.get() == "Bounds":
                self.root.main_plot.update_bounds(
                    "all", self.f, self.bound_lower, self.bound_upper)
                self.root.main_plot.update_all_lines("all")
            elif self.plot_style.get() == "Curves":
                self.root.main_plot.update_all_lines(
                    "all", self.f, self.all_displacements
                )
                self.root.main_plot.update_bounds("all")
        else:
            self.root.main_plot.update_all_lines("all")
            self.root.main_plot.update_bounds("all")
        
    def plot_min_disp(self):
        """Plot minimum displacement"""
        if self.plot_min_disp_var.get():
            self.root.main_plot.update_line("min_disp", self.f, self.min_disp)
            sc = self.min_disp_filters.sc
            lp = self.min_disp_filters.lp
            hp = self.min_disp_filters.hp
            self.root.sc_plot.update_line("min_disp", self.f, sc.mag)
            self.root.sc_plot.update_line("min_disp_comp", self.f, sc.mag_comp)
            self.root.blend_plot.update_line("min_disp", self.f, lp.mag)
            self.root.blend_plot.update_line("min_disp_comp", self.f, hp.mag)
        else:
            self.root.main_plot.update_line("min_disp")
            self.root.sc_plot.update_line("min_disp")
            self.root.sc_plot.update_line("min_disp_comp")
            self.root.blend_plot.update_line("min_disp")
            self.root.blend_plot.update_line("min_disp_comp")

    def plot_min_vel(self):
        """Plot minimum velocity"""
        if self.plot_min_vel_var.get():
            self.root.main_plot.update_line(
                "min_vel", self.f, self.min_vel
            )
            sc = self.min_vel_filters.sc
            lp = self.min_vel_filters.lp
            hp = self.min_vel_filters.hp
            self.root.sc_plot.update_line("min_vel", self.f, sc.mag)
            self.root.sc_plot.update_line("min_vel_comp", self.f, sc.mag_comp)
            self.root.blend_plot.update_line("min_vel", self.f, lp.mag)
            self.root.blend_plot.update_line("min_vel_comp", self.f, hp.mag)
        else:
            self.root.main_plot.update_line("min_vel")
            self.root.sc_plot.update_line("min_vel")
            self.root.sc_plot.update_line("min_vel_comp")
            self.root.blend_plot.update_line("min_vel")
            self.root.blend_plot.update_line("min_vel_comp")

    def plot_witness(self):
        """Plot witness"""
        if self.plot_witness_var.get() and self.witness is not None:
            self.root.main_plot.update_line("witness", self.f, self.witness)
        else:
            self.root.main_plot.update_line("witness")

    def plot_selected(self):
        """Plot selected"""
        #Enable selecteion tab
        if self.plot_selected_var.get():
            self.master.selection_tabs.enable()
        else:
            self.master.selection_tabs.disable()
