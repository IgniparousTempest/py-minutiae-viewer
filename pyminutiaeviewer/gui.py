from tkinter import NSEW
from tkinter.ttk import Frame, Style, Notebook

from pyminutiaeviewer.gui_draw_from_file import DrawFromFile


class Root(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        s = Style()
        s.theme_use("clam")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(sticky=NSEW)

        self.notebook = Notebook(self)
        self.notebook.grid(row=0, column=0, sticky=NSEW)
        draw_from_file_tab = DrawFromFile(self)
        self.notebook.add(draw_from_file_tab, text="Draw from File")
        self.notebook.add(Frame(self), text="Manual Labeling")
        self.notebook.add(Frame(self), text="MINDTCT")
