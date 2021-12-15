"""
small gui application capable of loading diffraction images, alongside pyFAI poni files
author: Laurenz Kremeyer
"""

import os
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import numpy as np
import pyFAI
from PIL import Image
from . import get_data_path, IMAGE_FORMATS, APP_ID


class PoniView(QtWidgets.QMainWindow):
    """
    main window class containing core functionalities
    """
    poni_path = None
    poni = None
    image_path = None
    image = None
    i_digits = 1  # number of maximal digits in the images intensity (used for string formatting)

    def __init__(self, poni_path, image_path, *args, **kwargs):
        """
        sets up the gui
        loads image and poni, if provided as command line arguments
        """
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(get_data_path(), 'lib', 'MainGui.ui'), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(get_data_path(), 'lib/icon.svg')))

        if image_path is not None:
            self.update_image(image_path)
        if poni_path is not None:
            self.update_poni(poni_path)
        self.update_window_title()

        self.plot.cursor_changed.connect(self.update_statusbar)
        self.setAcceptDrops(True)

        self.show()

    def update_statusbar(self, xy):
        """
        updates statusbar string, mainly triggered by mouse movement from the self.plot class
        """
        if self.image is None:
            self.statusbar.showMessage('')
            return
        if xy == (np.NaN, np.NaN):  # triggered when cursor outside of the image
            self.statusbar.showMessage('')
            return
        x, y = xy
        i = self.image[x, y]
        if self.poni is None:
            self.statusbar.showMessage(f'({x:4d}, {y:4d}) | I={i:5.0f}')
            return
        ax, ay = np.array([x]), np.array([y])
        tth = self.poni.tth(ay, ax)[0]
        q = 4.e-10 * np.pi / self.poni.wavelength * np.sin(.5 * tth)
        self.statusbar.showMessage(
            f'({x:4d}, {y:4d}) | 2θ={tth:5.2f}deg | q={q:5.2f}A^-1 | I={i:{self.i_digits}.0f}')

    def update_window_title(self):
        """
        update window title according to names of loaded files
        """
        poni, image = None, None
        if self.poni is not None:
            poni = self.poni_path.split('/')[-1]
        if self.image is not None:
            image = self.image_path.split('/')[-1]
        self.setWindowTitle(f'{poni}   {image}')

    def update_image(self, image_path):
        """
        update the shown diffraction image
        """
        if image_path.lower().endswith('.npy'):
            self.image = np.load(image_path)
        elif image_path.lower().endswith(IMAGE_FORMATS):
            self.image = np.array(Image.open(image_path))
            if self.image.ndim > 2:
                self.image = np.sum(self.image, axis=-1)
            print(self.image)
            print(self.image.shape)
        else:
            print(f'cannot read {image_path}')
            self.statusbar.showMessage('')
            return
        self.image = np.rot90(self.image, 3)  # use same orientation as pyFAI
        self.image_path = image_path
        self.plot.setImage(self.image)
        self.plot.x_size, self.plot.y_size = self.image.shape
        self.i_digits = len(str(int(self.image.max(initial=1))))
        self.statusbar.showMessage('')

    def update_poni(self, poni_path):
        """
        update poni file
        """
        self.poni = pyFAI.load(poni_path)
        self.poni_path = poni_path
        self.statusbar.showMessage('')

    def dragEnterEvent(self, event):
        """
        overrides the QWidget method, checks if the event contains an url
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        overrides the QWidget method, checks what has been dropped onto the application
        and takes appropriate action
        """
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        img_set, poni_set = False, False
        for f in files:
            if f.lower().endswith('.poni') and not poni_set:
                self.update_poni(f)
                self.update_window_title()
                poni_set = True
            if f.lower().endswith(IMAGE_FORMATS) and not img_set:
                self.update_image(f)
                self.update_window_title()
                img_set = True
            if img_set and poni_set:
                return


def run():
    """
    main function to run the application
    """
    from argparse import ArgumentParser
    import sys
    import ctypes

    parser = ArgumentParser()
    parser.add_argument("-p", "--poni", dest="poni", metavar="FILE",
                        help="file containing the diffraction parameter (poni-file)",
                        default=None)
    parser.add_argument("-i", "--image", dest="image", metavar="FILE",
                        help="diffraction image to display",
                        default=None)
    options = parser.parse_args()

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            QtCore.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            QtCore.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass  # catch error that's triggered when on a non-windows machine

    app = QtWidgets.QApplication(sys.argv)
    ui = PoniView(options.poni, options.image)
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
