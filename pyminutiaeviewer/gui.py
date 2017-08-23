from tkinter import NSEW
from tkinter.ttk import Frame, Style, Notebook

from pyminutiaeviewer.gui_editor import MinutiaeEditorFrame


class Root(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(sticky=NSEW)

        self.notebook = Notebook(self)
        self.notebook.grid(row=0, column=0, sticky=NSEW)
        editor_tab = MinutiaeEditorFrame(self)
        self.notebook.add(editor_tab, text="Minutiae Editor")
        self.notebook.add(Frame(self), text="MINDTCT")
