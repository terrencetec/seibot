import tkinter
import tkinter.filedialog

import seibot


class Menubar(tkinter.Menu):
    """Menubar"""
    def __init__(self, master):
        """Constructor"""
        super().__init__(master)
        file_menu = FileMenu(self, root=master)
        edit_menu = EditMenu(self, root=master)
        self.add_cascade(label="File", menu=file_menu)
        self.add_cascade(label="Edit", menu=edit_menu)


class FileMenu(tkinter.Menu):
    """File menu"""
    def __init__(self, master, root):
        """Constructor"""
        super().__init__(master)
        self.root = root
        self.add_command(label="New")
        self.add_command(label="Open", command=self.open_config)
        self.add_command(label="Save")
        self.add_command(label="Save as")
        self.add_command(label="Exit", command=self.exit)

    def open_config(self):
        """Open config"""
        config = tkinter.filedialog.askopenfilename(
            title="Open Seibot config",
            filetypes=((".ini files", ".ini*"), ("All files", "*.*"))
        )
        self.root.load_seibot(config)

    def exit(self):
        """Exit"""
        # pass
        self.root.destroy()


class EditMenu(tkinter.Menu):
    """Edit Menu"""
    def __init__(self, master, root):
        """Constructor"""
        super().__init__(master)
