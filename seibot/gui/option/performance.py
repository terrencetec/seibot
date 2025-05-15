import numpy as np
import tkinter


class Performance(tkinter.LabelFrame):
    """Performance panel"""
    def __init__(self, master, root):
        """Constructor

        master
            Tkinter parent.
        root
            Tkinter root.
        """
        super().__init__(master, text="RMS Performance")

        self.config(font=("Helvetica", 12, "bold"))

        self.master = master
        self.root = root

        self.choose_label = tkinter.Label(self, text="Choose:")
        
        self.option_var = tkinter.StringVar()
        self.option_var.set("displacement")
        self.displacement_button = tkinter.Radiobutton(
            self, text="Displacement (nm)", variable=self.option_var,
            value="displacement", command=self.option_clicked
        )
        self.velocity_button = tkinter.Radiobutton(
            self, text="Velocity (nm/s)", variable=self.option_var,
            value="velocity", command=self.option_clicked
        )

        performance_frame = tkinter.Frame(self)

        frequency_label = tkinter.Label(performance_frame, text="Frequency (Hz):")
        all_label = tkinter.Label(performance_frame, text="Overall")
        label_3e2_1e1 = tkinter.Label(performance_frame, text="(3e-2, 1e-1)")
        label_1e1_3e1 = tkinter.Label(performance_frame, text="(1e-1, 3e-1)")
        label_3e1_1 = tkinter.Label(performance_frame, text="(3e-1, 1)")
        label_1_3 = tkinter.Label(performance_frame, text="(1, 3)")

        self.current_label = tkinter.Label(performance_frame, text="Current:")
        self.current_rms = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10,
            bg="white")
        self.current_rms_3e2_1e1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.current_rms_1e1_3e1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.current_rms_3e1_1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.current_rms_1_3 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")

        self.selected_label = tkinter.Label(performance_frame, text="Selected:")
        self.selected_rms = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.selected_rms_3e2_1e1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.selected_rms_1e1_3e1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.selected_rms_3e1_1 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")
        self.selected_rms_1_3 = tkinter.Label(
            performance_frame, text="-", relief=tkinter.SUNKEN, width=10, bg="white")


        self.choose_label.grid(row=0, column=0, sticky="w")
        self.displacement_button.grid(row=0, column=1, sticky="w")
        self.velocity_button.grid(row=0, column=2, sticky="w")

        performance_frame.grid(
            row=1, column=0, columnspan=3, sticky="ensw")
        self.columnconfigure(0, weight=1)
        performance_frame.columnconfigure(0, weight=1)
        # self.all_label.grid(row=0, column=0, sticky="w")
        frequency_label.grid(row=0, column=0, sticky="w")
        all_label.grid(row=1, column=0, sticky="w")
        label_3e2_1e1.grid(row=2, column=0, sticky="w")
        label_1e1_3e1.grid(row=3, column=0, sticky="w")
        label_3e1_1.grid(row=4, column=0, sticky="w")
        label_1_3.grid(row=5, column=0, sticky="w")
        self.current_label.grid(row=0, column=1, sticky="w")
        self.current_rms.grid(row=1, column=1, sticky="w")
        self.current_rms_3e2_1e1.grid(row=2, column=1, sticky="w")
        self.current_rms_1e1_3e1.grid(row=3, column=1, sticky="w")
        self.current_rms_3e1_1.grid(row=4, column=1, sticky="w")
        self.current_rms_1_3.grid(row=5, column=1, sticky="w")
        self.selected_label.grid(row=0, column=2, sticky="w")
        self.selected_rms.grid(row=1, column=2, sticky="w")
        self.selected_rms_3e2_1e1.grid(row=2, column=2, sticky="w")
        self.selected_rms_1e1_3e1.grid(row=3, column=2, sticky="w")
        self.selected_rms_3e1_1.grid(row=4, column=2, sticky="w")
        self.selected_rms_1_3.grid(row=5, column=2, sticky="w")

        self.buttons = [self.displacement_button, self.velocity_button]
        for button in self.buttons:
            button.config(state="disabled")

        self.overall_c = None
        self.rms_3e2_1e1_c = None
        self.rms_1e1_3e1_c = None
        self.rms_3e1_1_c = None
        self.rms_1_3_c = None

    def initialize(self):
        """Initialize"""
        for button in self.buttons:
            button.config(state="normal")

        self.update_current()

    def option_clicked(self):
        """Option clicked"""
        self.update_rms()
        self.update_current()

    def update_current(self):
        """Get current performance"""
        selection = self.option_var.get()
        f = self.master.selection_tabs.f
        if self.master.plot_option.current is None:
            return
        displacement = self.master.plot_option.current.copy()
        if selection == "velocity":
            displacement *= 2*np.pi*f
        evaluate = self.root.seibot.evaluate
        self.overall_c = evaluate.get_rms(f, displacement) * 1e9
        mask = (f>3e-2) * (f<1e-1)
        self.rms_3e2_1e1_c = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>1e-1) * (f<3e-1)
        self.rms_1e1_3e1_c = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>3e-1) * (f<1)
        self.rms_3e1_1_c = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>1) * (f<3)
        self.rms_1_3_c = evaluate.get_rms(f[mask], displacement[mask]) * 1e9

        self.current_rms.config(text=f"{self.overall_c:.3g}")
        self.current_rms_3e2_1e1.config(text=f"{self.rms_3e2_1e1_c:.3g}")
        self.current_rms_1e1_3e1.config(text=f"{self.rms_1e1_3e1_c:.3g}")
        self.current_rms_3e1_1.config(text=f"{self.rms_3e1_1_c:.3g}")
        self.current_rms_1_3.config(text=f"{self.rms_1_3_c:.3g}")

    def update_rms(self):
        """Update rms values"""
        selection = self.option_var.get()
        f = self.master.selection_tabs.f
        displacement = self.master.selection_tabs.selected_displacement.copy()
        if selection == "velocity":
            displacement *= 2*np.pi*f
        evaluate = self.root.seibot.evaluate
        overall = evaluate.get_rms(f, displacement) * 1e9
        mask = (f>3e-2) * (f<1e-1)
        rms_3e2_1e1 = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>1e-1) * (f<3e-1)
        rms_1e1_3e1 = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>3e-1) * (f<1)
        rms_3e1_1 = evaluate.get_rms(f[mask], displacement[mask]) * 1e9
        mask = (f>1) * (f<3)
        rms_1_3 = evaluate.get_rms(f[mask], displacement[mask]) * 1e9

        fg = "black"
        if self.overall_c is not None:
            if overall > self.overall_c:
                fg = "red"
            else:
                fg = "green"
        self.selected_rms.config(text=f"{overall:.3g}", fg=fg)

        if self.rms_3e2_1e1_c is not None:
            if rms_3e2_1e1 > self.rms_3e2_1e1_c:
                fg = "red"
            else:
                fg = "green"
        self.selected_rms_3e2_1e1.config(text=f"{rms_3e2_1e1:.3g}", fg=fg)

        if self.rms_1e1_3e1_c is not None:
            if rms_1e1_3e1 > self.rms_1e1_3e1_c:
                fg = "red"
            else:
                fg = "green"
        self.selected_rms_1e1_3e1.config(text=f"{rms_1e1_3e1:.3g}", fg=fg)

        if self.rms_3e1_1_c is not None:
            if rms_3e1_1 > self.rms_3e1_1_c:
                fg = "red"
            else:
                fg = "green"
        self.selected_rms_3e1_1.config(text=f"{rms_3e1_1:.3g}", fg=fg)

        if self.rms_1_3_c is not None:
            if rms_1_3 > self.rms_1_3_c:
                fg = "red"
            else:
                fg = "green"
        self.selected_rms_1_3.config(text=f"{rms_1_3:.3g}", fg=fg)


