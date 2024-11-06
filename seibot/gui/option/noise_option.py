"""Seibot GUI Noise Option"""
import tkinter


class NoiseOption(tkinter.LabelFrame):
    """Noise option"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        root : tkinter.Tk
            Tkinter root.
        """
        super().__init__(master, text="Noise options")
        
        self.root = root

        self.config(font=("Helvetica", 12, "bold"))
        
        self.plot_all_var = tkinter.IntVar()
        self.plot_seismic_var = tkinter.IntVar()
        self.plot_seismometer_var = tkinter.IntVar()
        self.plot_relative_var = tkinter.IntVar()
        self.plot_inertial_var = tkinter.IntVar()

        plot_all_button = tkinter.Checkbutton(
            self, text="Plot all noises",
            variable=self.plot_all_var, command=self.plot_all_clicked
        )
        plot_seismic = tkinter.Checkbutton(
            self, text="Plot seismic noise",
            variable=self.plot_seismic_var, command=self.plot_all
        )
        plot_seismometer = tkinter.Checkbutton(
            self, text="Plot seismometer noise",
            variable=self.plot_seismometer_var, command=self.plot_all
        )
        plot_relative = tkinter.Checkbutton(
            self, text="Plot relative sensor noise",
            variable=self.plot_relative_var, command=self.plot_all
        )
        plot_inertial = tkinter.Checkbutton(
            self, text="Plot inertial sensor noise",
            variable=self.plot_inertial_var, command=self.plot_all
        )

        plot_all_button.grid(row=0, column=0, sticky="w")
        plot_seismic.grid(row=1, column=0, sticky="w", padx=10)
        plot_seismometer.grid(row=2, column=0, sticky="w", padx=10)
        plot_relative.grid(row=3, column=0, sticky="w", padx=10)
        plot_inertial.grid(row=4, column=0, sticky="w", padx=10)

        self.buttons = [
            plot_all_button, plot_seismic, plot_seismometer,
            plot_relative, plot_inertial
        ]

        for button in self.buttons:
            button.config(state="disabled")

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")

    def initialize(self):
        """Initialize"""
        seibot = self.root.seibot
        self.f = seibot.data.f
        self.seismic = seibot.data.seismic_noise
        self.seismometer = seibot.data.seismometer_noise
        self.relative = seibot.data.relative_sensor_noise
        self.inertial = seibot.data.inertial_sensor_noise
        self.enable()

    def plot_all_clicked(self):
        """Plot all_clicked"""
        if self.plot_all_var.get():
            self.plot_seismic_var.set(1)
            self.plot_seismometer_var.set(1)
            self.plot_relative_var.set(1)
            self.plot_inertial_var.set(1)
        else:
            self.plot_seismic_var.set(0)
            self.plot_seismometer_var.set(0)
            self.plot_relative_var.set(0)
            self.plot_inertial_var.set(0)
        self.plot_all()

    def plot_all(self):
        """Plot all"""
        if self.plot_seismic_var.get():
            self.root.main_plot.update_line("seismic", self.f, self.seismic)
        else:
            self.root.main_plot.update_line("seismic")

        if self.plot_seismometer_var.get():
            self.root.main_plot.update_line(
                "seismometer", self.f, self.seismometer)
        else:
            self.root.main_plot.update_line("seismometer")
        
        if self.plot_relative_var.get():
            self.root.main_plot.update_line("relative", self.f, self.relative)
        else:
            self.root.main_plot.update_line("relative")

        if self.plot_inertial_var.get():
            self.root.main_plot.update_line("inertial", self.f, self.inertial)
        else:
            self.root.main_plot.update_line("inertial")
