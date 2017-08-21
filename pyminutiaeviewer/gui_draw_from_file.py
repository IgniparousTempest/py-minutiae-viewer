import traceback
from tkinter import W, N, E, StringVar
from tkinter.filedialog import askopenfilename, sys
from tkinter.messagebox import showerror
from tkinter.ttk import Button, Label, Radiobutton

from pyminutiaeviewer.gui_common import NotebookTabBase, ControlsFrameBase
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class DrawFromFile(NotebookTabBase):
    def __init__(self, parent):
        NotebookTabBase.__init__(self, parent)

        self.minutiae_file_format = StringVar()

        controls = ControlsFrame(self, self.load_fingerprint_image, self.minutiae_file_format,
                                 self.load_minutiae_file, self.draw_minutiae)

        self.set_controls(controls)

    def load_minutiae_file(self):
        file_path = askopenfilename(filetypes=(("Text files", ('*.txt', '*.min')),
                                               ("All files", "*.*")))
        if file_path:
            if self.minutiae_file_format.get() == "Simple":
                reader = MinutiaeReader(MinutiaeFileFormat.SIMPLE)
            elif self.minutiae_file_format.get() == "NBIST":
                reader = MinutiaeReader(MinutiaeFileFormat.NBIST)
            else:
                print("The File Type was not set", file=sys.stderr)
                return

            try:
                self.minutiae = reader.read(file_path)
            except Exception as e:
                traceback.print_exc()
                showerror("Read Minutiae File", "There was an error in reading the minutiae file. Are you sure you "
                                                "selected the right format?\n\nThe error message was:\n{}".format(e))


class ControlsFrame(ControlsFrameBase):
    def __init__(self, parent, load_fingerprint_func, minutiae_format, load_minutiae_func, draw_minutiae_func):
        ControlsFrameBase.__init__(self, parent, load_fingerprint_func)

        self.radio_label = Label(self, text="Minutiae File Format:")
        self.radio_label.grid(row=1, column=0, sticky=N)
        self.radio_simple = Radiobutton(self, text="Simple", variable=minutiae_format, value="Simple")
        self.radio_simple.grid(row=2, column=0, sticky=W)
        self.radio_nbist = Radiobutton(self, text="NBIST/MINDTC", variable=minutiae_format, value="NBIST")
        self.radio_nbist.grid(row=3, column=0, sticky=W)
        minutiae_format.set("NBIST")

        self.open_minutiae_txt_btn = Button(self, text="Open Minutiae File", command=load_minutiae_func)
        self.open_minutiae_txt_btn.grid(row=4, column=0, sticky=N + W + E)

        self.draw_minutiae_btn = Button(self, text="Draw Minutiae", command=draw_minutiae_func)
        self.draw_minutiae_btn.grid(row=5, column=0, sticky=N + W + E)
