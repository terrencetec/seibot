"""Seibot GUI Main"""
import tkinter
import tkinter.font

import seibot.gui.menubar
import seibot.gui.plot
import seibot.gui.option




class Root(tkinter.Tk):
    """Root window"""
    def __init__(self):
        """Constructor"""
        super().__init__()
        self.attributes("-type", "dialog")
        default_font = tkinter.font.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        self.option_add("*Font", default_font)

        menubar = seibot.gui.menubar.Menubar(self)
        self.config(menu=menubar)

        self.main_plot = seibot.gui.plot.MainPlot(self)
        self.main_plot.grid(row=0, column=0, columnspan=2, sticky="ewns")

        self.sc_plot = seibot.gui.plot.SensorCorrectionPlot(self)
        self.sc_plot.grid(row=1, column=0, sticky="ewns")

        self.blend_plot = seibot.gui.plot.BlendPlot(self)
        self.blend_plot.grid(row=1, column=1, sticky="ewns")

        self.option_panel = seibot.gui.option.OptionPanel(self)
        self.option_panel.grid(row=0, column=2, rowspan=2, sticky="ewns")

        self.seibot = None

    @property
    def seibot(self):
        """Seibot instance"""
        return self._seibot

    @seibot.setter
    def seibot(self, _seibot):
        """Seibot setter"""
        self._seibot = _seibot

    def run(self):
        """Run loop"""
        self.mainloop()

    def load_seibot(self, config):
        """Load seibot"""
        self.seibot = seibot.Seibot(config)
        self.initialize()
        self.enable_options()

    def initialize(self):
        """Initialize"""
        pass

    def enable_options(self):
        """Enable option panel"""
        self.option_panel.enable()
        
