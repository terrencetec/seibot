"""Seibot GUI Threshold option"""
import tkinter


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
        self.config(font=("Helvetica", 12, "bold"))
        
        plot_all_frame = tkinter.LabelFrame(
            self, text="All within RMS thresholds")
        plot_all_frame.config(font=("Helvetica", 12, "italic"))
        plot_all_frame.grid(row=0, column=0, columnspan=3, sticky="ewns")
        self.columnconfigure(0, weight=1)
        # plot_all_frame.columnconfigure(0, weight=1)g

        plot_all_button = tkinter.Checkbutton(
            plot_all_frame, text="Plot all", command=self.plot_all)
        plot_all_label = tkinter.Label(
            plot_all_frame, text="Select plot style: ")
        plot_bounds = tkinter.Radiobutton(
            plot_all_frame, text="Bounds (fast)")
        plot_curves = tkinter.Radiobutton(
            plot_all_frame, text="Curves (slow)")
        plot_all_button.grid(row=0, column=0, columnspan=2, sticky="w")
        plot_all_label.grid(row=1, column=0, sticky="w")
        plot_bounds.grid(row=1, column=1, sticky="w")
        plot_curves.grid(row=1, column=2, sticky="w")

        rms_disp_label = tkinter.Label(
            self, text="Select RMS displacement threshold: ")
        rms_disp_entry = tkinter.Entry(self, justify="right", width=10)
        rms_disp_unit = tkinter.Label(self, text="nm")
        rms_vel_label = tkinter.Label(
            self, text="Select RMS velocity threshold: ")
        rms_vel_entry = tkinter.Entry(self, justify="right", width=10)
        rms_vel_unit = tkinter.Label(self, text="nm/s")

        rms_disp_label.grid(row=1, column=0, sticky="w")
        rms_disp_entry.grid(row=1, column=1, sticky="e")
        rms_disp_unit.grid(row=1, column=2, sticky="w")
        rms_vel_label.grid(row=2, column=0, sticky="w")
        rms_vel_entry.grid(row=2, column=1, sticky="e")
        rms_vel_unit.grid(row=2, column=2, sticky="w")
        
        plot_tebo_button = tkinter.Checkbutton(
            self, text="Plot band optimized within RMS thresholds")
        optimize_displacement = tkinter.Radiobutton(
            self, text="Optimize RMS displacement")
        optimize_velocity = tkinter.Radiobutton(
            self, text="Optimize RMS velocity")
        frequency_lower_label = tkinter.Label(
            self, text="Frequency band (lower)")
        frequency_lower_entry = tkinter.Entry(
            self, justify="right", width=10)
        frequency_lower_unit = tkinter.Label(
            self, text="Hz")
        frequency_upper_label = tkinter.Label(
            self, text="Frequency band (upper)")
        frequency_upper_entry = tkinter.Entry(
            self, justify="right", width=10)
        frequency_upper_unit = tkinter.Label(
            self, text="Hz")

        plot_tebo_button.grid(row=3, column=0, columnspan=2, sticky="w")
        optimize_displacement.grid(row=4, column=0, sticky="w")
        optimize_velocity.grid(row=4, column=1, sticky="w")

        frequency_lower_label.grid(row=5, column=0, sticky="w")
        frequency_lower_entry.grid(row=5, column=1, sticky="e")
        frequency_lower_unit.grid(row=5, column=2, sticky="w")
        frequency_upper_label.grid(row=6, column=0, sticky="w")
        frequency_upper_entry.grid(row=6, column=1, sticky="e")
        frequency_upper_unit.grid(row=6, column=2, sticky="w")
    
        self.buttons = [
            plot_all_button, plot_bounds, plot_curves,
            rms_disp_entry, rms_vel_entry,
            plot_tebo_button, optimize_displacement, optimize_velocity,
            frequency_lower_entry, frequency_upper_entry
        ]
        
        for button in self.buttons:
            button.config(state="disabled")

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")
        
    def plot_all(self):
        """plot all"""
        pass
