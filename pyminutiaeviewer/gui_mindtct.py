from tkinter import N, W, E, DoubleVar, IntVar
from tkinter.ttk import LabelFrame, Label, Entry, Scale, Radiobutton, Button
from types import LambdaType, FunctionType
from typing import Union

from PIL import ImageEnhance
from overrides import overrides

from pyminutiaeviewer.gui_common import NotebookTabBase, validation_command, validate_float_between_0_and_1, \
    validate_int_between_0_and_100, validate_int_between_neg_100_and_100
from pyminutiaeviewer.mindtct import mindtct


class MindtctFrame(NotebookTabBase):
    def __init__(self, parent, load_fingerprint_func):
        super(self.__class__, self).__init__(parent, load_fingerprint_func)
        self.root = parent

        self.min_quality_var = DoubleVar()
        self.fp_opacity_var = IntVar()
        self.min_opacity_var = IntVar()
        self.fp_brightness_var = IntVar()
        self.fp_contrast_var = IntVar()
        self.algorithm_var = IntVar()
        self.image_width_var = IntVar()
        self.image_height_var = IntVar()
        self.minutiae_count_var = IntVar()
        self.restore_default_values()

        self.display_settings_frame = InfoFrame(self, self.image_width_var, self.image_height_var,
                                                self.minutiae_count_var)
        self.display_settings_frame.grid(row=1, column=0, padx=4, sticky=N + W + E)

        self.display_settings_frame = DisplaySettingsFrame(self, self.min_quality_var, self.fp_opacity_var,
                                                           self.min_opacity_var)
        self.display_settings_frame.grid(row=2, column=0, padx=4, sticky=N + W + E)

        self.image_settings_frame = ImageSettingsFrame(self, self.fp_brightness_var, self.fp_contrast_var)
        self.image_settings_frame.grid(row=3, column=0, padx=4, sticky=N + W + E)

        self.algorithm_selection_frame = AlgorithmSelectionFrame(self, self.algorithm_var)
        self.algorithm_selection_frame.grid(row=4, column=0, padx=4, sticky=N + W + E)

        self.buttons_frame = ButtonsFrame(self, self.reset, self.extract_minutiae)
        self.buttons_frame.grid(row=5, column=0, padx=4, sticky=N + W + E)

    def restore_default_values(self):
        """
        Sets all variables to their default value. 
        """

        # Reset sliders:
        self.min_quality_var.set(0.0)
        self.fp_opacity_var.set(100)
        self.min_opacity_var.set(0)
        self.fp_brightness_var.set(0)
        self.fp_contrast_var.set(0)
        self.algorithm_var.set(0)
        self.minutiae_count_var.set(0)

    def reset(self):
        """
        Resets all the controls. And redraws the image.
        """
        self.restore_default_values()

        self.root.minutiae = []

        # Redraw the image
        self.root.redraw()

    def extract_minutiae(self):
        # TODO: Get the real image
        minutiae = mindtct(self.root.image_raw)
        self.root.minutiae = minutiae
        self.restore_default_values()
        self.minutiae_count_var.set(len(minutiae))

        self.root.redraw()

    @overrides
    def load_fingerprint_image(self, image):
        self.image_width_var.set(image.width)
        self.image_height_var.set(image.height)

        self.reset()

    @overrides
    def fingerprint_drawing(self, image):
        # Apply opacity settings
        image.putalpha(int(self.fp_opacity_var.get() * 2.55))

        # Apply brightness settings
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(2.0 * (self.fp_brightness_var.get() + 100.0) / 200.0)

        # Apply contrast setting
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0 * (self.fp_contrast_var.get() + 100.0) / 200.0)

        return image

    @overrides
    def minutiae_filtering(self, minutiae):
        return list(filter(lambda m: m.quality > self.min_quality_var.get(), minutiae))


class InfoFrame(LabelFrame):
    def __init__(self, parent, width_var, height_var, minutiae_var):
        super(self.__class__, self).__init__(parent, text="Display Settings")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.width_label = Label(self, text="Width:")
        self.width_label.grid(row=0, column=0)
        self.height_label = Label(self, text="Height:")
        self.height_label.grid(row=0, column=1)

        self.width_entry = Entry(self, textvariable=width_var, justify='center', state='readonly', width=7)
        self.width_entry.grid(row=1, column=0)
        self.height_entry = Entry(self, textvariable=height_var, justify='center', state='readonly', width=7)
        self.height_entry.grid(row=1, column=1)

        self.total_minutiae_label = Label(self, text="Total Minutiae Detected:")
        self.total_minutiae_label.grid(row=2, column=0, columnspan=2)
        self.total_minutiae_entry = Entry(self, textvariable=minutiae_var, justify='center', state='readonly', width=11)
        self.total_minutiae_entry.grid(row=3, column=0, columnspan=2, pady=(0, 4))


class DisplaySettingsFrame(LabelFrame):
    def __init__(self, parent, quality_var, fp_opacity_var, min_opacity_var):
        super(self.__class__, self).__init__(parent, text="Display Settings")

        self.min_quality_label = Label(self, text="Minutiae Quality > ", padding=(5, 5))
        self.min_quality_label.grid(row=0, column=0, sticky=W)

        validation = validation_command(parent, validate_float_between_0_and_1)
        self.min_quality_entry = Entry(self, textvariable=quality_var, width=5, **validation)
        self.min_quality_entry.grid(row=0, column=1, sticky=E)

        self.min_quality_scale = Scale(self, to=1.0,
                                       command=_functions(_make_two_float(quality_var), parent.root.draw_minutiae),
                                       variable=quality_var)
        self.min_quality_scale.grid(row=1, column=0, columnspan=2, sticky=W + E)

        self.fp_opacity_label = Label(self, text="FP Opacity (%)", padding=(5, 5))
        self.fp_opacity_label.grid(row=2, column=0, sticky=W)

        validation = validation_command(parent, validate_int_between_0_and_100)
        self.fp_opacity_entry = Entry(self, textvariable=fp_opacity_var, width=5, **validation)
        self.fp_opacity_entry.grid(row=2, column=1, sticky=E)

        self.fp_opacity_scale = Scale(self, to=100, command=_functions(_make_whole(fp_opacity_var), parent.root.redraw),
                                      variable=fp_opacity_var)
        self.fp_opacity_scale.grid(row=3, column=0, columnspan=2, sticky=W + E)

        self.min_opacity_label = Label(self, text="Min Opacity (%)", padding=(5, 5))
        self.min_opacity_label.grid(row=4, column=0, sticky=W)

        self.min_opacity_entry = Entry(self, textvariable=min_opacity_var, width=5, **validation)
        self.min_opacity_entry.grid(row=4, column=1, sticky=E)

        self.min_opacity_scale = Scale(self, to=100, command=_make_whole(min_opacity_var), variable=min_opacity_var)
        self.min_opacity_scale.grid(row=5, column=0, columnspan=2, sticky=W + E, pady=(0, 4))


class ImageSettingsFrame(LabelFrame):
    def __init__(self, parent, fp_brightness_var, fp_contrast_var):
        super(self.__class__, self).__init__(parent, text="Image Settings")

        self.fp_brightness_label = Label(self, text="FP Brightness (%)", padding=(5, 5))
        self.fp_brightness_label.grid(row=0, column=0, sticky=W)

        validation = validation_command(parent, validate_int_between_neg_100_and_100)
        self.fp_brightness_entry = Entry(self, textvariable=fp_brightness_var, width=5, **validation)
        self.fp_brightness_entry.grid(row=0, column=1, sticky=E)

        self.fp_brightness_scale = Scale(self, from_=-100, to=100,
                                         command=_functions(_make_whole(fp_brightness_var), parent.root.redraw),
                                         variable=fp_brightness_var)
        self.fp_brightness_scale.grid(row=1, column=0, columnspan=2, sticky=W + E)

        self.fp_contrast_label = Label(self, text="FP Contrast (%)", padding=(5, 5))
        self.fp_contrast_label.grid(row=2, column=0, sticky=W)

        self.fp_contrast_entry = Entry(self, textvariable=fp_contrast_var, width=5, **validation)
        self.fp_contrast_entry.grid(row=2, column=1, sticky=E)

        self.fp_contrast_scale = Scale(self, from_=-100, to=100,
                                       command=_functions(_make_whole(fp_contrast_var), parent.root.redraw),
                                       variable=fp_contrast_var)
        self.fp_contrast_scale.grid(row=3, column=0, columnspan=2, sticky=W + E, pady=(0, 4))


class AlgorithmSelectionFrame(LabelFrame):
    def __init__(self, parent, algorithm_var: IntVar):
        super(self.__class__, self).__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.iafis_radio = Radiobutton(self, text="IAFIS", variable=algorithm_var, value=0)
        self.iafis_radio.grid(row=0, column=0)
        self.m1_radio = Radiobutton(self, text="M1", variable=algorithm_var, value=1)
        self.m1_radio.grid(row=0, column=1, pady=(0, 4))


class ButtonsFrame(LabelFrame):
    def __init__(self, parent, reset_func, minutiae_extraction_func):
        super(self.__class__, self).__init__(parent)

        self.columnconfigure(0, weight=1)

        self.nfiq_var = IntVar()

        self.min_detect_button = Button(self, text="Min. Detect", command=minutiae_extraction_func)
        self.min_detect_button.grid(row=0, column=0, pady=(0, 4))

        self.nfiq_score_button = Button(self, text="NFIQ Score", command=None)
        self.nfiq_score_button.grid(row=1, column=0)

        self.nfiq_entry = Entry(self, textvariable=self.nfiq_var, justify='center', state='disabled', width=5)
        self.nfiq_entry.grid(row=2, column=0, pady=4)

        self.reset_button = Button(self, text="reset", command=reset_func)
        self.reset_button.grid(row=3, column=0, pady=(0, 4))


def _make_whole(variable: IntVar):
    """
    Ensures that a variable will always be a whole number.
    :param variable: The variable to maintain as a whole number.
    :return: The function as a lambda.
    """
    return lambda _=None: variable.set('{0:d}'.format(round(variable.get())))


def _make_two_float(variable: DoubleVar):
    """
    Ensures that a variable will always have two decimal places.
    :param variable: The variable to with the value to read and set.
    :return: The function as a lambda.
    """
    return lambda _=None: variable.set('{0:.2f}'.format(variable.get()))


def _functions(*args: Union[FunctionType, LambdaType]):
    """
    Wraps multiple functions in a lambda to be executed sequentially when called.
    :param args: The functions to execute.
    :return: A lambda to execute the provided functions.
    """
    return lambda _=None: [f() for f in args]
