import tkinter


class RMSOption(tkinter.LabelFrame):
    """RMS option"""
    def __init__(self, master, root):
        """Constructor"""
        super().__init__(master, text="Minimize RMS")
        
        self.master = master
        self.root = root
        self.config(font=("Helvetica", 12, "bold"))
        
        self.optimize_option = tkinter.StringVar()
        self.optimize_option.set("displacement")
        optimize_displacement = tkinter.Radiobutton(
            self, text="Optimize RMS displacement",
            variable=self.optimize_option, value="displacement",
            command=self.update
        )
        optimize_velocity = tkinter.Radiobutton(
            self, text="Optimize RMS velocity",
            variable=self.optimize_option, value="velocity",
            command=self.update
        )

        self.optimize_band = tkinter.BooleanVar()
        self.optimize_band_button = tkinter.Checkbutton(
            self, text="Optimize band-limited RMS",
            variable=self.optimize_band,
            onvalue=True, offvalue=False, command=self.band_button_clicked)
        band_frame = tkinter.LabelFrame(self, text="Select Band")

        self.band = tkinter.IntVar()
        # self.optimize_0_3e_2 = tkinter.Radiobutton(
        #     band_frame, text="0 Hz - 0.03 Hz",
        #     command=self._optimize_0_3e_2,
        #     variable=self.band, value=0)
        self.optimize_3e_2_1e_1 = tkinter.Radiobutton(
            band_frame, text="0.03 Hz - 0.1 Hz",
            command=self._optimize_3e_2_1e_1,
            variable=self.band, value=1)
        self.optimize_1e_1_3e_1 = tkinter.Radiobutton(
            band_frame, text="0.1 Hz - 0.3 Hz",
            command=self._optimize_1e_1_3e_1,
            variable=self.band, value=2)
        self.optimize_3e_1_1 = tkinter.Radiobutton(
            band_frame, text="0.3 Hz - 1 Hz",
            command=self._optimize_3e_1_1,
            variable=self.band, value=3)
        self.optimize_1_3 = tkinter.Radiobutton(
            band_frame, text="1 Hz - 3 Hz",
            command=self._optimize_1_3,
            variable=self.band, value=4)
        # self.optimize_3_10 = tkinter.Radiobutton(
        #     band_frame, text="3 Hz - 10 Hz",
        #     command=self._optimize_3_10,
        #     variable=self.band, value=5)
        # self.optimize_10_30 = tkinter.Radiobutton(
        #     band_frame, text="10 Hz - 30 Hz",
        #     command=self._optimize_10_30,
        #     variable=self.band, value=6)
        # self.optimize_30_100 = tkinter.Radiobutton(
        #     band_frame, text="30 Hz - 100 Hz",
        #     command=self._optimize_30_100,
        #     variable=self.band, value=7)
        self.optimize_custom = tkinter.Radiobutton(
            band_frame, text="Custom",
            command=self._optimize_custom,
            variable=self.band, value=8)

        self.frequency_lower = 0.03
        self.frequency_upper = 0.1

        frequency_lower_label = tkinter.Label(
            self, text="Frequency band (Hz) (lower)")
        self.frequency_lower_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_lower_entry.insert(0, 0.03)
        self.frequency_lower_entry.bind("<Return>", self.update_band)

        frequency_upper_label = tkinter.Label(
            self, text="Frequency band (Hz) (upper)")
        self.frequency_upper_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_upper_entry.insert(0, 0.1)
        self.frequency_upper_entry.bind("<Return>", self.update_band)

        self.apply = tkinter.Button(
            self, text="Apply", command=self.update_band)

        optimize_displacement.grid(row=0, column=0, sticky="w")
        optimize_velocity.grid(row=0, column=1, sticky="w")

        self.optimize_band_button.grid(row=3, column=0, sticky="w")
        band_frame.grid(row=4, column=0, sticky="ensw", columnspan=2)
        band_frame.columnconfigure(0, weight=1)
        # self.optimize_0_3e_2.grid(row=0, column=2, sticky="w")
        self.optimize_3e_2_1e_1.grid(row=1, column=2, sticky="w")
        self.optimize_1e_1_3e_1.grid(row=2, column=2, sticky="w")
        self.optimize_3e_1_1.grid(row=3, column=2, sticky="w")
        self.optimize_1_3.grid(row=4, column=2, sticky="w")
        # self.optimize_3_10.grid(row=5, column=2, sticky="w")
        # self.optimize_10_30.grid(row=6, column=2, sticky="w")
        # self.optimize_30_100.grid(row=7, column=2, sticky="w")
        self.optimize_custom.grid(row=8, column=2, sticky="w")

        frequency_lower_label.grid(row=5, column=0, sticky="w")
        self.frequency_lower_entry.grid(row=5, column=1, sticky="e")
        frequency_upper_label.grid(row=6, column=0, sticky="w")
        self.frequency_upper_entry.grid(row=6, column=1, sticky="e")
        self.apply.grid(row=7, column=1, sticky="e")

        self.columnconfigure(1, weight=1)

        self.buttons = [
            optimize_displacement, optimize_velocity,
            self.optimize_band_button,
        ]
        self.band_buttons = [
            # self.optimize_0_3e_2,
            self.optimize_3e_2_1e_1,
            self.optimize_1e_1_3e_1,
            self.optimize_3e_1_1,
            self.optimize_1_3,
            # self.optimize_3_10,
            # self.optimize_10_30,
            # self.optimize_30_100,
            self.optimize_custom,
        ]

        for button in self.buttons:
            button.config(state="disabled")

        for button in self.band_buttons:
            button.config(state="disabled")

        self.frequency_lower_entry.config(state="disabled")
        self.frequency_upper_entry.config(state="disabled")
        self.apply.config(state="disabled")

    def initialize(self):
        """Initialize"""
        self.seibot = self.root.seibot
        self.enable()

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")

    def band_button_clicked(self):
        """Band button clicked"""
        if self.optimize_band.get():
            for button in self.band_buttons:
                button.config(state="normal")
        else:
            for button in self.band_buttons:
                button.config(state="disabled")

        self.update()

    def plot(self):
        """Plot"""
        if self.master.enabled:
            self.master.plot()

    def update(self):
        """Update filter selections"""
        if self.optimize_band.get():
            f_lower = self.frequency_lower
            f_upper = self.frequency_upper
        else:
            f_lower = None
            f_upper = None

        if self.optimize_option.get() == "displacement":
            filters = self.seibot.evaluate.min_rms_displacement(
                f_lower=f_lower, f_upper=f_upper)
        elif self.optimize_option.get() == "velocity":
            filters = self.seibot.evaluate.min_rms_velocity(
                f_lower=f_lower, f_upper=f_upper)
        self.master.selected_sc = filters.sc
        self.master.selected_lp = filters.lp
        self.master.selected_hp = filters.hp

        self.plot()

    def update_band(self, _=None):
        """Update frequency band"""
        frequency1 = float(self.frequency_lower_entry.get())
        frequency2 = float(self.frequency_upper_entry.get())
        self.frequency_lower = min(frequency1, frequency2)
        self.frequency_upper = max(frequency1, frequency2)
        
        self.update()

    def _optimize_0_3e_2(self):
        """Change optimized band to 0 Hz - 0.03 Hz"""
        self._optimize_x_x(0, 0.03)

    def _optimize_3e_2_1e_1(self):
        """Change optimized band to 0.03 Hz - 0.1 Hz"""
        self._optimize_x_x(0.03, 0.1)

    def _optimize_1e_1_3e_1(self):
        """Change optimized band to 0.1 Hz - 0.3 Hz"""
        self._optimize_x_x(0.1, 0.3)

    def _optimize_3e_1_1(self):
        """Change optimized band to 0.3 Hz - 1 Hz"""
        self._optimize_x_x(0.3, 1)

    def _optimize_1_3(self):
        """Change optimized band to 1 Hz - 3 Hz"""
        self._optimize_x_x(1, 3)

    def _optimize_3_10(self):
        """Change optimized band to 3 Hz - 10 Hz"""
        self._optimize_x_x(3, 10)

    def _optimize_10_30(self):
        """Change optimized band to 10 Hz - 30 Hz"""
        self._optimize_x_x(10, 30)

    def _optimize_30_100(self):
        """Change optimized band to 30 Hz - 100 Hz"""
        self._optimize_x_x(30, 100)

    def _optimize_x_x(self, lower, upper):
        """Optimize band
        
        Parameters
        ----------
        lower : float
            Frequency lower band.
        upper : float
            Frequency upper band.
        """
        # Disable custom option
        self.frequency_lower_entry.config(state="normal")
        self.frequency_upper_entry.config(state="normal")
        self.frequency_lower_entry.delete(0, "end")
        self.frequency_upper_entry.delete(0, "end")
        self.frequency_lower_entry.insert(0, lower)
        self.frequency_upper_entry.insert(0, upper)
        self.frequency_lower_entry.config(state="readonly")
        self.frequency_upper_entry.config(state="readonly")
        self.apply.config(state="disabled")
        self.frequency_lower = lower
        self.frequency_upper = upper

        self.update()

    def _optimize_custom(self):
        """Optimize custom"""
        self.frequency_lower_entry.config(state="normal")
        self.frequency_upper_entry.config(state="normal")
        self.apply.config(state="normal")

        self.update_band()
