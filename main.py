#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import glob
from PyQt5 import QtWidgets, QtCore

from ui.mainwindow import MainWindow


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    translationFiles = glob.glob("i18n/*.qm")
    translator = QtCore.QTranslator()
    for translationFile in translationFiles:
        translator.load(translationFile)
        app.installTranslator(translator)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
