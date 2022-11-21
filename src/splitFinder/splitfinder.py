#!/usr/bin/env python
# coding: utf-8

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import  QMessageBox, QLineEdit, QInputDialog, QTableWidgetItem, QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from src.splitFinder.splitfinder_ui import Ui_splitFinder

import matplotlib
matplotlib.use('qt5agg')

from src.splitFinder.isotopes import find_split


class Splitfinder(QtWidgets.QMainWindow):
    """ This class is the main application """

    USERDATA_ROLE = QtCore.Qt.UserRole

    def __init__(self):
        """ Set up the class from ... """

        # initialize from super class
        super().__init__()
        self.setWindowTitle("Isotope Finder")
        self.setWindowIcon(QtGui.QIcon("Py2MC_icon.png"))
        
        
        self.ui = Ui_splitFinder()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # NO TITLE BAR
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        
        # connection ui <=> functions
        widgets.pushButton_start_isotopinator.clicked.connect(self.star_button_function)
        widgets.list_split_name.clicked.connect(self.select_change_split)
        widgets.list_range.clicked.connect(self.select_change_range)
        widgets.closeAppBtn.clicked.connect(lambda: self.close())
        widgets.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())
        
        
        def moveWindow(event):
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()    
        widgets.titleRightInfo.mouseMoveEvent = moveWindow
      
    def mousePressEvent(self, event):
        """
        SET DRAG POS WINDOW
        """
        self.dragPos = event.globalPos()
            
    def star_button_function(self):
        """ button to look for isotopes split """

        # clear current list
        widgets.list_split_name.clear()
        widgets.list_range.clear()

        # teste si le champ est vide ?
        # chez moi ça ne marche pas. Si j'écris rien dans le champs ça plante
        try:
            requested_split = float(widgets.requested_split.text())
        except:
            QMessageBox.about(self, "Error", "Split mass not entered")
        try:
            tolerance = float(widgets.precision.text())
        except:
            QMessageBox.about(self, "Error", "Tolerance mass not entered")

        candidates, min_idx = find_split(requested_split, tolerance)
        for name, error in candidates:
            widgets.list_split_name.addItem(QtWidgets.QListWidgetItem(name))
            widgets.list_range.addItem(f"{error:.7f}")
        
        if len(candidates) >= 1:
            widgets.list_range.item(min_idx).setBackground(QtGui.QColor('#FFFF06'))
            widgets.list_split_name.item(min_idx).setBackground(QtGui.QColor('#FFFF06'))
        elif len(candidates) == 0:
            widgets.list_split_name.addItem("None")
            widgets.list_range.addItem("None")
            
    def select_change_split(self):
        i = widgets.list_split_name.currentIndex().row()
        widgets.list_range.item(i).setSelected(True)

    def select_change_range(self):
        i = widgets.list_range.currentIndex().row()
        widgets.list_split_name.item(i).setSelected(True)

if __name__ == "__main__":
     app = QtWidgets.QApplication([])
     main = Splitfinder()
     main.show()
     app.exec()       