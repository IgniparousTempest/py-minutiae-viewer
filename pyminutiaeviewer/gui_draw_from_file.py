import traceback
from tkinter import W, N, E, StringVar, NSEW, Canvas, RAISED
from tkinter.filedialog import askopenfilename, sys
from tkinter.messagebox import showerror
from tkinter.ttk import Frame, Button, Label, Radiobutton

from PIL import ImageTk, Image

from pyminutiaeviewer.gui_common import scale_image_to_fit_minutiae_canvas
from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class DrawFromFile(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(sticky=NSEW)

        self.minutiae_file_format = StringVar()
        self.minutiae = None

        self.image_raw = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        self.image_minutiae = None
        self.image = ImageTk.PhotoImage(self.image_raw)

        self.controls_frame = ControlsFrame(self, self.load_fingerprint_image, self.minutiae_file_format,
                                            self.load_minutiae_file, self.draw_minutiae)
        self.controls_frame.grid(row=0, column=0, sticky=NSEW)

        self.image_canvas = Canvas(self, bd=0, highlightthickness=0)
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.image_canvas.grid(row=0, column=1, sticky=NSEW)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        if self.image_minutiae is not None:
            self.draw_minutiae()
            return
        resized, _ = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        self.image = ImageTk.PhotoImage(resized)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")

    def load_fingerprint_image(self):
        file_path = askopenfilename(filetypes=(("Image files", ('*.bmp', '*.jpeg', '*.jpg', '*.png')),
                                               ("All files", "*.*")))
        if file_path:
            self.image_raw = Image.open(file_path).convert("RGBA")
            self.image = ImageTk.PhotoImage(self.image_raw)
            self.image_minutiae = None
            self.image_canvas.delete("IMG")
            self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
            self.resize(None)
            self.update_idletasks()

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

    def draw_minutiae(self):
        if self.minutiae is None:
            showerror("Draw Minutiae", "The minutiae file has not been set.")
            return
        if self.image_raw is None:
            showerror("Draw Minutiae", "The image file has not been set.")
            return

        scaled_raw_image, ratio = scale_image_to_fit_minutiae_canvas(self.image_canvas, self.image_raw)
        minutiae = [Minutia(int(m.x * ratio), int(m.y * ratio), m.angle, m.minutia_type) for m in self.minutiae]
        self.image_minutiae = draw_minutiae(scaled_raw_image, minutiae)

        self.image = ImageTk.PhotoImage(self.image_minutiae)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()


class ControlsFrame(Frame):
    def __init__(self, parent, load_fingerprint_func, minutiae_format, load_minutiae_func, draw_minutiae_func):
        Frame.__init__(self, parent, relief=RAISED, borderwidth=1)
        self.open_fingerprint_image_button = Button(self, text="Open Fingerprint Image", command=load_fingerprint_func)
        self.open_fingerprint_image_button.grid(row=0, column=0, sticky=N + W + E)

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
