"""Seibot Gui Manual option"""
import tkinter


class ManualOption(tkinter.LabelFrame):
    """Manual option"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        root : tkinter.Tk
            Tkinter root
        """
        super().__init__(master, text="Manual selection options")

        self.root = root

        self.config(font=("Helvetica", 12, "bold"))
        
        self.plot_var = tkinter.IntVar()
        self.plot_var.set(0)

        plot_button = tkinter.Checkbutton(
            self, text="Plot selected",
            variable=self.plot_var, command=self.plot
        )

        sc_label = tkinter.Label(
            self, text="Select sensor correction filters: ")
        self.sc_option = tkinter.IntVar()
        self.sc_dropdown = tkinter.OptionMenu(
            self, self.sc_option, 0, command=self.sc_dropdown_clicked)
        sc_left = tkinter.Button(
            self, text="<", command=self.sc_left_clicked)
        sc_right = tkinter.Button(
            self, text=">", command=self.sc_right_clicked)

        blend_label = tkinter.Label(
            self, text="Select complementary filters (blends): ")
        self.blend_option = tkinter.IntVar()
        self.blend_dropdown = tkinter.OptionMenu(
            self, self.blend_option, 0, command=self.blend_dropdown_clicked)
        blend_left = tkinter.Button(
            self, text="<", command=self.blend_left_clicked)
        blend_right = tkinter.Button(
            self, text=">", command=self.blend_right_clicked)

        plot_button.grid(row=0, column=0, columnspan=4, sticky="w")
        sc_label.grid(row=1, column=0, sticky="w")
        self.sc_dropdown.grid(row=1, column=2, sticky="e")
        sc_left.grid(row=1, column=1, sticky="e")
        sc_right.grid(row=1, column=3, sticky="e")


        blend_label.grid(row=2, column=0, sticky="w")
        self.blend_dropdown.grid(row=2, column=2, sticky="e")
        blend_left.grid(row=2, column=1, sticky="e")
        blend_right.grid(row=2, column=3, sticky="e")

        self.buttons = [
            plot_button, self.sc_dropdown, sc_left, sc_right,
            self.blend_dropdown, blend_left, blend_right
        ]

        for button in self.buttons:
            button.config(state="disabled")

    def initialize(self):
        """Initialize"""
        seibot = self.root.seibot
        self.sc_pool = seibot.filter_configurations.sc_pool
        self.lp_pool = seibot.filter_configurations.lp_pool
        self.hp_pool = seibot.filter_configurations.hp_pool
        self.sc_dropdown["menu"].delete(0, "end")
        for i in range(len(self.sc_pool)):
            self.sc_dropdown["menu"].add_command(
                label=i,
                command=lambda option=i: self.sc_dropdown_clicked(option)
            )

        self.blend_dropdown["menu"].delete(0, "end")
        for i in range(len(self.lp_pool)):
            self.blend_dropdown["menu"].add_command(
                label=i,
                command=lambda option=i: self.blend_dropdown_clicked(option)
            )
        self.f = seibot.data.f
        self.dm = seibot.evaluate.displacement_matrix
        self.filters = seibot.filter_configurations(
            self.sc_option.get(), self.blend_option.get())

        self.enable()


    def enable(self):
        """Enable buttons"""
        for button in self.buttons:
            button.config(state="normal")

    def plot(self):
        """plot"""
        self.plot_displacement()
        self.plot_sc()
        self.plot_blend()

    def plot_displacement(self):
        """Plot displacement"""
        if self.plot_var.get():
            sc_i = self.sc_option.get()
            blend_i = self.blend_option.get()
            xdata = self.f
            ydata = self.dm[sc_i, blend_i]
            self.root.main_plot.update_line("selected", xdata, ydata)
        else:
            self.root.main_plot.update_line("selected")

    def plot_sc(self):
        """Plot sensor correction"""
        if self.plot_var.get():
            sc_i = self.sc_option.get()
            xdata = self.f
            ydata = self.sc_pool[sc_i].mag
            ydata_comp = self.sc_pool[sc_i].mag_comp
            self.root.sc_plot.update_line("selected", xdata, ydata)
            self.root.sc_plot.update_line("selected_comp", xdata, ydata_comp)
        else:
            self.root.sc_plot.update_line("selected")
            self.root.sc_plot.update_line("selected_comp")

    def plot_blend(self):
        """Plot sensor correction"""
        if self.plot_var.get():
            blend_i = self.blend_option.get()
            xdata = self.f
            ydata = self.lp_pool[blend_i].mag
            ydata_comp = self.hp_pool[blend_i].mag
            self.root.blend_plot.update_line("selected", xdata, ydata)
            self.root.blend_plot.update_line(
                "selected_comp", xdata, ydata_comp)
        else:
            self.root.blend_plot.update_line("selected")
            self.root.blend_plot.update_line("selected_comp")

    def sc_dropdown_clicked(self, i):
        """sc dropdown clicked"""
        self.sc_option.set(i)
        self.update_selected_sc()

    def sc_left_clicked(self):
        """sc left clicked"""
        self.sc_option.set(self.sc_option.get()-1)
        self.update_selected_sc()
    
    def sc_right_clicked(self):
        """sc right clicked"""
        self.sc_option.set(self.sc_option.get()+1)
        self.update_selected_sc()

    def update_selected_sc(self):
        """Update selected sc"""
        if self.sc_option.get() < 0:
            self.sc_option.set(0)
        elif self.sc_option.get() > len(self.sc_pool)-1:
            self.sc_option.set(len(self.sc_pool)-1)

        seibot = self.root.seibot
        self.filters = seibot.filter_configurations(
            self.sc_option.get(), self.blend_option.get())

        self.plot()

    def blend_dropdown_clicked(self, i):
        """blend dropdown clicked"""
        self.blend_option.set(i)
        self.update_selected_blend()

    def blend_left_clicked(self):
        """blend left clicked"""
        self.blend_option.set(self.blend_option.get()-1)
        self.update_selected_blend()

    def blend_right_clicked(self):
        """blend right clicked"""
        self.blend_option.set(self.blend_option.get()+1)
        self.update_selected_blend()

    def update_selected_blend(self):
        """Update selected blend"""
        if self.blend_option.get() < 0:
            self.blend_option.set(0)
        elif self.blend_option.get() > len(self.lp_pool)-1:
            self.blend_option.set(len(self.lp_pool)-1)

        seibot = self.root.seibot

        self.filters = seibot.filter_configurations(
            self.sc_option.get(), self.blend_option.get())

        self.plot()

