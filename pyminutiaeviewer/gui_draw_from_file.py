from tkinter import W, N, E
from tkinter.ttk import Button

from pyminutiaeviewer.gui_common import NotebookTabBase, ControlsFrameBase


class DrawFromFile(NotebookTabBase):
    def __init__(self, parent):
        NotebookTabBase.__init__(self, parent)

        controls = ControlsFrame(self, self.load_fingerprint_image, self.load_minutiae_file)

        self.set_controls(controls)


class ControlsFrame(ControlsFrameBase):
    def __init__(self, parent, load_fingerprint_func, load_minutiae_func):
        ControlsFrameBase.__init__(self, parent, load_fingerprint_func)

        self.open_minutiae_txt_btn = Button(self, text="Open Minutiae File", command=load_minutiae_func)
        self.open_minutiae_txt_btn.grid(row=1, column=0, sticky=N + W + E)
