"""
module containing widget(s)
"""
import pyqtgraph as pg
from numpy import NaN
from PyQt5.QtCore import pyqtSignal


class MainPlot(pg.ImageView):
    """
    main image plot widget, showing image and adjustment tools
    """
    x_size = 0
    y_size = 0
    cursor_changed = pyqtSignal(tuple)

    def __init__(self, parent=None):
        """
        setup plot widget
        """
        super().__init__()
        pg.setConfigOption('background', (240, 240, 240))
        pg.setConfigOption('foreground', 'k')
        self.setParent(parent)
        self.proxy = pg.SignalProxy(self.scene.sigMouseMoved,
                                    rateLimit=60, slot=self.__callback_move)
        self.setColorMap(pg.colormap.get('inferno'))

    def __callback_move(self, evt):
        """
        callback function for mouse movement on image
        -> triggers status bar update
        """
        qpoint = self.view.mapSceneToView(evt[0])
        x = int(qpoint.x())
        y = int(qpoint.y())
        if x < 0 or x >= self.x_size:
            self.cursor_changed.emit((NaN, NaN))
            return
        if y < 0 or y >= self.y_size:
            self.cursor_changed.emit((NaN, NaN))
            return
        self.cursor_changed.emit((x, y))
