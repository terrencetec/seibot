import tkinter

import seibot.filter


class ExportOption(tkinter.Frame):
    """Export"""
    def __init__(self, master, root):
        """Constructor"""
        super().__init__(master)

        self.master = master
        self.root = root

        self.export_button = tkinter.Button(
            self, text="Export selected filters",
            command=self.export_clicked)

        self.export_button.pack()
        
        self.buttons = [self.export_button]
        for button in self.buttons:
            button.config(state="disabled")

    def initialize(self):
        """Initialize"""
        for button in self.buttons:
            button.config(state="normal")

    def export_clicked(self):
        """Export clicked"""
        path = tkinter.filedialog.asksaveasfilename(
            title="Save filter configuration file",
            filetypes=((".ini files", ".ini*"), ("All files", "*.*"))
        )
        sc = self.master.selection_tabs.selected_sc
        lp = self.master.selection_tabs.selected_lp
        hp = self.master.selection_tabs.selected_hp
        
        filters = seibot.filter.FilterConfiguration(sc=sc, lp=lp, hp=lp)
        filters.export(path)
