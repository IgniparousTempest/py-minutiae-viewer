import platform
from pathlib import Path
from tkinter import NSEW, PhotoImage
from tkinter.ttk import Notebook, Frame

from ttkthemes import ThemedTk

from pyminutiaeviewer.gui_editor import MinutiaeEditorFrame


class Root(ThemedTk):
    def __init__(self):
        ThemedTk.__init__(self)
        if platform.system() is 'Windows':
            self.set_theme("vista")
        else:
            self.set_theme("clearlooks")

        self.set_title()
        img = PhotoImage(file=Path(__file__).resolve().parent / 'images' / 'icon.png')
        self.iconphoto(True, img)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.notebook = Notebook(self)
        self.notebook.grid(row=0, column=0, sticky=NSEW)
        editor_tab = MinutiaeEditorFrame(self)
        self.notebook.add(editor_tab, text="Minutiae Editor")
        self.notebook.add(Frame(self), text="MINDTCT")

    def set_title(self, title: str=None):
        """
        Sets the main window's title. If a string is provided then the title will be set to 
        "[string] - [programme name]". If None is supplied just the programme name is displayed.
        :param title: The text to set as the title. 
        """
        text = "" if title is None else "{0} - ".format(title)
        self.title(text + "Py Minutiae Viewer")
