# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import (pyqtSlot, QObject, pyqtSignal, QThreadPool,
                          QRunnable, QCoreApplication)
from PyQt5.QtWidgets import (QMainWindow, QProgressBar, QDialogButtonBox,
                             QFileDialog, QMessageBox, QApplication,
                             QTableWidget, QTableWidgetItem)

from .Ui_mainwindow import Ui_MainWindow
from .mplwidget import MplWidget
from pydsf import Experiment, PlotResults
import os

VERSION = "1.0"
_translate = QCoreApplication.translate


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
            cbar_range = (self.owner.doubleSpinBox_cbar_start,
                          self.owner.doubleSpinBox_cbar_end)
        if self.owner.groupBox_signal_threshold.isChecked():
            signal_threshold = self.owner.spinBox_signal_threshold.value()

        items = (self.owner.listWidget_data.item(i)
                 for i in range(self.owner.listWidget_data.count()))

        files = []
        for item in items:
            files.append(item.text())
        self.exp = Experiment(exp_type=instrument_type,
                              files=files,
                              t1=self.owner.doubleSpinBox_tmin.value(),
                              t2=self.owner.doubleSpinBox_tmax.value(),
                              dt=self.owner.doubleSpinBox_dt.value(),
                              cols=12,
                              rows=8,
                              cutoff_low=c_lower,
                              cutoff_high=c_upper,
                              signal_threshold=signal_threshold,
                              color_range=cbar_range)
        self.exp.analyze()
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
        self.statusBar.showMessage(_translate("MainWindow",
                                              "Welcome to PyDSF"))

        self.buttonBox_process.addButton(
            _translate("MainWindow", "&Start Processing"),
            QDialogButtonBox.AcceptRole)

        self.tasks = Tasks()
        self.worker = Worker(self)

        self.outputPath = None

    @pyqtSlot("QAbstractButton*")
    def on_buttonBox_open_reset_clicked(self, button):
        """
        Slot documentation goes here.
        """
        if button == self.buttonBox_open_reset.button(QDialogButtonBox.Open):
            filenames = QFileDialog.getOpenFileNames(
                self,
                _translate("MainWindow", "Open data file"), '',
                _translate("MainWindow", "Text files (*.txt *.csv)"))
            self.listWidget_data.addItems(filenames[0])
            if self.listWidget_data.count() > 1:
                self.groupBox_replicates.setChecked(True)
                self.radioButton_rep_files.setEnabled(True)
        elif button == self.buttonBox_open_reset.button(
                QDialogButtonBox.Reset):
            self.listWidget_data.clear()

    @pyqtSlot("QAbstractButton*")
    def on_buttonBox_output_clicked(self, button):
        if button == self.buttonBox_output.button(QDialogButtonBox.Open):
            path = QFileDialog.getExistingDirectory(parent=self, caption=_translate(
                'MainWindow', 'Choose output path'), options=QFileDialog.ShowDirsOnly)
            self.lineEdit_output.setText(path.strip())

    @pyqtSlot("QString")
    def on_comboBox_instrument_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if p0 == 'Analytik Jena qTOWER 2.0/2.2':
            self.groupBox_temp.setEnabled(True)
        else:
            self.groupBox_temp.setEnabled(False)

    def generate_plot_tab(self, name):
        tab = MplWidget(parent=self.tabWidget)
        tab.setObjectName(name)
        return tab

    def remove_plate_tabs(self):
        for i in range(self.tabWidget.count()):
            try:
                widget = self.tabWidget.widget(i)
                widget.deleteLater()
            except IndexError:
                pass
        self.tabWidget.clear()

    def generate_plate_tabs(self, plate):
        plotter = PlotResults()

        if plate.id != 'average':
            tab = self.generate_plot_tab("tab_heatmap_{}".format(plate.id))
            title = _translate("MainWindow", "Heatmap #")
            self.tabWidget.addTab(tab, title + str(plate.id))
            plotter.plot_tm_heatmap_single(plate, tab)
            if self.checkBox_saveplots.isChecked():
                tab.canvas.save(
                    "{}/heatmap_{}.svg".format(self.outputPath, plate.id))

            tab = self.generate_plot_tab("tab_raw_{}".format(plate.id))
            title = _translate("MainWindow", "Raw Data #")
            self.tabWidget.addTab(tab, title + str(plate.id))
            plotter.plot_raw(plate, tab)
            if self.checkBox_saveplots.isChecked():
                tab.canvas.save(
                    "{}/raw_{}.svg".format(self.outputPath, plate.id))

            tab = self.generate_plot_tab("tab_derivative_{}".format(plate.id))
            title = _translate("MainWindow", "Derivatives #")
            self.tabWidget.addTab(tab, title + str(plate.id))
            plotter.plot_derivative(plate, tab)
            if self.checkBox_saveplots.isChecked():
                tab.canvas.save(
                    "{}/derivatives_{}.svg".format(self.outputPath, plate.id))
        else:
            tab = self.generate_plot_tab("tab_heatmap_{}".format(plate.id))
            title = _translate("MainWindow", "Heatmap ")
            self.tabWidget.addTab(tab, title + str(plate.id))
            plotter.plot_tm_heatmap_single(plate, tab)
            if self.checkBox_saveplots.isChecked():
                tab.canvas.save(
                    "{}/heatmap_{}.svg".format(self.outputPath, plate.id))

    @pyqtSlot()
    def on_buttonBox_process_accepted(self):
        """
        Slot documentation goes here.
        """

        if self.listWidget_data.count() < 1:
            QMessageBox.critical(
                self, _translate("MainWindow", "Error"),
                _translate("MainWindow", "No data file loaded!"),
                QMessageBox.Close, QMessageBox.Close)
            return
        if self.groupBox_output.isChecked() and self.lineEdit_output.text().strip() == '':
            QMessageBox.critical(
                self, _translate("MainWindow", "Error"),
                _translate("MainWindow", "No output path set!"),
                QMessageBox.Close, QMessageBox.Close)
            return
        elif self.groupBox_output.isChecked() and self.lineEdit_output.text().strip() != '':
            path = self.lineEdit_output.text().strip()
            if os.path.isdir(path):
                self.outputPath = self.lineEdit_output.text().strip()
            else:
                QMessageBox.critical(
                    self, _translate("MainWindow", "Error"),
                    _translate("MainWindow", "Output path does not exist!"),
                    QMessageBox.Close, QMessageBox.Close)

        if self.spinBox_signal_threshold.value(
        ) == 0 and self.groupBox_signal_threshold.isChecked():
            QMessageBox.warning(
                self, _translate("MainWindow", "Warning"),
                _translate(
                    "MainWindow",
                    "Signal threshold is currently set to zero."),
                QMessageBox.Ok, QMessageBox.Ok)

        self.remove_plate_tabs()
        self.progressBar.setEnabled(True)
        self.statusBar.showMessage(_translate("MainWindow", "Processing..."))

        self.tasks.signals.finished.connect(self.on_processing_finished)
        self.tasks.add_task(self.worker)
        self.tasks.start()

    @pyqtSlot()
    def on_processing_finished(self):
        # For now, only read the first entry
        exp = self.tasks.data[0]

        for i in range(len(self.worker.exp.plates)):

            plate = exp.plates[i]
            self.generate_plate_tabs(plate)

        if exp.avg_plate:

            plate = exp.avg_plate
            self.generate_plate_tabs(plate)

        if self.groupBox_output.isChecked():
            if self.checkBox_savetables.isChecked():
                for plate in exp.plates:
                    plate.write_tm_table(
                        '{}/plate_{}_tm.csv'.format(self.outputPath, str(plate.id)))
                    plate.write_data_table(
                        '{}/plate_{}_dI_dT.csv'.format(self.outputPath, str(plate.id)), dataType='derivative')
                    plate.write_data_table(
                        '{}/plate_{}_filtered_data.csv'.format(self.outputPath,
                                                               str(plate.id)), dataType='filtered')
                    plate.write_data_table('{}/plate_{}_raw_data.csv'.format(
                        self.outputPath, str(plate.id)))

                if exp.avg_plate:
                    exp.avg_plate.write_tm_table(
                        '{}/plate_{}_tm_avg.csv'.format(
                            self.outputPath, str(self.worker.exp.avg_plate.id)), avg=True)

        self.progressBar.setEnabled(False)
        self.statusBar.showMessage(_translate("MainWindow", "Finished!"))

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
    def on_groupBox_cutoff_toggled(self):
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
