import argparse

from pyminutiaeviewer import gui

parser = argparse.ArgumentParser(description='Py Minutiae Viewer')
parser.add_argument('-d', '--draw-minutiae', nargs='+', dest='draw_minutiae',
                    metavar=('FINGERPRINT_IMAGE', 'MINUTIAE_FILE'),
                    help='Draws minutiae on to the FINGERPRINT_IMAGE, needs the output-image flag to be set. '
                         'If no MINUTIAE_FILE is set then a .min file with the same names as the FINGERPRINT_IMAGE '
                         'is assumed.')
parser.add_argument('-o', '--output-image', nargs=1, dest='output_image',
                    metavar='OUTPUT_IMAGE',
                    help='The location to save the output image.')

args = parser.parse_args()

if args.draw_minutiae is not None:
    if args.output_image is None:
        parser.error('Missing output image, set --output-image.')
    pass
else:
    gui.Root().mainloop()
