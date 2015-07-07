from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as
                                                NavigationToolbar)
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=4, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # override mouseMoveEvent with non-functional dummy
    # this will prevent the gui thread to hang while moving the mouse
    # while a large number of plots is shown simultaniously
    def mouseMoveEvent(self, event):
        pass

    def clear(self):
        self.ax.clear()
        self.fig.clear()


class CustomNavigationToolbar(NavigationToolbar):
    toolitems = (
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None), )

    def __init__(self, canvas, parent, coordinates=True):
        NavigationToolbar.__init__(self, canvas, parent,
                                   coordinates=coordinates)


class MplWidget(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        self.canvas = MplCanvas()
        self.ntb = CustomNavigationToolbar(self.canvas, self,
                                           coordinates=False)
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.ntb)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
