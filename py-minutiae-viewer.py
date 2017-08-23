import platform

from pathlib import Path
from tkinter import PhotoImage
from ttkthemes import ThemedTk

from pyminutiaeviewer import gui

root = ThemedTk()
if platform.system() is 'Windows':
    root.set_theme("vista")
else:
    root.set_theme("clearlooks")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.title("Py Minutiae Viewer")
img = PhotoImage(file=Path(__file__).resolve().parent / 'pyminutiaeviewer' / 'images' / 'icon.png')
root.iconphoto(True, img)
app = gui.Root(root)
app.mainloop()
