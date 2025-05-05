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

        # TODO Add predefined bands

        frequency_lower_label = tkinter.Label(
            self, text="Frequency band (lower)")
        self.frequency_lower_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_lower_entry.insert(0, 0.1)
        self.frequency_lower_entry.bind("<Return>", self.update)
        frequency_lower_unit = tkinter.Label(
            self, text="Hz")

        frequency_upper_label = tkinter.Label(
            self, text="Frequency band (upper)")
        self.frequency_upper_entry = tkinter.Entry(
            self, justify="right", width=10)
        self.frequency_upper_entry.insert(0, 0.5)
        self.frequency_upper_entry.bind("<Return>", self.update)
        frequency_upper_unit = tkinter.Label(
            self, text="Hz")

        optimize_displacement.grid(row=4, column=0, sticky="w")
        optimize_velocity.grid(row=4, column=1, sticky="w")

        frequency_lower_label.grid(row=5, column=0, sticky="w")
        self.frequency_lower_entry.grid(row=5, column=1, sticky="e")
        frequency_lower_unit.grid(row=5, column=2, sticky="w")
        frequency_upper_label.grid(row=6, column=0, sticky="w")
        self.frequency_upper_entry.grid(row=6, column=1, sticky="e")
        frequency_upper_unit.grid(row=6, column=2, sticky="w")

        self.buttons = [
            optimize_displacement, optimize_velocity,
            self.frequency_lower_entry, self.frequency_upper_entry,
        ]

        for button in self.buttons:
            button.config(state="disabled")

    def initialize(self):
        """Initialize"""
        self.seibot = self.root.seibot
        self.enable()

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")

    def plot(self):
        """Plot"""
        self.master.plot()

    def update(self):
        """Update filter selections"""
        if self.optimize_option.get() == "displacement":
            filters = self.seibot.evaluate.min_rms_displacement()
        elif self.optimize_option.get() == "velocity":
            filters = self.seibot.evaluate.min_rms_velocity()
        self.master.selected_sc = filters.sc
        self.master.selected_lp = filters.lp
        self.master.selected_hp = filters.hp
        self.plot()
