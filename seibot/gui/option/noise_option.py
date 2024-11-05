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
        """
        super().__init__(master, text="Noise options")
        self.config(font=("Helvetica", 12, "bold"))
        
        plot_all_button = tkinter.Checkbutton(
            self, text="Plot all noises")
        plot_seismic = tkinter.Checkbutton(
            self, text="Plot seismic noise")
        plot_seismometer = tkinter.Checkbutton(
            self, text="Plot seismometer noise")
        plot_relative = tkinter.Checkbutton(
            self, text="Plot relative sensor noise")
        plot_inertial = tkinter.Checkbutton(
            self, text="Plot inertial sensor noise")

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
