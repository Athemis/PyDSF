#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import glob
from PyQt5 import QtWidgets, QtCore

from ui.mainwindow import MainWindow


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    # get system locale
    systemLocale = QtCore.QLocale.system().name()
    translationFile = "i18n/{}".format(systemLocale)
    # load translation file and install translator
    translator.load(translationFile)
    app.installTranslator(translator)
    # fire up main ui
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
