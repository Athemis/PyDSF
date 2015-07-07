# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import (pyqtSlot,
                          QObject,
                          pyqtSignal,
                          QThreadPool,
                          QRunnable,)
from PyQt5.QtWidgets import (QMainWindow,
                             QProgressBar,
                             QDialogButtonBox,
                             QFileDialog,
                             QMessageBox,
                             QApplication,
                             QScrollArea)

from .Ui_mainwindow import Ui_MainWindow
import ui.libs.pyqtgraph as pg
from pydsf import Experiment, PlotResults

pg.setConfigOptions(antialias=True)

VERSION = "1.0"


class WorkerSignals(QObject):

    finished = pyqtSignal()


class Worker(QRunnable):
    finished = pyqtSignal(int)

    def __init__(self, owner):
        super(Worker, self).__init__()
        self.exp = None
        self.owner = owner
        self.signals = WorkerSignals()

    def run(self):
        c_lower = None
        c_upper = None
        cbar_range = None
        signal_threshold = None
        instrument_type = self.owner.comboBox_instrument.currentText()
        if self.owner.groupBox_cutoff.isChecked():
            c_lower = self.owner.doubleSpinBox_lower.value()
            c_upper = self.owner.doubleSpinBox_upper.value()
        if self.owner.groupBox_cbar.isChecked():
            cbar_range = (self.owner.doubleSpinBox_cbar_start, self.owner.doubleSpinBox_cbar_end)
        if self.owner.groupBox_signal_threshold.isChecked():
            signal_threshold = self.owner.spinBox_signal_threshold.value()

        items = (self.owner.listWidget_data.item(i) for i in range(self.owner.listWidget_data.count()))

        files = []
        for item in items:
            files.append(item.text())
        self.exp = Experiment(exp_type=instrument_type, files=files, t1=self.owner.doubleSpinBox_tmin.value(), t2=self.owner.doubleSpinBox_tmax.value(),
                              dt=self.owner.doubleSpinBox_dt.value(), cols=12, rows=8, cutoff_low=c_lower, cutoff_high=c_upper,
                              signal_threshold=signal_threshold, color_range=cbar_range)
        print("Start processing of data... ")
        self.exp.analyze()
        print("done!")
        self.signals.finished.emit()


class TaskSignals(QObject):
    finished = pyqtSignal(list)


class Tasks(QObject):
    def __init__(self):
        super(Tasks, self).__init__()

        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(1)
        self.tasks = []
        self.data = []
        self.signals = TaskSignals()

    def add_task(self, task):
        self.tasks.append(task)

    def get_data(self):
        self.pool.waitForDone()
        return self.data

    def start(self):
        for task in self.tasks:
            self.pool.start(task)
        self.pool.waitForDone()

        for task in self.tasks:
            self.data.append(task.exp)

        print(self.data)
        self.signals.finished.emit(self.data)


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """

    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget (QWidget)
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setEnabled(False)
        self.statusBar.addPermanentWidget(self.progressBar)
        self.statusBar.showMessage("Welcome to PyDSF")

        self.buttonBox_process.addButton("&Start Processing", QDialogButtonBox.AcceptRole)

    @pyqtSlot("QAbstractButton*")
    def on_buttonBox_open_reset_clicked(self, button):
        """
        Slot documentation goes here.
        """
        if button == self.buttonBox_open_reset.button(QDialogButtonBox.Open):
            filenames, filter = QFileDialog.getOpenFileNames(self, 'Open data file', '', "Text files (*.txt *.csv)")
            self.listWidget_data.addItems(filenames)
            if self.listWidget_data.count() > 1:
                self.groupBox_replicates.setChecked(True)
                self.radioButton_rep_files.setEnabled(True)
        elif button == self.buttonBox_open_reset.button(QDialogButtonBox.Reset):
            self.listWidget_data.clear()
            print("Data cleared")
        # self.radioButton_rep_rows.setEnabled(False)
        #            self.radioButton_rep_columns.setEnabled(False)

    @pyqtSlot("QString")
    def on_comboBox_instrument_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if p0 == 'Analytik Jena qTOWER 2.0/2.2':
            print(p0)
            self.groupBox_temp.setEnabled(True)
        else:
            self.groupBox_temp.setEnabled(False)
        # self.groupBox_data.setEnabled(True)
        #        self.groupBox_cutoff.setEnabled(True)
        #        self.groupBox_cbar.setEnabled(True)
        #        self.groupBox_signal_threshold.setEnabled(True)

    def generate_plot_tab(self, name):
        tab = QScrollArea()
        tab.setObjectName(name)
        tab.setWidgetResizable(True)
        return tab

    def generate_plate_tabs(self, plate):
        # TODO: not implemented yet
        # raise NotImplementedError
        plotter = PlotResults()

        if id != 'average':
        #    tab = self.generate_plot_tab("tab_heatmap_{}".format(id))
        #    self.tabWidget.addTab(tab, "Heatmap #{}".format(plate.id))
        #    plotter.plot_tm_heatmap_single(plate, tab)

            tab = self.generate_plot_tab("tab_raw_{}".format(id))
            plt = pg.GraphicsLayoutWidget()
            tab.setWidget(plt)
            self.tabWidget.addTab(tab, "Raw Data #{}".format(plate.id))
            plotter.plot_raw(plate, plt)

        #    tab = self.generate_plot_tab("tab_derivative_{}".format(id))
        #    self.tabWidget.addTab(tab, "Derivatives #{}".format(plate.id))
        #    plotter.plot_derivative(plate, tab)
        #else:
        #    tab = self.generate_plot_tab("tab_heatmap_{}".format(id))
        #    self.tabWidget.addTab(tab, "Heatmap ({})".format(plate.id))
        #    plotter.plot_tm_heatmap_single(plate, tab)

    @pyqtSlot()
    def on_buttonBox_process_accepted(self):
        """
        Slot documentation goes here.
        """

        if self.listWidget_data.count() < 1:
            QMessageBox.critical(self, 'Error', "No data file loaded!", QMessageBox.Close, QMessageBox.Close)
            return
        if self.spinBox_signal_threshold.value() == 0 and self.groupBox_signal_threshold.isChecked():
            QMessageBox.warning(self, 'Warning', "Signal threshold is currently set to zero.", QMessageBox.Ok,
                                QMessageBox.Ok)

        self.progressBar.setEnabled(True)
        self.statusBar.showMessage("Processing...")

        self.tasks = Tasks()
        self.tasks.signals.finished.connect(self.on_processing_finished)
        self.worker = Worker(self)
        self.tasks.add_task(self.worker)
        self.tasks.start()

    @pyqtSlot()
    def on_processing_finished(self):
        # For now, only read the first entry
        exp = self.tasks.data[0]

        save_data = QMessageBox.question(self, 'Save data', "Calculations are finished. Save results?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if save_data == QMessageBox.Yes:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.Directory)
            folder = dialog.getExistingDirectory(self, 'Choose path for results')
            for plate in exp.plates:
                plate.write_tm_table('{}/plate_{}_04_tm.csv'.format(folder, str(plate.id)))
                plate.write_derivative_table('{}/plate_{}_03_dI_dT.csv'.format(folder, str(plate.id)))
                plate.write_filtered_table('{}/plate_{}_02_filtered_data.csv'.format(folder, str(plate.id)))
                plate.write_raw_table('{}/plate_{}_01_raw_data.csv'.format(folder, str(plate.id)))

            if exp.avg_plate:
                exp.avg_plate.write_avg_tm_table('{}/plate_{}_05_tm_avg.csv'.format(folder, str(self.worker.exp.avg_plate.id)))

        for i in range(len(self.worker.exp.plates)):

            plate = exp.plates[i]
            self.generate_plate_tabs(plate)

        if exp.avg_plate:

            plate = exp.avg_plate
            self.generate_plate_tabs(plate)

        self.progressBar.setEnabled(False)
        self.statusBar.showMessage("Finished!")

    @pyqtSlot()
    def on_buttonBox_process_rejected(self):
        """
        Slot documentation goes here.
        """
        QApplication.quit()

    pyqtSlot()

    def on_actionQuit_triggered(self):
        """
        Slot documentation goes here.
        """
        QApplication.quit()

    @pyqtSlot("bool")
    def on_groupBox_cutoff_toggled(self, p0):
        """
        Slot documentation goes here.
        """
        self.doubleSpinBox_upper.setValue(self.doubleSpinBox_tmax.value())
        self.doubleSpinBox_lower.setValue(self.doubleSpinBox_tmin.value())

    @pyqtSlot()
    def on_actionAbout_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError

    @pyqtSlot()
    def on_actionAbout_Qt_triggered(self):
        """
        Slot documentation goes here.
        """
        QApplication.aboutQt()
