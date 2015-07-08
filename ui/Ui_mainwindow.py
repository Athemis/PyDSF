# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1066, 795)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setOpaqueResize(False)
        self.splitter.setHandleWidth(2)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")
        self.groupBox_experiment = QtWidgets.QGroupBox(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_experiment.sizePolicy().hasHeightForWidth())
        self.groupBox_experiment.setSizePolicy(sizePolicy)
        self.groupBox_experiment.setMinimumSize(QtCore.QSize(100, 300))
        self.groupBox_experiment.setSizeIncrement(QtCore.QSize(0, 0))
        self.groupBox_experiment.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_experiment.setFlat(False)
        self.groupBox_experiment.setCheckable(False)
        self.groupBox_experiment.setObjectName("groupBox_experiment")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox_experiment)
        self.formLayout_3.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_instrument = QtWidgets.QLabel(self.groupBox_experiment)
        self.label_instrument.setObjectName("label_instrument")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_instrument)
        self.comboBox_instrument = QtWidgets.QComboBox(self.groupBox_experiment)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_instrument.sizePolicy().hasHeightForWidth())
        self.comboBox_instrument.setSizePolicy(sizePolicy)
        self.comboBox_instrument.setObjectName("comboBox_instrument")
        self.comboBox_instrument.addItem("")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_instrument)
        self.groupBox_data = QtWidgets.QGroupBox(self.groupBox_experiment)
        self.groupBox_data.setEnabled(True)
        self.groupBox_data.setObjectName("groupBox_data")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_data)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.buttonBox_open_reset = QtWidgets.QDialogButtonBox(self.groupBox_data)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox_open_reset.sizePolicy().hasHeightForWidth())
        self.buttonBox_open_reset.setSizePolicy(sizePolicy)
        self.buttonBox_open_reset.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox_open_reset.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox_open_reset.setStandardButtons(QtWidgets.QDialogButtonBox.Open|QtWidgets.QDialogButtonBox.Reset)
        self.buttonBox_open_reset.setCenterButtons(False)
        self.buttonBox_open_reset.setObjectName("buttonBox_open_reset")
        self.gridLayout_4.addWidget(self.buttonBox_open_reset, 0, 1, 1, 1)
        self.groupBox_replicates = QtWidgets.QGroupBox(self.groupBox_data)
        self.groupBox_replicates.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_replicates.setCheckable(True)
        self.groupBox_replicates.setChecked(False)
        self.groupBox_replicates.setObjectName("groupBox_replicates")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_replicates)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.radioButton_rep_files = QtWidgets.QRadioButton(self.groupBox_replicates)
        self.radioButton_rep_files.setEnabled(False)
        self.radioButton_rep_files.setChecked(True)
        self.radioButton_rep_files.setObjectName("radioButton_rep_files")
        self.gridLayout_3.addWidget(self.radioButton_rep_files, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_replicates, 2, 0, 1, 2)
        self.listWidget_data = QtWidgets.QListWidget(self.groupBox_data)
        self.listWidget_data.setAlternatingRowColors(True)
        self.listWidget_data.setObjectName("listWidget_data")
        self.gridLayout_4.addWidget(self.listWidget_data, 0, 0, 2, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 1, 1, 1, 1)
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.groupBox_data)
        self.groupBox_processing = QtWidgets.QGroupBox(self.groupBox_experiment)
        self.groupBox_processing.setObjectName("groupBox_processing")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_processing)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_temp = QtWidgets.QGroupBox(self.groupBox_processing)
        self.groupBox_temp.setEnabled(True)
        self.groupBox_temp.setAutoFillBackground(False)
        self.groupBox_temp.setCheckable(False)
        self.groupBox_temp.setObjectName("groupBox_temp")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_temp)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.formLayout.setObjectName("formLayout")
        self.label_tmin = QtWidgets.QLabel(self.groupBox_temp)
        self.label_tmin.setObjectName("label_tmin")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_tmin)
        self.doubleSpinBox_tmin = QtWidgets.QDoubleSpinBox(self.groupBox_temp)
        self.doubleSpinBox_tmin.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox_tmin.setDecimals(1)
        self.doubleSpinBox_tmin.setProperty("value", 20.0)
        self.doubleSpinBox_tmin.setObjectName("doubleSpinBox_tmin")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_tmin)
        self.label_tmax = QtWidgets.QLabel(self.groupBox_temp)
        self.label_tmax.setObjectName("label_tmax")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_tmax)
        self.doubleSpinBox_tmax = QtWidgets.QDoubleSpinBox(self.groupBox_temp)
        self.doubleSpinBox_tmax.setDecimals(1)
        self.doubleSpinBox_tmax.setProperty("value", 95.0)
        self.doubleSpinBox_tmax.setObjectName("doubleSpinBox_tmax")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_tmax)
        self.label_dt = QtWidgets.QLabel(self.groupBox_temp)
        self.label_dt.setObjectName("label_dt")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_dt)
        self.doubleSpinBox_dt = QtWidgets.QDoubleSpinBox(self.groupBox_temp)
        self.doubleSpinBox_dt.setDecimals(1)
        self.doubleSpinBox_dt.setProperty("value", 1.0)
        self.doubleSpinBox_dt.setObjectName("doubleSpinBox_dt")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_dt)
        self.gridLayout.addWidget(self.groupBox_temp, 0, 0, 1, 1)
        self.groupBox_cutoff = QtWidgets.QGroupBox(self.groupBox_processing)
        self.groupBox_cutoff.setEnabled(True)
        self.groupBox_cutoff.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_cutoff.setCheckable(True)
        self.groupBox_cutoff.setChecked(False)
        self.groupBox_cutoff.setObjectName("groupBox_cutoff")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_cutoff)
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout_2.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_cutoff_high = QtWidgets.QLabel(self.groupBox_cutoff)
        self.label_cutoff_high.setObjectName("label_cutoff_high")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_cutoff_high)
        self.doubleSpinBox_upper = QtWidgets.QDoubleSpinBox(self.groupBox_cutoff)
        self.doubleSpinBox_upper.setPrefix("")
        self.doubleSpinBox_upper.setDecimals(1)
        self.doubleSpinBox_upper.setObjectName("doubleSpinBox_upper")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_upper)
        self.label_cutoff_low = QtWidgets.QLabel(self.groupBox_cutoff)
        self.label_cutoff_low.setObjectName("label_cutoff_low")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_cutoff_low)
        self.doubleSpinBox_lower = QtWidgets.QDoubleSpinBox(self.groupBox_cutoff)
        self.doubleSpinBox_lower.setDecimals(1)
        self.doubleSpinBox_lower.setObjectName("doubleSpinBox_lower")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_lower)
        self.gridLayout.addWidget(self.groupBox_cutoff, 0, 1, 1, 1)
        self.groupBox_signal_threshold = QtWidgets.QGroupBox(self.groupBox_processing)
        self.groupBox_signal_threshold.setEnabled(True)
        self.groupBox_signal_threshold.setCheckable(True)
        self.groupBox_signal_threshold.setChecked(False)
        self.groupBox_signal_threshold.setObjectName("groupBox_signal_threshold")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_signal_threshold)
        self.verticalLayout.setObjectName("verticalLayout")
        self.spinBox_signal_threshold = QtWidgets.QSpinBox(self.groupBox_signal_threshold)
        self.spinBox_signal_threshold.setMaximum(1000000)
        self.spinBox_signal_threshold.setObjectName("spinBox_signal_threshold")
        self.verticalLayout.addWidget(self.spinBox_signal_threshold)
        self.gridLayout.addWidget(self.groupBox_signal_threshold, 1, 0, 1, 1)
        self.groupBox_cbar = QtWidgets.QGroupBox(self.groupBox_processing)
        self.groupBox_cbar.setEnabled(True)
        self.groupBox_cbar.setCheckable(True)
        self.groupBox_cbar.setChecked(False)
        self.groupBox_cbar.setObjectName("groupBox_cbar")
        self.formLayout_4 = QtWidgets.QFormLayout(self.groupBox_cbar)
        self.formLayout_4.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label_cbar_start = QtWidgets.QLabel(self.groupBox_cbar)
        self.label_cbar_start.setObjectName("label_cbar_start")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_cbar_start)
        self.doubleSpinBox_cbar_start = QtWidgets.QDoubleSpinBox(self.groupBox_cbar)
        self.doubleSpinBox_cbar_start.setDecimals(1)
        self.doubleSpinBox_cbar_start.setObjectName("doubleSpinBox_cbar_start")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_cbar_start)
        self.label_cbar_end = QtWidgets.QLabel(self.groupBox_cbar)
        self.label_cbar_end.setObjectName("label_cbar_end")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_cbar_end)
        self.doubleSpinBox_cbar_end = QtWidgets.QDoubleSpinBox(self.groupBox_cbar)
        self.doubleSpinBox_cbar_end.setDecimals(1)
        self.doubleSpinBox_cbar_end.setObjectName("doubleSpinBox_cbar_end")
        self.formLayout_4.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_cbar_end)
        self.gridLayout.addWidget(self.groupBox_cbar, 1, 1, 1, 1)
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.groupBox_processing)
        self.buttonBox_process = QtWidgets.QDialogButtonBox(self.groupBox_experiment)
        self.buttonBox_process.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        self.buttonBox_process.setObjectName("buttonBox_process")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.buttonBox_process)
        self.groupBox_results = QtWidgets.QGroupBox(self.splitter)
        self.groupBox_results.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(6)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_results.sizePolicy().hasHeightForWidth())
        self.groupBox_results.setSizePolicy(sizePolicy)
        self.groupBox_results.setSizeIncrement(QtCore.QSize(0, 0))
        self.groupBox_results.setObjectName("groupBox_results")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_results)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.groupBox_results)
        self.tabWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 300))
        self.tabWidget.setSizeIncrement(QtCore.QSize(0, 0))
        self.tabWidget.setObjectName("tabWidget")
        self.horizontalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1066, 28))
        self.menuBar.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout_Qt = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/qtlogo.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout_Qt.setIcon(icon)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.label_instrument.setBuddy(self.comboBox_instrument)
        self.label_tmin.setBuddy(self.doubleSpinBox_tmin)
        self.label_tmax.setBuddy(self.doubleSpinBox_tmax)
        self.label_dt.setBuddy(self.doubleSpinBox_dt)
        self.label_cutoff_high.setBuddy(self.doubleSpinBox_upper)
        self.label_cutoff_low.setBuddy(self.doubleSpinBox_lower)
        self.label_cbar_start.setBuddy(self.doubleSpinBox_cbar_start)
        self.label_cbar_end.setBuddy(self.doubleSpinBox_cbar_end)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PyDSF"))
        self.groupBox_experiment.setTitle(_translate("MainWindow", "Experimental Setup"))
        self.label_instrument.setText(_translate("MainWindow", "Instrument"))
        self.comboBox_instrument.setItemText(0, _translate("MainWindow", "Analytik Jena qTOWER 2.0/2.2"))
        self.groupBox_data.setToolTip(_translate("MainWindow", "<html><head/><body><p>Add data files to the experiment. If multiple files are loaded, they are treated as replicates.</p></body></html>"))
        self.groupBox_data.setTitle(_translate("MainWindow", "Data File"))
        self.groupBox_replicates.setTitle(_translate("MainWindow", "Replicates"))
        self.radioButton_rep_files.setText(_translate("MainWindow", "Files"))
        self.groupBox_processing.setTitle(_translate("MainWindow", "Processing Options"))
        self.groupBox_temp.setToolTip(_translate("MainWindow", "<html><head/><body><p>Temperature range of the data points. Only applies, if the data file does not contain any temperature information.</p></body></html>"))
        self.groupBox_temp.setTitle(_translate("MainWindow", "Temperature settings"))
        self.label_tmin.setText(_translate("MainWindow", "<html><head/><body><p>T<span style=\" vertical-align:sub;\">min</span></p></body></html>"))
        self.doubleSpinBox_tmin.setSuffix(_translate("MainWindow", " °C"))
        self.label_tmax.setText(_translate("MainWindow", "<html><head/><body><p>T<span style=\" vertical-align:sub;\">max</span></p></body></html>"))
        self.doubleSpinBox_tmax.setSuffix(_translate("MainWindow", " °C"))
        self.label_dt.setText(_translate("MainWindow", "<html><head/><body><p>&Delta;T</p></body></html>"))
        self.doubleSpinBox_dt.setSuffix(_translate("MainWindow", " °C"))
        self.groupBox_cutoff.setToolTip(_translate("MainWindow", "<html><head/><body><p>Only T<span style=\" vertical-align:sub;\">m</span> values within this limit are considered valid.</p></body></html>"))
        self.groupBox_cutoff.setTitle(_translate("MainWindow", "&Cutoff"))
        self.label_cutoff_high.setText(_translate("MainWindow", "&Upper"))
        self.doubleSpinBox_upper.setSuffix(_translate("MainWindow", " °C"))
        self.label_cutoff_low.setText(_translate("MainWindow", "Lower"))
        self.doubleSpinBox_lower.setSuffix(_translate("MainWindow", " °C"))
        self.groupBox_signal_threshold.setToolTip(_translate("MainWindow", "<html><head/><body><p>If the signal exceeds this threshold, the coresponding well is assumed to be denatured.</p></body></html>"))
        self.groupBox_signal_threshold.setTitle(_translate("MainWindow", "Signal &Threshold"))
        self.groupBox_cbar.setToolTip(_translate("MainWindow", "<html><head/><body><p>Defines the range of the colorbar used for the T<span style=\" vertical-align:sub;\">m</span> heatmap.</p></body></html>"))
        self.groupBox_cbar.setTitle(_translate("MainWindow", "&Colorbar"))
        self.label_cbar_start.setText(_translate("MainWindow", "S&tart"))
        self.doubleSpinBox_cbar_start.setSuffix(_translate("MainWindow", " °C"))
        self.label_cbar_end.setText(_translate("MainWindow", "En&d"))
        self.doubleSpinBox_cbar_end.setSuffix(_translate("MainWindow", " °C"))
        self.groupBox_results.setTitle(_translate("MainWindow", "Plots"))
        self.menuFile.setTitle(_translate("MainWindow", "Fi&le"))
        self.menuHelp.setTitle(_translate("MainWindow", "Hel&p"))
        self.actionQuit.setText(_translate("MainWindow", "&Quit"))
        self.actionAbout.setText(_translate("MainWindow", "&About"))
        self.actionAbout_Qt.setText(_translate("MainWindow", "About &Qt"))

