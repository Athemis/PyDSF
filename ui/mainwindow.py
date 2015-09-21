# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
"""
from PyQt5.QtCore import (pyqtSlot, QObject, pyqtSignal, QThreadPool,
                          QRunnable, QCoreApplication)
from PyQt5.QtWidgets import (QMainWindow, QProgressBar, QDialogButtonBox,
                             QFileDialog, QMessageBox, QApplication, QDialog)

from .Ui_mainwindow import Ui_MainWindow
from .Ui_dialogabout import Ui_DialogAbout
from .mplwidget import MplWidget
from pydsf import Experiment, PlotResults
import os

# Import available instruments
try:
    from instruments.analytikJenaqTower2 import AnalytikJenaqTower2
except ImportError as err:
    raise ImportError('Error while loading instrument plugins:', err)

VERSION = "1.0"
_translate = QCoreApplication.translate


class WorkerSignals(QObject):

    finished = pyqtSignal()


class Worker(QRunnable):
    finished = pyqtSignal(int)

    def __init__(self, owner):
        super().__init__()
        self.exp = None
        self.owner = owner
        self.signals = WorkerSignals()

    def run(self):
        c_lower = None
        c_upper = None
        cbar_range = None
        signal_threshold = None
        if self.owner.groupBox_cutoff.isChecked():
            c_lower = self.owner.doubleSpinBox_lower.value()
            c_upper = self.owner.doubleSpinBox_upper.value()
        if self.owner.groupBox_cbar.isChecked():
            cbar_range = (self.owner.doubleSpinBox_cbar_start.value(),
                          self.owner.doubleSpinBox_cbar_end.value())
        if self.owner.groupBox_signal_threshold.isChecked():
            signal_threshold = self.owner.spinBox_signal_threshold.value()

        items = (self.owner.listWidget_data.item(i)
                 for i in range(self.owner.listWidget_data.count()))

        files = []
        for item in items:
            files.append(item.text())

        replicates = self.owner.groupBox_replicates.isChecked()
        row_replicates = self.owner.radioButton_rep_rows.isChecked()

        if replicates and row_replicates:
            average_rows = self.owner.spinBox_avg_rows.value()
        else:
            average_rows = None

        self.exp = Experiment(instrument=self.owner.instrument,
                              files=files,
                              t1=self.owner.doubleSpinBox_tmin.value(),
                              t2=self.owner.doubleSpinBox_tmax.value(),
                              dt=self.owner.doubleSpinBox_dt.value(),
                              cols=12,
                              rows=8,
                              cutoff_low=c_lower,
                              cutoff_high=c_upper,
                              signal_threshold=signal_threshold,
                              color_range=cbar_range,
                              concentrations=self.owner.concentrations,
                              average_rows=average_rows)
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

    def remove_task(self, task):
        self.tasks.remove(task)

    def clear(self):
        self.tasks.clear()

    def get_data(self):
        self.pool.waitForDone()
        return self.data

    def clear_data(self):
        self.data = []

    def start(self):
        for task in self.tasks:
            self.pool.start(task)
        self.pool.waitForDone()

        for task in self.tasks:
            self.data.append(task.exp)
            self.remove_task(task)

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
        self.tasks.signals.finished.connect(self.on_processing_finished)
        self.lineEdit_conc.textChanged.connect(
            self.on_lineEdit_conc_textChanged)
        self.worker = None
        self.outputPath = None
        self.concentrations = None
        self.populateInstrumentList()
        self.instrument = self.getSelectedInstrument()

    def populateInstrumentList(self):
        self.instruments = [AnalytikJenaqTower2()]
        for i in range(len(self.instruments)):
            instrument = self.instruments[i]
            self.comboBox_instrument.setItemText(i, instrument.name)

    @pyqtSlot()
    def getInstrumentFromName(self, name):
        for instrument in self.instruments:
            if instrument.name == name:
                return instrument
        raise IndexError("Requested instrument not")

    def getSelectedInstrument(self):
        name = str(self.comboBox_instrument.currentText())
        instrument = self.getInstrumentFromName(name)
        return instrument

    @pyqtSlot("QAbstractButton*")
    def on_buttonBox_open_reset_clicked(self, button):
        """
        Triggered when either the open or reset button in the data file
        dialog is clicked. Spawns an open file dialog or resets the listview.
        """
        if button == self.buttonBox_open_reset.button(QDialogButtonBox.Open):
            filenames = QFileDialog.getOpenFileNames(
                self, _translate("MainWindow", "Open data file"), '',
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
            caption = _translate('MainWindow', 'Choose output path')
            path = QFileDialog.getExistingDirectory(
                parent=self,
                caption=caption,
                options=QFileDialog.ShowDirsOnly)
            self.lineEdit_output.setText(path.strip())

    @pyqtSlot("QString")
    def on_comboBox_instrument_currentIndexChanged(self, p0):
        """
        Triggered when another instrument is selected from the combobox.
        """
        self.instrument = self.getInstrumentFromName(p0)
        if self.instrument.providesTempRange:
            self.groupBox_temp.setEnabled(False)
        else:
            self.groupBox_temp.setEnabled(True)

    def generate_plot_tab(self, name, mouse_event=False):
        if mouse_event:
            tab = MplWidget(parent=self.tabWidget, mouse_event=True)
        else:
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
            tab = self.generate_plot_tab("tab_heatmap_{}".format(plate.id),
                                         mouse_event=True)
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

            if self.groupBox_conc.isChecked():
                tab = self.generate_plot_tab("tab_derivative_{}".format(
                    plate.id))
                title = _translate("MainWindow", "Parameter Dependency #")
                self.tabWidget.addTab(tab, title + str(plate.id))
                if self.lineEdit_par_label.text():
                    par_label = self.lineEdit_par_label.text()
                    plotter.plot_concentration_dependency(
                        plate,
                        tab,
                        parameter_label=par_label)
                else:
                    plotter.plot_concentration_dependency(plate, tab)
                if self.checkBox_saveplots.isChecked():
                    tab.canvas.save(
                        "{}/para_{}.svg".format(self.outputPath, plate.id))
        else:
            tab = self.generate_plot_tab("tab_heatmap_{}".format(plate.id),
                                         mouse_event=True)
            title = _translate("MainWindow", "Heatmap ")
            self.tabWidget.addTab(tab, title + str(plate.id))
            plotter.plot_tm_heatmap_single(plate, tab)
            if self.checkBox_saveplots.isChecked():
                tab.canvas.save(
                    "{}/heatmap_{}.svg".format(self.outputPath, plate.id))

            if self.groupBox_conc.isChecked():
                tab = self.generate_plot_tab("tab_derivative_{}".format(
                    plate.id))
                title = _translate("MainWindow", "Parameter Dependency #")
                self.tabWidget.addTab(tab, title + str(plate.id))
                if self.lineEdit_par_label.text():
                    par_label = self.lineEdit_par_label.text()
                    plotter.plot_concentration_dependency(
                        plate,
                        tab,
                        parameter_label=par_label,
                        error_bars=True)
                else:
                    plotter.plot_concentration_dependency(plate,
                                                          tab,
                                                          error_bars=True)
                if self.checkBox_saveplots.isChecked():
                    tab.canvas.save(
                        "{}/para_{}.svg".format(self.outputPath, plate.id))

    @pyqtSlot()
    def on_buttonBox_process_accepted(self):
        """
        Slot documentation goes here.
        """

        self.remove_plate_tabs()
        self.instrument = self.getSelectedInstrument()

        if self.listWidget_data.count() < 1:
            QMessageBox.critical(
                self, _translate("MainWindow", "Error"),
                _translate("MainWindow", "No data file loaded!"),
                QMessageBox.Close, QMessageBox.Close)
            return
        if self.groupBox_conc.isChecked():
            self.concentrations = self.lineEdit_conc.text().split(',')
        if (self.groupBox_output.isChecked() and
            self.lineEdit_output.text().strip() == ''):
            QMessageBox.critical(
                self, _translate("MainWindow", "Error"),
                _translate("MainWindow", "No output path set!"),
                QMessageBox.Close, QMessageBox.Close)
            return
        elif (self.groupBox_output.isChecked() and
              self.lineEdit_output.text().strip() != ''):
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
                self, _translate("MainWindow", "Warning"), _translate(
                    "MainWindow",
                    "Signal threshold is currently set to zero."),
                QMessageBox.Ok, QMessageBox.Ok)

        self.progressBar.setEnabled(True)
        self.statusBar.showMessage(_translate("MainWindow", "Processing..."))

        self.worker = Worker(self)
        self.tasks.add_task(self.worker)
        self.tasks.start()

    @pyqtSlot()
    def on_processing_finished(self):
        # Clear all jobs from task list
        # self.tasks.clear()
        # For now, only read the first entry
        exp = self.tasks.data[0]
        # clear data in tasks object
        self.tasks.clear_data()

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
                        '{}/plate_{}_tm.csv'.format(self.outputPath, str(
                            plate.id)))
                    plate.write_data_table(
                        '{}/plate_{}_dI_dT.csv'.format(self.outputPath,
                                                       str(plate.id)),
                        dataType='derivative')
                    plate.write_data_table(
                        '{}/plate_{}_filtered_data.csv'.format(self.outputPath,
                                                               str(plate.id)),
                        dataType='filtered')
                    plate.write_data_table('{}/plate_{}_raw_data.csv'.format(
                        self.outputPath, str(plate.id)))

                if exp.avg_plate:
                    exp.avg_plate.write_tm_table(
                        '{}/plate_{}_tm_avg.csv'.format(
                            self.outputPath,
                            str(self.worker.exp.avg_plate.id)),
                        avg=True)

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
        dialog = QDialog()
        dialog.ui = Ui_DialogAbout()
        dialog.ui.setupUi(dialog)
        dialog.exec_()

    @pyqtSlot()
    def on_actionAbout_Qt_triggered(self):
        """
        Slot documentation goes here.
        """
        QApplication.aboutQt()

    @pyqtSlot()
    def on_lineEdit_conc_textChanged(self):
        """
        Slot documentation goes here.
        """
        num_conc = len(self.lineEdit_conc.text().split(','))
        self.spinBox_num_conc.setValue(num_conc)
        if self.comboBox_direction.currentIndex() == 0:
            max_wells = self.instrument.wells_horizontal
        else:
            max_wells = self.instrument.wells_vertical
        if num_conc > max_wells:
            self.spinBox_num_conc.setStyleSheet("QSpinBox { color : red; }")
        else:
            self.spinBox_num_conc.setStyleSheet("QSpinBox { color : black; }")
