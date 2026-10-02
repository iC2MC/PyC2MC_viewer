# ///////////////////////////////////////////////////////////////
#
# ----------------------------------------------------------------
# Written by Julien Maillard, Maxime Sueur, Oscar Lacroix-Andrivet
# Github : https://github.com/iC2MC/PyC2MC_viewer
# -----------------------------------------------------------------------------
#
# //////////////////////////////////////////////////////////////
# IMPORTATION
# //////////////////////////////////////////////////////////////

import os
import pandas
import matplotlib
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import QMessageBox
from modules.pyc2mc_ui import Ui_MainWindow
from modules.ui_functions import UIFunctions

try:
    import pyi_splash

    splash = True
except:
    splash = False
    pass
matplotlib.use("qt5agg")
import matplotlib.pyplot as plt

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


if splash:  # Closing splash
    pyi_splash.close()


from modules.plot_helpers import color_list, plot_fun
from modules.app_functions import AppFunctions
from modules.window_actions import WindowActionsMixin
from modules.file_operations import FileOperationsMixin
from modules.data_views import DataViewsMixin
from modules.plots import PlotsMixin
from modules.comparison import ComparisonMixin
from modules.molecular_maps import MolecularMapsMixin


class MainWindow(
    AppFunctions,
    WindowActionsMixin,
    FileOperationsMixin,
    DataViewsMixin,
    PlotsMixin,
    ComparisonMixin,
    MolecularMapsMixin,
    QtWidgets.QMainWindow,
):

    # role for storing the data frames in the items
    USERDATA_ROLE = QtCore.Qt.UserRole

    def __init__(self):
        super().__init__()

        # SET UP UI
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        # NO TITLE BAR
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        # GET PARAMETERS
        UIFunctions.uiDefinitions(self)

        # Dict of most abundant isotopes and corresponding exact masses

        df = pandas.read_csv("Isotopes.csv", sep=";")
        df.fillna(1, inplace=True)
        self.isotopes_dict = dict(zip(df["Atom"], df["Mass"]))

        def getSettings():

            if QSettings("PyC2MC", "def").value("def") == "false":
                pass

            else:  # Default setting for 1st launch
                self.settingsExit = QSettings("PyC2MC", "ExitConfirm")
                self.settingsExit.setValue("ExitConfirm", "True")

                self.settingsMinimize = QSettings("PyC2MC", "Minimize")
                self.settingsMinimize.setValue("Minimize", "True")

                self.settingsDotSize = QSettings("PyC2MC", "FontSize")
                self.settingsDotSize.setValue("DotSize", "130")

                self.settingsFontSize = QSettings("PyC2MC", "FontSize")
                self.settingsFontSize.setValue("FontSize", "16")

                self.settingsSaveDPI = QSettings("PyC2MC", "SaveDPI")
                self.settingsSaveDPI.setValue("SaveDPI", "300")

                self.settingsFPS = QSettings("PyC2MC", "FPS")
                self.settingsFPS.setValue("FPS", "2")

                self.settingsDotType = QSettings("PyC2MC", "DotType")
                self.settingsDotType.setValue("DotType", "size_and_color")

                self.settingsColormap = QSettings("PyC2MC", "Colormap")
                self.settingsDotType.setValue("Colormap", "viridis")

                self.settingsDotEdge = QSettings("PyC2MC", "Edge")
                self.settingsDotEdge.setValue("Edge", "true")

                self.settingsNormalization = QSettings("PyC2MC", "Normalization")
                self.settingsNormalization.value("Normalization", "all")

                self.settingsdefault = QSettings("PyC2MC", "def")
                self.settingsdefault.setValue("def", "false")

            self.settingsExit = QSettings("PyC2MC", "ExitConfirm")
            if self.settingsExit.value("ExitConfirm") == "true":
                self.ui.btn_confirmClose.setChecked(True)
            else:
                self.ui.btn_confirmClose.setChecked(False)

            self.settingsDotSize = QSettings("PyC2MC", "FontSize")
            self.ui.dot_size.setText(self.settingsDotSize.value("DotSize"))

            self.settingsFontSize = QSettings("PyC2MC", "FontSize")
            self.ui.font_size.setText(self.settingsFontSize.value("FontSize"))

            self.settingsSaveDPI = QSettings("PyC2MC", "SaveDPI")
            self.ui.saveDPI.setText(self.settingsSaveDPI.value("SaveDPI"))

            self.settingsFPS = QSettings("PyC2MC", "FPS")
            self.ui.gif_fps.setText(self.settingsFPS.value("FPS"))

            self.settingsMinimize = QSettings("PyC2MC", "Minimize")
            if self.settingsMinimize.value("Minimize") == "true":
                self.ui.btn_minimizeAuto.setChecked(True)
            else:
                self.ui.btn_minimizeAuto.setChecked(False)

            self.settingsDotType = QSettings("PyC2MC", "DotType")
            if self.settingsDotType.value("DotType") == "size_and_color":
                self.ui.radio_size_and_color.setChecked(True)
            elif self.settingsDotType.value("DotType") == "color":
                self.ui.radio_color.setChecked(True)
            elif self.settingsDotType.value("DotType") == "size":
                self.ui.radio_size.setChecked(True)

            self.settingsColormap = QSettings("PyC2MC", "Colormap")
            [
                self.ui.list_color_map.setCurrentItem(x)
                for x in self.ui.list_color_map.findItems(
                    self.settingsColormap.value("Colormap"), QtCore.Qt.MatchExactly
                )
            ]

            self.settingsDotEdge = QSettings("PyC2MC", "Edge")
            if self.settingsDotEdge.value("Edge") == "true":
                self.ui.CheckBox_edge.setChecked(True)
            else:
                self.ui.CheckBox_edge.setChecked(False)

            self.settingsNormalization = QSettings("PyC2MC", "Normalization")
            if self.settingsNormalization.value("Normalization") == "all":
                self.ui.radioButton_norm_a.setChecked(True)
            elif self.settingsNormalization.value("Normalization") == "selected":
                self.ui.radioButton_norm_c.setChecked(True)
            elif self.settingsNormalization.value("Normalization") == "displayed":
                self.ui.radioButton_norm_d.setChecked(True)

        # SAVE PARAMETERS
        def saveSettings():

            self.settingsExit.setValue(
                "ExitConfirm", self.ui.btn_confirmClose.isChecked()
            )

            self.settingsMinimize.setValue(
                "Minimize", self.ui.btn_minimizeAuto.isChecked()
            )

            self.settingsDotSize.setValue("DotSize", self.ui.dot_size.text())

            self.settingsFontSize.setValue("FontSize", self.ui.font_size.text())

            self.settingsSaveDPI.setValue("SaveDPI", self.ui.saveDPI.text())

            self.settingsFPS.setValue("FPS", self.ui.gif_fps.text())

            if self.ui.radio_size_and_color.isChecked():
                self.settingsDotType.setValue("DotType", "size_and_color")
            elif self.ui.radio_color.isChecked():
                self.settingsDotType.setValue("DotType", "color")
            elif self.ui.radio_size.isChecked():
                self.settingsDotType.setValue("DotType", "size")

            self.settingsColormap.setValue("Colormap", self.color_map)

            self.settingsDotEdge.setValue("Edge", self.ui.CheckBox_edge.isChecked())

            if self.ui.radioButton_norm_a.isChecked():
                self.settingsNormalization.setValue("Normalization", "all")
            elif self.ui.radioButton_norm_c.isChecked():
                self.settingsNormalization.setValue("Normalization", "selected")
            elif self.ui.radioButton_norm_d.isChecked():
                self.settingsNormalization.setValue("Normalization", "displayed")

            QSettings("PyC2MC", "def").setValue("def", "false")

        # MOVE WINDOW
        def moveWindow(event):
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.ui.titleRightInfo.mouseMoveEvent = moveWindow

        getSettings()
        self.colormap()
        # matplotlib.rcParams['savefig.dpi'] = self.ui.saveDPI.text() #res figures
        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "PyC2MC Viewer Edition"
        description = "Python tools for Complex Matrices Molecular Characterization. Viewer Edition"
        # APPLY TEXTS
        self.setWindowTitle(title)

        # EXTRA SETTINGS BOX
        def openCloseSettingsBox():
            UIFunctions.toggleSettingsBox(self, True)

        # EXTRA PROCESS BOX
        def openCloseProcessBox():
            UIFunctions.toggleProcessBox(self, True)

        # EXTRA VIEW BOX
        def openCloseViewBox():
            sender = self.sender().objectName()
            if (
                self.settingsMinimize.value("Minimize") == "true"
                or sender == "btn_view"
                or sender == "viewCloseColumnBtn"
            ):
                UIFunctions.toggleViewBox(self, True)

        # EXTRA COMPARE BOX
        def openCloseCompareBox():
            sender = self.sender().objectName()
            if (
                self.settingsMinimize.value("Minimize") == "true"
                or sender == "btn_compare"
                or sender == "compareCloseColumnBtn"
            ):
                UIFunctions.toggleCompareBox(self, True)

        # EXTRA STATS BOX
        def openCloseStatsBox():
            sender = self.sender().objectName()
            if (
                self.settingsMinimize.value("Minimize") == "true"
                or sender == "btn_stats"
                or sender == "statsCloseColumnBtn"
            ):
                UIFunctions.toggleStatsBox(self, True)

        # CLOSE BOXES BOX
        def closeBoxes():
            UIFunctions.start_box_animation(self, 0, 0, 0)

        # ALPHABETIC SORTING
        def list_sorting():
            self.split_classes()
            self.split_classes_compare()
            if self.ui.check_alphabetic_error.isChecked():
                self.ui.list_classes_error.sortItems()
            if self.ui.check_alphabetic_distrib.isChecked():
                self.ui.list_classes_distrib.sortItems()
            if self.ui.check_alphabetic_DBE.isChecked():
                self.ui.list_classes_DBE.sortItems()
            if self.ui.check_alphabetic_VK.isChecked():
                self.ui.list_classes_VK.sortItems()
            if self.ui.check_alphabetic_DBE_compare.isChecked():
                self.ui.list_classes_DBE_compare.sortItems()
            if self.ui.check_alphabetic_VK_compare.isChecked():
                self.ui.list_classes_VK_compare.sortItems()
            if self.ui.check_alphabetic_DBE_comp.isChecked():
                self.ui.list_classes_DBE_comp.sortItems()
            if self.ui.check_alphabetic_VK_comp.isChecked():
                self.ui.list_classes_VK_comp.sortItems()
            if self.ui.check_alphabetic_KMD_comp.isChecked():
                self.ui.list_classes_Kendrick_comp.sortItems()
            if self.ui.check_alphabetic_MD_comp.isChecked():
                self.ui.list_classes_Kendrick_univ_comp.sortItems()
            if self.ui.check_alphabetic_mass_spec.isChecked():
                self.ui.list_classes_mass_spec.sortItems()
            if self.ui.check_alphabetic_mass_spec_comp.isChecked():
                self.ui.list_classes_mass_spec_comp.sortItems()
            if self.ui.check_alphabetic_KMD.isChecked():
                self.ui.list_classes_Kendrick.sortItems()
            if self.ui.check_alphabetic_MD.isChecked():
                self.ui.list_classes_Kendrick_univ.sortItems()
            if self.ui.check_alphabetic_Kroll.isChecked():
                self.ui.list_classes_ACOS.sortItems()
            if self.ui.check_alphabetic_MAI.isChecked():
                self.ui.list_classes_MAI.sortItems()
            if self.ui.check_alphabetic_MCR.isChecked():
                self.ui.list_classes_MCR.sortItems()
            if self.ui.check_alphabetic_Kroll_comp.isChecked():
                self.ui.list_classes_ACOS_comp.sortItems()
            if self.ui.check_alphabetic_MAI_comp.isChecked():
                self.ui.list_classes_MAI_comp.sortItems()
            if self.ui.check_alphabetic_MCR_comp.isChecked():
                self.ui.list_classes_MCR_comp.sortItems()
            if self.ui.check_alphabetic_distrib_compare.isChecked():
                self.ui.list_classes_distrib_compare.sortItems()
            if self.ui.check_alphabetic_KMD_compare.isChecked():
                self.ui.list_classes_KMD_compare.sortItems()
            if self.ui.check_alphabetic_MD_compare.isChecked():
                self.ui.list_classes_MD_compare.sortItems()

        # INITIALIZATIONS
        self.start_counter = False
        self.ui.radio_color_pc1.hide()
        self.ui.radio_color_pc2.hide()
        self.ui.radio_color_pc1_comp.hide()
        self.ui.radio_color_pc2_comp.hide()
        self.ui.radio_color_pc1_VK.hide()
        self.ui.radio_color_pc2_VK.hide()
        self.ui.radio_color_pc1_VK_comp.hide()
        self.ui.radio_color_pc2_VK_comp.hide()
        self.ui.radio_color_pc1_ACOS.hide()
        self.ui.radio_color_pc2_ACOS.hide()
        self.ui.radio_color_pc1_ACOS_comp.hide()
        self.ui.radio_color_pc2_ACOS_comp.hide()
        self.ui.K_PC1.hide()
        self.ui.K_PC2.hide()
        self.ui.radio_color_pc1.setEnabled(False)
        self.ui.radio_color_pc2.setEnabled(False)
        self.ui.radio_color_pc1_comp.setEnabled(False)
        self.ui.radio_color_pc2_comp.setEnabled(False)
        self.ui.radio_color_pc1_VK.setEnabled(False)
        self.ui.radio_color_pc2_VK.setEnabled(False)
        self.ui.radio_color_pc1_VK_comp.setEnabled(False)
        self.ui.radio_color_pc2_VK_comp.setEnabled(False)
        self.ui.radio_color_pc1_ACOS.setEnabled(False)
        self.ui.radio_color_pc2_ACOS.setEnabled(False)
        self.ui.radio_color_pc1_ACOS_comp.setEnabled(False)
        self.ui.radio_color_pc2_ACOS_comp.setEnabled(False)
        self.ui.K_PC1.setEnabled(False)
        self.ui.K_PC2.setEnabled(False)
        self.ui.volc_color_classes.setEnabled(True)
        self.ui.volc_color_dbe.setEnabled(True)
        self.ui.pbar.hide()

        # ------------------------------------------------------------------------------
        # BUTTONS ASSIGNMENTS (DISPLAY SECTION)
        # ------------------------------------------------------------------------------

        # ///////////////////////////////////////////////
        # SPLIT FINDER CONNECTION
        # ///////////////////////////////////////////////
        self.ui.btn_split.clicked.connect(self.start_splitfinder)

        # ///////////////////////////////////////////////
        # APP PARAMETER CONNECTIONS
        # ///////////////////////////////////////////////

        self.ui.settingsTopBtn.clicked.connect(openCloseSettingsBox)
        self.ui.settingsTopBtn.clicked.connect(saveSettings)
        self.ui.settingsCloseColumnBtn.clicked.connect(openCloseSettingsBox)
        self.ui.settingsCloseColumnBtn.clicked.connect(saveSettings)
        self.ui.closeAppBtn.clicked.connect(saveSettings)

        # ///////////////////////////////////////////////
        # GRAPHIC PARAMETER CONNECTIONS
        # ///////////////////////////////////////////////

        self.ui.btn_settings.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_param)
        )
        self.ui.btn_settings.clicked.connect(closeBoxes)
        self.ui.btn_settings.clicked.connect(self.buttonColor)

        # ///////////////////////////////////////////////
        # PROCESS BUTTONS CONNECTIONS
        # ///////////////////////////////////////////////

        # Classic open/close
        self.ui.btn_process.clicked.connect(openCloseProcessBox)
        self.ui.processCloseColumnBtn.clicked.connect(openCloseProcessBox)

        # Merge attributed
        self.ui.btn_merge_att.clicked.connect(openCloseProcessBox)
        # Merge unattributed
        self.ui.btn_merge_una.clicked.connect(openCloseProcessBox)
        # Fuse
        self.ui.btn_fuse.clicked.connect(openCloseProcessBox)
        # Merge already merged or fused
        self.ui.btn_merge_mer.clicked.connect(openCloseProcessBox)
        # Merge csv from same sepctrum
        self.ui.btn_merge_xcalibur.clicked.connect(openCloseProcessBox)

        # ///////////////////////////////////////////////
        #   CHEMICAL CLASSES SORTING
        # ///////////////////////////////////////////////

        # Sorts chemical classes by alphabetic order
        self.ui.check_alphabetic_error.clicked.connect(list_sorting)
        self.ui.check_alphabetic_distrib.clicked.connect(list_sorting)
        self.ui.check_alphabetic_DBE.clicked.connect(list_sorting)
        self.ui.check_alphabetic_VK.clicked.connect(list_sorting)
        self.ui.check_alphabetic_DBE_compare.clicked.connect(list_sorting)
        self.ui.check_alphabetic_VK_compare.clicked.connect(list_sorting)
        self.ui.check_alphabetic_mass_spec.clicked.connect(list_sorting)
        self.ui.check_alphabetic_mass_spec_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_KMD.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MD.clicked.connect(list_sorting)
        self.ui.check_alphabetic_Kroll.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MAI.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MCR.clicked.connect(list_sorting)
        self.ui.check_alphabetic_distrib_compare.clicked.connect(list_sorting)
        self.ui.check_alphabetic_DBE_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_VK_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_KMD_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MD_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_Kroll_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MAI_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MCR_comp.clicked.connect(list_sorting)
        self.ui.check_alphabetic_KMD_compare.clicked.connect(list_sorting)
        self.ui.check_alphabetic_MD_compare.clicked.connect(list_sorting)

        # ///////////////////////////////////////////////
        # VIEW BUTTONS CONNECTIONS
        # ///////////////////////////////////////////////

        # Classic open/close
        self.ui.btn_view.clicked.connect(openCloseViewBox)
        self.ui.viewCloseColumnBtn.clicked.connect(openCloseViewBox)

        # Overview
        self.ui.btn_overview.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.view)
        )
        self.ui.btn_overview.clicked.connect(
            lambda: self.ui.choose_plot_stacked.setCurrentWidget(self.ui.page_overview)
        )
        self.ui.btn_overview.clicked.connect(self.buttonColor)
        self.ui.btn_overview.clicked.connect(openCloseViewBox)
        self.ui.btn_overview.clicked.connect(lambda: self.colorTab("View"))
        # DBE
        self.ui.btn_DBE.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.view)
        )
        self.ui.btn_DBE.clicked.connect(
            lambda: self.ui.choose_plot_stacked.setCurrentWidget(self.ui.page_DBE)
        )
        self.ui.btn_DBE.clicked.connect(self.buttonColor)
        self.ui.btn_DBE.clicked.connect(openCloseViewBox)
        self.ui.btn_DBE.clicked.connect(lambda: self.colorTab("View"))
        # VK
        self.ui.btn_van_krevelen.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.view)
        )
        self.ui.btn_van_krevelen.clicked.connect(
            lambda: self.ui.choose_plot_stacked.setCurrentWidget(self.ui.page_VK)
        )
        self.ui.btn_van_krevelen.clicked.connect(self.buttonColor)
        self.ui.btn_van_krevelen.clicked.connect(openCloseViewBox)
        self.ui.btn_van_krevelen.clicked.connect(lambda: self.colorTab("View"))
        # Kendrick
        self.ui.btn_kendricks.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.view)
        )
        self.ui.btn_kendricks.clicked.connect(
            lambda: self.ui.choose_plot_stacked.setCurrentWidget(self.ui.page_Kendrick)
        )
        self.ui.btn_kendricks.clicked.connect(self.buttonColor)
        self.ui.btn_kendricks.clicked.connect(openCloseViewBox)
        self.ui.btn_kendricks.clicked.connect(lambda: self.colorTab("View"))
        # EV
        self.ui.btn_EV.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.view)
        )
        self.ui.btn_EV.clicked.connect(
            lambda: self.ui.choose_plot_stacked.setCurrentWidget(self.ui.page_EV)
        )
        self.ui.btn_EV.clicked.connect(self.buttonColor)
        self.ui.btn_EV.clicked.connect(openCloseViewBox)
        self.ui.btn_EV.clicked.connect(lambda: self.colorTab("View"))

        # ///////////////////////////////////////////////
        #   VIEW\OVERVIEW BUTTONS CONNECTIONS
        # ///////////////////////////////////////////////
        # Displays composition page
        self.ui.radio_composition.clicked.connect(
            lambda: self.ui.stackedWidget_overview.setCurrentWidget(
                self.ui.page_composition
            )
        )
        # Displays error plots page
        self.ui.radio_error_plots.clicked.connect(
            lambda: self.ui.stackedWidget_overview.setCurrentWidget(
                self.ui.page_error_plots
            )
        )
        # Displays Intensity vs DBE plots page
        self.ui.radio_distributions.clicked.connect(
            lambda: self.ui.stackedWidget_overview.setCurrentWidget(
                self.ui.page_intens_vs_DBE
            )
        )
        # Displays spectrum page
        self.ui.radio_mass_spectrum.clicked.connect(
            lambda: self.ui.stackedWidget_overview.setCurrentWidget(
                self.ui.page_mass_spectrum
            )
        )

        # /////////////////////////////////
        #   VIEW\KENDRICK BUTTONS CONNECTIONS
        # /////////////////////////////////
        self.ui.buttonKendrickStd.clicked.connect(
            lambda: self.ui.stackedWidget_Kendrick.setCurrentWidget(self.ui.page_std)
        )
        self.ui.buttonKendrickExt.clicked.connect(
            lambda: self.ui.stackedWidget_Kendrick.setCurrentWidget(self.ui.page_ext)
        )
        self.ui.buttonKendrickUniv.clicked.connect(
            lambda: self.ui.stackedWidget_Kendrick.setCurrentWidget(self.ui.page_univ)
        )

        # /////////////////////////////////
        #   VIEW\EV BUTTONS CONNECTIONS
        # /////////////////////////////////

        self.ui.radio_ACOS.clicked.connect(
            lambda: self.ui.stackedWidget_EV.setCurrentWidget(self.ui.page_ACOS)
        )
        self.ui.radio_MAI.clicked.connect(
            lambda: self.ui.stackedWidget_EV.setCurrentWidget(self.ui.page_MAI)
        )
        self.ui.radio_MCR.clicked.connect(
            lambda: self.ui.stackedWidget_EV.setCurrentWidget(self.ui.page_MCR)
        )

        # ///////////////////////////////////////////////
        # COMPARE BUTTONS CONNECTIONS
        # ///////////////////////////////////////////////

        # Classic open/close
        self.ui.btn_compare.clicked.connect(openCloseCompareBox)
        self.ui.compareCloseColumnBtn.clicked.connect(openCloseCompareBox)

        # Overview
        self.ui.btn_overview_compare.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_overview_compare.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_compare_overview
            )
        )
        self.ui.btn_overview_compare.clicked.connect(self.buttonColor)
        self.ui.btn_overview_compare.clicked.connect(openCloseCompareBox)
        self.ui.btn_overview_compare.clicked.connect(lambda: self.colorTab("Compare"))

        # FC maps
        self.ui.btn_molecular_cartographies.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_molecular_cartographies.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_molecular_cartographies
            )
        )
        self.ui.btn_molecular_cartographies.clicked.connect(self.buttonColor)
        self.ui.btn_molecular_cartographies.clicked.connect(openCloseCompareBox)
        self.ui.btn_molecular_cartographies.clicked.connect(
            lambda: self.colorTab("Compare")
        )

        # DBE maps
        self.ui.btn_DBE_compare_menu.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_DBE_compare_menu.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_compare_DBE
            )
        )
        self.ui.btn_DBE_compare_menu.clicked.connect(self.buttonColor)
        self.ui.btn_DBE_compare_menu.clicked.connect(openCloseCompareBox)
        self.ui.btn_DBE_compare_menu.clicked.connect(lambda: self.colorTab("Compare"))

        # VK plot
        self.ui.btn_VK_compare_menu.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_VK_compare_menu.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_compare_VK
            )
        )
        self.ui.btn_VK_compare_menu.clicked.connect(self.buttonColor)
        self.ui.btn_VK_compare_menu.clicked.connect(openCloseCompareBox)
        self.ui.btn_VK_compare_menu.clicked.connect(lambda: self.colorTab("Compare"))

        # KMD plot
        self.ui.btn_KMD_compare_menu.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_KMD_compare_menu.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_compare_KMD
            )
        )
        self.ui.btn_KMD_compare_menu.clicked.connect(self.buttonColor)
        self.ui.btn_KMD_compare_menu.clicked.connect(openCloseCompareBox)
        self.ui.btn_KMD_compare_menu.clicked.connect(lambda: self.colorTab("Compare"))

        # EV plot
        self.ui.btn_EV_compare_menu.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.compare)
        )
        self.ui.btn_EV_compare_menu.clicked.connect(
            lambda: self.ui.Compare_stacked_widget.setCurrentWidget(
                self.ui.page_compare_EV
            )
        )
        self.ui.btn_EV_compare_menu.clicked.connect(self.buttonColor)
        self.ui.btn_EV_compare_menu.clicked.connect(openCloseCompareBox)
        self.ui.btn_EV_compare_menu.clicked.connect(lambda: self.colorTab("Compare"))

        # /////////////////////////////////
        #   COMPARE\OVERVIEW BUTTONS CONNECTIONS
        # /////////////////////////////////

        # Displays mass spectrum widget
        self.ui.radio_mass_spectrum_compare.clicked.connect(
            lambda: self.ui.stackedWidget_overview_compare.setCurrentWidget(
                self.ui.page_mass_spectrum_compare
            )
        )
        # Displays distribution widget
        self.ui.radio_distribution_compare.clicked.connect(
            lambda: self.ui.stackedWidget_overview_compare.setCurrentWidget(
                self.ui.page_distribution_compare
            )
        )
        # Displays Composition widget
        self.ui.radio_composition_compare.clicked.connect(
            lambda: self.ui.stackedWidget_overview_compare.setCurrentWidget(
                self.ui.page_composition_compare
            )
        )

        # /////////////////////////////////
        #   COMPARE\FC PLOTS BUTTONS CONNECTIONS
        # /////////////////////////////////

        # Displays DBE widget
        self.ui.btn_DBE_compare.clicked.connect(
            lambda: self.ui.stackedWidget_FC.setCurrentWidget(self.ui.page_DBE_compare)
        )
        # Displays Van Krevelen widget
        self.ui.btn_VK_compare.clicked.connect(
            lambda: self.ui.stackedWidget_FC.setCurrentWidget(self.ui.page_VK_compare)
        )
        # Displays KMD widget
        self.ui.btn_KMD_compare.clicked.connect(
            lambda: self.ui.stackedWidget_FC.setCurrentWidget(self.ui.page_KMD_compare)
        )
        # Displays MD widget
        self.ui.btn_MD_compare.clicked.connect(
            lambda: self.ui.stackedWidget_FC.setCurrentWidget(self.ui.page_MD_compare)
        )

        # /////////////////////////////////
        #   COMPARE\KENDRICK BUTTONS CONNECTIONS
        # /////////////////////////////////
        self.ui.buttonKendrickStd_comp.clicked.connect(
            lambda: self.ui.stackedWidget_Kendrick_comp.setCurrentWidget(
                self.ui.page_std_comp
            )
        )
        self.ui.buttonKendrickUniv_comp.clicked.connect(
            lambda: self.ui.stackedWidget_Kendrick_comp.setCurrentWidget(
                self.ui.page_univ_2
            )
        )

        # /////////////////////////////////
        #   COMPARE\EV BUTTONS CONNECTIONS
        # /////////////////////////////////

        self.ui.radio_ACOS_comp.clicked.connect(
            lambda: self.ui.stackedWidget_EV_comp.setCurrentWidget(
                self.ui.page_ACOS_comp
            )
        )
        self.ui.radio_MAI_comp.clicked.connect(
            lambda: self.ui.stackedWidget_EV_comp.setCurrentWidget(
                self.ui.page_MAI_comp
            )
        )
        self.ui.radio_MCR_comp.clicked.connect(
            lambda: self.ui.stackedWidget_EV_comp.setCurrentWidget(
                self.ui.page_MCR_comp
            )
        )

        # ///////////////////////////////////////////////
        # STATS BUTTONS CONNECTIONS
        # ///////////////////////////////////////////////

        # Classic open/close
        self.ui.btn_stats.clicked.connect(openCloseStatsBox)
        self.ui.statsCloseColumnBtn.clicked.connect(openCloseStatsBox)

        # Displays venn page
        self.ui.btn_venn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stats)
        )
        self.ui.btn_venn.clicked.connect(
            lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_venn)
        )
        self.ui.btn_venn.clicked.connect(self.buttonColor)
        self.ui.btn_venn.clicked.connect(openCloseStatsBox)
        self.ui.btn_venn.clicked.connect(lambda: self.colorTab("Stats"))

        # Displays PCA page
        self.ui.btn_PCA.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stats)
        )
        self.ui.btn_PCA.clicked.connect(
            lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_PCA)
        )
        self.ui.btn_PCA.clicked.connect(self.buttonColor)
        self.ui.btn_PCA.clicked.connect(openCloseStatsBox)
        self.ui.btn_PCA.clicked.connect(lambda: self.colorTab("Stats"))

        # Displays HCA page
        self.ui.btn_HCA.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stats)
        )
        self.ui.btn_HCA.clicked.connect(
            lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_HCA)
        )
        self.ui.btn_HCA.clicked.connect(self.buttonColor)
        self.ui.btn_HCA.clicked.connect(openCloseStatsBox)
        self.ui.btn_HCA.clicked.connect(lambda: self.colorTab("Stats"))

        # Displays volcano page
        self.ui.btn_Volcano.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stats)
        )
        self.ui.btn_Volcano.clicked.connect(
            lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_Volcano)
        )
        self.ui.btn_Volcano.clicked.connect(self.buttonColor)
        self.ui.btn_Volcano.clicked.connect(openCloseStatsBox)
        self.ui.btn_Volcano.clicked.connect(lambda: self.colorTab("Stats"))

        # Displays pl comparison page
        self.ui.btn_pl_comp.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.stats)
        )
        self.ui.btn_pl_comp.clicked.connect(
            lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_pl_comp)
        )
        self.ui.btn_pl_comp.clicked.connect(self.buttonColor)
        self.ui.btn_pl_comp.clicked.connect(openCloseStatsBox)
        self.ui.btn_pl_comp.clicked.connect(lambda: self.colorTab("Stats"))

        # Displays KMD widget
        self.ui.btn_KMD_stats.clicked.connect(
            lambda: self.ui.stackedWidget_FC_stats.setCurrentWidget(
                self.ui.page_KMD_compare_2
            )
        )
        # Displays MD widget
        self.ui.btn_MD_stats.clicked.connect(
            lambda: self.ui.stackedWidget_FC_stats.setCurrentWidget(
                self.ui.page_MD_compare_2
            )
        )

        # ------------------------------------------------------------------------------
        # BUTTONS ASSIGNMENTS (FUNCTIONS SECTION)
        # ------------------------------------------------------------------------------

        # Plot buttons

        # Loaded files list

        self.ui.list_loaded_file.itemSelectionChanged.connect(self.btn_enabling)
        self.ui.list_loaded_file.itemSelectionChanged.connect(self.split_classes)
        self.ui.list_loaded_file_2.itemSelectionChanged.connect(
            self.split_classes_merged
        )
        self.ui.list_distribution.itemSelectionChanged.connect(self.distrib_pannel)
        self.ui.list_distribution_compare.itemSelectionChanged.connect(
            self.distribution_compare_pannel
        )
        self.ui.list_loaded_file_compare.itemSelectionChanged.connect(
            self.compare_calculation
        )
        self.ui.list_loaded_file_compare.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.ui.list_classes_distrib.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.ui.list_compare_sample_1.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.ui.list_compare_sample_2.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.ui.list_sample_1_stats.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )
        self.ui.list_sample_2_stats.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        # Plot View
        self.ui.plot_button_view.clicked.connect(self.viewPlot)
        self.ui.plot_button_view_GIF.clicked.connect(self.viewGif)

        # Overview

        self.ui.list_classes_mass_spec.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.ui.list_classes_mass_spec_comp.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # Kendrick

        self.ui.pushButton_clearSeries.clicked.connect(self.clear_series)
        self.ui.plot_button_saveKendrick.clicked.connect(self.save_kendrick_series)
        self.ui.edit_motif.textChanged.connect(self.kendrick_motif_calculation)
        self.ui.pushButton_deformulation.clicked.connect(self.deformulation)
        self.ui.pushButton_save_defo.clicked.connect(self.save_deformulation)
        self.ui.mz_extraction.clicked.connect(self.KMD_ext_label_update)
        self.ui.KMD_Extraction.clicked.connect(self.KMD_ext_label_update)

        # Graphic parameters

        self.ui.list_color_map.itemSelectionChanged.connect(self.colormap)

        # Compare buttons
        ##Overview
        self.ui.plot_compare.clicked.connect(self.comparePlot)
        self.ui.plot_compare_GIF.clicked.connect(self.comparePlotGIF)

        ##FC maps
        ### KMD
        self.ui.edit_motif_compare.textChanged.connect(
            self.kendrick_motif_compare_calculation
        )

        # Stat buttons
        ##Plot Stats
        self.ui.plot_button_stats.clicked.connect(self.statsPlot)

        # PCA
        self.ui.save_button_pca_coef.clicked.connect(self.save_pca_coef)

        # HCA
        self.ui.hca_intensity_classic.clicked.connect(self.plot_HCA)
        self.ui.hca_intensity_sqrt.clicked.connect(self.plot_HCA)
        self.ui.hca_orientation_left.clicked.connect(self.plot_HCA)
        self.ui.hca_orientation_top.clicked.connect(self.plot_HCA)

        # Venn
        self.ui.list_sets.itemSelectionChanged.connect(self.select_set_venn)
        self.ui.Save_Sets_Button.clicked.connect(self.save_sets_venn)

        # KMD
        self.ui.edit_motif_stats.textChanged.connect(
            self.kendrick_motif_stats_calculation
        )

        # File
        self.ui.btn_load_file.clicked.connect(self.load_file_method)
        self.ui.btn_clear.clicked.connect(self.clear_loaded_list)
        self.ui.btn_settings.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.graph_param)
        )
        self.ui.btn_save.clicked.connect(self.save_file)

        # Process
        self.ui.btn_merge_att.clicked.connect(self.merge_files)
        self.ui.btn_fuse.clicked.connect(self.fusion_replicats)
        self.ui.btn_merge_mer.clicked.connect(self.merge_merged_files)
        self.ui.btn_merge_xcalibur.clicked.connect(self.merge_Multicsv)
        self.ui.btn_merge_una.clicked.connect(self.merge_unattributed_files)

        # ///////////////////////////////////////////////
        # MISC
        # ///////////////////////////////////////////////
        # About
        self.ui.btn_about.clicked.connect(self.about)

        self.last_modified = "23/10/2024"

        # Easter
        self.ui.Easter_egg.clicked.connect(self.easter_egg)
        self.ui.Easter_egg2.clicked.connect(self.easter_egg)

    # ///////////////////////////////////////////////
    # GENERAL EVENTS
    # ///////////////////////////////////////////////

    # WINDOW OPENING EVENTS
    # ///////////////////////////////////////////////////////////////





    # RECOLOR/UI UPDATE EVENTS
    # ///////////////////////////////////////////////////////////////



    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////

    # ///////////////////////////////////////////////
    # APP FUNCTIONS
    # ///////////////////////////////////////////////
    # ---------------------------------------
    #      Select plot to draw from View tab
    # ---------------------------------------


    # ---------------------------------------
    #      Select plot to draw from View tab (GIF version)
    # ---------------------------------------

    # ---------------------------------------
    #      Select plot to draw from Compare tab
    # ---------------------------------------


    # ---------------------------------------
    #      Select plot to draw from Compare tab (GIF version)
    # ---------------------------------------


    # ---------------------------------------
    #      Select plot to draw from Stats tab
    # ---------------------------------------


    # ---------------------------------------
    #      GUI reset on selection change
    # ---------------------------------------


    # ---------------------------------------
    #       Color map choice
    # ---------------------------------------


    # ---------------------------------------
    #       Clear loaded lists
    # ---------------------------------------


    # ---------------------------------------
    #       Load files
    # ---------------------------------------


    # ---------------------------------------
    #  Calling the merge function/module
    # ---------------------------------------






    # ---------------------------------------
    #       Read graphic parameter
    # ---------------------------------------


    # ---------------------------------------
    #    Distribution pannel activation
    #          on selection changes
    # ---------------------------------------



    # ---------------------------------------
    # Splitting classes on selection changes
    #                  +
    #      GUI adaptation to dataset
    #                  +
    #          Data qualification
    # ---------------------------------------




    # ---------------------------------------
    #   Plot section
    # ---------------------------------------















        ###


























    def closeEvent(self, event):
        """
        Closes the GUI and all the plots
        """
        if self.settingsExit.value("ExitConfirm") == "false":
            try:
                plt.close("all")
            except:
                pass
            try:
                if self.splitfinder:
                    self.splitfinder.close()
            except:
                pass
            event.accept()
        else:
            quit_msg = "No data will be saved. Confirm ?"
            reply = QMessageBox.question(
                self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    plt.close("all")
                except:
                    pass
                try:
                    if self.splitfinder:
                        self.splitfinder.close()
                except:
                    pass
                event.accept()
            else:
                event.ignore()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.move(0, 50)
    main.show()
    app.exec()
