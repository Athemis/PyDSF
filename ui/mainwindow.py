# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

VERSION = "1.0"

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QMainWindow, QMessageBox, QFileDialog, QApplication, QProgressBar

from .Ui_mainwindow import Ui_MainWindow
from pydsf import *

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
        
    
    @pyqtSignature("QAbstractButton*")
    def on_buttonBox_open_clicked(self, button):
        """
        Slot documentation goes here.
        """
        filenames = QFileDialog.getOpenFileNames(self, 'Open data file', '',  "Text files (*.txt *.csv)")
        self.listWidget_data.addItems(filenames)
        if self.listWidget_data.count() > 1:
            self.groupBox_replicates.setChecked(True)
            self.radioButton_rep_files.setEnabled(True)
#            self.radioButton_rep_rows.setEnabled(False)
#            self.radioButton_rep_columns.setEnabled(False)

    
    @pyqtSignature("QString")
    def on_comboBox_instrument_currentIndexChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if p0 == 'Analytik Jena qTOWER 2.0/2.2':
            print(p0)
            self.groupBox_temp.setEnabled(True)
        else:
            self.groupBox_temp.setEnabled(False)
#        self.groupBox_data.setEnabled(True)
#        self.groupBox_cutoff.setEnabled(True)
#        self.groupBox_cbar.setEnabled(True)
#        self.groupBox_signal_threshold.setEnabled(True)

    @pyqtSignature("")
    def on_buttonBox_process_accepted(self):
        """
        Slot documentation goes here.
        """
        if self.listWidget_data.count() < 1:
            QMessageBox.critical(self, 'Error', "No data file loaded!", QMessageBox.Close, QMessageBox.Close)
            return
        if self.spinBox_signal_threshold.value() == 0 and self.groupBox_signal_threshold.isChecked():
            QMessageBox.warning(self, 'Warning', "Signal threshold is currently set to zero.", QMessageBox.Ok, QMessageBox.Ok)
    
        self.pb = QProgressBar()
        c_lower = None
        c_upper = None
        cbar_range = None
        signal_threshold = None
        type = self.comboBox_instrument.currentText()
        if self.groupBox_cutoff.isChecked():
            c_lower = self.doubleSpinBox_lower.value()
            c_upper = self.doubleSpinBox_upper.value()
        if self.groupBox_cbar.isChecked():
            cbar_range = (self.doubleSpinBox_cbar_start,  self.doubleSpinBox_cbar_end)
        if self.groupBox_signal_threshold.isChecked():
            signal_threshold = self.spinBox_signal_threshold.value()
            
        items = (self.listWidget_data.item(i) for i in xrange(self.listWidget_data.count()))
        
        files = []
        for item in items:
            files.append(item.text())
        exp = Experiment(type=type, files=files, t1=self.doubleSpinBox_tmin.value(), t2=self.doubleSpinBox_tmax.value(), dt=self.doubleSpinBox_dt.value(), cols=12, rows=8,  cutoff_low=c_lower,  cutoff_high=c_upper,  signal_threshold=signal_threshold,  color_range=cbar_range)
        exp.analyze()
            
        # plate = Plate(type=type, filename=self.lineEdit_data_file.text(), t1=self.doubleSpinBox_tmin.value(), t2=self.doubleSpinBox_tmax.value(), dt=self.doubleSpinBox_dt.value(), cols=12, rows=8,  cutoff_low=c_lower,  cutoff_high=c_upper,  signal_threshold=signal_threshold,  color_range=cbar_range)
        # self.statusBar.addWidget(self.pb, 100)
        #plate.analyze(gui=self)
        save_data = QMessageBox.question(self, 'Save data', "Calculations are finished. Save results?", 
                                         QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        if save_data == QMessageBox.Yes: 
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.Directory)
            folder = dialog.getExistingDirectory(self, 'Choose path for results')
            for plate in exp.plates:
                plate.write_tm_table('{}/plate_{}_04_tm.csv'.format(folder,  str(plate.id)))
                plate.write_derivative_table('{}/plate_{}_03_dI_dT.csv'.format(folder,  str(plate.id)))
                plate.write_filtered_table('{}/plate_{}_02_filtered_data.csv'.format(folder,  str(plate.id)))
                plate.write_raw_table('{}/plate_{}_01_raw_data.csv'.format(folder,  str(plate.id)))
            
            if exp.avg_plate:
                exp.avg_plate.write_avg_tm_table('{}/plate_{}_05_tm_avg.csv'.format(folder,  str(exp.avg_plate.id)))
            #plot(plate, self)
            
        plot(exp)
        
    
    @pyqtSignature("")
    def on_buttonBox_process_rejected(self):
        """
        Slot documentation goes here.
        """
        QApplication.quit()
    
    @pyqtSignature("")
    def on_actionQuit_triggered(self):
        """
        Slot documentation goes here.
        """
        QApplication.quit()
    
    @pyqtSignature("bool")
    def on_groupBox_cutoff_toggled(self, p0):
        """
        Slot documentation goes here.
        """
        self.doubleSpinBox_upper.setValue(self.doubleSpinBox_tmax.value())
        self.doubleSpinBox_lower.setValue(self.doubleSpinBox_tmin.value())
    
    @pyqtSignature("")
    def on_actionAbout_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        raise NotImplementedError
    
    @pyqtSignature("")
    def on_actionAbout_Qt_triggered(self):
        """
        Slot documentation goes here.
        """
        QApplication.aboutQt()
