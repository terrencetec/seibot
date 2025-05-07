"""Seibot GUI Option Panel"""
import tkinter

import seibot.gui.option.plot_option
import seibot.gui.option.manual_option
import seibot.gui.option.threshold_option
import seibot.gui.option.noise_option
import seibot.gui.export
import seibot.gui.option.selection_tabs


class OptionPanel(tkinter.LabelFrame):
    """Option panel"""
    def __init__(self, master):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        """
        super().__init__(master)
        self.plot_option = seibot.gui.option.plot_option.PlotOption(
            self, master)
        self.selection_tabs = seibot.gui.option.selection_tabs.SelectionTabs(
            self, master)
        # self.manual_option = seibot.gui.option.manual_option.ManualOption(
        #     self, master)
        # self.threshold_option = (
        #     seibot.gui.option.threshold_option.ThresholdOption(self, master)
        # )
        # self.noise_option = seibot.gui.option.noise_option.NoiseOption(
        #     self, master)
        # self.export = seibot.gui.export.Export(
        #     self, master)


        self.plot_option.grid(row=0, column=0, sticky="ewns", pady=3)
        self.selection_tabs.grid(row=1, column=0, sticky="ewns", pady=3)
        # self.manual_option.grid(row=1, column=0, sticky="ewns", pady=3)
        # self.threshold_option.grid(row=2, column=0, sticky="ewns", pady=3)
        # self.noise_option.grid(row=3, column=0, sticky="ewns", pady=3)
        # self.export.grid(row=4, column=0, sticky="ewns", pady=3)

    def enable(self):
        """Enable options"""
        self.plot_option.initialize()
        self.selection_tabs.initialize()
        # self.manual_option.initialize()
        # self.threshold_option.initialize()
        # self.noise_option.initialize()
        # self.export.initialize()
