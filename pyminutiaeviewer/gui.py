import copy
import platform
import traceback
from pathlib import Path
from tkinter import NSEW, Canvas, N, W
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showerror
from tkinter.ttk import Notebook

from PIL import Image, ImageTk
from ttkthemes import ThemedTk

from pyminutiaeviewer.gui_common import scale_image_to_fit_minutiae_canvas, MenuBar
from pyminutiaeviewer.gui_editor import MinutiaeEditorFrame
from pyminutiaeviewer.gui_mindtct import MindtctFrame
from pyminutiaeviewer.minutia import Minutia
from pyminutiaeviewer.minutiae_drawing import draw_minutiae
from pyminutiaeviewer.minutiae_encoder import MinutiaeEncoder
from pyminutiaeviewer.minutiae_reader import MinutiaeReader, MinutiaeFileFormat


class Root(ThemedTk):
    def __init__(self):
        ThemedTk.__init__(self)
        if platform.system() is 'Windows':
            self.set_theme("vista")
        else:
            self.set_theme("clearlooks")

        self.set_title()
        img = ImageTk.PhotoImage(file=Path(__file__).resolve().parent / 'images' / 'icon.png')
        self.iconphoto(True, img)

        self.menu_bar = MenuBar(self)
        self.config(menu=self.menu_bar)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.minutiae = []

        self.file_path = Path()

        self.image_raw = Image.new('RGBA', (512, 512), (255, 255, 255, 255))
        self.image_fingerprint = self.image_raw
        self.image_minutiae = None
        self.image = ImageTk.PhotoImage(self.image_raw)

        self.image_canvas = Canvas(self, bd=0, highlightthickness=0)
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.image_canvas.grid(row=0, column=1, sticky=NSEW)

        self.notebook = Notebook(self)
        self.notebook.grid(row=0, column=0, sticky=NSEW)
        self.tabs = [
            MindtctFrame(self, self.load_fingerprint_image),
            MinutiaeEditorFrame(self, self.load_fingerprint_image, self.load_minutiae_file, self.save_minutiae_file)
        ]
        self.notebook.add(self.tabs[0], text="MINDTCT")
        self.notebook.add(self.tabs[1], text="Minutiae Editor")

        self.image_canvas.bind("<Button-1>", self.on_canvas_mouse_left_click)
        self.image_canvas.bind("<Control-Button-1>", self.on_canvas_ctrl_mouse_left_click)
        self.image_canvas.bind("<B1-Motion>", self.on_canvas_mouse_left_drag)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_canvas_mouse_left_release)
        self.image_canvas.bind("<Button-3>", self.on_canvas_mouse_right_click)
        self.bind("<Configure>", self.redraw)

    def set_title(self, title: str = None):
        """
        Sets the main window's title. If a string is provided then the title will be set to 
        "[string] - [programme name]". If None is supplied just the programme name is displayed.
        :param title: The text to set as the title. 
        """
        text = "" if title is None else "{0} - ".format(title)
        self.title(text + "Py Minutiae Viewer")

    def redraw(self, _=None):
        im = self.image_raw.copy()

        # Apply drawing from each active tab
        for tab in self.tabs:
            im = tab.fingerprint_drawing(im)

        # Scale image to fit canvas
        im, _ = scale_image_to_fit_minutiae_canvas(self.image_canvas, im)
        self.image_fingerprint = im
        self.image = ImageTk.PhotoImage(self.image_fingerprint)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")

        # Draw minutiae
        self.draw_minutiae()

    def load_fingerprint_image(self):
        file_path = askopenfilename(filetypes=(("Image files", ('*.bmp', '*.jpeg', '*.jpg', '*.png')),
                                               ("All files", "*.*")))
        if file_path:
            self.image_raw = Image.open(file_path).convert("RGBA")
            self.redraw()
            self.file_path = Path(file_path).resolve()
            self.set_title(self.file_path.name)
            self.minutiae = []
            self.update_idletasks()

            self.tabs[self.notebook.index("current")].load_fingerprint_image(self.image_raw)

    def load_minutiae_file(self):
        file_path = askopenfilename(initialfile=self.file_path.stem,
                                    filetypes=(("All minutiae files", ('*.min', '*.sim')),
                                               ("Simple minutiae file", '*.sim'),
                                               ("NBIST minutiae file", '*.min'),
                                               ("All files", "*.*")))
        if file_path:
            # Select the correct file format
            if Path(file_path).suffix == '.sim':
                reader = MinutiaeReader(MinutiaeFileFormat.SIMPLE)
            elif Path(file_path).suffix == '.min':
                reader = MinutiaeReader(MinutiaeFileFormat.NBIST)
            else:
                showerror("Read Minutiae File", "The chosen file had an extension of '{}', which can't be interpreted."
                          .format(Path(file_path).suffix))
                return

            try:
                self.minutiae = reader.read(file_path)
                self.draw_minutiae()

                self.tabs[self.notebook.index("current")].load_minutiae_file()
            except Exception as e:
                traceback.print_exc()
                showerror("Read Minutiae File", "There was an error in reading the minutiae file.\n\n"
                                                "The error message was:\n{}".format(e))

    def save_minutiae_file(self):
        file_path = asksaveasfilename(initialfile=self.file_path.stem,
                                      filetypes=(("Simple minutiae file", '*.sim'),
                                                 ("NBIST minutiae file", '*.min')))
        if file_path:
            # Select the correct file format
            if Path(file_path).suffix == '.sim':
                writer = MinutiaeEncoder(MinutiaeFileFormat.SIMPLE)
            elif Path(file_path).suffix == '.min':
                writer = MinutiaeEncoder(MinutiaeFileFormat.NBIST)
            else:
                showerror("Save Minutiae File", "The chosen file had an extension of '{}', which can't be interpreted."
                          .format(Path(file_path).suffix))
                return

            try:
                writer.write(file_path, self.minutiae, self.image_raw)
            except Exception as e:
                traceback.print_exc()
                showerror("Save Minutiae File", "There was an error in saving the minutiae file.\n\n"
                                                "The error message was:\n{}".format(e))

    def exit_application(self):
        """
        Attempts to exit the application. 
        """
        self.destroy()

    def draw_minutiae(self):

        # Apply filtering from each active module
        minutiae = [m.copy() for m in self.minutiae]
        for tab in self.tabs:
            minutiae = tab.minutiae_filtering(minutiae)

        # Scale minutiae
        ratio = self.image_fingerprint.width / self.image_raw.width
        minutiae = [Minutia(int(m.x * ratio), int(m.y * ratio), m.angle, m.minutia_type, m.quality) for m in minutiae]

        im = Image.new('RGBA', self.image_fingerprint.size, (0, 0, 0, 0))
        self.image_minutiae = draw_minutiae(im, minutiae)

        im = self.image_fingerprint.copy()
        im.paste(self.image_minutiae, (0, 0), self.image_minutiae)
        self.image = ImageTk.PhotoImage(im)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()

    def draw_single_minutia(self, minutia: Minutia):
        temp_image = draw_minutiae(self.image_minutiae, [minutia])
        im = self.image_fingerprint.copy()
        im.paste(temp_image, (0, 0), temp_image)

        self.image = ImageTk.PhotoImage(im)
        self.image_canvas.delete("IMG")
        self.image_canvas.create_image(0, 0, image=self.image, anchor=N + W, tags="IMG")
        self.update_idletasks()

    def number_of_minutiae(self):
        """
        Returns the number of minutiae features.
        :return: Number of minutiae.
        """
        return len(self.minutiae)

    def is_point_in_canvas_image(self, x: int, y: int) -> bool:
        """
        Tests if a point is within the fingerprint image.
        :param x: x co-ordinate of the point to test.
        :param y: y co-ordinate of the point to test.
        :return: True if point is in the image, false otherwise.
        """
        if x > self.image.width() or y > self.image.height():
            return False
        else:
            return True

    def canvas_image_scale_factor(self) -> float:
        """
        Calculates the ratio between the canvas image's actual size and its displayed size.
        :return: The ratio.
        """
        return self.image_raw.width / self.image.width()

    def on_canvas_mouse_left_click(self, event):
        self.tabs[self.notebook.index('current')].on_canvas_mouse_left_click(event)

    def on_canvas_ctrl_mouse_left_click(self, event):
        self.tabs[self.notebook.index('current')].on_canvas_ctrl_mouse_left_click(event)

    def on_canvas_mouse_left_drag(self, event):
        self.tabs[self.notebook.index('current')].on_canvas_mouse_left_drag(event)

    def on_canvas_mouse_left_release(self, event):
        self.tabs[self.notebook.index('current')].on_canvas_mouse_left_release(event)

    def on_canvas_mouse_right_click(self, event):
        self.tabs[self.notebook.index('current')].on_canvas_mouse_right_click(event)
