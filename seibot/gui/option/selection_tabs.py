import tkinter
import tkinter.ttk

from . import manual_option
from . import rms_option


class SelectionTabs(tkinter.ttk.Notebook):
    """Selection Tabs"""
    def __init__(self, master, root):
        """Constructor
        
        Parameters
        ----------
        master
            Tkinter parent.
        """
        super().__init__(master)
        self.root = root
        
        # Selection methods:
        # Manual, Min rms, min blrms,
        # Future: TEBO and the like
        self.manual = manual_option.ManualOption(self, root)
        self.manual.pack()
        self.add(self.manual, text="Manual")

        self.rms = rms_option.RMSOption(self, root)
        self.rms.pack()
        self.add(self.rms, text="RMS")

        self.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.selected_sc = None
        self.selected_lp = None
        self.selected_hp = None

        self.ready = False
        self.enabled = False
        self.disable()

    def initialize(self):
        """Initialize"""
        # Get data from root.seibot
        seibot = self.root.seibot
        
        self.sc_pool = seibot.filter_configurations.sc_pool
        self.lp_pool = seibot.filter_configurations.lp_pool
        self.hp_pool = seibot.filter_configurations.hp_pool

        self.f = seibot.data.f
        self.dm = seibot.evaluate.displacement_matrix
        self.seismic_noise = seibot.data.seismic_noise
        self.iso = seibot.isolation_system
        
        # Preselect:
        self.selected_sc = self.sc_pool[0]
        self.selected_lp = self.lp_pool[0]
        self.selected_hp = self.hp_pool[0]
        self.selected_displacement = self.dm[0, 0]

        # Initialize tabs
        self.manual.initialize()
        self.rms.initialize()
        self.ready = True  # Wait for tabs to get initialized

    def enable(self):
        """Enable tabs"""
        self.enabled = True
        # self.plot()
        self.tab_changed(None)
    
    def disable(self):
        """Disable tab"""
        self.enabled = False
        self.unplot()

    @property
    def selected_sc(self):
        """selected_sc"""
        return self._selected_sc

    @selected_sc.setter
    def selected_sc(self, _selected_sc):
        """selected_sc.setter"""
        self._selected_sc = _selected_sc
        self.update_displacement()

    @property
    def selected_lp(self):
        """Selected_lp"""
        return self._selected_lp

    @selected_lp.setter
    def selected_lp(self, _selected_lp):
        """Selected_lp.setter"""
        self._selected_lp = _selected_lp
        self.update_displacement()

    @property
    def selected_hp(self):
        """Selected_hp"""
        return self._selected_hp

    @selected_hp.setter
    def selected_hp(self, _selected_hp):
        """Selected_hp.setter"""
        self._selected_hp = _selected_hp
        self.update_displacement()

    def update_displacement(self):
        """Update sensor correction
        
        sc : seibot.filter.Filter
            Sensor correction filter
        """
        if (self.selected_sc is not None and self.selected_lp is not None
                and self.selected_hp is not None):
            self.iso.sensor_correction_filter = self.selected_sc
            self.iso.low_pass_filter = self.selected_lp
            self.iso.high_pass_filter = self.selected_hp
            displacement = self.iso.get_displacement(self.seismic_noise)
            self.selected_displacement = displacement
            self.master.performance.update_rms()
        
    def plot(self):
        """Plot displacement, sensor correction and blends"""
        self.plot_displacement()
        self.plot_sc()
        self.plot_blend()

    def plot_displacement(self):
        """Plot displacement"""
        xdata = self.f
        ydata = self.selected_displacement
        self.root.main_plot.update_line("selected", xdata, ydata)

    def plot_sc(self):
        """Plot sensor correction"""
        xdata = self.f
        sc = self.selected_sc
        ydata = sc.mag
        ydata_comp = sc.mag_comp
        self.root.sc_plot.update_line("selected", xdata, ydata)
        self.root.sc_plot.update_line("selected_comp", xdata, ydata_comp)

    def plot_blend(self):
        """Plot blend"""
        xdata = self.f
        lp = self.selected_lp
        hp = self.selected_hp
        ydata = lp.mag
        ydata_comp = hp.mag
        self.root.blend_plot.update_line("selected", xdata, ydata)
        self.root.blend_plot.update_line("selected_comp", xdata, ydata_comp)

    def unplot(self):
        """Unplot"""
        self.root.main_plot.update_line("selected")
        self.root.sc_plot.update_line("selected")
        self.root.sc_plot.update_line("selected_comp")
        self.root.blend_plot.update_line("selected")
        self.root.blend_plot.update_line("selected_comp")

    def tab_changed(self, _):
        """Tab changed"""
        if self.ready:
            index = self.index(self.select())
            if index == 0:
                self.manual.update_selected_sc()
                self.manual.update_selected_blend()
            elif index == 1:
                self.rms.update()
