"""Seibot GUI export"""
import tkinter


class Export(tkinter.LabelFrame):
    """export"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        root : tkinter.Tk
            Tkinter root.
        """
        super().__init__(master, text="Export")
        
        self.root = root

        self.config(font=("Helvetica", 12, "bold"))

        select_label = tkinter.Label(self, text="Select configuration: ")
        option_list = [
            "Selected",
            "Min. RMS disp.",
            "Min. RMS vel.",
            "TEBO",
        ]
        self.option = tkinter.StringVar()
        self.option.set("Selected")
        self.dropdown = tkinter.OptionMenu(
            self, self.option, *option_list, command=self.update_filter)

        file_label = tkinter.Label(self, text="Foton file: ")
        self.file = tkinter.Label(self, text="")
        module_label = tkinter.Label(self, text="Module: ")
        self.module = tkinter.Label(self, text="")
        fm_label = tkinter.Label(self, text="FM: ")
        self.fm = tkinter.Label(self, text="")
        
        export_button = tkinter.Button(
            self, text="Export", command=self.export)

        select_label.grid(row=0, column=0, sticky="w")
        self.dropdown.grid(row=0, column=1, sticky="e")
        file_label.grid(row=1, column=0, sticky="w")
        self.file.grid(row=1, column=1, sticky="e")
        module_label.grid(row=2, column=0, sticky="w")
        self.module.grid(row=2, column=1, sticky="e")
        fm_label.grid(row=3, column=0, sticky="w")
        self.fm.grid(row=3, column=1, sticky="e")
        export_button.grid(row=4, column=1, sticky="es")

        self.buttons = [self.dropdown, export_button]

        for button in self.buttons:
            button.config(state="disabled")

    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")

    def initialize(self):
        """Initialize"""
        self.update_filter()
        self.enable()

    def get_filter(self):
        """Get filter"""
        if self.option.get() == "Selected":
            filters = self.root.option_panel.manual_option.filters
        elif self.option.get() == "Min. RMS disp.":
            filters = self.root.option_panel.plot_option.min_disp_filters
        elif self.option.get() == "Min. RMS vel.":
            filters = self.root.option_panel.plot_option.min_vel_filters
        elif self.option.get() == "TEBO":
            filters = self.root.option_panel.threshold_option.tebo_filters

        return filters

    def update_filter(self, _=None):
        """Update filters"""
        filters = self.get_filter()
        file = filters.sc.filter_file
        module = filters.sc.module
        fm = filters.sc.fm
        self.file.config(text=file)
        self.module.config(text=module)
        self.fm.config(text=str(fm))

    def export(self):
        """export"""
        pass



