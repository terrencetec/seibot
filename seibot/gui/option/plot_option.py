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

        self.plot_current_var = tkinter.IntVar()
        self.plot_current_var.set(0)
        plot_current_button = tkinter.Checkbutton(
            self, text="Plot current",
            variable=self.plot_current_var, command=self.plot_current
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
        plot_current_button.grid(row=4, column=0, sticky="w")
        plot_selected_button.grid(row=5, column=0, sticky="w")

        self.buttons = [
            plot_all_button, plot_bounds, plot_curves,
            # plot_min_disp_button, plot_min_vel_button,
            plot_witness_button, plot_current_button, plot_selected_button]

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
        self.current, self.current_filters = self.get_current()

        self.enable()
        self.noise.initialize()
        self.plot()

    def plot(self):
        """Replot all"""
        self.noise.plot_all()
        self.plot_all()
        self.plot_witness()
        self.plot_current()
        self.plot_selected()
        # selection = self.plot_selected_var.get()
        # if selection == 1:
        #     self.plot_selected_var.set(0)
        #     self.plot_selected()
        #     self.plot_selected_var.set(1)
        #     self.plot_selected()

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

    def get_current(self):
        """Get current displacement and current filters
        
        Returns
        -------
        current : array or None
            The current prediction
        current_filters : seibot.filter.FilterConfiguration
            The currently engaged filters
        """
        current_filters = self.root.seibot.current_filters
        if current_filters is None:
            return None, None
        iso = self.root.seibot.isolation_system
        seismic = self.root.seibot.data.seismic_noise
        iso.filter_configuration = current_filters
        current = iso.get_displacement(seismic)

        return current, current_filters

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
        
    def plot_witness(self):
        """Plot witness"""
        if self.plot_witness_var.get() and self.witness is not None:
            self.root.main_plot.update_line("witness", self.f, self.witness)
        else:
            self.root.main_plot.update_line("witness")

    def plot_current(self):
        """Plot current"""
        if self.plot_current_var.get() and self.current is not None:
            self.root.main_plot.update_line("current", self.f, self.current)
        else:
            self.root.main_plot.update_line("current")

        if self.plot_current_var.get() and self.current_filters is not None:
            sc = self.current_filters.sc
            lp = self.current_filters.lp
            hp = self.current_filters.hp

            self.root.sc_plot.update_line("current", self.f, sc.mag)
            self.root.sc_plot.update_line("current_comp", self.f, sc.mag_comp)

            self.root.blend_plot.update_line("current", self.f, lp.mag)
            self.root.blend_plot.update_line("current_comp", self.f, hp.mag)
        else:
            self.root.sc_plot.update_line("current")
            self.root.sc_plot.update_line("current_comp")

            self.root.blend_plot.update_line("current")
            self.root.blend_plot.update_line("current_comp")

    def plot_selected(self):
        """Plot selected"""
        #Enable selecteion tab
        if self.plot_selected_var.get():
            self.master.selection_tabs.enable()
        else:
            self.master.selection_tabs.disable()
