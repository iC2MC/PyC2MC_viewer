# ///////////////////////////////////////////////////////////////
#
#----------------------------------------------------------------
# Written by Julien Maillard, Maxime Sueur, Oscar Lacroix-Andrivet
# Github : https://github.com/MaximeS5/PyC2MC
#-----------------------------------------------------------------------------
#
# ///////////////////////////////////////////////////////////////
# IMPORTATION
# ///////////////////////////////////////////////////////////////

from modules import *
from widgets import *
import os
import win32com.client
import numpy as np
import chemparse as cp
import math
from src.processing.merge_function import merge_file,merge_for_compare
from src.processing.merge_csv_from_same_spectrum import merge_Multicsv
from src.processing.fuse_replicates import fuse_replicates
from src.processing.merge_merged_function import merge_merged_file
from src.loading.loading_function import load_MS_file
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
from src.pyc2mc_ui import Ui_PyC2MC
from PyQt5.QtWidgets import  QMessageBox, QLineEdit, QInputDialog, QTableWidgetItem
from matplotlib.animation import FuncAnimation,PillowWriter
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch
from venn import venn_diag,venn_sets
import pandas
from sklearn import preprocessing
from math import sqrt
import mplcursors
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.backends.backend_svg
import openpyxl
from Image import easter
from src.splitFinder.splitfinder import Splitfinder
import time
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram
from scipy import stats
from src.stats.HCA_function import plot_dendrogram
from src.stats.PCA_function import plot_pca
from src.processing.merge_unattributed import merge_non_attributed
import imageio #For GIF
from PIL import Image, ImageSequence
from IPython import display

try:
    import pyi_splash
    splash = True
except:
    splash = False
    pass
matplotlib.use('qt5agg')

# matplotlib.rcParams['savefig.dpi'] = 300 #High res figures
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%



if splash:  #Closing splash
    pyi_splash.close()
    


# GENERAL FUNCTIONS
# ///////////////////////////////////////////////////////////////
def plot_fun(kind,x,y,d_color='blue',dot_type="sc",cmap="jet",edge=True
               ,size=100,b_width=1,error_data=0,stem_color='',e_color = 'k'
               ,bar_color = 'grey', alpha = 1):
    """
    Built-in plot function

    Args
    ----------
    kind : str
        Plot type : "scatter", "spectrum", "histo".
    x : Pandas.Series
        Data of x-axis.
    y : Pandas.Series
        Data of y-axis.
    d_color : str, optional
        Points color. The default is 'blue'.
    dot_type : str, optional
        Points size and color based on 3rd dimension ? : "sc" size and color, "s" size only , "c" color only. The default is "sc".
    cmap : str, optional
        Color map definition. The default is "jet".
    edge : bool, optional
        Enable points edge. The default is True.
    size : int, optional
        Set the points size scale. The default is 100.
    b_width : int, optional
        Set the bar width for bar and histo plots. The default is 1.
    error_data : Pandas.Series, optional
        Error bars data for bar and histo plots. The default is 0.
    stem_color : str, optional
        Stem color for spectrum plots. The default is ''.
    e_color : str, optional
        Edge color. The default is 'k'.

    Returns
    -------
    plt : Figure
        Figure object

    """
    #Dot type ?
    if dot_type == 'sc':
        color=d_color
        d_size=size
    elif dot_type=='s':
        color='blue'
        d_size=size
    elif dot_type=='c':
        color=d_color
        d_size=size/color
    #Edge ?
    if edge == True:
        e=0.7
    elif edge == False:
        e=0
    #Plot type ?
    if kind=='scatter': #Scatter plot for DBE, Van krevelen, Kendricks and ppm vs mz plots.
        plt.scatter(x,y,s=d_size,c=color,cmap=cmap,edgecolor=e_color,linewidths=e,alpha=alpha)
        return(plt)

    elif kind=='spectrum': #Stem plot for mass spectrum
        plt.stem(x,y,stem_color,markerfmt=" ", basefmt="k")
        return(plt)

    elif kind=='histo': #Bar diagram for composition, error distribution, DBE distribution (solo and merged),
        plt.bar(x,y,yerr=error_data, width=b_width*0.05,color = bar_color, align='center', ecolor='black',capsize=1/(len(x)))
        return(plt)

#Set of 9 colors for plots
color_list=[(0.83921568627451,0.145098039215686,0.254901960784314) #Red
            ,(0.0666666666666667,0.380392156862745,0.666666666666667) #Blue
            ,(0.423529411764706,0.701960784313725,0.294117647058824) #Light green
            ,(0.4,0.0980392156862745,0.537254901960784) #Purple
            ,(0.0235294117647059,0.662745098039216,0.415686274509804) #Forest green
            ,(0.925490196078431,0.364705882352941,0.2) #Orange
            ,(0.627450980392157,0.0470588235294118,0.352941176470588)#Crimson
            ,(0.0392156862745098,0.63921568627451,0.8) #Cyan
            ,(1,0.92156862745098,0.00392156862745098)] #Yellow

# MAIN CLASS
# ///////////////////////////////////////////////////////////////

class MainWindow(QtWidgets.QMainWindow):
    
    # role for storing the data frames in the items
    USERDATA_ROLE = QtCore.Qt.UserRole
    def __init__(self):
        super().__init__()

        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        global widgets
        widgets = self.ui
        
        # NO TITLE BAR
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        #GET PARAMETERS
        UIFunctions.uiDefinitions(self)
        
        
        
        
        
        
        
        def getSettings():
            
            if QSettings('PyC2MC','def').value('def') == 'false':
                pass
                
            else: #Default setting for 1st launch
                self.settingsExit = QSettings('PyC2MC','ExitConfirm')
                self.settingsExit.setValue('ExitConfirm', 'True')
                
                self.settingsMinimize = QSettings('PyC2MC','Minimize')
                self.settingsMinimize.setValue('Minimize','True')
                
                self.settingsDotSize = QSettings('PyC2MC','FontSize')
                self.settingsDotSize.setValue('DotSize','130')
                
                self.settingsFontSize = QSettings('PyC2MC','FontSize')
                self.settingsFontSize.setValue('FontSize','16')
                
                self.settingsSaveDPI = QSettings('PyC2MC','SaveDPI')
                self.settingsSaveDPI.setValue('SaveDPI','300')
                
                self.settingsFPS = QSettings('PyC2MC','FPS')
                self.settingsFPS.setValue('FPS','2')
                
                self.settingsDotType = QSettings('PyC2MC','DotType')
                self.settingsDotType.setValue('DotType','size_and_color')
                
                self.settingsColormap = QSettings('PyC2MC','Colormap')
                self.settingsDotType.setValue('Colormap','viridis')
                    
                self.settingsDotEdge = QSettings('PyC2MC','Edge')  
                self.settingsDotEdge.setValue('Edge','true')
                
                self.settingsNormalization = QSettings('PyC2MC','Normalization')
                self.settingsNormalization.value('Normalization','all')
                
                self.settingsdefault = QSettings('PyC2MC','def') 
                self.settingsdefault.setValue('def','false')
            
            self.settingsExit = QSettings('PyC2MC','ExitConfirm')
            if self.settingsExit.value('ExitConfirm') == 'true':
                widgets.btn_confirmClose.setChecked(True)
            else:
                widgets.btn_confirmClose.setChecked(False)
                
            self.settingsDotSize = QSettings('PyC2MC','FontSize')
            widgets.dot_size.setText(self.settingsDotSize.value('DotSize'))
            
            self.settingsFontSize = QSettings('PyC2MC','FontSize')
            widgets.font_size.setText(self.settingsFontSize.value('FontSize'))
            
            self.settingsSaveDPI = QSettings('PyC2MC','SaveDPI')
            widgets.saveDPI.setText(self.settingsSaveDPI.value('SaveDPI'))
            
            self.settingsFPS = QSettings('PyC2MC','FPS')
            widgets.gif_fps.setText(self.settingsFPS.value('FPS'))
            
            self.settingsMinimize = QSettings('PyC2MC','Minimize')
            if self.settingsMinimize.value('Minimize') == 'true':
                widgets.btn_minimizeAuto.setChecked(True)
            else:
                widgets.btn_minimizeAuto.setChecked(False)
            
            self.settingsDotType = QSettings('PyC2MC','DotType')
            if self.settingsDotType.value('DotType') == 'size_and_color':
                widgets.radio_size_and_color.setChecked(True)
            elif self.settingsDotType.value('DotType') == 'color':
                widgets.radio_color.setChecked(True)
            elif self.settingsDotType.value('DotType') == 'size':
                widgets.radio_size.setChecked(True)
            
            self.settingsColormap = QSettings('PyC2MC','Colormap')
            [widgets.list_color_map.setCurrentItem(x) for x in widgets.list_color_map.findItems(self.settingsColormap.value('Colormap'),QtCore.Qt.MatchExactly)]
            
            self.settingsDotEdge = QSettings('PyC2MC','Edge')  
            if self.settingsDotEdge.value('Edge') == 'true':
                widgets.CheckBox_edge.setChecked(True)
            else:
                widgets.CheckBox_edge.setChecked(False)
            
            self.settingsNormalization = QSettings('PyC2MC','Normalization')
            if self.settingsNormalization.value('Normalization') == 'all':
                widgets.radioButton_norm_a.setChecked(True)
            elif self.settingsNormalization.value('Normalization') == 'selected':
                widgets.radioButton_norm_c.setChecked(True)
            elif self.settingsNormalization.value('Normalization') == 'displayed':
                widgets.radioButton_norm_d.setChecked(True)
            
        #SAVE PARAMETERS
        def saveSettings():
            
            self.settingsExit.setValue('ExitConfirm',widgets.btn_confirmClose.isChecked())
            
            self.settingsMinimize.setValue('Minimize',widgets.btn_minimizeAuto.isChecked())
            
            self.settingsDotSize.setValue('DotSize',widgets.dot_size.text())
            
            self.settingsFontSize.setValue('FontSize',widgets.font_size.text())
            
            self.settingsSaveDPI.setValue('SaveDPI', widgets.saveDPI.text())
            
            self.settingsFPS.setValue('FPS',widgets.gif_fps.text())
            
            if widgets.radio_size_and_color.isChecked():
                self.settingsDotType.setValue('DotType','size_and_color')
            elif widgets.radio_color.isChecked():
                self.settingsDotType.setValue('DotType','color')
            elif widgets.radio_size.isChecked():
                self.settingsDotType.setValue('DotType','size')
                
            self.settingsColormap.setValue('Colormap',self.color_map)
            
            self.settingsDotEdge.setValue('Edge',widgets.CheckBox_edge.isChecked())
            
            if widgets.radioButton_norm_a.isChecked():
                self.settingsNormalization.setValue('Normalization','all')
            elif widgets.radioButton_norm_c.isChecked():
                self.settingsNormalization.setValue('Normalization','selected')
            elif widgets.radioButton_norm_d.isChecked():
                self.settingsNormalization.setValue('Normalization','displayed')
            
            QSettings('PyC2MC','def').setValue('def','false')
            
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
        # matplotlib.rcParams['savefig.dpi'] = widgets.saveDPI.text() #res figures
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
            if self.settingsMinimize.value('Minimize') == 'true' or sender =='btn_view' or sender == 'viewCloseColumnBtn':
                UIFunctions.toggleViewBox(self, True)
            
        # EXTRA COMPARE BOX
        def openCloseCompareBox():
            sender = self.sender().objectName()
            if self.settingsMinimize.value('Minimize') == 'true' or sender =='btn_compare' or sender == 'compareCloseColumnBtn':
                UIFunctions.toggleCompareBox(self, True)
        
        # EXTRA STATS BOX
        def openCloseStatsBox():
            sender = self.sender().objectName()
            if self.settingsMinimize.value('Minimize') == 'true' or sender =='btn_stats' or sender == 'statsCloseColumnBtn':
                UIFunctions.toggleStatsBox(self, True)
            
        # CLOSE BOXES BOX
        def closeBoxes():
            UIFunctions.start_box_animation(self,0,0,0)
            
            
        # ALPHABETIC SORTING
        def list_sorting():
            self.split_classes()
            self.split_classes_compare()
            if widgets.check_alphabetic_error.isChecked():
                widgets.list_classes_error.sortItems()
            if widgets.check_alphabetic_distrib.isChecked():
                widgets.list_classes_distrib.sortItems()
            if widgets.check_alphabetic_DBE.isChecked():
                widgets.list_classes_DBE.sortItems()
            if widgets.check_alphabetic_VK.isChecked():
                widgets.list_classes_VK.sortItems()
            if widgets.check_alphabetic_DBE_compare.isChecked():
                widgets.list_classes_DBE_compare.sortItems()
            if widgets.check_alphabetic_VK_compare.isChecked():
                widgets.list_classes_VK_compare.sortItems()
            if widgets.check_alphabetic_DBE_comp.isChecked():
                widgets.list_classes_DBE_comp.sortItems()
            if widgets.check_alphabetic_VK_comp.isChecked():
                widgets.list_classes_VK_comp.sortItems()
            if widgets.check_alphabetic_KMD_comp.isChecked():
                widgets.list_classes_Kendrick_comp.sortItems()
            if widgets.check_alphabetic_MD_comp.isChecked():
                widgets.list_classes_Kendrick_univ_comp.sortItems()
            if widgets.check_alphabetic_mass_spec.isChecked():
                widgets.list_classes_mass_spec.sortItems()
            if widgets.check_alphabetic_mass_spec_comp.isChecked():
                widgets.list_classes_mass_spec_comp.sortItems()
            if widgets.check_alphabetic_KMD.isChecked():
                widgets.list_classes_Kendrick.sortItems()
            if widgets.check_alphabetic_MD.isChecked():
                widgets.list_classes_Kendrick_univ.sortItems()   
            if widgets.check_alphabetic_Kroll.isChecked():
                widgets.list_classes_ACOS.sortItems()
            if widgets.check_alphabetic_MAI.isChecked():
                widgets.list_classes_MAI.sortItems()    
            if widgets.check_alphabetic_MCR.isChecked():
                widgets.list_classes_MCR.sortItems()
            if widgets.check_alphabetic_Kroll_comp.isChecked():
                widgets.list_classes_ACOS_comp.sortItems()
            if widgets.check_alphabetic_MAI_comp.isChecked():
                widgets.list_classes_MAI_comp.sortItems()    
            if widgets.check_alphabetic_MCR_comp.isChecked():
                widgets.list_classes_MCR_comp.sortItems()
            if widgets.check_alphabetic_distrib_compare.isChecked():
                widgets.list_classes_distrib_compare.sortItems()    
                
 
                

                
        # INITIALIZATIONS
        self.start_counter=False
        widgets.radio_color_pc1.setEnabled(False)
        widgets.radio_color_pc2.setEnabled(False)
        widgets.radio_color_pc1_comp.setEnabled(False)
        widgets.radio_color_pc2_comp.setEnabled(False)
        widgets.radio_color_pc1_VK.setEnabled(False)
        widgets.radio_color_pc2_VK.setEnabled(False)
        widgets.radio_color_pc1_VK_comp.setEnabled(False)
        widgets.radio_color_pc2_VK_comp.setEnabled(False)
        widgets.radio_color_pc1_ACOS.setEnabled(False)
        widgets.radio_color_pc2_ACOS.setEnabled(False)
        widgets.radio_color_pc1_ACOS_comp.setEnabled(False)
        widgets.radio_color_pc2_ACOS_comp.setEnabled(False)
        widgets.volc_color_classes.setEnabled(True)
        widgets.volc_color_dbe.setEnabled(True)
        widgets.pbar.hide()
        
#------------------------------------------------------------------------------   
#BUTTONS ASSIGNMENTS (DISPLAY SECTION)
#------------------------------------------------------------------------------   
        

        
#///////////////////////////////////////////////     
#SPLIT FINDER CONNECTION
#///////////////////////////////////////////////  
        widgets.btn_split.clicked.connect(self.start_splitfinder)
        
#///////////////////////////////////////////////     
#APP PARAMETER CONNECTIONS
#///////////////////////////////////////////////   

        widgets.settingsTopBtn.clicked.connect(openCloseSettingsBox)
        widgets.settingsTopBtn.clicked.connect(saveSettings)
        widgets.settingsCloseColumnBtn.clicked.connect(openCloseSettingsBox)
        widgets.settingsCloseColumnBtn.clicked.connect(saveSettings)
        widgets.closeAppBtn.clicked.connect(saveSettings)
        
        
        
#///////////////////////////////////////////////     
#GRAPHIC PARAMETER CONNECTIONS
#///////////////////////////////////////////////   

        widgets.btn_settings.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.graph_param))
        widgets.btn_settings.clicked.connect(closeBoxes)
        widgets.btn_settings.clicked.connect(self.buttonColor)

#///////////////////////////////////////////////     
#PROCESS BUTTONS CONNECTIONS
#///////////////////////////////////////////////     

        #Classic open/close
        widgets.btn_process.clicked.connect(openCloseProcessBox)
        widgets.processCloseColumnBtn.clicked.connect(openCloseProcessBox) 
        
        #Merge attributed
        widgets.btn_merge_att.clicked.connect(openCloseProcessBox)
        #Merge unattributed
        widgets.btn_merge_una.clicked.connect(openCloseProcessBox)
        #Fuse
        widgets.btn_fuse.clicked.connect(openCloseProcessBox)
        #Merge already merged or fused
        widgets.btn_merge_mer.clicked.connect(openCloseProcessBox) 
        #Merge csv from same sepctrum
        widgets.btn_merge_xcalibur.clicked.connect(openCloseProcessBox) 

#///////////////////////////////////////////////       
#   CHEMICAL CLASSES SORTING
#///////////////////////////////////////////////

        #Sorts chemical classes by alphabetic order
        widgets.check_alphabetic_error.clicked.connect(list_sorting)
        widgets.check_alphabetic_distrib.clicked.connect(list_sorting)
        widgets.check_alphabetic_DBE.clicked.connect(list_sorting)
        widgets.check_alphabetic_VK.clicked.connect(list_sorting)
        widgets.check_alphabetic_DBE_compare.clicked.connect(list_sorting)
        widgets.check_alphabetic_VK_compare.clicked.connect(list_sorting)
        widgets.check_alphabetic_mass_spec.clicked.connect(list_sorting)
        widgets.check_alphabetic_mass_spec_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_KMD.clicked.connect(list_sorting)
        widgets.check_alphabetic_MD.clicked.connect(list_sorting)
        widgets.check_alphabetic_Kroll.clicked.connect(list_sorting)
        widgets.check_alphabetic_MAI.clicked.connect(list_sorting)
        widgets.check_alphabetic_MCR.clicked.connect(list_sorting)
        widgets.check_alphabetic_distrib_compare.clicked.connect(list_sorting)
        widgets.check_alphabetic_DBE_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_VK_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_KMD_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_MD_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_Kroll_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_MAI_comp.clicked.connect(list_sorting)
        widgets.check_alphabetic_MCR_comp.clicked.connect(list_sorting)
        
#///////////////////////////////////////////////     
#VIEW BUTTONS CONNECTIONS
#///////////////////////////////////////////////     

        #Classic open/close
        widgets.btn_view.clicked.connect(openCloseViewBox)
        widgets.viewCloseColumnBtn.clicked.connect(openCloseViewBox) 
        
        
        #Overview
        widgets.btn_overview.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.view))
        widgets.btn_overview.clicked.connect(lambda : widgets.choose_plot_stacked.setCurrentWidget(widgets.page_overview))
        widgets.btn_overview.clicked.connect(self.buttonColor)
        widgets.btn_overview.clicked.connect(openCloseViewBox)
        widgets.btn_overview.clicked.connect(lambda :self.colorTab('View'))
        #DBE
        widgets.btn_DBE.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.view))
        widgets.btn_DBE.clicked.connect(lambda : widgets.choose_plot_stacked.setCurrentWidget(widgets.page_DBE))
        widgets.btn_DBE.clicked.connect(self.buttonColor)
        widgets.btn_DBE.clicked.connect(openCloseViewBox)
        widgets.btn_DBE.clicked.connect(lambda :self.colorTab('View'))
        #VK
        widgets.btn_van_krevelen.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.view))
        widgets.btn_van_krevelen.clicked.connect(lambda : widgets.choose_plot_stacked.setCurrentWidget(widgets.page_VK))
        widgets.btn_van_krevelen.clicked.connect(self.buttonColor)
        widgets.btn_van_krevelen.clicked.connect(openCloseViewBox)
        widgets.btn_van_krevelen.clicked.connect(lambda :self.colorTab('View'))
        #Kendrick
        widgets.btn_kendricks.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.view))
        widgets.btn_kendricks.clicked.connect(lambda : widgets.choose_plot_stacked.setCurrentWidget(widgets.page_Kendrick))
        widgets.btn_kendricks.clicked.connect(self.buttonColor)
        widgets.btn_kendricks.clicked.connect(openCloseViewBox)
        widgets.btn_kendricks.clicked.connect(lambda :self.colorTab('View'))
        #EV
        widgets.btn_EV.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.view))
        widgets.btn_EV.clicked.connect(lambda : widgets.choose_plot_stacked.setCurrentWidget(widgets.page_EV))
        widgets.btn_EV.clicked.connect(self.buttonColor)
        widgets.btn_EV.clicked.connect(openCloseViewBox)
        widgets.btn_EV.clicked.connect(lambda :self.colorTab('View'))

#///////////////////////////////////////////////       
#   VIEW\OVERVIEW BUTTONS CONNECTIONS
#///////////////////////////////////////////////
        #Displays composition page
        widgets.radio_composition.clicked.connect(lambda : widgets.stackedWidget_overview.setCurrentWidget(widgets.page_composition))
        #Displays error plots page
        widgets.radio_error_plots.clicked.connect(lambda : widgets.stackedWidget_overview.setCurrentWidget(widgets.page_error_plots))
        #Displays Intensity vs DBE plots page
        widgets.radio_distributions.clicked.connect(lambda : widgets.stackedWidget_overview.setCurrentWidget(widgets.page_intens_vs_DBE))
        #Displays spectrum page
        widgets.radio_mass_spectrum.clicked.connect(lambda : widgets.stackedWidget_overview.setCurrentWidget(widgets.page_mass_spectrum))

#/////////////////////////////////    
#   VIEW\KENDRICK BUTTONS CONNECTIONS
#/////////////////////////////////
        widgets.buttonKendrickStd.clicked.connect(lambda : widgets.stackedWidget_Kendrick.setCurrentWidget(widgets.page_std))
        widgets.buttonKendrickExt.clicked.connect(lambda : widgets.stackedWidget_Kendrick.setCurrentWidget(widgets.page_ext))
        widgets.buttonKendrickUniv.clicked.connect(lambda : widgets.stackedWidget_Kendrick.setCurrentWidget(widgets.page_univ))
        
#/////////////////////////////////  
#   VIEW\EV BUTTONS CONNECTIONS
#/////////////////////////////////  

        widgets.radio_ACOS.clicked.connect(lambda : widgets.stackedWidget_EV.setCurrentWidget(widgets.page_ACOS))
        widgets.radio_MAI.clicked.connect(lambda : widgets.stackedWidget_EV.setCurrentWidget(widgets.page_MAI))
        widgets.radio_MCR.clicked.connect(lambda : widgets.stackedWidget_EV.setCurrentWidget(widgets.page_MCR))

#///////////////////////////////////////////////       
#COMPARE BUTTONS CONNECTIONS
#///////////////////////////////////////////////

        #Classic open/close
        widgets.btn_compare.clicked.connect(openCloseCompareBox)
        widgets.compareCloseColumnBtn.clicked.connect(openCloseCompareBox) 
        
        #Overview
        widgets.btn_overview_compare.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_overview_compare.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_compare_overview))        
        widgets.btn_overview_compare.clicked.connect(self.buttonColor)
        widgets.btn_overview_compare.clicked.connect(openCloseCompareBox) 
        widgets.btn_overview_compare.clicked.connect(lambda :self.colorTab('Compare'))

        
        #FC maps
        widgets.btn_molecular_cartographies.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_molecular_cartographies.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_molecular_cartographies))  
        widgets.btn_molecular_cartographies.clicked.connect(self.buttonColor)
        widgets.btn_molecular_cartographies.clicked.connect(openCloseCompareBox) 
        widgets.btn_molecular_cartographies.clicked.connect(lambda :self.colorTab('Compare'))
        
        #DBE maps
        widgets.btn_DBE_compare_menu.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_DBE_compare_menu.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_compare_DBE))  
        widgets.btn_DBE_compare_menu.clicked.connect(self.buttonColor)
        widgets.btn_DBE_compare_menu.clicked.connect(openCloseCompareBox) 
        widgets.btn_DBE_compare_menu.clicked.connect(lambda :self.colorTab('Compare'))
        
        #VK plot
        widgets.btn_VK_compare_menu.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_VK_compare_menu.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_compare_VK))  
        widgets.btn_VK_compare_menu.clicked.connect(self.buttonColor)
        widgets.btn_VK_compare_menu.clicked.connect(openCloseCompareBox) 
        widgets.btn_VK_compare_menu.clicked.connect(lambda :self.colorTab('Compare'))
        
        #KMD plot
        widgets.btn_KMD_compare_menu.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_KMD_compare_menu.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_compare_KMD))  
        widgets.btn_KMD_compare_menu.clicked.connect(self.buttonColor)
        widgets.btn_KMD_compare_menu.clicked.connect(openCloseCompareBox) 
        widgets.btn_KMD_compare_menu.clicked.connect(lambda :self.colorTab('Compare'))
        
        #EV plot
        widgets.btn_EV_compare_menu.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.compare))
        widgets.btn_EV_compare_menu.clicked.connect(lambda : widgets.Compare_stacked_widget.setCurrentWidget(widgets.page_compare_EV))  
        widgets.btn_EV_compare_menu.clicked.connect(self.buttonColor)
        widgets.btn_EV_compare_menu.clicked.connect(openCloseCompareBox) 
        widgets.btn_EV_compare_menu.clicked.connect(lambda :self.colorTab('Compare'))

#/////////////////////////////////    
#   COMPARE\OVERVIEW BUTTONS CONNECTIONS
#/////////////////////////////////

            #Displays mass spectrum widget
        widgets.radio_mass_spectrum_compare.clicked.connect(lambda : widgets.stackedWidget_overview_compare.setCurrentWidget(widgets.page_mass_spectrum_compare))
            #Displays distribution widget
        widgets.radio_distribution_compare.clicked.connect(lambda : widgets.stackedWidget_overview_compare.setCurrentWidget(widgets.page_distribution_compare))

            #Displays Composition widget
        widgets.radio_composition_compare.clicked.connect(lambda : widgets.stackedWidget_overview_compare.setCurrentWidget(widgets.page_composition_compare))
        
#/////////////////////////////////    
#   COMPARE\FC PLOTS BUTTONS CONNECTIONS
#/////////////////////////////////        
        
            #Displays DBE widget
        widgets.btn_DBE_compare.clicked.connect(lambda : widgets.stackedWidget_FC.setCurrentWidget(widgets.page_DBE_compare))
            #Displays Van Krevelen widget
        widgets.btn_VK_compare.clicked.connect(lambda : widgets.stackedWidget_FC.setCurrentWidget(widgets.page_VK_compare))

#/////////////////////////////////    
#   COMPARE\KENDRICK BUTTONS CONNECTIONS
#/////////////////////////////////
        widgets.buttonKendrickStd_comp.clicked.connect(lambda : widgets.stackedWidget_Kendrick_comp.setCurrentWidget(widgets.page_std_comp))
        widgets.buttonKendrickUniv_comp.clicked.connect(lambda : widgets.stackedWidget_Kendrick_comp.setCurrentWidget(widgets.page_univ_2))

#/////////////////////////////////  
#   COMPARE\EV BUTTONS CONNECTIONS
#/////////////////////////////////  

        widgets.radio_ACOS_comp.clicked.connect(lambda : widgets.stackedWidget_EV_comp.setCurrentWidget(widgets.page_ACOS_comp))
        widgets.radio_MAI_comp.clicked.connect(lambda : widgets.stackedWidget_EV_comp.setCurrentWidget(widgets.page_MAI_comp))
        widgets.radio_MCR_comp.clicked.connect(lambda : widgets.stackedWidget_EV_comp.setCurrentWidget(widgets.page_MCR_comp))
        
#///////////////////////////////////////////////       
#STATS BUTTONS CONNECTIONS
#///////////////////////////////////////////////

        #Classic open/close
        widgets.btn_stats.clicked.connect(openCloseStatsBox)
        widgets.statsCloseColumnBtn.clicked.connect(openCloseStatsBox) 

        #Displays venn page
        widgets.btn_venn.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.stats))
        widgets.btn_venn.clicked.connect(lambda : widgets.stats_stacked_widget.setCurrentWidget(widgets.page_venn))
        widgets.btn_venn.clicked.connect(self.buttonColor)
        widgets.btn_venn.clicked.connect(openCloseStatsBox) 
        widgets.btn_venn.clicked.connect(lambda :self.colorTab('Stats'))

        #Displays PCA page
        widgets.btn_PCA.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.stats))
        widgets.btn_PCA.clicked.connect(lambda : widgets.stats_stacked_widget.setCurrentWidget(widgets.page_PCA))
        widgets.btn_PCA.clicked.connect(self.buttonColor)
        widgets.btn_PCA.clicked.connect(openCloseStatsBox) 
        widgets.btn_PCA.clicked.connect(lambda :self.colorTab('Stats'))

        #Displays HCA page
        widgets.btn_HCA.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.stats))
        widgets.btn_HCA.clicked.connect(lambda : widgets.stats_stacked_widget.setCurrentWidget(widgets.page_HCA))
        widgets.btn_HCA.clicked.connect(self.buttonColor)
        widgets.btn_HCA.clicked.connect(openCloseStatsBox) 
        widgets.btn_HCA.clicked.connect(lambda :self.colorTab('Stats'))

        #Displays volcano page
        widgets.btn_Volcano.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.stats))
        widgets.btn_Volcano.clicked.connect(lambda : widgets.stats_stacked_widget.setCurrentWidget(widgets.page_Volcano))
        widgets.btn_Volcano.clicked.connect(self.buttonColor)
        widgets.btn_Volcano.clicked.connect(openCloseStatsBox) 
        widgets.btn_Volcano.clicked.connect(lambda :self.colorTab('Stats'))
 
        
#------------------------------------------------------------------------------   
#BUTTONS ASSIGNMENTS (FUNCTIONS SECTION)
#------------------------------------------------------------------------------    

#Plot buttons

    #Loaded files list

        widgets.list_loaded_file.itemSelectionChanged.connect(self.btn_enabling)
        widgets.list_loaded_file.itemSelectionChanged.connect(self.split_classes)
        widgets.list_loaded_file_2.itemSelectionChanged.connect(self.split_classes_merged)
        widgets.list_distribution.itemSelectionChanged.connect(self.distrib_pannel)
        widgets.list_distribution_compare.itemSelectionChanged.connect(self.distribution_compare_pannel)
        widgets.list_loaded_file_compare.itemSelectionChanged.connect(self.compare_calculation)
        widgets.list_loaded_file_compare.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        widgets.list_classes_distrib.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        widgets.list_compare_sample_1.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        widgets.list_compare_sample_2.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    
    
    #Plot View
        widgets.plot_button_view.clicked.connect(self.viewPlot)
        widgets.plot_button_view_GIF.clicked.connect(self.viewGif)
        

    #Overview
    
        
        widgets.list_classes_mass_spec.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        widgets.list_classes_mass_spec_comp.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
    
    
    
    #Kendrick
     
        widgets.pushButton_clearSeries.clicked.connect(self.clear_series)
        widgets.plot_button_saveKendrick.clicked.connect(self.save_kendrick_series)
        widgets.edit_motif.textChanged.connect(self.kendrick_motif_calculation)
    
    
    #Graphic parameters
     
        widgets.list_color_map.itemSelectionChanged.connect(self.colormap)
        
    
    
    #Compare buttons
    ##Overview    
        widgets.plot_compare.clicked.connect(self.comparePlot)
        widgets.plot_compare_GIF.clicked.connect(self.comparePlotGIF)

        
    #Stat buttons
    ##Plot Stats
        widgets.plot_button_stats.clicked.connect(self.statsPlot)

    
        #PCA
        widgets.save_button_pca_coef.clicked.connect(self.save_pca_coef)
    
        #HCA
        widgets.hca_intensity_classic.clicked.connect(self.plot_HCA)
        widgets.hca_intensity_sqrt.clicked.connect(self.plot_HCA)
        widgets.hca_orientation_left.clicked.connect(self.plot_HCA)
        widgets.hca_orientation_top.clicked.connect(self.plot_HCA)
    
        #Venn
        widgets.list_sets.itemSelectionChanged.connect(self.select_set_venn)
        widgets.Save_Sets_Button.clicked.connect(self.save_sets_venn)
    
        
    
    #File
        widgets.btn_load_file.clicked.connect(self.load_file_method)
        widgets.btn_clear.clicked.connect(self.clear_loaded_list)
        widgets.btn_settings.clicked.connect(lambda : widgets.stackedWidget.setCurrentWidget(widgets.graph_param))
        widgets.btn_save.clicked.connect(self.save_file)  
    
    #Process
        widgets.btn_merge_att.clicked.connect(self.merge_files)
        widgets.btn_fuse.clicked.connect(self.fusion_replicats)
        widgets.btn_merge_mer.clicked.connect(self.merge_merged_files)
        widgets.btn_merge_xcalibur.clicked.connect(self.merge_Multicsv)
        widgets.btn_merge_una.clicked.connect(self.merge_asc)


#///////////////////////////////////////////////     
#MISC
#///////////////////////////////////////////////  
    #About
        widgets.btn_about.clicked.connect(self.about)
    
        sh = win32com.client.gencache.EnsureDispatch('Shell.Application', 0)
        ns = sh.NameSpace(os.getcwd())
    
        # Enumeration is necessary because ns.GetDetailsOf only accepts an integer as 2nd argument
        
        item = ns.ParseName('PyC2MC_Viewer.exe')
        ind = 3
        if item == None:
            item = ns.ParseName('main.py')
            ind = 4
        self.last_modified = ns.GetDetailsOf(item, ind)
        
    #Easter
        widgets.Easter_egg.clicked.connect(self.easter_egg)
        widgets.Easter_egg2.clicked.connect(self.easter_egg)

#///////////////////////////////////////////////       
#GENERAL EVENTS
#///////////////////////////////////////////////

    # WINDOW OPENING EVENTS
    # ///////////////////////////////////////////////////////////////

    def start_splitfinder(self):
        """
        Starts the SplitFinder module.
        """
        try:
            if self.splitfinder:
                self.splitfinder.close()
        except:
            pass
        self.splitfinder = Splitfinder()
        self.splitfinder.show()

    def easter_egg(self):
        """
        Find out yourself !
        """
        if self.start_counter:
            self.click_count=self.click_count+1
            if time.time() - self.start_counter > 1.5:
                self.start_counter=False
                self.click_count=[]
                return
            if self.click_count==5:
                try:
                    easter()
                except:
                    return

        else:
            self.start_counter=time.time()
            self.click_count=1
    
    def write_csv_df(self,path, filename, df):
        # Give the filename you wish to save the file to
        pathfile = os.path.normpath(os.path.join(path,filename))

        # Use this function to search for any files which match your filename
        files_present = os.path.isfile(pathfile) 
        # if no matching files, write to csv, if there are matching files, print statement
        if not files_present:
            df.to_csv(pathfile, sep=';',index = False)
            QMessageBox.about(self, "FYI box", "Your file was correctly saved.")
        else:
            overwrite_msg = "A file with this name already exist in this directory. Would you like to overwrite it ?"
            overwrite = QMessageBox.question(self, 'Message',
                             overwrite_msg, QMessageBox.Yes, QMessageBox.No)
            if overwrite == QMessageBox.Yes:
                try:
                    df.to_csv(pathfile, sep=';', index = False)
                    QMessageBox.about(self, "FYI box", "Your file was correctly saved.")
                except:
                    msg = "A problem occured. Check if the file to replace is open."
                    reply = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok, QMessageBox.Ok)   
                    return
            elif overwrite == QMessageBox.No:
                new_filename, okPressed = QInputDialog.getText(self, "Save Name","Name of the merged file: ", QLineEdit.Normal, "")
                self.write_csv_df(path,new_filename+'.csv',df)
            else:
                msg = "Not a valid input. Data is NOT saved!\n"
                reply = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok, QMessageBox.Ok)      
                
    def about(self,last_modified):
        """
        Links the github page in a new window
        """
        link_git = "https://github.com/iC2MC/PyC2MC_viewer"
        email = "maxime.sueur1@univ-rouen.fr"
        link_preprint = "https://doi.org/10.26434/chemrxiv-2022-cmnk3"
        msg = "PyC2MC Viewer: a FTMS data visualization software. <br><br>\
            Want to improve the application ? Join us on <a href='%s'>GitHub</a> <br><br> \
            When using PyC2MC, please cite our <a href='%s'>preprint article</a>. <br><br>\
            Version modified on %s <br><br> \
            GUI based on PyDracula by Wanderson M. Pimenta." % (link_git,link_preprint,self.last_modified)
        reply = QMessageBox.information(self, 'Message', msg, QMessageBox.Ok, QMessageBox.Ok)
    # RECOLOR EVENTS
    # ///////////////////////////////////////////////////////////////
    def colorTab(self,tab):
        """
        CHANGES THE COLOR OF THE ACTIVE  TAB
        """
        if hasattr(self,'bak_view') :
            widgets.btn_view.setStyleSheet(self.bak_view)
            widgets.btn_compare.setStyleSheet(self.bak_comp)
            widgets.btn_stats.setStyleSheet(self.bak_stats)
            
        self.bak_view = widgets.btn_view.styleSheet()
        self.bak_comp = widgets.btn_compare.styleSheet()
        self.bak_stats = widgets.btn_stats.styleSheet()
        
        if tab == 'View':
            widgets.btn_view.setStyleSheet(self.bak_view+ "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}")
        elif tab == "Compare":
            widgets.btn_compare.setStyleSheet(self.bak_comp+ "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}")
        elif tab == 'Stats':
            widgets.btn_stats.setStyleSheet(self.bak_stats+ "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}")
        
    def buttonColor(self):
        """
        CHANGES THE COLOR OF THE LAST BUTTON CLICKED
        """
        
        btn = self.sender()
        if btn.objectName() == "list_loaded_file": #Exception for peaklists:
            btn = widgets.btn_kendricks
        if hasattr(self,'btn_bak') :
            self.btn_bak.setStyleSheet(self.style_backup)
        self.style_backup = btn.styleSheet()
        if btn.objectName() == "btn_settings": # Exception to keep the icon
            btn.setStyleSheet("QPushButton {background-color:  rgb(200,200,200);\n" + self.style_backup + "}")
            self.colorTab('')
        else:
            btn.setStyleSheet("QPushButton {background-color:  rgb(208,208,208);\n" + self.style_backup + "}")
        self.btn_bak = btn

        
    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        """
        Update Size Grips
        """
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        """
        SET DRAG POS WINDOW
        """
        self.dragPos = event.globalPos()
       
#///////////////////////////////////////////////       
#APP FUNCTIONS
#///////////////////////////////////////////////       
    #---------------------------------------
    #      Select plot to draw from View tab
    #---------------------------------------

    def viewPlot(self):
        """
        Select plot to draw from View tab
        """
        ind=widgets.choose_plot_stacked.currentIndex()
        
        if ind == 0:
            self.overview()
        elif ind == 1:
            self.plot_DBE()
        elif ind == 2:
            self.plot_VK()
        elif ind == 3:
            self.plot_Kendrick()
        elif ind == 4:
            self.envt_selector()
            
    #---------------------------------------
    #      Select plot to draw from View tab (GIF version)
    #---------------------------------------      
    def viewGif(self):
        """
        Select plot to draw from View tab
        """
        ind=widgets.choose_plot_stacked.currentIndex()
        if ind == 0:
            self.overview(gif = True)
        elif ind == 1:
            self.plot_DBE(gif = True)
        elif ind == 2:
            self.plot_VK(gif = True)
        elif ind == 3:
            self.plot_Kendrick(gif = True)
        elif ind == 4:
            self.envt_selector(gif = True)
    #---------------------------------------
    #      Select plot to draw from Compare tab
    #---------------------------------------

    def comparePlot(self):
        """
        Select plot to draw from Compare tab
        """
        ind = widgets.Compare_stacked_widget.currentIndex()
        
        if ind == 0: #overview
            ind_bis = widgets.stackedWidget_overview_compare.currentIndex()
            if ind_bis == 0:
                self.plot_composition_compare()
            elif ind_bis == 1:
                self.plot_distrib_compare()
            elif ind_bis == 2:
                self.plot_spectrum_compare()
        
        elif ind == 1: #FC
            ind_bis = widgets.stackedWidget_FC.currentIndex()
            if ind_bis == 0:
                self.plot_molecular_carto_DBE()
            elif ind_bis == 1:
                self.plot_molecular_carto_VK()
        
        elif ind == 2:  #DBE
            self.plot_DBE_compare()
                
        elif ind == 3: #VK
            self.plot_VK_compare()
            
        elif ind == 4: #KMD
            self.plot_KMD_compare()
        
        elif ind == 5: #EV variables
            self.envt_selector_compare()
            
    #---------------------------------------
    #      Select plot to draw from Compare tab (GIF version)
    #---------------------------------------

    def comparePlotGIF(self):
        """
        Select plot to draw from Compare tab
        """
        ind = widgets.Compare_stacked_widget.currentIndex()
        
        if ind == 0:
            ind_bis = widgets.stackedWidget_overview_compare.currentIndex()
            if ind_bis == 0:
                self.plot_composition_compare()
            elif ind_bis == 1:
                self.plot_distrib_compare(gif = True)
            elif ind_bis == 2:
                self.plot_spectrum_compare()
        
        elif ind == 1:
            ind_bis = widgets.stackedWidget_FC.currentIndex()
            if ind_bis == 0:
                self.plot_molecular_carto_DBE(gif = True)
            elif ind_bis == 1:
                self.plot_molecular_carto_VK(gif = True)
                
        elif ind == 2:  #DBE
            self.plot_DBE_compare(gif = True)
                
        elif ind == 3: #VK
            self.plot_VK_compare(gif = True)
            
        elif ind == 4: #KMD
            self.plot_KMD_compare(gif = True)
            
        elif ind == 5: #EV variables
            self.envt_selector_compare(gif = True)    
            
    #---------------------------------------
    #      Select plot to draw from Stats tab
    #---------------------------------------

    def statsPlot(self):
        """
        Select plot to draw from Stats tab
        """
        ind=widgets.stats_stacked_widget.currentIndex()
        
        if ind == 0:
            self.venn()
        elif ind == 1:
            self.plot_PCA()
        elif ind == 2:
            self.plot_HCA()
        elif ind == 3:
            self.volcano()
            
            
    #---------------------------------------
    #      GUI reset on selection change
    #---------------------------------------

    def btn_enabling(self):
        """
        Enables every GUI button (acts as a GUI reset).
        """
        widgets.btn_stats.setEnabled(True)
        widgets.btn_overview.setEnabled(True)
        widgets.btn_DBE.setEnabled(True)
        widgets.btn_EV.setEnabled(True)
        widgets.btn_van_krevelen.setEnabled(True) 
        widgets.plot_button_view.setEnabled(True)
        widgets.plot_compare.setEnabled(True)
        widgets.plot_compare_GIF.setEnabled(True)
        widgets.radio_composition.setEnabled(True)
        widgets.radio_error_plots.setEnabled(True)
        widgets.radio_distributions.setEnabled(True)
        widgets.radio_mass_spectrum.setEnabled(True)

    #---------------------------------------
    #       Color map choice
    #---------------------------------------

    def colormap(self):
        """
        Reads the colormap parameter in the GUI.
        """
        cmp=widgets.list_color_map.currentItem()
        self.color_map=cmp.text()
        white_text_cm =['viridis','cividis','plasma']
    
        if cmp.text() in white_text_cm:
            self.cm_text_color = "white"
        else:
            self.cm_text_color = "black"
        
    #---------------------------------------
    #       Clear loaded lists
    #---------------------------------------

    def clear_loaded_list(self):
        """
        Clears the loaded files lists
        """
        widgets.list_loaded_file.clear()
        widgets.list_loaded_file_2.clear()
        widgets.list_loaded_file_compare.clear()
        widgets.list_compare_sample_1.clear()
        widgets.list_compare_sample_2.clear()
        widgets.list_classes_mass_spec_comp.clear()
        widgets.list_classes_distrib_compare.clear()
        widgets.list_classes_DBE_compare.clear()
        widgets.list_classes_VK_compare.clear()
        widgets.list_classes_DBE_comp.clear()
        widgets.list_classes_VK_comp.clear()
        widgets.list_classes_Kendrick_comp.clear()
        widgets.list_classes_Kendrick_univ_comp.clear()
        try :
            plt.close("all")
        except:
            pass
        
    #---------------------------------------
    #       Load files
    #---------------------------------------

    def load_file_method(self):
        """
        Prepares the GUI and call the Loading_function
        """
        widgets.list_classes_DBE.clear()
        widgets.list_classes_mass_spec.clear()
        widgets.list_classes_error.clear()
        widgets.list_classes_VK.clear()
        widgets.list_classes_Kendrick.clear()
        widgets.list_classes_Kendrick_univ.clear()
        widgets.pbar.show()
        type_color={"PyC2MC_fusion":'#dd324d',"Peaklist":'#2d6bad',"Attributed":'#f0a23e',"PyC2MC_merged":'#42d66a',"PyC2MC_merged_unattributed":'#bfb0b7'}
        p = 0
        # Get the filepath
        filepath, _ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose one result file or more to import",filter="Results files (*.csv;*.asc;*.xlsx;*.xls)")
        if not filepath:
            widgets.pbar.hide()
            return
        path_old = os.getcwd()
        n=0
        widgets.pbar.setValue(p)

        while n<len(filepath):
            p = (n+1)/len(filepath)*100

            path_to_file = os.path.dirname(filepath[n])
            filename = str(os.path.basename(filepath[n]))
            # read data and create data frame
            os.chdir(path_to_file)
            # try :
            dataframe = load_MS_file(filename)
            # except Exception as err:  
            #     QMessageBox.about(self, "FYI box", f"A problem has occured with the following file: '{filename}', error is : {err}")
            #     n = n +1
            #     if n<len(filepath):
            #         p = (n+1)/len(filepath)*100

            #         path_to_file = os.path.dirname(filepath[n])
            #         filename = str(os.path.basename(filepath[n]))
            #         os.chdir(path_to_file)
            #         try :
            #             dataframe = load_MS_file(filename)
            #         except :  
            #             QMessageBox.about(self, "FYI box", f"A problem has occured with the following file: '{filename}'")
            pass
            
            try :
                test_var = dataframe.df 
                del test_var
            except : 
                return
            
            if dataframe.df_type == 'Error':
                QMessageBox.about(self, "FYI box", f".xlsx files should only come from CERES processing, '{filename}' isn't such a file")
                dataframe.df = pandas.DataFrame()
                pass
            os.chdir(path_old)
            if 'PC1' in dataframe.df: #Activates option if PCA coefficient are in dataframe
                widgets.radio_color_pc1.show()
                widgets.radio_color_pc2.show()
                widgets.radio_color_pc1_VK.show()
                widgets.radio_color_pc2_VK.show()
                widgets.radio_color_pc1_ACOS.show()
                widgets.radio_color_pc2_ACOS.show()

            ###-----------------------------------------------------------###
            # Display the dataframe(s) item(s) in the appropriate GUI lists #
            ###-----------------------------------------------------------###

            if dataframe.df_type == 'PyC2MC_merged':
                if 'std_dev_rel' in dataframe.df: #Fused replicates file (specific merging type)
                    #create items with text = filename for every appropriate Qlist (view and compare)
                    item = QtWidgets.QListWidgetItem(filename)
                    item_2 = QtWidgets.QListWidgetItem(filename+" ")
                    #Attribute data loaded to the items
                    item.setData(self.USERDATA_ROLE, dataframe)
                    item_2.setData(self.USERDATA_ROLE, dataframe)
                    #Display items in their respective Qlist
                    widgets.list_loaded_file_compare.addItem(item)
                    widgets.list_loaded_file.addItem(item_2)
                    #Set the color of the item for better identification
                    i=widgets.list_loaded_file.count()-1
                    j=widgets.list_loaded_file_compare.count()-1
                    qcolor=QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                    qcolor.setAlphaF(0.3)
                    widgets.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
                    widgets.list_loaded_file.item(i).setBackground(QColor(qcolor))

                else:    #Classical Merged file
                    #create items with text = filename for every appropriate Qlist (view and stats)
                    item = QtWidgets.QListWidgetItem(filename)
                    item_2 = QtWidgets.QListWidgetItem(filename+" ")
                    #Attribute data loaded to the items
                    item.setData(self.USERDATA_ROLE, dataframe)
                    item_2.setData(self.USERDATA_ROLE, dataframe)
                    #Display items in their respective Qlist
                    widgets.list_loaded_file.addItem(item)
                    widgets.list_loaded_file_2.addItem(item_2)
                    #Set the color of the item for better identification
                    i=widgets.list_loaded_file.count()-1
                    j=widgets.list_loaded_file_2.count()-1
                    qcolor=QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                    qcolor.setAlphaF(0.3)
                    widgets.list_loaded_file.item(i).setBackground(QColor(qcolor))
                    widgets.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
            elif dataframe.df_type == 'PyC2MC_merged_unattributed':  
                    item = QtWidgets.QListWidgetItem(filename)
                    #Attribute data loaded to the items
                    item.setData(self.USERDATA_ROLE, dataframe)
                    #Display items in their respective Qlist
                    widgets.list_loaded_file_2.addItem(item)
                    #Set the color of the item for better identification
                    j=widgets.list_loaded_file_2.count()-1
                    qcolor=QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                    qcolor.setAlphaF(0.3)
                    widgets.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
            
            elif dataframe.df_type == 'Peaklist':
                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                widgets.list_loaded_file.addItem(item)

                i=widgets.list_loaded_file.count()-1
                qcolor=QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                qcolor.setAlphaF(0.3)
                widgets.list_loaded_file.item(i).setBackground(QColor(qcolor))
            
            elif dataframe.df_type == 'Error':
                pass
                
            else: # simply attributed data
                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                widgets.list_loaded_file.addItem(item)

                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                widgets.list_loaded_file_compare.addItem(item)

                i=widgets.list_loaded_file.count()-1
                j=widgets.list_loaded_file_compare.count()-1
                qcolor=QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                qcolor.setAlphaF(0.3)
                widgets.list_loaded_file_compare.item(j).setBackground(QColor(qcolor))
                widgets.list_loaded_file.item(i).setBackground(QColor(qcolor))
            widgets.pbar.setValue(p)
            n=n+1

        
        self.latest_path=os.path.dirname(filepath[n-1])
        
        widgets.pbar.setValue(p)
        widgets.pbar.hide()

#---------------------------------------
#  Calling the merge function/module
#---------------------------------------

    def merge_files(self):
        """
        Calls the Merge Function and load the newly created .csv in the GUI
        """

    

        widgets.pbar.show()
        i=0
        widgets.pbar.setValue(i)
        try:
            filepath,_ = QtWidgets.QFileDialog.getOpenFileNames(filter="Results files (*.csv;*.asc;*.xlsx;*.xls)")
            names = []
            n = 0
            while n<len(filepath):
                i = (n+1)/len(filepath)*100
                widgets.pbar.setValue(i)
                
                filename = str(os.path.basename(filepath[n]))
                names.append(filename)
                n = n + 1
            path_to_file = os.path.dirname(filepath[0])
            os.chdir(path_to_file)
            path_old = os.getcwd()
            
        except:
            path_old = os.getcwd()
            return
        if len(names) == 1 :
            QMessageBox.about(self, "FYI box", "Only one file was selected ! Please, select several files.")
            widgets.pbar.hide()
            return
        save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        if okPressed and save_name != '':
            try :
                self.merged_data = merge_file(names)
            except:
                widgets.pbar.hide()
                QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
                return
        else:
            widgets.pbar.hide()
            QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
            return
        
        # os.chdir(path_to_file)
        # self.merged_data.to_csv(save_name +".csv",index = False)
        self.write_csv_df(path_to_file, save_name +".csv", self.merged_data)
        filename = save_name +".csv"
        dataframe = load_MS_file(filename)
        os.chdir(path_old)
        
        widgets.pbar.hide()
        
        
        #Load the created merged file
        item = QtWidgets.QListWidgetItem(filename)
        item_2 = QtWidgets.QListWidgetItem(filename+" ")
        #Attribute data loaded to the items
        item.setData(self.USERDATA_ROLE, dataframe)
        item_2.setData(self.USERDATA_ROLE, dataframe)
        #Display items in their respective Qlist
        widgets.list_loaded_file.addItem(item)
        widgets.list_loaded_file_2.addItem(item_2)
        #Set the color of the item for better identification
        i=widgets.list_loaded_file.count()-1
        j=widgets.list_loaded_file_2.count()-1
        qcolor=QColor('#42d66a')
        qcolor.setAlphaF(0.3)
        widgets.list_loaded_file.item(i).setBackground(QColor(qcolor))
        widgets.list_loaded_file_2.item(j).setBackground(QColor(qcolor))

    def fusion_replicats(self): 
        """
        Calls the Fusion_Replicats and load the newly created .csv in the GUI
        """
        widgets.pbar.show()
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(filter="Results files (*.csv;*.asc;*.xls;*.xlsx)")
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
        except:
            return
        try:
            replicats_tuple = QInputDialog.getInt(self,"Extraction of species common to x replicates","Species must be found in at least x samples : ",min=1,max=len(names[0]))
        except:
            QMessageBox.about(self, "FYI box", "Aborted")
        save_name, okPressed = QInputDialog.getText(self, "Filename and save name","Your name:", QLineEdit.Normal, "")
        i = 50
        widgets.pbar.setValue(i)
        replicats = replicats_tuple[0]
        if okPressed and save_name != '':
            try :
                self.merged_data = fuse_replicates(names,replicats)
            except:
                widgets.pbar.hide()
                QMessageBox.about(self, "FYI box", "Error, no files merged")
        self.write_csv_df(path_to_file, save_name +".csv", self.merged_data)
        os.chdir(path_old)
        widgets.pbar.hide()

    def merge_merged_files(self): 
        """
        Calls the Merge_merged_files function and load the newly created .csv in the GUI
        """
        widgets.pbar.show()
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(filter="Results files (*.csv)")
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
            save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        except:
            return
        i = 50
        widgets.pbar.setValue(i)
        if okPressed and save_name != '':
            try :
                self.merged_data = merge_merged_file(names)
            except:
                widgets.pbar.hide()
                QMessageBox.about(self, "FYI box", "You can only merge the same type of file")
                return
        # os.chdir(path_to_file)
        # self.merged_data.to_csv(save_name +".csv",index = False)
        self.write_csv_df(path_to_file, save_name +".csv", self.merged_data)

        os.chdir(path_old)
        widgets.pbar.hide()

    def merge_Multicsv(self) : #Merged files from sequential attribution (Obritrap only) (To update ?)
        
        widgets.pbar.show()
        i=0
        widgets.pbar.setValue(i)
        try:
            filepath,_ = QtWidgets.QFileDialog.getOpenFileNames(filter="Results files (*.csv;*.asc;*.xlsx;*.xls)")
            names = []
            n = 0
            while n<len(filepath):
                i = (n+1)/len(filepath)*100
                widgets.pbar.setValue(i)
                
                filename = str(os.path.basename(filepath[n]))
                names.append(filename)
                n = n + 1
            path_to_file = os.path.dirname(filepath[0])
            os.chdir(path_to_file)
            path_old = os.getcwd()
            
        except:
            path_old = os.getcwd()
            return
        if len(names) == 1 :
            QMessageBox.about(self, "FYI box", "Only one file was selected ! Please, select several files.")
            widgets.pbar.hide()
            return
    
        
        save_name, okPressed = QInputDialog.getText(self, "Save Name","Name of the merged file:", QLineEdit.Normal, "")
        
        i = 50
        widgets.pbar.setValue(i)
        try:
            if okPressed and save_name != '':
                widgets.merged_data = merge_Multicsv(names)
        except:
            QMessageBox.about(self, "FYI box", "An error has occurred")
            widgets.pbar.hide()
            return
        os.chdir(path_to_file)
        self.write_csv_df(path_to_file, save_name +".csv", widgets.merged_data)

        os.chdir(path_old)
        widgets.pbar.hide()

    def merge_asc(self):
        """
        Calls the Merge Function for unnatributed data and load the newly created .csv in the GUI
        """
        widgets.pbar.show()
        i=0
        widgets.pbar.setValue(i)
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(filter="Ascii files from DA (*.asc)")
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
            os.chdir(path_to_file)
            tol = QInputDialog.getDouble(self,"Choose of the Tolerance for merging","I want to use a tolerance of (Da, min = 0.00001 max : 0.0005): ",value  = 0.00010,min=0.00001,max=0.00050,decimals = 5)
            save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")

        except:
            path_old = os.getcwd()
            return
        i = 50     
        widgets.pbar.setValue(i)
        if okPressed and save_name != '':
            try :
                self.merged_data = merge_non_attributed(names,tol)
            except:
                widgets.pbar.hide()
                QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
                return
        else:
            widgets.pbar.hide()
            QMessageBox.about(self, "FYI box", "No or wrong saving name")
            return
        try :
            self.write_csv_df(path_to_file, save_name +".csv", self.merged_data)

            filename = save_name +".csv"
            dataframe = load_MS_file(filename)
            os.chdir(path_old)
            widgets.pbar.hide()
            
            #Load the created merged file
            item_2 = QtWidgets.QListWidgetItem(filename+" ")
            #Attribute data loaded to the items
            item_2.setData(self.USERDATA_ROLE, dataframe)
            #Display items in their respective Qlist
            widgets.list_loaded_file_2.addItem(item_2)
            #Set the color of the item for better identification
            j=widgets.list_loaded_file_2.count()-1
            qcolor=QColor('#bfb0b7')
            qcolor.setAlphaF(0.3)
            widgets.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
        except:
            widgets.pbar.hide()
            QMessageBox.about(self, "FYI box", "An error occurs during the saving of your file")
            return      
        
#---------------------------------------
#       Read graphic parameter
#---------------------------------------

    def read_param(self):
        """
        Reads graphic paramaters from the GUI
        """
        if widgets.radio_size_and_color.isChecked():
            self.dot_type='sc'
        elif widgets.radio_color.isChecked():
            self.dot_type='c'
        elif widgets.radio_size.isChecked():
            self.dot_type='s'

        self.d_size=float(widgets.dot_size.text())
        self.fontsize = float(widgets.font_size.text())
        self.edge=widgets.CheckBox_edge.isChecked()
        self.para_dict = {'dt' : self.dot_type,'ds' : self.d_size, 'fs' : self.fontsize, 'cm' : self.color_map}
        
        self.fps = float(widgets.gif_fps.text())
        matplotlib.rcParams['savefig.dpi'] = widgets.saveDPI.text()


#---------------------------------------
#    Distribution pannel activation
#          on selection changes
#---------------------------------------

    def distrib_pannel(self):
        """
        Enables GUI elements in the View->Overview->Distribution panel
        """
        x_axes = widgets.list_distribution.currentRow()
        if x_axes == 0:
            widgets.groupBox_18.setEnabled(True)
        if x_axes == 1:
            widgets.groupBox_18.setEnabled(False)
            widgets.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 2:
            widgets.groupBox_18.setEnabled(False)
            widgets.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 3:
            widgets.groupBox_18.setEnabled(False)
            widgets.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 4:
            widgets.groupBox_18.setEnabled(False)
            widgets.radio_both_intens_vs_DBE.setChecked(True)

    def distribution_compare_pannel(self):
        """
        Enables GUI elements in the Compare->Overview->Distribution panel
        """
        x_axes = widgets.list_distribution_compare.currentRow()
        if x_axes == 0:
            widgets.groupBox_37.setEnabled(True)
        if x_axes == 1:
            widgets.groupBox_37.setEnabled(False)
            widgets.radio_both_DBE_compare.setChecked(True)
        if x_axes == 2:
            widgets.groupBox_37.setEnabled(False)
            widgets.radio_both_DBE_compare.setChecked(True)
        if x_axes == 3:
            widgets.groupBox_37.setEnabled(False)
            widgets.radio_both_DBE_compare.setChecked(True)
        if x_axes == 4:
            widgets.groupBox_37.setEnabled(False)
            widgets.radio_both_DBE_compare.setChecked(True)
#---------------------------------------
#Splitting classes on selection changes
#                  +
#      GUI adaptation to dataset
#                  +
#          Data qualification
#---------------------------------------

    def split_classes(self):
        """
        Identifies chemical classes and PCA coeficient (if any) of the loaded Peak_list class and activates relevants GUI elements
        """
        
        
        widgets.list_classes_DBE.clear()
        widgets.list_classes_mass_spec.clear()
        widgets.list_classes_error.clear()
        widgets.list_classes_VK.clear()
        widgets.list_classes_Kendrick.clear()
        widgets.list_classes_Kendrick_univ.clear()
        widgets.list_classes_distrib.clear()
        widgets.list_classes_ACOS.clear()
        widgets.list_classes_MAI.clear()
        widgets.list_classes_MCR.clear()
        widgets.list_classes_ACOS_comp.clear()
        widgets.list_classes_MAI_comp.clear()
        widgets.list_classes_MCR_comp.clear()
        items = widgets.list_loaded_file.selectedItems()
        if not items:
            return
        item = items[0]
        self.data = item.data(self.USERDATA_ROLE)
        n = 0
        if self.data.df_type == "PyC2MC_merged":
            widgets.stackedWidget_overview.setCurrentWidget(widgets.page_composition)
            widgets.radio_composition.setChecked(True)
            widgets.radio_error_plots.setEnabled(False)
            widgets.radio_distributions.setEnabled(True)
            widgets.radio_mass_spectrum.setEnabled(False)
            widgets.K_nitrogen.setEnabled(True)
            widgets.K_oxygen.setEnabled(True)
            widgets.K_sulfur.setEnabled(True)
            widgets.btn_kendricks.setEnabled(True)


        elif self.data.df_type == "PyC2MC_fusion":
            widgets.stackedWidget_overview.setCurrentWidget(widgets.page_composition)
            widgets.radio_composition.setChecked(True)
            widgets.radio_error_plots.setEnabled(False)
            widgets.radio_distributions.setEnabled(True)
            widgets.radio_mass_spectrum.setEnabled(True)
            widgets.K_nitrogen.setEnabled(True)
            widgets.K_oxygen.setEnabled(True)
            widgets.K_sulfur.setEnabled(True)
            widgets.btn_kendricks.setEnabled(True)

        elif self.data.df_type == "Peaklist":
            widgets.choose_plot_stacked.setCurrentWidget(widgets.page_Kendrick)
            widgets.stackedWidget_overview.setCurrentWidget(widgets.page_mass_spectrum)
            widgets.btn_stats.setEnabled(False)
            widgets.btn_overview.setEnabled(False)
            widgets.btn_EV.setEnabled(False)
            widgets.radio_composition.setEnabled(False)
            widgets.radio_mass_spectrum.setChecked(True)
            widgets.radio_error_plots.setEnabled(False)
            widgets.radio_distributions.setEnabled(False)
            widgets.btn_DBE.setEnabled(False)
            widgets.btn_van_krevelen.setEnabled(False)
            widgets.K_nitrogen.setEnabled(False)
            widgets.K_oxygen.setEnabled(False)
            widgets.K_sulfur.setEnabled(False)
            widgets.btn_kendricks.setEnabled(True)
            self.buttonColor()
            return
        elif self.data.df_type == "PyC2MC_merged_unattributed":
            widgets.plot_button_view.setEnabled(False)
            widgets.plot_compare.setEnabled(False)
            widgets.plot_compare_GIF.setEnabled(False)
            return    

        if 'PC1' in self.data.df:
            widgets.radio_color_pc1.show()
            widgets.radio_color_pc2.show()
            widgets.radio_color_pc1_VK.show()
            widgets.radio_color_pc2_VK.show()
            widgets.radio_color_pc1.setEnabled(True)
            widgets.radio_color_pc2.setEnabled(True)
            widgets.radio_color_pc1_VK.setEnabled(True)
            widgets.radio_color_pc2_VK.setEnabled(True)
            widgets.radio_color_pc1_ACOS.setEnabled(True)
            widgets.radio_color_pc2_ACOS.setEnabled(True)
            widgets.K_nitrogen.setEnabled(True)
            widgets.K_oxygen.setEnabled(True)
            widgets.K_sulfur.setEnabled(True)
            widgets.btn_kendricks.setEnabled(True)

        else:
            widgets.radio_color_pc1.hide()
            widgets.radio_color_pc2.hide()
            widgets.radio_color_pc1_VK.hide()
            widgets.radio_color_pc2_VK.hide()
            widgets.radio_color_pc1.setEnabled(False)
            widgets.radio_color_pc2.setEnabled(False)
            widgets.radio_color_pc1_VK.setEnabled(False)
            widgets.radio_color_pc2_VK.setEnabled(False)
            widgets.radio_color_pc1_ACOS.setEnabled(False)
            widgets.radio_color_pc2_ACOS.setEnabled(False)
            widgets.radio_color_intensity_2.setChecked(True)
            widgets.radio_color_intensity_3.setChecked(True)
            widgets.K_nitrogen.setEnabled(True)
            widgets.K_oxygen.setEnabled(True)
            widgets.K_sulfur.setEnabled(True)
            widgets.btn_kendricks.setEnabled(True)
            
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_DBE.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_VK.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_Kendrick.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_Kendrick_univ.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_mass_spec.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_distrib.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_ACOS.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_MAI.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_MCR.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_error.addItem(item_classes)
        

        while n < len(self.data.classes):
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_DBE.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_VK.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_Kendrick.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_Kendrick_univ.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_mass_spec.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_distrib.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_ACOS.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_MAI.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_MCR.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_ACOS_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_MAI_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_MCR_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.data.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n,0])
            widgets.list_classes_error.addItem(item_classes)
            n = n+1
        widgets.list_classes_distrib.setCurrentRow(0)
        widgets.list_classes_error.setCurrentRow(0)

    def split_classes_merged(self):
        """
        Identifies chemical classes and PCA coeficient (if any) of the loaded Peak_list class and activates relevants GUI elements (for a merged file)
        """
        widgets.list_sample_1.clear()
        widgets.list_sample_2.clear()
        widgets.volc_color_classes.setEnabled(True)
        widgets.volc_color_dbe.setEnabled(True)
        widgets.volc_color_oc.setEnabled(True)
        item_file = widgets.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        if data_selected.df_type == 'PyC2MC_merged':
            volc_data = data_selected.volc_data
            volc_data.columns=volc_data.columns.str.replace(".csv","")
            volc_data.columns=volc_data.columns.str.replace('Rel_intens_','')
            self.volc_data=volc_data
            n=2
            while n < len(volc_data.columns)-5:
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                widgets.list_sample_1.addItem(item_sample)
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                widgets.list_sample_2.addItem(item_sample)
                n=n+1
        elif data_selected.df_type == 'PyC2MC_merged_unattributed' :
            widgets.volc_color_classes.setEnabled(False)
            widgets.volc_color_dbe.setEnabled(False)
            widgets.volc_color_oc.setEnabled(False)
            widgets.volc_color_mz.setChecked(True)
            volc_data = data_selected.volc_data
            volc_data.columns=volc_data.columns.str.replace('Rel_intens_','')
            self.volc_data=volc_data
            n=2
            while n < len(volc_data.columns):
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                widgets.list_sample_1.addItem(item_sample)
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                widgets.list_sample_2.addItem(item_sample)
                n=n+1
                            
    def save_file(self):
        """
        Export chemical classes data of the selected file to .csv
        """

        
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        os.chdir(save_path)
        # data_selected.df.to_csv(save_name +".csv",index = False)
        self.write_csv_df(save_path, save_name +".csv", data_selected.df)
        

#---------------------------------------
#   Plot section
#---------------------------------------

    def overview(self, gif = False):
        """
        Plotting function in the overview panel
        """
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        self.read_param()
        font_size = self.fontsize
            
        ##############
        #Composition
        ##############
        
        if widgets.radio_composition.isChecked():
            if widgets.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            data_selected = item.data(self.USERDATA_ROLE)
            data = data_selected.classes
            item_classes = widgets.list_loaded_file.selectedItems()
            if not item_classes:
                return
            fig, ax = plt.subplots()

            for i in range(len(item_classes)):
                data_selected = item_classes[i].data(self.USERDATA_ROLE)
                if 'count' in data_selected.df:
                    capsize=5
                    if widgets.radio_classes.isChecked():
                        if widgets.edit_min_intensity_classes.text():
                            min_intens_classes = float(widgets.edit_min_intensity_classes.text())
                            data = data_selected.classes[~data_selected.classes['variable'].str.contains("x")]
                            data = data[data['value'] > min_intens_classes]
                        else:
                            data = data_selected.classes[~data_selected.classes['variable'].str.contains("x")]
                    else:
                        if widgets.edit_min_intensity_classes.text():
                            min_intens_classes = float(widgets.edit_min_intensity_classes.text())
                            data = data_selected.classes[data_selected.classes['variable'].str.contains("x")]
                            if 'CH' in data_selected.classes['variable'].values:
                                data = data.append(data_selected.classes[data_selected.classes['variable'].str.contains("CH")])
                            data = data[data['value'] > min_intens_classes]
                        else:
                            data = data_selected.classes[data_selected.classes['variable'].str.contains("x")]
                    data = data.sort_values('value',ascending = False)
                    data = data.reset_index(drop = True)
                    if widgets.radio_comp_int.isChecked():
                        ax.bar(data['variable'], data['value'],yerr=data['std_dev_rel'], align='center', ecolor='black', capsize=capsize)
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(str(data['variable'].iloc[sel.target.index]) 
                        + ': Rel. Intensity  = ' + str(round(data['value'].iloc[sel.target.index],2)) + '%, std deviation = ' 
                        + str(round(data['std_dev_rel'].iloc[sel.target.index],2)) + '%'))
                    elif widgets.radio_comp_nb.isChecked():
                        ax.bar(data['variable'], data['number'])
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(str(data['variable'].iloc[sel.target.index]) 
                        + ': Count  = ' + str(int(data['number'].iloc[sel.target.index]))))

                else:
                    if widgets.radio_classes.isChecked():
                        if widgets.edit_min_intensity_classes.text():
                            min_intens_classes = float(widgets.edit_min_intensity_classes.text())
                            data = data[~data['variable'].str.contains("x")]
                            data = data[data['value'] > min_intens_classes]
                        else:
                            data = data[~data['variable'].str.contains("x")]
                    else:
                        if widgets.edit_min_intensity_classes.text():
                            min_intens_classes = float(widgets.edit_min_intensity_classes.text())
                            data_temp = data[data['variable'].str.contains("x")]
                            data  = data_temp.append(data[data['variable'].str.contains("CH")])
                            data = data[data['value'] > min_intens_classes]
                        else:
                            data_temp = data[data['variable'].str.contains("x")]
                            data  = data_temp.append(data[data['variable'].str.contains("CH")])
                    data = data.sort_values('value',ascending = False)
                    data = data.reset_index(drop = True)
                    if widgets.radio_comp_int.isChecked():
                        ax.bar(data['variable'], data['value'])
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(str(data['variable'].iloc[sel.target.index]) 
                        + ': Rel. Intensity  = ' + str(round(data['value'].iloc[sel.target.index],2)) + '%'))
                    elif widgets.radio_comp_nb.isChecked():
                        ax.bar(data['variable'], data['number'])
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(str(data['variable'].iloc[sel.target.index])
                        + ': Count  = ' + str(int(data['number'].iloc[sel.target.index]))))
            
            plt.suptitle('Heteroatom class distribution', fontsize=font_size+2)
            if widgets.radio_comp_int.isChecked():
                plt.ylabel("Relative intensity (%)", fontsize=font_size+2)
            elif widgets.radio_comp_nb.isChecked():
                plt.ylabel("Number", fontsize=font_size+2)

            plt.xticks(fontsize=font_size,rotation=45)
            plt.yticks(fontsize=font_size)
            plt.gca().set_ylim(bottom=(0))
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,640, 545)
            plt.show()

        ##############
        #Error
        ##############
        
        elif widgets.radio_error_plots.isChecked():
            dot_size = self.d_size
            data_selected = item.data(self.USERDATA_ROLE)
            frames = []
            item_classes = widgets.list_classes_error.selectedItems()
            if not item_classes:
                return           
            if widgets.checkBox_old_figures.isChecked():
                    if plt.get_fignums():
                        plt.close("all")
            for item in item_classes:
                classe_selected = item.data(self.USERDATA_ROLE)
                data_extract = data_selected.df.copy()
                
                if classe_selected == 'All':
                    pass
                else:
                    classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                    if 'x' in classe_selected:
                        index_classes = (data_selected.df[classe_selected] == True)
                    else:
                        index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                    data_extract = data_extract[index_classes]
                    
            #-----------------------------------#
            #  Normalization on selected class  #
            #-----------------------------------#
        
                if widgets.radioButton_norm_c.isChecked():
                    intens=data_extract["Normalized_intensity"].copy()
                    intens=intens.values.reshape(-1,1)
                    if intens.shape[0]>1:
                        min_max_scaler = preprocessing.MinMaxScaler()
                        Intens_scaled = min_max_scaler.fit_transform(intens)
                        data_extract["Normalized_intensity"] = Intens_scaled
                        data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                    elif intens.shape[0]==1:
                        data_extract["Normalized_intensity"]=1
                    else :
                        QMessageBox.about(self, "Error", "No species to be displayed.")
                        continue
        
            #-----------------------------------------#
            #  Normalization on selected class (end)  #
            #-----------------------------------------#
        
            #-----------------------------------#
            #  Normalization on displayed data  #
            #-----------------------------------#
        
                if widgets.radioButton_norm_d.isChecked():
                    intens=data_extract["Normalized_intensity"].copy()
                    intens=intens.values.reshape(-1,1)
                    if intens.shape[0]>1:
                        min_max_scaler = preprocessing.MinMaxScaler()
                        Intens_scaled = min_max_scaler.fit_transform(intens)
                        data_extract["Normalized_intensity"] = Intens_scaled
                        data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                    elif intens.shape[0]==1:
                        data_extract["Normalized_intensity"]=1
                    else :
                        QMessageBox.about(self, "Error", "No species to be displayed.")
                        continue
        
            #-----------------------------------------#
            #  Normalization on displayed data (end)  #
            #-----------------------------------------#   
                    self.read_param()
                    data_extract.classe_selected = classe_selected
                    frames.append(data_extract)
                
                def Anim(frames):
                    if gif == False:
                        fig = plt.figure()
                        transf = fig.transFigure
                    else:
                        Figure.clear()
                        transf = Figure.transFigure
                    
                    ### ppm vs m/z ###
                    if widgets.radio_ppm.isChecked():
        
                        x_data=frames["m/z"]
                        y_data=frames["err_ppm"]
                        third_dim=frames["Normalized_intensity"]
        
                        plot_fun("scatter",x=x_data,y=y_data,d_color=third_dim,size=(dot_size)*third_dim,dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)
        
        
                        if widgets.mz_min.text():
                            mz_min = float(widgets.mz_min.text())
                            plt.gca().set_xlim(left=mz_min)
                        if widgets.mz_max.text():
                            mz_max = float(widgets.mz_max.text())
                            plt.gca().set_xlim(right=mz_max)
                        if widgets.error_min.text():
                            error_min = float(widgets.error_min.text())
                            plt.gca().set_ylim(bottom=error_min)
                        if widgets.error_max.text():
                            error_max = float(widgets.error_max.text())
                            plt.gca().set_ylim(top=error_max)
                        if widgets.font_size.text():
                            font_size = float(widgets.font_size.text())
                        plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.5)
                        cbar = plt.colorbar()
                        cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                        plt.xlabel('m/z', fontsize=font_size+2)
                        plt.ylabel('Error (ppm)', fontsize=font_size+2)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                        if "m/z" in frames:
                            mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index]))
                    
                    ### Box plot ###
                    
                    elif widgets.radio_boxplot.isChecked():
                        
                        plt.boxplot(frames["err_ppm"])
                        if widgets.font_size.text():
                            font_size = float(widgets.font_size.text())
                        plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.5)
                        plt.ylabel("Error (ppm)", fontsize=font_size)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        yaxes = plt.gca().yaxis
                        yaxes.offsetText.set_fontsize(font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                        
                    ### bar plot  ###
                    else:

                        lst_error= []
                        min_error = min(frames['err_ppm'])
                        max_error = max(frames['err_ppm'])
                        n_bin = 50
                        error_range = (max(frames['err_ppm'])+abs(min(frames['err_ppm'])))/(n_bin+1) # Calculates error range and divides it into 50 sections
                        if widgets.radio_histo.isChecked():
                            Data= frames.groupby(pandas.cut(frames['err_ppm'], np.arange(min_error, max_error, error_range))).sum()
                        elif widgets.radio_histo_2.isChecked():
                            Data= frames.groupby(pandas.cut(frames['err_ppm'], np.arange(min_error, max_error, error_range))).count()
                        # Creates the 20 sections and determines errors value for each
                        for i in range(len(Data['err_ppm'])) :
                            lst_error.append(min_error+(error_range/2)+i*error_range)
                        #Mean error list
                        d = {'col1': lst_error,'col2': Data['absolute_intensity']}
                        df = pandas.DataFrame(data=d)
                        plt.bar(df['col1'],df['col2'], width=1/n_bin)
                        if widgets.error_min.text():
                            error_min = float(widgets.error_min.text())
                            plt.gca().set_xlim(left=error_min)
                        if widgets.error_max.text():
                            error_max = float(widgets.error_max.text())
                            plt.gca().set_xlim(right=error_max)
                        if widgets.font_size.text():
                            font_size = float(widgets.font_size.text())
                        plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.97,x=0.5)
                        plt.title("error distribution", fontsize=font_size+2)
                        plt.xlabel('Errors', fontsize=font_size)
                        if widgets.radio_histo.isChecked():
                            plt.ylabel("Summed intensities (a.u)", fontsize=font_size)
                        elif widgets.radio_histo_2.isChecked():
                            plt.ylabel("Number", fontsize=font_size)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        yaxes = plt.gca().yaxis
                        yaxes.offsetText.set_fontsize(font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text('Intensity = ' + str(format(df['col2'].iloc[sel.target.index],'.1E'))))
                    
                          
                        
            if gif == False:
                for i in frames:
                    Anim(i)   
                plt.show()
            else:
                Figure = plt.figure()
                plt.show()
                anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                writergif = PillowWriter(fps=self.fps) 
                anim_created.save("animation.gif", writer=writergif)
                plt.ion()        


             


            

        ##############
        #Spectra
        ##############

        elif widgets.radio_mass_spectrum.isChecked():
            if widgets.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            fig = plt.figure()
            item_file = widgets.list_loaded_file.selectedItems()
            if not item_file:
                return
            item = item_file[0]
            data_selected = item.data(self.USERDATA_ROLE)
            leg=list()
            
            if data_selected.df_type == 'Peaklist':
                item_classes = []
                classe_selected = 'All'
                data_filtered = data_selected.df
                third_dimension = data_filtered["normalized_intensity"]
                Intens = third_dimension.values.reshape(-1,1)
                min_max_scaler = preprocessing.MinMaxScaler()
                Intens_scaled = min_max_scaler.fit_transform(Intens)
                data_filtered["normalized_intensity"] = Intens_scaled
           
            else:
                item_classes = widgets.list_classes_mass_spec.selectedItems()
                if not item_classes:
                    item_classes = [widgets.list_classes_mass_spec.item(0)]
                for i in range(len(item_classes)):
                    
                    classe_selected = item_classes[i].data(self.USERDATA_ROLE)
    
                    if classe_selected == 'All':
                        data_filtered = data_selected.df
                        
                    else:
                        classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                        if 'x' in classe_selected:
                            index_classes = (data_selected.df[classe_selected] == True)
                        else:
                            index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                        data_filtered = data_selected.df[index_classes]
                        third_dimension = data_filtered["Normalized_intensity"]
                        Intens = third_dimension.values.reshape(-1,1)
                        min_max_scaler = preprocessing.MinMaxScaler()
                        Intens_scaled = min_max_scaler.fit_transform(Intens)
                        data_filtered["Normalized_intensity"] = Intens_scaled
                    data_filtered = data_filtered.sort_values(by=["Normalized_intensity"], ascending=True)
                    if i == 0:
                        c = 'k'
                    elif i == 1:
                        c = 'b'
                    elif i == 2:
                        c = 'r'
                    elif i == 3:
                        c = 'g'
                    elif i == 4:
                        c = 'm'
                    elif i == 5:
                        c = 'c'
                    patch=mpatches.Patch(color=c, label = item_classes[i].text())
                    leg.append(patch)
                    plt.stem(data_filtered["m/z"], data_filtered["absolute_intensity"],c,markerfmt=" ", basefmt="k")
            if widgets.mz_min_2.text():
                mz_min_2 = float(widgets.mz_min_2.text())
                plt.gca().set_xlim(left=mz_min_2)
            if widgets.mz_max_2.text():
                mz_max_2 = float(widgets.mz_max_2.text())
                plt.gca().set_xlim(right=mz_max_2)
            if widgets.intens_min.text():
                intens_min = float(widgets.intens_min.text())
                plt.gca().set_ylim(bottom=intens_min)
            if widgets.intens_max.text():
                intens_max = float(widgets.intens_max.text())
                plt.gca().set_ylim(top=intens_max)
            if widgets.font_size.text():
                font_size = float(widgets.font_size.text())
            plt.gca().legend(handles=leg,fontsize=font_size-2)
            plt.xlabel('m/z', fontsize=font_size+2,style='italic')
            plt.ylabel('Intensity', fontsize=font_size+2)
            plt.xticks(fontsize=font_size)
            plt.yticks(fontsize=font_size)
            yaxes = plt.gca().yaxis
            yaxes.offsetText.set_fontsize(font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,640, 545)
            plt.show()

        ##############
        #Distrib
        ##############

        elif widgets.radio_distributions.isChecked():
            
            self.read_param()
            font_size = self.fontsize
            frames = []
            item_file = widgets.list_loaded_file.selectedItems()
            if not item_file:
                return
            item = item_file[0]
            data_selected = item.data(self.USERDATA_ROLE)

            item_classes = widgets.list_classes_distrib.selectedItems()
            if not item_classes:
                return
            if widgets.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            
            for item in item_classes:
                classe_selected = item.data(self.USERDATA_ROLE)
                
                data_extract = data_selected.df.copy()
            
            
                if classe_selected == 'All':
                    pass
                else:
                    classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                    if 'x' in classe_selected:
                        index_classes = (data_selected.df[classe_selected] == True)
                    else:
                        index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                    data_extract = data_extract[index_classes]
                    
                data_extract.classe_selected = classe_selected
                frames.append(data_extract)   
                
        
                def Anim(frames, data_selected):
                    if gif == False:
                        fig = plt.figure()
                        transf = fig.transFigure
                    else:
                        Figure.clear()
                        transf = Figure.transFigure
                    x_axes = widgets.list_distribution.currentRow()
                
                    if x_axes == 0: #DBE
                        
                        x_label = 'DBE'
                        bar_color = 'grey'
                        
                        dbe_both = dict()          
                        dbe_odd = dict()
                        dbe_even = dict()
                        m = float(-0.5)
                        while m <= max(frames.DBE):
                            index_DBE = (frames.DBE==m)
                            data_DBE = frames[index_DBE]
                            intensity_DBE = sum(data_DBE["Normalized_intensity"])*100/sum(data_selected.df["Normalized_intensity"])
                            number_DBE = len(data_DBE)
                            if  intensity_DBE  :
                                dbe_both[m] = [intensity_DBE,number_DBE]
                                if m.is_integer():
                                    dbe_odd[m] = [intensity_DBE,number_DBE]
                                else :
                                    dbe_even[m] = [intensity_DBE,number_DBE]
                            m=m+0.5
                        
                        if widgets.radio_even_intens_vs_DBE.isChecked():
                            dbe=dbe_even
                            dbe_text="Even ions"
                            w = 1
                        elif widgets.radio_odd_intens_vs_DBE.isChecked():
                            dbe=dbe_odd
                            dbe_text="Odd ions"
                            w = 1
                        elif widgets.radio_both_intens_vs_DBE.isChecked():
                            dbe=dbe_both
                            dbe_text="Even and odd ions"
                            w = 0.5
                        dbe=pandas.DataFrame.from_dict(dbe)
                        x = dbe.columns
                        if widgets.radio_dist_int.isChecked() :
                            y =dbe.values.tolist()[0]
                            y_label = "Relative Intensity (%)"
                        elif widgets.radio_dist_nb.isChecked() :
                            y = dbe.values.tolist()[1]
                            y_label = "Number of attribution"
                        title = f'{y_label} vs {x_label}'
        
                    elif x_axes == 1: #C
                        x_label = "#C"
                        bar_color = 'grey'
                        C_both = dict()
                        m = float(1)
                        while m <= max(frames.C):
                            index_C = (frames.C==m)
                            data_C = frames[index_C]
                            intensity_C = sum(data_C["Normalized_intensity"])*100/sum(data_selected.df["Normalized_intensity"])
                            number_C = len(data_C)
                            if  intensity_C  :
                                C_both[m] = [intensity_C,number_C]
                            m=m+1
                        C_both=pandas.DataFrame.from_dict(C_both)
                        dbe_text="Even and odd ions"
                        w = 1
                        x = C_both.columns
                        if widgets.radio_dist_int.isChecked() :
                            y =C_both.values.tolist()[0]
                            y_label = "Relative Intensity (%)"
                        elif widgets.radio_dist_nb.isChecked() :
                            y = C_both.values.tolist()[1]
                            y_label = "Number of attribution"
                        title = f'{y_label} vs {x_label}'
                        
                    elif x_axes == 2:
                        x_label = "#N"
                        bar_color = 'blue'
                        w = 1
                        N_both = dict()
                        m = int(0)
                        while m <= max(frames.N):
                            index_N = (frames.N==m)
                            data_N = frames[index_N]
                            intensity_N = sum(data_N["Normalized_intensity"])*100/sum(data_selected.df["Normalized_intensity"])
                            number_N = len(data_N)
                            if  intensity_N  :
                                N_both[m] = [intensity_N,number_N]
                            m=m+1
                        N_both=pandas.DataFrame.from_dict(N_both)
                        dbe_text="Even and odd ions"
                        x = N_both.columns
                        if widgets.radio_dist_int.isChecked() :
                            y =N_both.values.tolist()[0]
                            y_label = "Relative Intensity (%)"
                        elif widgets.radio_dist_nb.isChecked() :
                            y = N_both.values.tolist()[1]
                            y_label = "Number of attribution"
                        title = f'{y_label} vs {x_label}'
                        
                        
                    elif x_axes == 3:
                        x_label = "#O"
                        bar_color = 'red'
                        w = 1
                        O_both = dict()
                        m = int(0)
                        while m <= max(frames.O):
                            index_O = (frames.O==m)
                            data_O = frames[index_O]
                            intensity_O = sum(data_O["Normalized_intensity"])*100/sum(data_selected.df["Normalized_intensity"])
                            number_O = len(data_O)
                            if  intensity_O  :
                                O_both[m] = [intensity_O,number_O]
                            m=m+1
                        O_both=pandas.DataFrame.from_dict(O_both)
                        dbe_text="Even and odd ions"
                        x = O_both.columns
                        if widgets.radio_dist_int.isChecked() :
                            y =O_both.values.tolist()[0]
                            y_label = "Relative Intensity (%)"
                        elif widgets.radio_dist_nb.isChecked() :
                            y = O_both.values.tolist()[1]
                            y_label = "Number of attribution"
                        title = f'{y_label} vs {x_label}'
                        
                    elif x_axes == 4:
                        x_label = "#S"
                        bar_color = 'yellow'
                        w = 1
                        S_both = dict()
                        m = int(0)
                        while m <= max(frames.S):
                            index_S = (frames.S==m)
                            data_S = frames[index_S]
                            intensity_S = sum(data_S["Normalized_intensity"])*100/sum(data_selected.df["Normalized_intensity"])
                            number_S = len(data_S)
                            if  intensity_S  :
                                S_both[m] = [intensity_S,number_S]
                            m=m+1
                        S_both=pandas.DataFrame.from_dict(S_both)
                        dbe_text="Even and odd ions"
                        x = S_both.columns
                        if widgets.radio_dist_int.isChecked() :
                            y =S_both.values.tolist()[0]
                            y_label = "Relative Intensity (%)"
                        elif widgets.radio_dist_nb.isChecked() :
                            y = S_both.values.tolist()[1]
                            y_label = "Number of attribution"
                        title = f'{y_label} vs {x_label}'   
                        
                        
                    plt.bar(x,y,width=w,color = bar_color, edgecolor='black', linewidth=2)
                    plt.suptitle(f'{title}',fontsize=font_size+4,y=0.98,x=0.45)
                    plt.xlabel(x_label, fontsize=font_size+2)
                    plt.ylabel(y_label, fontsize=font_size+2)
                    cursor = mplcursors.cursor(multiple=True)   
                    @cursor.connect("add")
                    def on_add(sel):
                        x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
                        sel.annotation.set(text=f"#S: {round(x+width/2,0)}; Rel.Int.: {round(height,4)}%",
                                           position=(0, 20), anncoords="offset points")
                        sel.annotation.xy = (x + width / 2, y + height)
                    
                    plt.xticks(fontsize=font_size)
                    plt.yticks(fontsize=font_size)
                    if widgets.Int_vs_DBE_min.text():
                        C_min = float(widgets.Int_vs_DBE_min.text())
                        plt.gca().set_xlim(left=C_min)
                    if widgets.Int_vs_DBE_max.text():
                        C_max = float(widgets.Int_vs_DBE_max.text())
                        plt.gca().set_xlim(right=C_max)
                    if gif == False:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                    plt.text(0.68,0.9,dbe_text,horizontalalignment='center',
                             verticalalignment='center', transform = transf,fontsize=font_size+2)
                    plt.text(0.12,0.9,f'{frames.classe_selected}',horizontalalignment='left',
                             verticalalignment='center', transform = transf,fontsize=font_size+2)
    
            if gif == False:
                for i in frames:
                    Anim(i,data_selected)   
                plt.show()
            else:
                Figure = plt.figure()
                plt.show()
                anim_created = FuncAnimation(Figure, Anim, frames, fargs = (data_selected,), interval=1000/self.fps)  
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                writergif = PillowWriter(fps=self.fps) 
                anim_created.save("animation.gif", writer=writergif)
                plt.ion()

    def plot_DBE(self, gif = False):
        """
        DBE vs C# plots
        """
        
        frames = []
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        item_classes = widgets.list_classes_DBE.selectedItems()
        if not item_classes:
            return
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        for item in item_classes:
            classe_selected = item.data(self.USERDATA_ROLE)
    
            if 'PC1' in data_selected.df:
                widgets.radio_color_pc1.show()
                widgets.radio_color_pc2.show()
    
            data_extract = data_selected.df.copy()
    
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
        
            

            Intens = data_extract["Normalized_intensity"].values.reshape(-1,1)
    
            
            
            if widgets.check_classic.isChecked():
                Intens= Intens
            if widgets.check_sqrt.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
            if classe_selected == 'All':
                pass
            else:
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (data_selected.df[classe_selected] == True)
                else:
                    index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
    
        #-----------------------------------#
        #  Normalization on selected class  #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", f"No species to be displayed for the class : {classe_selected}.")
                    continue
    
        #-----------------------------------------#
        #  Normalization on selected class (end)  #
        #-----------------------------------------#
    
            
            if widgets.radio_even_DBE.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==1]
                dbe_text="Even ions"
            elif widgets.radio_odd_DBE.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==0]
                dbe_text="Odd ions"
            else :       
                dbe_text="Even and odd ions"
            if widgets.dot_size.text():
                dot_size = float(widgets.dot_size.text())
            if widgets.font_size.text():
                font_size = float(widgets.font_size.text())
            
    
        #-----------------------------------#
        #  Normalization on displayed data  #
        #-----------------------------------#
    
            if widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", f"No species to be displayed for the class : {classe_selected}.")
                    continue
    
        #-----------------------------------------#
        #  Normalization on displayed data (end)  #
        #-----------------------------------------#
        
            if widgets.radio_color_intensity_2.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc1.isChecked():
                third_dimension = data_extract["PC1"]
            elif widgets.radio_color_pc2.isChecked():
                third_dimension = data_extract["PC2"]
            elif widgets.radio_color_O.isChecked():
                third_dimension = data_extract["O"]
            data_extract["third_dimension"] = third_dimension
            data_extract.classe_selected = classe_selected
            self.read_param()
            frames.append(data_extract)
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                frames.sort_values(by=["third_dimension","Normalized_intensity"],ascending = [True,True], inplace = True)
                plot_fun("scatter",x=frames["C"],y=frames["DBE"],d_color=frames["third_dimension"],size=dot_size*frames["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)
        
                if widgets.C_min_DBE.text():
                    C_min = float(widgets.C_min_DBE.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.C_max_DBE.text():
                    C_max = float(widgets.C_max_DBE.text())
                    plt.gca().set_xlim(right=C_max)
                else:
                    C_max = data_selected.df['C'][data_selected.df['C'].idxmax()]
                if widgets.DBE_min_DBE.text():
                    DBE_min = float(widgets.DBE_min_DBE.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if widgets.DBE_max_DBE.text():
                    DBE_max = float(widgets.DBE_max_DBE.text())
                    plt.gca().set_ylim(top=DBE_max)
                else:
                    DBE_max = frames['DBE'][frames['DBE'].idxmax()]
                if widgets.CheckBox_hap.isChecked():
                    plt.axline((13, 8.57), (19, 12.95), color="red", linestyle=(0, (5, 5)))
                plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.45)
                cbar = plt.colorbar()
                if widgets.radio_color_intensity_2.isChecked():
                    cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc1.isChecked():
                    cbar.set_label('PC1', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc2.isChecked():
                    cbar.set_label('PC2', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
        
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radio_color_pc1.isChecked():
                    plt.clim(np.min(data_selected.df['PC1']), np.max(data_selected.df['PC1']))
                elif widgets.radio_color_pc2.isChecked():
                    plt.clim(np.min(data_selected.df['PC2']), np.max(data_selected.df['PC2']))
                plt.xlabel('#C', fontsize=font_size+4)
                plt.ylabel('DBE', fontsize=font_size+4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)             
                plt.text(0.68,0.9,dbe_text,horizontalalignment='center',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] +', #C = '+ str(frames['C'].iloc[sel.target.index]) +', DBE = ' + str(frames['DBE'].iloc[sel.target.index])))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
            
    def plot_VK(self, gif = False):
        """
        Van Krevelen plot
        """

        frames = []
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        item_classes = widgets.list_classes_VK.selectedItems()
        if not item_classes:
            return
        self.read_param()
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        
        for item in item_classes:
            classe_selected = item.data(self.USERDATA_ROLE)
            
            data_filtered = data_selected.df.copy()

            if classe_selected == 'All':
                pass
            elif 'x' in classe_selected:
                index_classes = (data_selected.df[classe_selected] == True)
                data_filtered = data_selected.df[index_classes]
            else:
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_filtered = data_selected.df[index_classes]
            
        

        
                
            Intens = data_filtered["Normalized_intensity"].values.reshape(-1,1)
            if widgets.check_classic_vk.isChecked():
                Intens= Intens
            if widgets.check_sqrt_vk.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_vk.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value, log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled
    
    
            dot_size = self.d_size
            x_axes = widgets.list_VK_x.currentRow()
            y_axes = widgets.list_VK_y.currentRow()
            
            #Tests the presence of sulfur
            if x_axes == 2 or y_axes == 3:
                try:
                    test=data_filtered["S/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No sulfur in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
            #Tests the presence of oxygen
            if x_axes == 0 or y_axes == 1:
                try:
                    test=data_filtered["O/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No oxygen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
            #Tests the presence of nitrogen
            if x_axes == 1 or y_axes == 2:
                try:
                    test=data_filtered["N/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No nitrogen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
    
            #Tests the presence of hydrogen
            if x_axes == 3 or y_axes == 0:
                try:
                    test=data_filtered["H/C"]
                    del test
                except:
                    QMessageBox.about(self, "Error", "No hydrogen in the selected data")
                    continue
                    
            if x_axes == 0:
                x_axes = data_filtered["O/C"]
                x_label = "O/C"
            elif x_axes == 1:
                x_axes = data_filtered["N/C"]
                x_label = "N/C"
            elif x_axes == 2:
                x_axes = data_filtered["S/C"]
                x_label = "S/C"
            elif x_axes == 3:
                x_axes = data_filtered["H/C"]
                x_label = "H/C"
            elif x_axes == 4:
                x_axes = data_filtered["m/z"]
                x_label = "m/z"
            if y_axes == 0:
                y_axes = data_filtered["H/C"]
                y_label = "H/C"
            elif y_axes == 1:
                y_axes = data_filtered["O/C"]
                y_label = "O/C"
            elif y_axes == 2:
                y_axes = data_filtered["N/C"]
                y_label = "N/C"
            elif y_axes == 3:
                y_axes = data_filtered["S/C"]
                y_label = "S/C"
        
                

            if widgets.radio_color_pc1_VK.isChecked():
                third_dimension = data_filtered["PC1"]
            elif widgets.radio_color_pc2_VK.isChecked():
                third_dimension = data_filtered["PC2"]
            elif widgets.radio_color_O_vk.isChecked():
                third_dimension = data_filtered["O"]
            else : 
                third_dimension = data_filtered["Normalized_intensity"]
            data_filtered["third_dimension"] = third_dimension
            data_filtered["x_axes"] = x_axes
            data_filtered["y_axes"] = y_axes
            data_filtered.x_label = x_label
            data_filtered.y_label = y_label
            data_filtered.classe_selected = classe_selected
            self.read_param()
            frames.append(data_filtered)
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                frames.sort_values(by=["third_dimension","Normalized_intensity"],ascending = [True,True], inplace = True)
                plot_fun("scatter",x=frames["x_axes"],y=frames["y_axes"],d_color=frames["third_dimension"],size=dot_size*frames["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)


                if widgets.x_min_VK.text():
                    C_min = float(widgets.x_min_VK.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_VK.text():
                    C_max = float(widgets.x_max_VK.text())
                    plt.gca().set_xlim(right=C_max)
                if widgets.y_min_VK.text():
                    DBE_min = float(widgets.y_min_VK.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if widgets.y_max_VK.text():
                    DBE_max = float(widgets.y_max_VK.text())
                    plt.gca().set_ylim(top=DBE_max)
                plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.45)
                cbar = plt.colorbar()
                if widgets.radio_color_intensity_3.isChecked():
                    cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc1_VK.isChecked():
                    cbar.set_label('PC1', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc2_VK.isChecked():
                    cbar.set_label('PC2', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_O_vk.isChecked():
                    cbar.set_label('#O', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radio_color_pc1_VK.isChecked():
                    plt.clim(np.min(data_selected.df['PC1']), np.max(data_selected.df['PC1']))
                elif widgets.radio_color_pc2_VK.isChecked():
                    plt.clim(np.min(data_selected.df['PC2']), np.max(data_selected.df['PC2']))
                plt.xlabel(frames.x_label, fontsize=font_size+4)
                plt.ylabel(frames.y_label, fontsize=font_size+4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] + ', ' + str(x_label) +' : '+ str(round(x_axes.iloc[sel.target.index],4)) + ', ' + str(y_label) +' = '+ str(round(y_axes.iloc[sel.target.index],4))))

                if widgets.checkBox_vk_area.isChecked() and widgets.list_VK_x.currentRow() == 0 and widgets.list_VK_y.currentRow() == 0:
                    border_width = 4
                    alpha = 1
                    left, bottom, width, height = (0.51, 1.52, 0.19, 0.5)
                    amino_sugars=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="orange",
                               linewidth = border_width,alpha = alpha)
                    left, bottom, width, height = (0.71, 1.52, 0.3, 0.8)
                    carbohydrates=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="green",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0.31, 0.51, 0.5, 0.99)
                    lignin=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="purple",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 1.72, 0.29, 0.6)
                    lipid=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="blue",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 0, 0.8, 0.49)
                    condensed_hyd=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="black",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 0.51, 0.29, 1.19)
                    unsat_hyd=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="red",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0.31, 1.52, 0.19, 0.49)
                    proteins=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="brown",
                               linewidth=border_width,alpha=alpha)
                    orange_patch = mpatches.Patch(color='orange', label='Amino sugars')
                    green_patch = mpatches.Patch(color='green', label='Carbohydrates')
                    purple_patch = mpatches.Patch(color='purple', label='Lignin')
                    blue_patch = mpatches.Patch(color='blue', label='Lipids')
                    black_patch = mpatches.Patch(color='black', label='Condensed Hydrocarbons')
                    red_patch = mpatches.Patch(color='red', label='Unsaturated Hydrocarbons')
                    brown_patch = mpatches.Patch(color='brown', label='Proteins')
                    plt.legend(handles=[orange_patch,green_patch,purple_patch,blue_patch ,black_patch ,red_patch,brown_patch])
                    plt.gca().add_patch(amino_sugars)
                    plt.gca().add_patch(carbohydrates)
                    plt.gca().add_patch(lignin)
                    plt.gca().add_patch(lipid)
                    plt.gca().add_patch(condensed_hyd)
                    plt.gca().add_patch(unsat_hyd)
                    plt.gca().add_patch(proteins)
                    
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_PCA(self):
        """
        Principal component analysis (plot only)
        """

        if widgets.radio_PCPC2.isChecked():
            axes = 0 #PC1PC2
        elif widgets.radio_PC2PC3.isChecked():
            axes = 1 #PC2PC3
        elif widgets.radio_PC1PC3.isChecked():
            axes = 2 #PC1PC3
        elif widgets.radio_3D.isChecked():
            axes = 3 #PC1PC3
        if widgets.PCA_ALL.isChecked() : 
            pca_on ='all'
        elif widgets.PCA_COMMON.isChecked() : 
            pca_on = 'common'
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        if not widgets.lineEdit_n_component.text():
            n_comp=5
        else:
            n_comp=int(widgets.lineEdit_n_component.text())



        item_file = widgets.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        pca_data = data_selected.pca_data
        # mz = data_selected.mass
        n_formula,n_ech=pca_data.shape 
        n_ech = n_ech - 2
        if int(widgets.lineEdit_n_component.text()) > n_ech or int(widgets.lineEdit_n_component.text()) < 3 :
            QMessageBox.about(self, "FYI box", "Number of component must be comprised between 3 and the number of compared samples, i.e. " + str(n_ech)+" in this case.")
            return
        self.read_param()
        data_old = list(data_selected.df)
        score_coef,first_comps= plot_pca(pca_data,axes,n_comp,pca_on,para_dict = self.para_dict)
        data_selected.df.columns = data_old
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,640, 545)
        self.data_with_coef = pandas.merge(left=data_selected.df, right=score_coef, left_on='m/z', right_on='m/z')
        self.data_with_coef = self.data_with_coef.rename(columns = {'m/z':'calc. m/z'})
        widgets.save_button_pca_coef.setEnabled(True)
        widgets.lineEdit_exp_var_3.setText(str(round(first_comps,2))+'%')

    def save_pca_coef(self):
        """
        Saves the PCA coefficient in a .csv file 
        """

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        if save_path == '':
            return
        save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        if save_name == '':
            return
        
        self.write_csv_df(save_path, save_name +".csv", self.data_with_coef)

    def plot_HCA(self):
        """
        Hierachical cluster analysis (plot only)
        """
        fig = plt.figure()
        item_file = widgets.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        hca_data = data_selected.pca_data.filter(like = 'Rel')
        hca_data = hca_data.transpose()
        model = AgglomerativeClustering(distance_threshold=True, n_clusters=None)
        labelist=hca_data.index.values.tolist()
        for i in range(len(labelist)):
            labelist[i]=labelist[i].replace('Rel_intens_','')
            labelist[i]=labelist[i].replace('.csv','')
        ##set intensity##
        if widgets.hca_intensity_classic.isChecked():
            hca_data= hca_data
        if widgets.hca_intensity_sqrt.isChecked():
            hca_data= np.sqrt(hca_data)
        ##set orientation##
        if widgets.hca_orientation_left.isChecked():
            orientation = 'left'
            plt.xlabel('Euclidean distance')
            val = 0
        if widgets.hca_orientation_top.isChecked():
            orientation = 'top'
            plt.ylabel('Euclidean distance')
            val = 90
        model = model.fit(hca_data)
        plt.title("Hierarchical Clustering Dendrogram")
        plot_dendrogram(model, truncate_mode="lastp", p=len(hca_data.index.values), labels = labelist, orientation=orientation)
        mngr = plt.get_current_fig_manager()
        plt.xticks(rotation=val)
        mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,640, 545)
        plt.show()
        plt.tight_layout()

    def volcano(self):
        """
        Volcano plots
        """
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        font_size=int(widgets.font_size.text())
        dot_size=int(widgets.dot_size.text())
        volc_data=self.volc_data.copy() #Retrieves data

        list_samp_1=[] #Sample 1 selection
        for i in widgets.list_sample_1.selectedItems():
            list_samp_1.append(i.text())

        list_samp_2=[] #Sample 2 selection
        for j in widgets.list_sample_2.selectedItems():
            list_samp_2.append(j.text())


        volc_data['Mean_int_1']=volc_data[list_samp_1].mean(axis=1) #Mean intensities in sample 1
        volc_data['Mean_int_2']=volc_data[list_samp_2].mean(axis=1) #Mean intensities in sample 2
        volc_data["fc"]=pandas.DataFrame(np.log2(volc_data['Mean_int_2']/volc_data['Mean_int_1'])) #Calculates log2(FC) values
        volc_data['p']=stats.ttest_ind(volc_data[list_samp_1],volc_data[list_samp_2],axis=1)[1].tolist() #Calculates p-values


        ####
        #Excluding infinite and NaN values (attribution in neither of the sample)
        volc_data['fc'].fillna(2e20,inplace=True)
        p_inf=(volc_data['fc'] >1e20).tolist()
        n_inf=(volc_data['fc'] <-1e20).tolist()

        inf_index=[i or j for i, j in zip(n_inf,p_inf)]
        widgets.lineEdit_tot_spec_volc.setText(str(volc_data.shape[0]))
        volc_data.drop(index=volc_data.index[inf_index],inplace=True,axis=0)
        try :
           min_fc=min(volc_data['fc'])
           max_fc=max(volc_data['fc'])
        except :
           QMessageBox.about(self, "FYI box", "No data selected.")
           return
        ####

        widgets.lineEdit_comp_spec_volc.setText(str(volc_data.shape[0]))
        volc_data.sort_values(by='fc',inplace=True)
        volc_data['p']=-np.log10(volc_data['p'])
        plt.figure()
        if widgets.cb_significancy_volc.isChecked():
            if widgets.cb_005.isChecked():
                pmin = 0.05
            if widgets.cb_001.isChecked():
                pmin = 0.01
            if widgets.cb_0001.isChecked():
                pmin = 0.001
        else:
            pmin = 100
        if widgets.cb_005.isChecked() == False and widgets.cb_001.isChecked() == False and widgets.cb_0001.isChecked() == False:
            pmin = 100
        if widgets.cb_fc_lim.isChecked():
            fcmin = 1
        else:
            fcmin = 0
        
        if not widgets.cb_volc_color.isChecked():
            grey_data_fc = volc_data.drop(volc_data[abs(volc_data['fc'])>fcmin].index)
            volc_data = pandas.concat([grey_data_fc,volc_data]).drop_duplicates(keep = False)
    
            grey_data_p = volc_data.drop(volc_data[volc_data['p'] > -np.log10(pmin)].index)
            volc_data = pandas.concat([grey_data_p,volc_data]).drop_duplicates(keep = False)
    
            grey_data_all = pandas.concat([grey_data_p,grey_data_fc]).drop_duplicates()        
            
            scatter = plot_fun('scatter',grey_data_all['fc'],grey_data_all['p'],d_color = "grey", alpha = 0.5)
        
        if widgets.volc_color_classes.isChecked():
            if widgets.cb_volc_sort.isChecked():
                volc_data.sort_values("family_name" , inplace = True)
            for fam in volc_data["family_name"].drop_duplicates():
                plt_ind=volc_data["family_name"] == fam
                to_plot=volc_data[plt_ind]
                scatter=plt.scatter(to_plot['fc'],to_plot['p'],
                                    s=dot_size*0.75,c=to_plot['family_color'].astype(str),
                                    label=fam,edgecolor='black',linewidths=0.75,alpha=0.8)
        elif widgets.volc_color_dbe.isChecked():
            if widgets.cb_volc_sort.isChecked():
                volc_data.sort_values("DBE" , inplace = True)
            scatter = plot_fun('scatter',volc_data['fc'],volc_data['p'],d_color = volc_data['DBE'],cmap = self.color_map)
            cbar= plt.colorbar()
            cbar.set_label('DBE', labelpad=-2.4*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
            cbar.ax.tick_params(labelsize=font_size-2)
            
        elif widgets.volc_color_mz.isChecked():
            if widgets.cb_volc_sort.isChecked():
                volc_data.sort_values("m/z" , inplace = True)
            scatter = plot_fun('scatter',volc_data['fc'],volc_data['p'],d_color = volc_data['m/z'],cmap = self.color_map)
            cbar= plt.colorbar()
            cbar.set_label('m/z', labelpad=-3*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
            cbar.ax.tick_params(labelsize=font_size-2)
            
        elif widgets.volc_color_oc.isChecked():
            if widgets.cb_volc_sort.isChecked():
                volc_data.sort_values("O/C" , inplace = True)
            scatter = plot_fun('scatter',volc_data['fc'],volc_data['p'],d_color = volc_data['O/C'],cmap = self.color_map)
            cbar= plt.colorbar()
            cbar.set_label('O/C', labelpad=-3.15*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
            cbar.ax.tick_params(labelsize=font_size-2)
            
        if widgets.cb_significancy_volc.isChecked():
            if widgets.cb_005.isChecked():
                plt.axline((-1, -np.log10(0.05)), (1, -np.log10(0.05)), color="black",ls=(0,(5,5)), lw=0.8)
                plt.text(max_fc*1.05,-np.log10(0.05),'*',horizontalalignment='center',
                             verticalalignment='center',fontsize=font_size-1)
            if widgets.cb_001.isChecked():
                plt.axline((-1, -np.log10(0.01)), (1, -np.log10(0.01)), color="black",ls=(0,(5,5)), lw=0.8)
                plt.text(max_fc*1.03,-np.log10(0.01),'**',horizontalalignment='center',
                             verticalalignment='center',fontsize=font_size-1)
            if widgets.cb_0001.isChecked():
                plt.axline((-1, -np.log10(0.001)), (1, -np.log10(0.001)), color="black",ls=(0,(5,5)), lw=0.8)
                plt.text(max_fc*1.01,-np.log10(0.001),'***',horizontalalignment='center',
                             verticalalignment='center',fontsize=font_size-1)
        if widgets.cb_fc_lim.isChecked():
            plt.axline((-1, 0), (-1,1), color="black",ls=(0,(5,5)), lw=0.8)
            plt.axline((1,0), (1,1), color="black",ls=(0,(5,5)), lw=0.8)
            
        




        plt.xlabel('log2(fold change)',fontsize=font_size-1)
        plt.ylabel('-log10(p-value)',fontsize=font_size-1)
        plt.suptitle(f'Left :{list_samp_1} \nRight :{list_samp_2}',fontsize=font_size*0.5,y=0.95,x=0.1,horizontalalignment='left')
        plt.legend(fontsize=font_size-4)
        try:
            volc_data['sum_formula']
            mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(volc_data['sum_formula'].iloc[sel.target.index]))
        except:
            try:
                mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(volc_data['m/z'].iloc[sel.target.index]))
            except:
                return
            
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,640, 545)
        plt.show()


    def kendrick_motif_calculation(self):
        """
        Returns the mass of the selected repetitive unit
        """

        formula = widgets.edit_motif.text() #Retrieves text from "edit_motif"

        form=cp.parse_formula(formula) #Creates a dict with symbols and mass

        dict_data={'C': 12,'H':1.007825,'N':14.003074,'O':15.994915,'S':31.972072,'Cl':34.968853,'Si':27.976928,'P':30.9737634\
                   ,'V':50.943963,'Li':7.016005,'Cu':62.929599,'Ni':57.935347,'F':18.998403,'B':11.009305} #Dictionnaire avec les masses molaires
        try:
            mass = 0 #Initialisation
            for atom in form:   #Loop
                mass = mass + form[atom]*dict_data[atom]
        except:
            QMessageBox.about(self, "FYI box", "Upper case only.")

        widgets.edit_mass_motif.setText(str(mass)) # Modify text in "mass_motif"

    def plot_Kendrick(self, gif = False):
        """
        Classic Kendrick plots and extracting series
        """

        frames = []
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        data_filtered = data_selected.df
        if data_selected.df_type == 'PyC2MC_merged':
            data_filtered = data_filtered.rename(columns={'summed_intensity':'normalized_intensity'})
        data_filtered = data_filtered.sort_values(by=["normalized_intensity"], ascending=True)
        self.read_param()
        dot_size = self.d_size
        font_size = self.fontsize
        if widgets.edit_mass_motif.text():
            repetive_unit_mass = float(widgets.edit_mass_motif.text())
            nominal_unit = round(repetive_unit_mass)
            
        
            
        if widgets.stackedWidget_Kendrick.currentIndex()==0: #KMD classic
            item_classes = widgets.list_classes_Kendrick.selectedItems()
        elif widgets.stackedWidget_Kendrick.currentIndex()==2: #MD 
            item_classes = widgets.list_classes_Kendrick_univ.selectedItems()
       #### KMD extract ####
        if  widgets.stackedWidget_Kendrick.currentIndex()==1:
            
            if "mz" in data_filtered:
                data_filtered['Kendrick mass']= data_filtered['mz']*(nominal_unit/repetive_unit_mass)
                data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])
            elif "count" in data_filtered:
                data_filtered['Kendrick mass']= data_filtered['m/z']*(nominal_unit/repetive_unit_mass)
                data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])
            elif "m/z" in data_filtered:
                data_filtered['Kendrick mass']= data_filtered['m/z']*(nominal_unit/repetive_unit_mass)
                data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])

            if widgets.roundUp.isChecked():
                data_filtered['Kendrick nominal mass']=data_filtered['Kendrick mass'].apply(np.ceil)
            elif widgets.roundClosest.isChecked():
                data_filtered['Kendrick nominal mass']=round(data_filtered['Kendrick mass'])
            data_filtered['Kendrick mass defect']=data_filtered['Kendrick nominal mass']-data_filtered['Kendrick mass']
            if data_selected.df_type == 'PyC2MC_merged':
                data_filtered = data_filtered.rename(columns={'summed_intensity':'normalized_intensity'})
            #Determination of the number of series (1 to 6):
            data_filtered['id'] = 0 # Colors species of interest
            n_series=0
            list_mass=[]
            self.kendrickSeries=pandas.DataFrame()
            list_series=[widgets.series_1,widgets.series_2,widgets.series_3,\
                         widgets.series_4,widgets.series_5,widgets.series_6,\
                             widgets.series_7,widgets.series_8,widgets.series_9,widgets.series_10]
            list_series_index=[]
            list_color=[widgets.comboBox_1.currentText(),widgets.comboBox_2.currentText(),\
                        widgets.comboBox_3.currentText(),widgets.comboBox_4.currentText(),\
                        widgets.comboBox_5.currentText(),widgets.comboBox_6.currentText(),\
                        widgets.comboBox_7.currentText(),widgets.comboBox_8.currentText(),\
                        widgets.comboBox_9.currentText(),widgets.comboBox_10.currentText(),]
            for n in range(10):
                if list_series[n].text():
                    n_series=n_series+1
                    list_mass.append(list_series[n].text())
                    list_series_index.append(n)
            if n_series==0:
                QMessageBox.about(self, "FYI box", "No series to look for ...")
                return

            for j in list_series_index :
                try:
                    m = float(list_series[j].text())
                except:
                    QMessageBox.about(self, "FYI box", "Only use digits and dots for m/z values (no comma !)")
                    return
                rep_pattern=repetive_unit_mass
                nominal_pattern=round(rep_pattern)
                km= m * (nominal_pattern/rep_pattern)
                if widgets.roundUp.isChecked():
                    nkm= math.ceil(km)
                elif widgets.roundClosest.isChecked():
                    nkm= round(km)
                kmd= nkm - km
                tol=kmd*0.05/100 #tolerance attribution
                n=0
                l=0
                i = 0
                lst = [round(m)]
                m_plus=m
                while m_plus <= max(data_filtered['m/z']) :
                    m_plus = m_plus + rep_pattern
                    if widgets.roundUp.isChecked():
                        i = math.ceil(m_plus * (nominal_pattern/rep_pattern))
                    elif widgets.roundClosest.isChecked():
                        i = round(m_plus * (nominal_pattern/rep_pattern))
                    lst.append(i)
                m_moins=m
                while m_moins >= min(data_filtered['m/z']) :
                    m_moins = m_moins - rep_pattern
                    if widgets.roundUp.isChecked():
                        i = math.ceil(m_moins * (nominal_pattern/rep_pattern))
                    elif widgets.roundClosest.isChecked():
                        i = round(m_moins * (nominal_pattern/rep_pattern))
                    lst.append(i)
                lst.sort()
                data_filtered.sort_values('m/z', ascending=True, inplace= True)
                data_filtered = data_filtered.reset_index(drop=True)
                for kmd_exp in data_filtered['Kendrick mass defect'] :
                    if kmd_exp >= kmd-tol and kmd_exp <= kmd+tol :
                        for o in lst:
                            if  o ==  data_filtered['Kendrick nominal mass'][l]:
                                data_filtered.at[l,'id'] = j+1
                    l=l+1
            d = {'col1': data_filtered['Kendrick nominal mass'], 'col2': data_filtered['Kendrick mass defect'], 'normalized_intensity': data_filtered['normalized_intensity'], 'id':data_filtered['id'],'m/z': data_filtered['m/z']}
            df = pandas.DataFrame(data=d)
            df = df.sort_values('normalized_intensity', ascending=True)
            if widgets.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            fig = plt.figure()
            if widgets.radioButtonWhole.isChecked():
                plt.scatter(df['col1'], df['col2'], color=[0, 0, 0, 0.1],s=df['normalized_intensity']*dot_size/100)
            for k in list_series_index:
                d_series= data_filtered[data_filtered['id'] == k+1]
                plt.scatter(d_series['Kendrick nominal mass'], d_series['Kendrick mass defect'], color=list_color[k],s=(d_series['normalized_intensity'])*dot_size/100, edgecolors='black')

            plt.clim(0,n_series)
            if widgets.KNM_min.text():
                KNM_min = float(widgets.KNM_min.text())
                plt.gca().set_xlim(left=KNM_min)
            if widgets.KNM_max.text():
                KNM_max = float(widgets.KNM_max.text())
                plt.gca().set_xlim(right=KNM_max)
            if widgets.KMD_min.text():
                KMD_min = float(widgets.KMD_min.text())
                plt.gca().set_ylim(bottom=KMD_min)
            if widgets.KMD_max.text():
                KMD_max = float(widgets.KMD_max.text())
                plt.gca().set_ylim(top=KMD_max)
            plt.xlabel('Kendrick nominal mass')
            plt.ylabel("Kendrick mass defect")
            mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(d_series['m/z'].iloc[sel.target.index]))
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            plt.show()
            self.kendrickSeries=data_filtered[data_filtered['id'] != 0]
            return        
   
        
        

                    
        #### KMD & MD vs m/z ####
        else:          
        
            if not item_classes:
                item_classes = ['Unatributed']
            
            for item in item_classes:
                data_filtered = data_selected.df.copy()
                if item == 'Unatributed':
                    classe_selected = ""
                    pass
                else:
                    classe_selected = item.data(self.USERDATA_ROLE)
                    if classe_selected == 'All':
                        pass
                    elif 'x' in classe_selected:
                        index_classes = (data_filtered[classe_selected] == True)
                        data_filtered = data_filtered[index_classes]
                    else:
                        classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                        index_classes = (data_filtered[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                        data_filtered = data_filtered[index_classes]   
                
                #KMD calculation
                if widgets.edit_motif.text():
                    edit_repetive_unit = widgets.edit_motif.text()
                if widgets.edit_mass_motif.text():
                    repetive_unit_mass = float(widgets.edit_mass_motif.text())
                    nominal_unit = round(repetive_unit_mass)
                if "mz" in data_filtered:
                    data_filtered['Kendrick mass']= data_filtered['mz']*(nominal_unit/repetive_unit_mass)
                    data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])
                elif "count" in data_filtered:
                    data_filtered['Kendrick mass']= data_filtered['m/z']*(nominal_unit/repetive_unit_mass)
                    data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])
                elif "m/z" in data_filtered:
                    data_filtered['Kendrick mass']= data_filtered['m/z']*(nominal_unit/repetive_unit_mass)
                    data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])

                if widgets.roundUp.isChecked():
                    data_filtered['Kendrick nominal mass']=data_filtered['Kendrick mass'].apply(np.ceil)
                elif widgets.roundClosest.isChecked():
                    data_filtered['Kendrick nominal mass']=round(data_filtered['Kendrick mass'])
                data_filtered['Kendrick mass defect']=data_filtered['Kendrick nominal mass']-data_filtered['Kendrick mass']
                if data_selected.df_type == 'PyC2MC_merged':
                    data_filtered = data_filtered.rename(columns={'summed_intensity':'normalized_intensity'})
                
                if data_selected.df_type == 'PyC2MC_merged':
                    data_filtered = data_filtered.rename(columns={'summed_intensity':'normalized_intensity'})
                if widgets.classic_intens_K.isChecked():
                    Intens= data_filtered["normalized_intensity"].copy()
                if widgets.sqrt_intens_K.isChecked():
                    Intens= data_filtered["normalized_intensity"].copy()
                    Intens= np.sqrt(Intens)
                if widgets.log_intens_K.isChecked():
                    Intens = np.log10(data_filtered["normalized_intensity"].copy()+1e-10)
                    Intens=(Intens - Intens.min()) / (Intens.max() - Intens.min())
                data_filtered["normalized_intensity"] = Intens
                data_filtered = data_filtered.sort_values(by=["normalized_intensity"], ascending=True)
    
                nominal_mass = round(data_filtered['m/z'])
                mass_defect = data_filtered['m/z'] - nominal_mass
                data_filtered['nominal_mass'] = nominal_mass
                data_filtered['mass_defect'] = mass_defect
                
                #-----------------------------------#
                #  Normalization on selected class  #
                #-----------------------------------#
                if widgets.radioButton_norm_d.isChecked():
                    intens=data_filtered["normalized_intensity"].copy()
                    intens=intens.values.reshape(-1,1)
                    if intens.shape[0]>1:
                        min_max_scaler = preprocessing.MinMaxScaler()
                        Intens_scaled = min_max_scaler.fit_transform(intens)
                        data_filtered["normalized_intensity"] = Intens_scaled
                        data_filtered = data_filtered.sort_values(by=["normalized_intensity"], ascending=True)
                    elif intens.shape[0]==1:
                        data_filtered["normalized_intensity"]=1
                    else :
                        QMessageBox.about(self, "Error", "No species to be displayed.")
                        continue
    
                
                data_filtered.classe_selected = classe_selected
                self.read_param()
                frames.append(data_filtered)
                def Anim(frames):
                    if gif == False:
                        fig = plt.figure()
                        transf = fig.transFigure
                    else:
                        Figure.clear()
                        transf = Figure.transFigure
                       
                    if widgets.stackedWidget_Kendrick.currentIndex()==0: #KMD classic
                        x_data = 'Kendrick nominal mass'
                        y_data = 'Kendrick mass defect'
                        x_label = 'Kendrick nominal mass'
                        y_label = 'Kendrick mass defect'
                        
                        #-----------------------------------#
                        #  Color by intensity               #
                        #-----------------------------------#
                        if widgets.K_intensity.isChecked():    
                            frames['third_dimension'] = frames["normalized_intensity"]
                            c_label = 'Normalized Intensity'
                            
                        #-----------------------------------#
                        #  Color by oxygen                  #
                        #-----------------------------------#
                        if widgets.K_oxygen.isChecked() :    
                            frames['third_dimension'] = frames["O"]
                            c_label = 'Oxygen number'
                        #-----------------------------------#
                        #  Color by nitrogen                #
                        #-----------------------------------#
                        if widgets.K_nitrogen.isChecked() :   
                            frames['third_dimension'] = frames["N"]
                            c_label = 'Nitrogen number'
                            
                            
                        #-----------------------------------#
                        #  Color by sulfur                  #
                        #-----------------------------------#
                        if widgets.K_sulfur.isChecked() :   
                            frames['third_dimension'] = frames["S"]
                            c_label = 'Sulfur number'

                        
                    elif  widgets.stackedWidget_Kendrick.currentIndex()==2: #Mass defect VS Nominal mass
                        x_data = 'nominal_mass'
                        y_data = 'mass_defect'
                        x_label = 'Nominal mass'
                        y_label = 'Mass defect'
                        
                        #-----------------------------------#
                        #  Color by intensity               #
                        #-----------------------------------#
                        if widgets.K_intensity_univ.isChecked():    
                            frames['third_dimension'] = frames["normalized_intensity"]
                            c_label = 'Normalized Intensity'

                        #-----------------------------------#
                        #  Color by oxygen                  #
                        #-----------------------------------#
                        if widgets.K_oxygen_univ.isChecked() :    
                            frames['third_dimension'] = frames["O"]
                            c_label = 'Oxygen number'

                        #-----------------------------------#
                        #  Color by nitrogen                #
                        #-----------------------------------#
                        if widgets.K_nitrogen_univ.isChecked() :   
                            frames['third_dimension'] = frames["N"]
                            c_label = 'Nitrogen number'
                            
                        #-----------------------------------#
                        #  Color by sulfur                  #
                        #-----------------------------------#
                        if widgets.K_sulfur_univ.isChecked() :   
                            frames['third_dimension'] = frames["S"]
                            c_label = 'Sulfur number'
                    
                    frames.sort_values(by=["third_dimension","normalized_intensity"],ascending = [True,True], inplace = True)

                    plot_fun("scatter",x = frames[x_data],y = frames[y_data],d_color = frames['third_dimension'] ,size = 1.5*dot_size*frames["normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)                  
                    
                    if widgets.KNM_min.text():
                        KNM_min = float(widgets.KNM_min.text())
                        plt.gca().set_xlim(left=KNM_min)
                    if widgets.KNM_max.text():
                        KNM_max = float(widgets.KNM_max.text())
                        plt.gca().set_xlim(right=KNM_max)
                    if widgets.KMD_min.text():
                        KMD_min = float(widgets.KMD_min.text())
                        plt.gca().set_ylim(bottom=KMD_min)
                    if widgets.KMD_max.text():
                        KMD_max = float(widgets.KMD_max.text())
                        plt.gca().set_ylim(top=KMD_max)
                    cbar = plt.colorbar()
                    cbar.ax.tick_params(labelsize=font_size-2)
                    cbar.set_label(c_label, labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)

                    plt.suptitle(f'{y_label} vs {x_label}',fontsize=font_size+4,y=0.96,x=0.45)
                    plt.xlabel(x_label, fontsize=font_size+4)
                    plt.ylabel(y_label, fontsize=font_size+4)
                    if 'molecular_formula' in frames:
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index]))
                    else:
                        mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['m/z'].iloc[sel.target.index]))
                    plt.xticks(fontsize=font_size)
                    plt.yticks(fontsize=font_size)
                    plt.text(0.12,0.9,f'{frames.classe_selected}',horizontalalignment='left',
                             verticalalignment='center', transform = transf,fontsize=font_size+2)
                    if gif == False:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                
            if gif == False:
                for i in frames:
                    Anim(i)   
                plt.show()
            else:
                Figure = plt.figure()
                plt.show()
                anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                writergif = PillowWriter(fps=self.fps) 
                anim_created.save("animation.gif", writer=writergif)
                plt.ion()
            return data_filtered
     

    def clear_series(self):
        """
        Clears m/z values in the KMD extraction panel
        """

        list_series=[widgets.series_1,widgets.series_2,widgets.series_3,\
                     widgets.series_4,widgets.series_5,widgets.series_6,\
                     widgets.series_7,widgets.series_8,widgets.series_9,widgets.series_10]
        for n in range(10):
            list_series[n].setText('')

    def save_kendrick_series(self):
        """
        Save the extracted series in a .csv file
        """

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        save_name, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        if save_name != '' and save_path!= '':
            # os.chdir(save_path)
            # self.kendrickSeries.to_csv(save_name +".csv",index = False)
            self.write_csv_df(save_path, save_name +".csv", self.kendrickSeries)
            
            QMessageBox.about(self, "FYI box", "Your file was correctly saved :)")
        else:
            QMessageBox.about(self, "Error box", "Either the save path or the  file name is missing.")
            return

    def envt_selector(self,gif = False):
        """
        Selects the appropriate environmental variable to plot
        """
        self.read_param()
        if widgets.radio_ACOS.isChecked():
            self.plot_ACOS(gif)
        elif widgets.radio_MAI.isChecked():
            self.plot_MAI(gif)
        elif widgets.radio_MCR.isChecked():
            self.plot_MCR(gif)


    def plot_ACOS(self,gif):
        """
        Average carbon oxydation plot
        """
        frames = []
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        item_classes = widgets.list_classes_ACOS.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)
            nc=widgets.nc_box.isChecked()



        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
    
            if widgets.radio_color_intensity_ACOS.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
                intens_for_size= data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc1_ACOS.isChecked():
                third_dimension = data_extract["PC1"]
                third_dimension = third_dimension+1
                intens_for_size= data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc2_ACOS.isChecked():
                third_dimension = data_extract["PC2"]
                third_dimension = third_dimension+1
                intens_for_size= data_extract["Normalized_intensity"]
            Intens = third_dimension.values.reshape(-1,1)
    
            if widgets.check_classic_ACOS.isChecked():
                Intens= Intens
            if widgets.check_sqrt_ACOS.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_ACOS.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract["point_size"]=intens_for_size
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)

            if classe_selected == 'All':
                pass
            else:
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (data_selected.df[classe_selected] == True)
                else:
                    index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
    
    
            if nc==True:
                data_extract['OSc']=2*data_extract["O/C"]-data_extract["H/C"]-5*data_extract["N/C"]
            else:
                data_extract['OSc']=2*data_extract["O/C"]-data_extract["H/C"]


        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                size=data_extract["point_size"].copy()
                size=size.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    Size_scaled = min_max_scaler.fit_transform(size)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract["point_size"] = Size_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                    data_extract["point_size"]=1
                else :
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue 


        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
            data_extract.classe_selected = classe_selected
            frames.append(data_extract)
            self.read_param()
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                plot_fun("scatter",x=frames["C"],y=frames["OSc"],d_color=frames["Normalized_intensity"],size=self.d_size*frames["point_size"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)
                plt.xlabel('#C', fontsize=self.fontsize+4)
                plt.ylabel('OSc', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
        
                plt.gca().invert_xaxis()
                if widgets.x_min_ACOS.text():
                    C_min = float(widgets.x_min_ACOS.text())
                    plt.gca().set_xlim(right=C_min)
                if widgets.x_max_ACOS.text():
                    C_max = float(widgets.x_max_ACOS.text())
                    plt.gca().set_xlim(left=C_max)
                plt.text(0.12,0.9,f'{frames.classe_selected}',horizontalalignment='left',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_ACOS.text():
                    ACOS_min = float(widgets.y_min_ACOS.text())
                    plt.gca().set_ylim(bottom=ACOS_min)
                if widgets.y_max_ACOS.text():
                    ACOS_max = float(widgets.y_max_ACOS.text())
                    plt.gca().set_ylim(top=ACOS_max)
                plt.suptitle('Average carbon oxidation state vs #C',fontsize=font_size+4,y=0.97,x=0.45)
                cbar = plt.colorbar()
                cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                    plt.clim(0,1)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] +', #C = '+ str(frames['C'].iloc[sel.target.index]) +', OCs = ' + str(round(frames['OSc'].iloc[sel.target.index],2))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_MAI(self, gif):
        """
        Plot a Van Krevelen diagram with the modified aromaticity index as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        item_classes = widgets.list_classes_MAI.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)

            if not 'S' in data_extract:
                data_extract['S']=0
            if not 'P' in data_extract:
                data_extract['P']=0
    
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
    
            Intens = data_extract["Normalized_intensity"].values.reshape(-1,1)
    
            if widgets.check_classic_MAI.isChecked():
                Intens= Intens
            if widgets.check_sqrt_MAI.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_MAI.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
            if not classe_selected == 'All':
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (data_selected.df[classe_selected] == True)
                else:
                    index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
    
            if widgets.MAI_box.isChecked():
                data_extract['AI']=(1+data_extract['C']-0.5*data_extract['O']-data_extract['S']-0.5*(data_extract['N']+data_extract['P']+data_extract['H']))/(data_extract['C']-0.5*data_extract['O']-data_extract['S']-data_extract['N']-data_extract['P'])
            else:
                data_extract['AI']=(1+data_extract['C']-data_extract['O']-data_extract['S']-0.5*(data_extract['N']+data_extract['P']+data_extract['H']))/(data_extract['C']-data_extract['O']-data_extract['S']-data_extract['N']-data_extract['P'])
            data_extract['AI'][data_extract['AI']<0]=0
            data_extract['AI'][data_extract['AI']>1]=1
    
            cond_1=pandas.Series(data_extract['AI']<=0.5) * pandas.Series(data_extract['AI']>=0)
            cond_2=pandas.Series(data_extract['AI']<=0.67) * pandas.Series(data_extract['AI']>0.5)
            cond_3=pandas.Series(data_extract['AI']<=1) * pandas.Series(data_extract['AI']>0.67)
    
    
    
        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(widgets, "Error", "No species to be displayed.")
                    continue
    
    
        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
    
            data_extract.classe_selected = classe_selected
            data_extract.cond_1 = cond_1.values
            data_extract.cond_2 = cond_2.values
            data_extract.cond_3 = cond_3.values
            frames.append(data_extract)
            self.read_param()
            
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
    
                d1=frames[frames.cond_1]
                d2=frames[frames.cond_2]
                d3=frames[frames.cond_3]
                ax1=plt.scatter(d1["O/C"],d1["H/C"],c='#06a96a',s=self.d_size*d1["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax2=plt.scatter(d2["O/C"],d2["H/C"],c='#f39c1b',s=self.d_size*d2["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax3=plt.scatter(d3["O/C"],d3["H/C"],c='#de281b',s=self.d_size*d3["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                plt.xlabel('O/C', fontsize=self.fontsize+4)
                plt.ylabel('H/C', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
        
        
                if widgets.x_min_MAI.text():
                    C_min = float(widgets.x_min_MAI.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_MAI.text():
                    C_max = float(widgets.x_max_MAI.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(0.12,0.9,f'{frames.classe_selected}',horizontalalignment='left',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_MAI.text():
                    MAI_min = float(widgets.y_min_MAI.text())
                    plt.gca().set_ylim(bottom=MAI_min)
                if widgets.y_max_MAI.text():
                    MAI_max = float(widgets.y_max_MAI.text())
                    plt.gca().set_ylim(top=MAI_max)
                plt.suptitle('Van Krevelen diagram',fontsize=font_size+4,y=0.97,x=0.45)
        
                cmap = (matplotlib.colors.ListedColormap(['#06a96a','#f39c1b', '#de281b']))
                bounds = [0, 0.5, 0.67,1 ]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar=plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing='proportional',
                    orientation='vertical',
                )
                cbar.set_label('Aromaticity Index', labelpad=-3.3*(font_size), rotation=90,fontsize=font_size, color = "white")
                cbar.ax.tick_params(labelsize=font_size-2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
        
                if "m/z" in frames:
                    mplcursors.cursor(ax1,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d1['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d1['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d1['AI'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax2,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d2['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d2['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d2['AI'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax3,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d3['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d3['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d3['AI'].iloc[sel.target.index].round(3))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
        
    def plot_MCR(self,gif):
        """
        Plot a Van Krevelen diagram with the maximum carbonyl ratio as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = widgets.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        
        item_classes = widgets.list_classes_MCR.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)
    
            if not 'S' in data_extract:
                data_extract['S']=0
            if not 'P' in data_extract:
                data_extract['P']=0
    
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
    
            Intens = data_extract["Normalized_intensity"].values.reshape(-1,1)
    
            if widgets.check_classic_MCR.isChecked():
                Intens= Intens
            if widgets.check_sqrt_MCR.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_MCR.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
            if classe_selected == 'All':
                pass
            else:
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (data_selected.df[classe_selected] == True)
                else:
                    index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
    
    
            data_extract['MCR']=data_extract['DBE']/data_extract['O']
            data_extract['MCR'][data_extract['MCR']<0]=0
            data_extract['MCR'][data_extract['MCR']>1]=1
    
            cond_1=pandas.Series(data_extract['MCR']<=0.2) * pandas.Series(data_extract['MCR']>=0)
            cond_2=pandas.Series(data_extract['MCR']<=0.5) * pandas.Series(data_extract['MCR']>0.2)
            cond_3=pandas.Series(data_extract['MCR']<=0.9) * pandas.Series(data_extract['MCR']>0.5)
            cond_4=pandas.Series(data_extract['MCR']<=1) * pandas.Series(data_extract['MCR']>0.9)
    
    
    
        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue
    
    
        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
    
            data_extract.classe_selected = classe_selected
            data_extract.cond_1 = cond_1.values
            data_extract.cond_2 = cond_2.values
            data_extract.cond_3 = cond_3.values
            data_extract.cond_4 = cond_4.values
            frames.append(data_extract)
            self.read_param()
            
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
    
    
                d1=frames[frames.cond_1]
                d2=frames[frames.cond_2]
                d3=frames[frames.cond_3]
                d4=frames[frames.cond_4]
                ax1=plt.scatter(d1["O/C"],d1["H/C"],c='#de281b',s=self.d_size*d1["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax2=plt.scatter(d2["O/C"],d2["H/C"],c='#f39c1b',s=self.d_size*d2["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax3=plt.scatter(d3["O/C"],d3["H/C"],c='#06a96a',s=self.d_size*d3["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax4=plt.scatter(d4["O/C"],d4["H/C"],c='#0f5fa8',s=self.d_size*d4["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                plt.xlabel('O/C', fontsize=self.fontsize+4)
                plt.ylabel('H/C', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
        
        
                if widgets.x_min_MCR.text():
                    C_min = float(widgets.x_min_MCR.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_MCR.text():
                    C_max = float(widgets.x_max_MCR.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(0.12,0.9,f'{frames.classe_selected}',horizontalalignment='left',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_MCR.text():
                    MCR_min = float(widgets.y_min_MCR.text())
                    plt.gca().set_ylim(bottom=MCR_min)
                if widgets.y_max_MCR.text():
                    MCR_max = float(widgets.y_max_MCR.text())
                    plt.gca().set_ylim(top=MCR_max)
                plt.suptitle('Van Krevelen diagram',fontsize=font_size+4,y=0.97,x=0.45)
                cmap = (matplotlib.colors.ListedColormap(['#de281b','#f39c1b', '#06a96a','#0f5fa8']))
                bounds = [0,0.2, 0.5, 0.9,1 ]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar=plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing='proportional',
                    orientation='vertical',
                )
                cbar.set_label('Maximum carbonyl ratio', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = "white")
                cbar.ax.tick_params(labelsize=font_size-2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
        
                if "m/z" in frames:
                    mplcursors.cursor(ax1,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d1['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d1['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d1['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax2,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d2['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d2['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d2['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax3,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d3['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d3['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d3['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax4,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d4['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d4['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d4['MCR'].iloc[sel.target.index].round(3))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()


    def venn(self):
        """
        Group molecular formula (or m/z ratio) to plot a Venn diagram.
        Groups are called sets.
        """

         # Select display mode
        if widgets.radio_count.isChecked():
            disp="{size}"
        elif widgets.radio_percentage.isChecked():
            disp="{percentage:.1f} %"
        #Select colormap
        color_map=(widgets.color.text())

        widgets.list_sets.clear()
        #Loads and store data in "data_selected" :
        item = widgets.list_loaded_file_2.selectedItems()
        item=item[0]
        if not item:
            return
        df=pandas.DataFrame()
        data_selected = item.data(self.USERDATA_ROLE)
        data_selected = data_selected.df
        inde = pandas.Series(data_selected['m/z'])
        data_venn=data_selected.set_index('m/z')
        filename=item.text().split(".")#Determines set's name ("xxx.csv" -> "xxx")
        n_heteroatoms=data_venn.columns.get_loc('count')
        n_ech=data_venn['count'].max() #n file= max(count)
        if n_ech < 2 or n_ech > 6:
            QMessageBox.about(self, "FYI box", "Number of samples to compare must be between 2 and 6")
            return
        for i in range(n_ech):
            df[i]=inde
        df=df.set_index(df[0])
        data_venn=data_venn.iloc[:,n_heteroatoms+1:n_heteroatoms+1+n_ech] #extracts intensity values

        #-----------------------------------------------------------------------------------
        #Creates a dataframe of the same dimensions as data_venn but filled with m/z
        #Mandatory since df.where was changed since last pandas version
        #-----------------------------------------------------------------------------------

        index_values=pandas.DataFrame({'a':data_venn.index.values},index =data_venn.index.values )
        index_df=index_values.copy()
        index_df.set_index('a',inplace=True)
        for i in range(data_venn.shape[1]):
            index_df=pandas.concat([index_df,index_values],axis=1)

        #-------
        # End
        #-------

        data_venn=data_venn.where(data_venn.eq(0),index_df.values) #Replaces non-null values by their corresponding index
        dict_venn={}

        for (columnName, columnData) in data_venn.iteritems():
            dict_venn[columnName]=set(columnData)

        venn_diag(dict_venn,fmt=disp, cmap=color_map).figure.show() #Plots using Venn.py (fonction venn_diag)
        sets=venn_sets(dict_venn) #EXctractiong and storage of data using Venn.py (fonction venn_sets)

        logic=[]
        for i in range(1, 2**n_ech):
            logic.append(bin(i)[2:].zfill(n_ech))

        for b in logic:
            widgets.list_sets.addItem(str(b))
        plt.show
        plt.tight_layout()
        #Variables globalization
        self.sets_all=sets
        self.sets_names=logic
        self.data_complete=data_selected
        widgets.Save_Sets_Button.setEnabled(True)

    def select_set_venn(self): 
        """
        Display values for the selected set
        """

        item_selected = widgets.list_sets.currentItem().text()
        data_se=self.data_complete
        data_se=data_se.loc[data_se['m/z'].isin(self.sets_all[item_selected])]
        data_se=data_se['m/z'].sort_values(ascending=True)

        widgets.set_content.setColumnCount(1)
        widgets.set_content.setRowCount(len(data_se))
        x=0
        for i in data_se.index:
            widgets.set_content.setItem(x,0,QTableWidgetItem(str(data_se[i])))
            x=x+1

    def save_sets_venn(self): 
        """
        Saves sets under a .xlsx file
        """

        #Progress bar#
        widgets.pbar.setMaximum(len(self.sets_names))
        value_pb_1=0
        widgets.pbar.setValue(value_pb_1)
        #\Progress bar#

        path = QtWidgets.QFileDialog.getExistingDirectory()
        if path == "":
            return
        filename, okPressed = QInputDialog.getText(self, "Save Name","Your name:", QLineEdit.Normal, "")
        if filename == "":
            return
        os.chdir(path)
        filename=(filename+".xlsx")
        data=self.data_complete

        for columnName, content in data.iteritems(): #drops columns Nx Ox Sx etc ..
            if len(columnName) == 2 and 'x' in columnName:
                data=data.drop(columnName,axis=1)
        with pandas.ExcelWriter(filename) as writer:
            for s in self.sets_names:
                df=data.loc[data['m/z'].isin(self.sets_all[s])]
                df.set_index('m/z',inplace=True)
                df.sort_index(ascending=True,inplace=True)
                names_dict = {'m/z':'calc. m/z'}
                df = df.rename(columns=names_dict)
                df.to_excel(writer,sheet_name=str(s))
                #Progress Bar#
                value_pb_1=value_pb_1+1
                widgets.pbar.setValue(value_pb_1)
                #\Progress bar#
                widgets.pbar.hide()
        QMessageBox.about(self, "FYI box", "Your file was correctly saved.")

    def plot_composition_compare(self):
        """
        Composition plots for the compare menu (Chemical family)
        """
        self.read_param()
        font_size = self.fontsize
        try : 
            self.compared_datas
        except : 
            QMessageBox.about(self, "FYI box", "Please select several data files.")
            return
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        if widgets.font_size.text():
            font_size = float(widgets.font_size.text())
        fig, ax = plt.subplots()
        if widgets.radio_classes_compare.isChecked():
            if widgets.edit_min_intensity_classes_compare.text():
                min_intens_classes = float(widgets.edit_min_intensity_classes_compare.text())
                classes = self.compared_datas.classes[~self.compared_datas.classes['variable'].str.contains("x")]
                classes = classes[classes['value'] > min_intens_classes]
            else:
                classes = self.compared_datas.classes[~self.compared_datas.classes['variable'].str.contains("x")]
        else:
            if widgets.edit_min_intensity_classes_compare.text():
                min_intens_classes = float(widgets.edit_min_intensity_classes_compare.text())
                classes = self.compared_datas.classes[self.compared_datas.classes['variable'].str.contains("x")]
                ch =  self.compared_datas.classes[self.compared_datas.classes['variable'].str.contains('CH')]
                classes = classes.append(ch)
                classes = classes[classes['value'] > min_intens_classes]
            else:
                classes = self.compared_datas.classes[self.compared_datas.classes['variable'].str.contains("x")]
                ch =  self.compared_datas.classes[self.compared_datas.classes['variable'].str.contains('CH')]
                classes = classes.append(ch)
        classes = classes.sort_values('value',ascending = False)
        classes = classes.reset_index(drop=True)
        if widgets.radio_classes_grouped.isChecked():
            capsize=5
            if widgets.radio_comp_int_compare.isChecked():
                ax.bar(classes['variable'], classes['value'],yerr=classes['std_dev_rel'], align='center', ecolor='black', capsize=capsize)
                plt.ylabel("Relative intensity (%)", fontsize=font_size+2)
            elif widgets.radio_comp_nb_compare.isChecked():
                ax.bar(classes['variable'], classes['number'])
                plt.ylabel("Number", fontsize=font_size+2)
            plt.suptitle('Heteroatom class distribution', fontsize=font_size+2)
            plt.xticks(fontsize=font_size,rotation=45)
            plt.yticks(fontsize=font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            plt.show()
        elif widgets.radio_one_by_one.isChecked():
            capsize=5
            leg = list(classes.variable.values)
            wid = float(widgets.compo_compare_width.text())
            gap = float(widgets.compo_compare_gap.text())
            y_max=int(len(classes.per_datas[0]))

            data_comp=pandas.DataFrame(columns=range(len(leg)),index=self.name.values())
            leg_raw = self.name.values()
            leg_2 = []
            for name in leg_raw:
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                leg_2.append(name)
                
            if widgets.radio_comp_int_compare.isChecked():
                for y in range(y_max):
                    for i in range(len(leg)):
                        data_comp.iloc[y,i]=classes.per_datas[i][y]
                plt.ylabel("Relative intensity (%)", fontsize=font_size+2)

            elif widgets.radio_comp_nb_compare.isChecked():
                for y in range(y_max):
                    for i in range(len(leg)):
                        data_comp.iloc[y,i]=classes.per_datas_nb[i][y]
                plt.ylabel("Number", fontsize=font_size+2)

            for y in range(y_max):
                ab=np.array( data_comp.columns)-gap*(0.5-((y+1)/(y_max+1)))/(y_max+1)
                plt.bar(ab,data_comp.iloc[y,:],width=(0.14*wid)/(y_max+1),color=color_list[y%9])
            plt.gca().legend(leg,fontsize=font_size-4)

            ax.set_xticks(range(len(leg)))
            ax.set_xticklabels(leg)
            cursor = mplcursors.cursor(multiple=True)
            @cursor.connect("add")
            def on_add(sel):
                x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
                sel.annotation.set(text=f"Rel.Int.: {round(height,4)}%",
                                   position=(0, 20), anncoords="offset points")
                sel.annotation.xy = (x + width / 2, y + height)
            plt.gca().legend(leg_2,fontsize=font_size-4)
            plt.suptitle('Heteroatom class distribution', fontsize=font_size+2)
            plt.xticks(fontsize=font_size,rotation=45)
            plt.yticks(fontsize=font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            plt.show()

    def plot_distrib_compare(self, gif = False):
        """
        Distribution plots for the compare menu
        """
        self.read_param()
        font_size = self.fontsize
        frames = []
        item_classes = widgets.list_classes_distrib_compare.selectedItems()
        if not item_classes:
            return
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        for classe_selected in item_classes:
            classe_selected = classe_selected.data(self.USERDATA_ROLE)
            if classe_selected == 'All':
                data = self.compared_datas.df
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data = self.compared_datas.df[index_classes]
            if len(data) == 0:
                QMessageBox.about(self, "FYI box", f"Nothing to display for {classe_selected} class.")
                continue
            data.classe_selected = classe_selected
            frames.append(data)
            def Anim(frames):
            ### Paramètres de subplot
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
    
                x_axes = widgets.list_distribution_compare.currentRow()
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                plt.ylabel('Relative Intensity (%)', fontsize=font_size+2)
                x_axes = widgets.list_distribution_compare.currentRow()
                
                ###
                if x_axes == 0: #DBE
                    dbe_both_m = pandas.DataFrame()
                    index_dbe_both_m = list()
                    dbe_odd_m = pandas.DataFrame()
                    dbe_even_m = pandas.DataFrame()
                    m = -0.5
                    while m < max(frames.DBE):
                        index_dbe_both_m.append(m)
                        m = m + 0.5
                    dbe_exp = frames.DBE
                    intens = frames.iloc[:,frames.columns.get_loc('count')+max(frames['count'])+1:
                                                frames.columns.get_loc('count')+max(frames['count'])*2+1] #stocke les intensités relatives des échantillons
                    df=pandas.concat([dbe_exp, intens],axis=1)
                    for y in index_dbe_both_m:
                        index_DBE_m = (df.DBE==y)
                        data_DBE_m = df[index_DBE_m].astype(float)
                        dbe_sum_m=pandas.DataFrame()
                        for i in range(max(frames['count'])):
                            intensity_DBE_m = sum(data_DBE_m.iloc[:,1+i])
                            dbe_sum_m[i] = [intensity_DBE_m]
                        dbe_both_m[y]=list(dbe_sum_m.values[0])
        
                        if y.is_integer():
                            dbe_odd_m[y]=list(dbe_sum_m.values[0])
                        else :
                            dbe_even_m[y]=list(dbe_sum_m.values[0])
        
                    dbe_both_m.index=list(data_DBE_m.columns[1:]) #Remplace l'index par le nom de l'échantillon
                    dbe_odd_m.index=list(data_DBE_m.columns[1:])
                    dbe_even_m.index=list(data_DBE_m.columns[1:])
                    if widgets.radio_even_DBE_compare.isChecked():
                        data_DBE_m=dbe_even_m
                        dbe_text="Even ions"
                    elif widgets.radio_odd_DBE_compare.isChecked():
                        data_DBE_m=dbe_odd_m
                        dbe_text="Odd ions"
                    elif widgets.radio_both_DBE_compare.isChecked():
                        data_DBE_m=dbe_both_m
                        dbe_text="Both parity"
                    leg_raw = list(data_DBE_m.index.values)
                    leg = []
                    for name in leg_raw:
                        name = name.replace("Rel_intens_","")
                        name = name.replace(".csv","")
                        name = name.replace(".xlsx","")
                        leg.append(name)
                    x_label = 'DBE'
                    y_max = len(data_DBE_m)
                    to_plt = data_DBE_m
        
                elif x_axes == 1: #C
                    dbe_text="Even and odd ions"
                    C_both = pandas.DataFrame()
                    intens = frames.iloc[:,frames.columns.get_loc('count')+max(frames['count'])+1:
                                                frames.columns.get_loc('count')+max(frames['count'])*2+1] #stocke les intensités relatives des échantillons
                    if "C" in frames:
                        all_C = frames.C.drop_duplicates()
                        df=pandas.concat([frames.C, intens],axis=1)
                        for y in all_C:
                            index_C_m = (df.C==y)
                            data_C_m = df[index_C_m].astype(float)
                            C_sum_m=pandas.DataFrame()
                            for i in range(max(frames['count'])):
                                intensity_C_m = sum(data_C_m.iloc[:,1+i])
                                C_sum_m[i] = [intensity_C_m]
                            C_both[y]=list(C_sum_m.values[0])
        
                        C_both.index=list(data_C_m.columns[1:])
                        leg_raw = list(C_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_","")
                            name = name.replace(".csv","")
                            name = name.replace(".xlsx","")
                            leg.append(name)
                        y_max=len(C_both)
                        x_label = '#C'
                        to_plt = C_both          
        
                elif x_axes == 2:
                    dbe_text="Even and odd ions"
                    N_both = pandas.DataFrame()
                    intens = frames.iloc[:,frames.columns.get_loc('count')+max(frames['count'])+1:
                                                frames.columns.get_loc('count')+max(frames['count'])*2+1] #stocke les intensités relatives des échantillons
                    if "N" in frames:
                        all_N = frames.N.drop_duplicates()
                        df=pandas.concat([frames.N, intens],axis=1)
                        for y in all_N:
                            index_N_m = (df.N==y)
                            data_N_m = df[index_N_m].astype(float)
                            N_sum_m=pandas.DataFrame()
                            for i in range(max(frames['count'])):
                                intensity_N_m = sum(data_N_m.iloc[:,1+i])
                                N_sum_m[i] = [intensity_N_m]
                            N_both[y]=list(N_sum_m.values[0])
        
                        N_both.index=list(data_N_m.columns[1:])
                        leg_raw = list(N_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_","")
                            name = name.replace(".csv","")
                            name = name.replace(".xlsx","")
                            leg.append(name)
                        y_max=len(N_both)
                        x_label = '#N'
                        to_plt = N_both  
                        
                elif x_axes == 3:
                    dbe_text="Even and odd ions"
                    O_both = pandas.DataFrame()
                    intens = frames.iloc[:,frames.columns.get_loc('count')+max(frames['count'])+1:
                                                frames.columns.get_loc('count')+max(frames['count'])*2+1] #stocke les intensités relatives des échantillons
                    if "O" in frames:
                        all_O = frames.O.drop_duplicates()
                        df=pandas.concat([frames.O, intens],axis=1)
                        for y in all_O:
                            index_O_m = (df.O==y)
                            data_O_m = df[index_O_m].astype(float)
                            O_sum_m=pandas.DataFrame()
                            for i in range(max(frames['count'])):
                                intensity_O_m = sum(data_O_m.iloc[:,1+i])
                                O_sum_m[i] = [intensity_O_m]
                            O_both[y]=list(O_sum_m.values[0])
        
                        O_both.index=list(data_O_m.columns[1:])
                        leg_raw = list(O_both.index.values)                
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_","")
                            name = name.replace(".csv","")
                            name = name.replace(".xlsx","")
                            leg.append(name)
                        y_max=len(O_both)
                        x_label = '#O'
                        to_plt = O_both  
                        
                elif x_axes == 4:
                    dbe_text="Even and odd ions"
                    S_both = pandas.DataFrame()
                    intens = frames.iloc[:,frames.columns.get_loc('count')+max(frames['count'])+1:
                                                frames.columns.get_loc('count')+max(frames['count'])*2+1] #stocke les intensités relatives des échantillons
                    if "S" in frames:
                        all_S = frames.S.drop_duplicates()
                        df=pandas.concat([frames.S, intens],axis=1)
                        for y in all_S:
                            index_S_m = (df.S==y)
                            data_S_m = df[index_S_m].astype(float)
                            S_sum_m=pandas.DataFrame()
                            for i in range(max(frames['count'])):
                                intensity_S_m = sum(data_S_m.iloc[:,1+i])
                                S_sum_m[i] = [intensity_S_m]
                            S_both[y]=list(S_sum_m.values[0])
        
                        S_both.index=list(data_S_m.columns[1:])
                        leg_raw = list(S_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_","")
                            name = name.replace(".csv","")
                            name = name.replace(".xlsx","")
                            leg.append(name)
                        y_max=len(S_both)
                        x_label = '#S'
                        to_plt = S_both  
                
                wid = float(widgets.Distrib_compare_width.text())
                gap = float(widgets.Distrib_compare_gap.text())
                for y in range(y_max):  #y_max = number of samples
                    ab=np.array(to_plt.columns)-gap*(0.5-((y+1)/(y_max+1)))/(y_max+1)
                    plt.bar(ab,to_plt.iloc[y,:],width=(0.14*wid)/(y_max+1),color=color_list[y%9])
                #Plot parameters :
                plt.gca().legend(leg,fontsize=font_size-4)        
                if widgets.x_compare_min.text():
                    x_min = float(widgets.x_compare_min.text())
                    plt.gca().set_xlim(left=x_min)
                if widgets.x_compare_max.text():
                    x_max = float(widgets.x_compare_max.text())
                    plt.gca().set_xlim(right=x_max)
                plt.xlabel(x_label, fontsize=font_size+2)
                plt.suptitle(f"Rel Intens. vs {x_label}",fontsize=font_size+4,y=0.98,x=0.45)
                plt.text(0.88,0.9,dbe_text,horizontalalignment='right',
                         verticalalignment='center', transform = transf,fontsize=font_size)
                plt.text(0.12,0.9,frames.classe_selected,horizontalalignment='left',
                         verticalalignment='center', transform = transf,fontsize=font_size)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                cursor = mplcursors.cursor(multiple=True)
                @cursor.connect("add")
                def on_add(sel):
                    x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
                    sel.annotation.set(text=f"Rel.Int.: {round(height,4)}%",
                                       position=(0, 20), anncoords="offset points")
                    sel.annotation.xy = (x + width / 2, y + height)
                    
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()        

    def plot_spectrum_compare(self):
        """
        Plots mass spectrum in the compare menu
        """
        self.read_param()
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        fig = plt.figure()

        data_selected = self.compared_datas

        item_classes = widgets.list_classes_mass_spec_comp.selectedItems()
        if not item_classes:
            return
        leg=list()
        for i in range(len(item_classes)):
            classe_selected = item_classes[i].data(self.USERDATA_ROLE)

            if classe_selected == 'All':
                data_filtered=data_selected.df
            else:
                classes_index = data_selected.classes[data_selected.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (data_selected.df[classe_selected] == True)
                else:
                    index_classes = (data_selected.df[data_selected.heteroatoms.columns] == data_selected.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_filtered = data_selected.df[index_classes]

            data_filtered = data_filtered.sort_values(by=["summed_intensity"], ascending=True)
            if i == 0:
                c = 'k'
            elif i == 1:
                c = 'b'
            elif i == 2:
                c = 'r'
            elif i == 3:
                c = 'g'
            elif i == 4:
                c = 'm'
            elif i == 5:
                c = 'c'
            patch=mpatches.Patch(color=c, label = item_classes[i].text())
            leg.append(patch)
            plt.stem(data_filtered["m/z"], data_filtered["summed_intensity"],c,markerfmt=" ", basefmt="k")
        if widgets.mz_min_2.text():
            mz_min_2 = float(widgets.mz_min_2.text())
            plt.gca().set_xlim(left=mz_min_2)
        if widgets.mz_max_2.text():
            mz_max_2 = float(widgets.mz_max_2.text())
            plt.gca().set_xlim(right=mz_max_2)
        if widgets.intens_min.text():
            intens_min = float(widgets.intens_min.text())
            plt.gca().set_ylim(bottom=intens_min)
        if widgets.intens_max.text():
            intens_max = float(widgets.intens_max.text())
            plt.gca().set_ylim(top=intens_max)
        if widgets.font_size.text():
            font_size = float(widgets.font_size.text())
        plt.gca().legend(handles=leg,fontsize=font_size-2)
        plt.xlabel('m/z', fontsize=font_size+2,style='italic')
        plt.ylabel('Intensity', fontsize=font_size+2)
        plt.xticks(fontsize=font_size)
        plt.yticks(fontsize=font_size)
        yaxes = plt.gca().yaxis
        yaxes.offsetText.set_fontsize(font_size)
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
        plt.show()

    def compare_calculation(self):
        """
        Creates an in-line merged file with the samples selected in the compare menu
        """

        widgets.plot_compare.setEnabled(False)
        widgets.plot_compare_GIF.setEnabled(False)
        widgets.status_compare.setStyleSheet("background-color: rgb(255, 150, 0); border-radius: 12px; color: white")
        widgets.status_compare.setText("Operating")
        data = {}
        self.name = {}
        compare_items = widgets.list_loaded_file_compare.selectedItems()
        if not compare_items or len(compare_items) < 2:
            widgets.status_compare.setStyleSheet("background-color: rgb(220, 0, 3); border-radius: 12px; color: white")
            widgets.status_compare.setText("No Files")
            return

        else:
            widgets.pbar.show()
            v=int(0)
            widgets.pbar.setValue(int(v))   
            for i in range(len(compare_items)):
                item = compare_items[i].data(self.USERDATA_ROLE)
                self.name[i] = compare_items[i].text()
                data[i] = pandas.DataFrame(item.df)
                v = 50*(i+1)/len(compare_items)
                widgets.pbar.setValue(int(v))   
            compared_datas = merge_for_compare(data,self.name)
            widgets.pbar.setValue(int(75))   
            self.compared_datas = load_MS_file(compared_datas)
            widgets.pbar.setValue(int(90))  
        widgets.status_compare.setStyleSheet("background-color: rgb(50, 150, 0); border-radius: 12px; color: white")
        widgets.status_compare.setText("Ready")
        widgets.pbar.setValue(int(100))
        widgets.pbar.hide()
        self.split_classes_compare()
        
    def split_classes_compare(self):
        if  widgets.status_compare.text() != "Ready":
            return
        
        widgets.list_classes_mass_spec_comp.clear()
        widgets.list_classes_distrib_compare.clear()
        widgets.list_classes_DBE_compare.clear()
        widgets.list_classes_VK_compare.clear()
        widgets.list_classes_DBE_comp.clear()
        widgets.list_classes_VK_comp.clear()
        widgets.list_classes_Kendrick_comp.clear()
        widgets.list_classes_Kendrick_univ_comp.clear()
        
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_mass_spec_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_distrib_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_DBE_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_VK_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_DBE_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_VK_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_Kendrick_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_Kendrick_univ_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_ACOS_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_MAI_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem('All')
        item_classes.setData(self.USERDATA_ROLE, 'All')
        widgets.list_classes_MCR_comp.addItem(item_classes)
        n=0
        while n < len(self.compared_datas.classes):
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_mass_spec_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_distrib_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_DBE_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_VK_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_DBE_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_VK_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_Kendrick_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_Kendrick_univ_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_ACOS_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_MAI_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(self.compared_datas.classes_concat.iloc[n,0])
            item_classes.setData(self.USERDATA_ROLE, self.compared_datas.classes.iloc[n,0])
            widgets.list_classes_MCR_comp.addItem(item_classes)
            n=n+1
        widgets.plot_compare.setEnabled(True)
        widgets.plot_compare_GIF.setEnabled(True)
        widgets.list_classes_distrib_compare.setCurrentRow(0)
        widgets.list_compare_sample_1.clear()
        widgets.list_compare_sample_2.clear()
        name_data = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])+1:self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])*2+1]
        name_data.columns=name_data.columns.str.replace(".csv","")
        name_data.columns=name_data.columns.str.replace(".xlsx","")
        name_data.columns=name_data.columns.str.replace('Rel_intens_','')
        n=0
        if 'PC1' in self.compared_datas.df:
            widgets.radio_color_pc1_comp.show()
            widgets.radio_color_pc1_comp.setEnabled(True)
            widgets.radio_color_pc2_comp.show()
            widgets.radio_color_pc2_comp.setEnabled(True)
            widgets.radio_color_pc1_VK_comp.show()
            widgets.radio_color_pc1_VK_comp.setEnabled(True)
            widgets.radio_color_pc2_VK_comp.show()
            widgets.radio_color_pc2_VK_comp.setEnabled(True)
            widgets.radio_color_pc1_ACOS_comp.show() 
            widgets.radio_color_pc1_ACOS_comp.setEnabled(True)
            widgets.radio_color_pc2_ACOS_comp.show()
            widgets.radio_color_pc2_ACOS_comp.setEnabled(True)

        else:
            widgets.radio_color_pc1_comp.hide()
            widgets.radio_color_pc1_comp.setEnabled(False)
            widgets.radio_color_pc2_comp.hide()
            widgets.radio_color_pc2_comp.setEnabled(False)
            widgets.radio_color_pc1_VK_comp.hide()
            widgets.radio_color_pc1_VK_comp.setEnabled(False)
            widgets.radio_color_pc2_VK_comp.hide()
            widgets.radio_color_pc2_VK_comp.setEnabled(False)
            widgets.radio_color_pc1_ACOS_comp.hide() 
            widgets.radio_color_pc1_ACOS_comp.setEnabled(False)
            widgets.radio_color_pc2_ACOS_comp.hide()
            widgets.radio_color_pc2_ACOS_comp.setEnabled(False)
            
        while n < len(name_data.columns):
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            widgets.list_compare_sample_1.addItem(item_sample)
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            widgets.list_compare_sample_2.addItem(item_sample)
            n=n+1
        widgets.list_classes_DBE_compare.setCurrentRow(0)
        widgets.list_classes_VK_compare.setCurrentRow(0)
        widgets.list_classes_DBE_comp.setCurrentRow(0)
        widgets.list_classes_VK_comp.setCurrentRow(0)
        widgets.list_classes_Kendrick_comp.setCurrentRow(0)
        widgets.list_classes_Kendrick_univ_comp.setCurrentRow(0)

    def plot_molecular_carto_DBE(self,gif = False):
        """
        DBE vs C# plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_1 = widgets.list_compare_sample_1.currentRow()
        sample_2 = widgets.list_compare_sample_2.currentRow()
        n_sample = max(self.compared_datas.df['count'])
        if widgets.radio_fold_rel.isChecked():
            fold_intens_1 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])+1+sample_1].values.astype(float).copy().reshape(-1, 1)
            fold_intens_2 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])+1+sample_2].values.astype(float).copy().reshape(-1, 1)
            min_max_scaler = preprocessing.MinMaxScaler()
            fold_intens_1 = min_max_scaler.fit_transform(fold_intens_1)
            fold_intens_2 = min_max_scaler.fit_transform(fold_intens_2)
            
            leg_1 = str(self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_1].name)
            leg_2 = str(self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_2].name)
            leg_1 = leg_1.replace(".csv","")
            leg_2 = leg_2.replace(".csv","")
            leg_1 = leg_1.replace(".xlsx","")
            leg_2 = leg_2.replace(".xlsx","")
            leg_1 = leg_1.replace("Rel_intens_","")
            leg_2 = leg_2.replace("Rel_intens_","")
        else:
            fold_intens_1 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_1].astype(float)
            fold_intens_2 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_2].astype(float)
            leg_1 = str(fold_intens_1.name)
            leg_2 = str(fold_intens_2.name)
            leg_1 = leg_1.replace(".csv","")
            leg_2 = leg_2.replace(".csv","")
            leg_1 = leg_1.replace(".xlsx","")
            leg_2 = leg_2.replace(".xlsx","")
            leg_1 = leg_1.replace("Abs_intens_","")
            leg_2 = leg_2.replace("Abs_intens_","")

        self.compared_datas.df["fc"] = np.log2(fold_intens_2/fold_intens_1)
        ####
        #Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df['fc'].fillna(2e20,inplace=True)
        p_inf=(self.compared_datas.df['fc'] >1e20).tolist()
        n_inf=(self.compared_datas.df['fc'] <-1e20).tolist()
        data_inf_pos = self.compared_datas.df[:][p_inf].copy()
        data_inf_neg = self.compared_datas.df[:][n_inf].copy()
        inf_index=[i or j for i, j in zip(n_inf,p_inf)]
        
        
        item_classes = widgets.list_classes_DBE_compare.selectedItems()
        if not item_classes:
            return
        
        for item in item_classes:
            data_extract = self.compared_datas.df.drop(index=self.compared_datas.df.index[inf_index],axis=0).copy()
            classe_selected = item.data(self.USERDATA_ROLE)
            
            
            data_extract = data_extract.sort_values(by=["fc"], ascending=False)
            Intens = data_extract.iloc[:,self.compared_datas.df.columns.get_loc('summed_intensity')-2].values.reshape(-1,1)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract.iloc[:,self.compared_datas.df.columns.get_loc('summed_intensity')-2] = Intens_scaled
            
            if classe_selected == 'All':
                pass 
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
                data_inf_neg = data_inf_neg[index_classes]
                data_inf_pos = data_inf_pos[index_classes]
    
            dbe_text="Even and odd ions"
            if widgets.radio_even_DBE_compare_2.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==1]
                data_inf_neg = data_inf_neg.loc[np.where(data_inf_neg['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==1]
                data_inf_pos = data_inf_pos.loc[np.where(data_inf_pos['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==1]
                dbe_text="Even ions"
            elif widgets.radio_odd_DBE_compare_2.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==0]
                data_inf_neg = data_inf_neg.loc[np.where(data_inf_neg['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==0]
                data_inf_pos = data_inf_pos.loc[np.where(data_inf_pos['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==0]
                dbe_text="Odd ions"
            
            Intens = data_extract["Normalized_intensity"].values.reshape(-1,1)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=['fc',"Normalized_intensity"], ascending=[False,True])  
            
            if len(data_extract) == 0:
                QMessageBox.about(self, "FYI box", f"Something went wrong trying to display {classe_selected}'s data \nNo common attributions")
                continue
            data = pandas.DataFrame()
            data.data_extract = data_extract 
            data.data_inf_neg = data_inf_neg 
            data.data_inf_pos = data_inf_pos
            data.classe_selected = classe_selected
            frames.append(data)
            def Anim(frames):   
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                self.read_param()
                if widgets.CheckBox_size_fc.isChecked() :
                    size = self.d_size*frames.data_extract.iloc[:,self.compared_datas.df.columns.get_loc('summed_intensity')-(n_sample)+sample_1].astype(float)
                    size_inf_neg = self.d_size*frames.data_inf_neg.iloc[:,self.compared_datas.df.columns.get_loc('summed_intensity')-(n_sample)+sample_1].astype(float)
                    size_inf_pos = self.d_size*frames.data_inf_pos.iloc[:,self.compared_datas.df.columns.get_loc('summed_intensity')-(n_sample)+sample_1].astype(float)
                else:
                    size = self.d_size
                    size_inf_neg = self.d_size
                    size_inf_pos = self.d_size
                    
                    
                if widgets.fc_all_dbe.isChecked() :
                    plot_fun("scatter",x=frames.data_inf_neg["C"],y=frames.data_inf_neg["DBE"],d_color='purple',dot_type=self.dot_type,edge=self.edge,size = size_inf_neg)
                    plot_fun("scatter",x=frames.data_inf_pos["C"],y=frames.data_inf_pos["DBE"],d_color='blue',dot_type=self.dot_type,edge=self.edge,size = size_inf_pos)
                plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = size)
                
                if widgets.C_min_DBE_compare.text():
                    C_min = float(widgets.C_min_DBE_compare.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.C_max_DBE_compare.text():
                    C_max = float(widgets.C_max_DBE_compare.text())
                    plt.gca().set_xlim(right=C_max)
        
                if widgets.DBE_min_DBE_compare.text():
                    DBE_min = float(widgets.DBE_min_DBE_compare.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if widgets.DBE_max_DBE_compare.text():
                    DBE_max = float(widgets.DBE_max_DBE_compare.text())
                    plt.gca().set_ylim(top=DBE_max)
                if widgets.CheckBox_hap_compare.isChecked():
                    plt.axline((13, 9), (19, 14), color="red", linestyle=(0, (5, 5)))
                plt.suptitle('DBE vs #C (fold change)',fontsize=font_size+4,y=0.97,x=0.45)
                
                cbar = plt.colorbar(ticks=[min(frames.data_extract["fc"]),max(frames.data_extract["fc"])])
                cbar.ax.set_yticklabels([leg_1,leg_2],fontsize=font_size-2,weight='bold',rotation = 90, va = 'center')  # vertically oriented colorbar
                cbar.set_label('log2(FC)', labelpad=-2.625*(font_size), rotation=90,fontsize=16)
                
                plt.xlabel('#C', fontsize=self.fontsize+4)
                plt.ylabel('DBE', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                plt.text(0.13,0.9,frames.classe_selected,horizontalalignment='left',
                              verticalalignment='center', transform = transf,fontsize=self.fontsize-1)
                
                plt.text(0.75,0.9,dbe_text,horizontalalignment='right',
                              verticalalignment='center', transform = transf,fontsize=self.fontsize-1)
                
                if widgets.fc_all_dbe.isChecked() :
                    legend_elements = [Patch(facecolor='purple', edgecolor='k',label=leg_1+ ' exclusive'),
                                        Patch(facecolor='blue', edgecolor='k',label=leg_2+ ' exclusive')]
                    plt.legend(handles=legend_elements,fontsize=font_size-4)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,800, 680)
                if "m/z" in frames.data_extract:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames.data_extract['molecular_formula'].iloc[sel.target.index] +', #C = '+ str(frames.data_extract['C'].iloc[sel.target.index]) +', DBE = ' + str(frames.data_extract['DBE'].iloc[sel.target.index])))
            
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,800, 680)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_molecular_carto_VK(self, gif = False):
        """
        Van Krevelen plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_1 = widgets.list_compare_sample_1.currentRow()
        sample_2 = widgets.list_compare_sample_2.currentRow()
        if widgets.radio_fold_rel.isChecked():
            fold_intens_1 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])+1+sample_1].astype(float)
            fold_intens_2 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+max(self.compared_datas.df['count'])+1+sample_2].astype(float)
            leg_1 = str(fold_intens_1.name)
            leg_2 = str(fold_intens_2.name)
            leg_1 = leg_1.replace(".csv","")
            leg_2 = leg_2.replace(".csv","")
            leg_1 = leg_1.replace(".xlsx","")
            leg_2 = leg_2.replace(".xlsx","")
            leg_1 = leg_1.replace("Rel_intens_","")
            leg_2 = leg_2.replace("Rel_intens_","")
        else:
            fold_intens_1 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_1].astype(float)
            fold_intens_2 = self.compared_datas.df.iloc[:,self.compared_datas.df.columns.get_loc('count')+1+sample_2].astype(float)
            leg_1 = str(fold_intens_1.name)
            leg_2 = str(fold_intens_2.name)
            leg_1 = leg_1.replace(".csv","")
            leg_2 = leg_2.replace(".csv","")
            leg_1 = leg_1.replace(".xlsx","")
            leg_2 = leg_2.replace(".xlsx","")
            leg_1 = leg_1.replace("Abs_intens_","")
            leg_2 = leg_2.replace("Abs_intens_","")

        self.compared_datas.df["fc"] = np.log2(fold_intens_2/fold_intens_1)
        ####
        #Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df['fc'].fillna(2e20,inplace=True)
        p_inf=(self.compared_datas.df['fc'] >1e20).tolist()
        n_inf=(self.compared_datas.df['fc'] <-1e20).tolist()
        inf_index=[i or j for i, j in zip(n_inf,p_inf)]
        data_inf_p = self.compared_datas.df[:][p_inf]
        data_inf_n = self.compared_datas.df[:][n_inf]
        item_classes = widgets.list_classes_VK_compare.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = self.compared_datas.df.drop(index=self.compared_datas.df.index[inf_index],axis=0).copy()
            classe_selected = item.data(self.USERDATA_ROLE)
            data_extract["Normalized_intensity"] = self.compared_datas.df['fc']
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = data_extract[index_classes]
                data_inf_p = data_inf_p[index_classes]
                data_inf_n = data_inf_n[index_classes]
            x_axes = widgets.list_VK_x_2.currentRow()
            y_axes = widgets.list_VK_y_2.currentRow()
            if x_axes == 0:
                x_axes = data_extract["O/C"]
                x_axes_p = data_inf_p["O/C"]
                x_axes_n = data_inf_n["O/C"]
                x_label = "O/C"
            elif x_axes == 1:
                x_axes = data_extract["N/C"]
                x_axes_p = data_inf_p["N/C"]
                x_axes_n = data_inf_n["N/C"]
                x_label = "N/C"
            elif x_axes == 2:
                x_axes = data_extract["S/C"]
                x_axes_p = data_inf_p["S/C"]
                x_axes_n = data_inf_n["S/C"]
                x_label = "S/C"
            elif x_axes == 3:
                x_axes = data_extract["H/C"]
                x_axes_p = data_inf_p["H/C"]
                x_axes_n = data_inf_n["H/C"]
                x_label = "H/C"
            elif x_axes == 4:
                x_axes = data_extract["m/z"]
                x_axes_p = data_inf_p["m/z"]
                x_axes_n = data_inf_n["m/z"]
                x_label = "m/z"
            if y_axes == 0:
                y_axes = data_extract["H/C"]
                y_axes_p = data_inf_p["H/C"]
                y_axes_n = data_inf_n["H/C"]
                y_label = "H/C"
            elif y_axes == 1:
                y_axes = data_extract["O/C"]
                y_axes_p = data_inf_p["O/C"]
                y_axes_n = data_inf_n["O/C"]
                y_label = "O/C"
            elif y_axes == 2:
                y_axes = data_extract["N/C"]
                y_axes_p = data_inf_p["N/C"]
                y_axes_n = data_inf_n["N/C"]
                y_label = "N/C"
            elif y_axes == 3:
                y_axes = data_extract["S/C"]
                y_axes_p = data_inf_p["S/C"]
                y_axes_n = data_inf_n["S/C"]
                y_label = "S/C"
            if widgets.font_size.text():
                font_size = float(widgets.font_size.text())
            if widgets.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            if len(data_extract) == 0:
                QMessageBox.about(self, "FYI box", f"Something went wrong trying to display {classe_selected}'s data \nNo common attributions")
                continue     
            data = pandas.DataFrame()
            data.data_extract = data_extract
            data.x_axes = x_axes 
            data.y_axes = y_axes 
            data.x_axes_n = x_axes_n 
            data.y_axes_n = y_axes_n
            data.x_axes_p = x_axes_p 
            data.y_axes_p = y_axes_p
            data.classe_selected = classe_selected
            frames.append(data)
            def Anim(frames,x_label,y_label):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                self.read_param()
                if widgets.fc_all_vk.isChecked():
                    plot_fun("scatter",x=frames.x_axes_n,y=frames.y_axes_n,d_color="purple",dot_type=self.dot_type,edge=self.edge,size = self.d_size)
                    plot_fun("scatter",x=frames.x_axes_p,y=frames.y_axes_p,d_color="blue",dot_type=self.dot_type,edge=self.edge,size = self.d_size)
            
             
                plot_fun("scatter",x=frames.x_axes,y=frames.y_axes,d_color=frames.data_extract["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = self.d_size)
        
        
                if widgets.x_min_VK_compare.text():
                    C_min = float(widgets.x_min_VK_compare.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_VK_compare.text():
                    C_max = float(widgets.x_max_VK_compare.text())
                    plt.gca().set_xlim(right=C_max)
                if widgets.y_min_VK_compare.text():
                    y_min = float(widgets.y_min_VK_compare.text())
                    plt.gca().set_ylim(bottom=y_min)
                if widgets.y_max_VK_compare.text():
                    y_max = float(widgets.y_max_VK_compare.text())
                    plt.gca().set_ylim(top=y_max)
                plt.suptitle('Van Krevelen (fold change)',fontsize=20,y=0.97,x=0.45)
                cbar = plt.colorbar(ticks=[min(frames.data_extract["Normalized_intensity"]),max(frames.data_extract["Normalized_intensity"])])
                cbar.ax.set_yticklabels([leg_1,leg_2],fontsize=font_size-2,weight='bold',rotation = -45)  # vertically oriented colorbar
                cbar.set_label('log2(FC)', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size)
                plt.xlabel(x_label, fontsize=font_size+4)
                plt.ylabel(y_label, fontsize=font_size+4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                plt.text(0.13,0.9,frames.classe_selected,horizontalalignment='left',
                              verticalalignment='center', transform = transf,fontsize=self.fontsize-1)
                
                if widgets.fc_all_vk.isChecked() :
                    legend_elements = [Patch(facecolor='purple', edgecolor='k',label=leg_1+ ' exclusive'),
                                       Patch(facecolor='blue', edgecolor='k',label=leg_2+ ' exclusive')]
                    plt.legend(handles=legend_elements,fontsize=font_size-4)
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(self.pos().x()+640,self.pos().y()+200,800, 680)
                mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames.data_extract['molecular_formula'].iloc[sel.target.index] + ', ' + str(x_label) +' : '+ str(round(frames.x_axes.iloc[sel.target.index],4)) + ', ' + str(y_label) +' = '+ str(round(frames.y_axes.iloc[sel.target.index],4))))
                
        if gif == False:
            for i in frames:
                Anim(i,x_label,y_label)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames,farg = (x_label,y_label,), interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,800, 680)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion() 
        

    def plot_DBE_compare(self,gif = False):
        
        """
        DBE vs C# plots
        """
        
        frames = []
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = widgets.list_classes_DBE_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                    data_selected.columns.get_loc('count')+item_count*2+1].columns
        for item in sample_list:
            if not item_classes:
                return
            if 'PC1' in data_selected:
                widgets.radio_color_pc1_comp.show()
                widgets.radio_color_pc2_comp.show()
    
            data_extract = data_selected.copy()
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = self.compared_datas.df[index_classes]   
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
            data_extract.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_extract.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity

            Intens = data_extract["Normalized_intensity"].values.astype(float).reshape(-1,1) #astype(float) or crash!
            if widgets.check_classic_comp.isChecked():
                Intens= Intens
            if widgets.check_sqrt_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_comp.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
    
        #-----------------------------------#
        #  Normalization on selected class  #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", f"No species to be displayed for the class : {classe_selected}.")
                    continue
    
        #-----------------------------------------#
        #  Normalization on selected class (end)  #
        #-----------------------------------------#
    
            
            if widgets.radio_even_DBE_comp.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==1]
                dbe_text="Even ions"
            elif widgets.radio_odd_DBE_comp.isChecked():
                data_extract = data_extract.loc[np.where(data_extract['DBE'].apply(lambda x: x.is_integer()), 0, 1) ==0]
                dbe_text="Odd ions"
            else :       
                dbe_text="Even and odd ions"
            if widgets.dot_size.text():
                dot_size = float(widgets.dot_size.text())
            if widgets.font_size.text():
                font_size = float(widgets.font_size.text())
            
    
        #-----------------------------------#
        #  Normalization on displayed data  #
        #-----------------------------------#
    
            if widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", f"No species to be displayed for the class : {classe_selected}.")
                    continue
    
        #-----------------------------------------#
        #  Normalization on displayed data (end)  #
        #-----------------------------------------#
        
            if widgets.radio_color_intensity_comp.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc1_comp.isChecked():
                third_dimension = data_extract["PC1"]
            elif widgets.radio_color_pc2_comp.isChecked():
                third_dimension = data_extract["PC2"]
            elif widgets.radio_color_O_comp.isChecked():
                third_dimension = data_extract["O"]
            data_extract["third_dimension"] = third_dimension
            data_extract.classe_selected = classe_selected
            data_extract.sample_name = item
            self.read_param()
            frames.append(data_extract)
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                
                plot_fun("scatter",x=frames["C"],y=frames["DBE"],d_color=frames["third_dimension"],size=dot_size*frames["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)
        
                if widgets.C_min_DBE_comp.text():
                    C_min = float(widgets.C_min_DBE_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.C_max_DBE_comp.text():
                    C_max = float(widgets.C_max_DBE_comp.text())
                    plt.gca().set_xlim(right=C_max)
                else:
                    C_max = data_selected.df['C'][data_selected.df['C'].idxmax()]
                if widgets.DBE_min_DBE_comp.text():
                    DBE_min = float(widgets.DBE_min_DBE_comp.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if widgets.DBE_max_DBE_comp.text():
                    DBE_max = float(widgets.DBE_max_DBE_comp.text())
                    plt.gca().set_ylim(top=DBE_max)
                else:
                    DBE_max = frames['DBE'][frames['DBE'].idxmax()]
                if widgets.CheckBox_hap_comp.isChecked():
                    plt.axline((13, 8.57), (19, 12.95), color="red", linestyle=(0, (5, 5)))
                plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.45)
                cbar = plt.colorbar()
                if widgets.radio_color_intensity_comp.isChecked():
                    cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc1_comp.isChecked():
                    cbar.set_label('PC1', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc2_comp.isChecked():
                    cbar.set_label('PC2', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
        
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radio_color_pc1_comp.isChecked():
                    plt.clim(np.min(data_selected.df['PC1']), np.max(data_selected.df['PC1']))
                elif widgets.radio_color_pc2_comp.isChecked():
                    plt.clim(np.min(data_selected.df['PC2']), np.max(data_selected.df['PC2']))
                plt.xlabel('#C', fontsize=font_size+4)
                plt.ylabel('DBE', fontsize=font_size+4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)  
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                plt.text(0.68,0.9,dbe_text,horizontalalignment='center',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] +', #C = '+ str(frames['C'].iloc[sel.target.index]) +', DBE = ' + str(frames['DBE'].iloc[sel.target.index])))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_VK_compare(self,gif = False):
        """
        Van Krevelen plot
        """

        frames = []
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = widgets.list_classes_VK_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        self.read_param()
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                    data_selected.columns.get_loc('count')+item_count*2+1].columns
        for item in sample_list:
        
            if not item_classes:
                return
            if 'PC1' in data_selected:
                widgets.radio_color_pc1_VK_comp.show()
                widgets.radio_color_pc2_VK_comp.show()
        
            
            data_filtered = data_selected.copy()

            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_filtered = self.compared_datas.df[index_classes]   
            
            #-----------------------------#
            #  3rd dimension selection    #
            #-----------------------------#

            data_filtered.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_filtered.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity

            Intens = data_filtered["Normalized_intensity"].values.astype(float).reshape(-1,1) #astype(float) or crash!
            if widgets.check_classic_vk_comp.isChecked():
                Intens= Intens
            if widgets.check_sqrt_vk_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_vk_comp.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value, log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled
    
    
            dot_size = self.d_size
            x_axes = widgets.list_VK_x_comp.currentRow()
            y_axes = widgets.list_VK_y_comp.currentRow()
            
            #Tests the presence of sulfur
            if x_axes == 2 or y_axes == 3:
                try:
                    test=data_filtered["S/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No sulfur in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
            #Tests the presence of oxygen
            if x_axes == 0 or y_axes == 1:
                try:
                    test=data_filtered["O/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No oxygen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
            #Tests the presence of nitrogen
            if x_axes == 1 or y_axes == 2:
                try:
                    test=data_filtered["N/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(self, "Error", "No nitrogen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.")
    
            #Tests the presence of hydrogen
            if x_axes == 3 or y_axes == 0:
                try:
                    test=data_filtered["H/C"]
                    del test
                except:
                    QMessageBox.about(self, "Error", "No hydrogen in the selected data")
                    continue
                    
            if x_axes == 0:
                x_axes = data_filtered["O/C"]
                x_label = "O/C"
            elif x_axes == 1:
                x_axes = data_filtered["N/C"]
                x_label = "N/C"
            elif x_axes == 2:
                x_axes = data_filtered["S/C"]
                x_label = "S/C"
            elif x_axes == 3:
                x_axes = data_filtered["H/C"]
                x_label = "H/C"
            elif x_axes == 4:
                x_axes = data_filtered["m/z"]
                x_label = "m/z"
            if y_axes == 0:
                y_axes = data_filtered["H/C"]
                y_label = "H/C"
            elif y_axes == 1:
                y_axes = data_filtered["O/C"]
                y_label = "O/C"
            elif y_axes == 2:
                y_axes = data_filtered["N/C"]
                y_label = "N/C"
            elif y_axes == 3:
                y_axes = data_filtered["S/C"]
                y_label = "S/C"
        
                

            if widgets.radio_color_pc1_VK_comp.isChecked():
                third_dimension = data_filtered["PC1"]
            elif widgets.radio_color_pc2_VK_comp.isChecked():
                third_dimension = data_filtered["PC2"]
            elif widgets.radio_color_O_vk_comp.isChecked():
                third_dimension = data_filtered["O"]
            else : 
                third_dimension = data_filtered["Normalized_intensity"]
            data_filtered["third_dimension"] = third_dimension
            data_filtered["x_axes"] = x_axes
            data_filtered["y_axes"] = y_axes
            data_filtered.sample_name = item
            data_filtered.x_label = x_label
            data_filtered.y_label = y_label
            data_filtered.classe_selected = classe_selected
            self.read_param()
            frames.append(data_filtered)
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                frames.sort_values(by=["third_dimension","Normalized_intensity"],ascending = [True,True], inplace = True)               
                plot_fun("scatter",x=frames["x_axes"],y=frames["y_axes"],d_color=frames["third_dimension"],size=dot_size*frames["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)


                if widgets.x_min_VK_comp.text():
                    C_min = float(widgets.x_min_VK_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_VK_comp.text():
                    C_max = float(widgets.x_max_VK_comp.text())
                    plt.gca().set_xlim(right=C_max)
                if widgets.y_min_VK_comp.text():
                    DBE_min = float(widgets.y_min_VK_comp.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if widgets.y_max_VK_comp.text():
                    DBE_max = float(widgets.y_max_VK_comp.text())
                    plt.gca().set_ylim(top=DBE_max)
                plt.suptitle(f'{frames.classe_selected}',fontsize=font_size+4,y=0.95,x=0.45)
                cbar = plt.colorbar()
                if widgets.radio_color_intensity_comp_2.isChecked():
                    cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc1_VK_comp.isChecked():
                    cbar.set_label('PC1', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_pc2_VK_comp.isChecked():
                    cbar.set_label('PC2', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                elif widgets.radio_color_O_vk_comp.isChecked():
                    cbar.set_label('#O', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radio_color_pc1_VK_comp.isChecked():
                    plt.clim(np.min(data_selected.df['PC1']), np.max(data_selected.df['PC1']))
                elif widgets.radio_color_pc2_VK_comp.isChecked():
                    plt.clim(np.min(data_selected.df['PC2']), np.max(data_selected.df['PC2']))
                plt.xlabel(frames.x_label, fontsize=font_size+4)
                plt.ylabel(frames.y_label, fontsize=font_size+4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] + ', ' + str(x_label) +' : '+ str(round(x_axes.iloc[sel.target.index],4)) + ', ' + str(y_label) +' = '+ str(round(y_axes.iloc[sel.target.index],4))))

                if widgets.checkBox_vk_area_comp.isChecked() and widgets.list_VK_x_comp.currentRow() == 0 and widgets.list_VK_y_comp.currentRow() == 0:
                    border_width = 4
                    alpha = 1
                    left, bottom, width, height = (0.51, 1.52, 0.19, 0.5)
                    amino_sugars=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="orange",
                               linewidth = border_width,alpha = alpha)
                    left, bottom, width, height = (0.71, 1.52, 0.3, 0.8)
                    carbohydrates=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="green",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0.31, 0.51, 0.5, 0.99)
                    lignin=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="purple",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 1.72, 0.29, 0.6)
                    lipid=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="blue",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 0, 0.8, 0.49)
                    condensed_hyd=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="black",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0, 0.51, 0.29, 1.19)
                    unsat_hyd=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="red",
                               linewidth= border_width,alpha = alpha)
                    left, bottom, width, height = (0.31, 1.52, 0.19, 0.49)
                    proteins=mpatches.Rectangle((left,bottom),width,height,
                                fill=False,
                                color="brown",
                               linewidth=border_width,alpha=alpha)
                    orange_patch = mpatches.Patch(color='orange', label='Amino sugars')
                    green_patch = mpatches.Patch(color='green', label='Carbohydrates')
                    purple_patch = mpatches.Patch(color='purple', label='Lignin')
                    blue_patch = mpatches.Patch(color='blue', label='Lipids')
                    black_patch = mpatches.Patch(color='black', label='Condensed Hydrocarbons')
                    red_patch = mpatches.Patch(color='red', label='Unsaturated Hydrocarbons')
                    brown_patch = mpatches.Patch(color='brown', label='Proteins')
                    plt.legend(handles=[orange_patch,green_patch,purple_patch,blue_patch ,black_patch ,red_patch,brown_patch])
                    plt.gca().add_patch(amino_sugars)
                    plt.gca().add_patch(carbohydrates)
                    plt.gca().add_patch(lignin)
                    plt.gca().add_patch(lipid)
                    plt.gca().add_patch(condensed_hyd)
                    plt.gca().add_patch(unsat_hyd)
                    plt.gca().add_patch(proteins)
                    
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
        
    def plot_KMD_compare(self,gif = False):
        """
        Classic Kendrick plots
        """

        frames = []
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
                
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                    data_selected.columns.get_loc('count')+item_count*2+1].columns
        self.read_param()
        dot_size = self.d_size
        font_size = self.fontsize   
        if widgets.stackedWidget_Kendrick_comp.currentIndex()==0: #KMD classic
            item_classes = widgets.list_classes_Kendrick_comp.selectedItems()[0]
        elif widgets.stackedWidget_Kendrick_comp.currentIndex()==1: #MD 
            item_classes = widgets.list_classes_Kendrick_univ_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)  
        
        #### KMD & MD vs m/z ####            
        
        if not item_classes:
            return
        
        for item in sample_list:
            data_filtered = data_selected.copy()  
            
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_filtered = self.compared_datas.df[index_classes]     
            #KMD calculation
            if widgets.edit_motif_comp.text():
                edit_repetive_unit = widgets.edit_motif_comp.text()
            if widgets.edit_mass_motif_comp.text():
                repetive_unit_mass = float(widgets.edit_mass_motif_comp.text())
                nominal_unit = round(repetive_unit_mass)
            data_filtered['Kendrick mass']= data_filtered['m/z']*(nominal_unit/repetive_unit_mass)
            data_filtered['Kendrick nominal mass']=round(data_filtered['m/z'])

            if widgets.roundUp_comp.isChecked():
                data_filtered['Kendrick nominal mass']=data_filtered['Kendrick mass'].apply(np.ceil)
            elif widgets.roundClosest_comp.isChecked():
                data_filtered['Kendrick nominal mass']=round(data_filtered['Kendrick mass'])
            data_filtered['Kendrick mass defect']=data_filtered['Kendrick nominal mass']-data_filtered['Kendrick mass']
           
            data_filtered.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_filtered.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity
 
            Intens = data_filtered["Normalized_intensity"].values.astype(float).reshape(-1,1) #astype(float) or crash!
            if widgets.classic_intens_K_comp.isChecked():
                Intens= Intens
            if widgets.sqrt_intens_K_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.log_intens_K_comp.isChecked():
                Intens = np.log10(Intens+1e-10)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled
            data_filtered = data_filtered.sort_values(by=["Normalized_intensity"], ascending=True)

            nominal_mass = round(data_filtered['m/z'])
            mass_defect = data_filtered['m/z'] - nominal_mass
            data_filtered['nominal_mass'] = nominal_mass
            data_filtered['mass_defect'] = mass_defect
            
            #-----------------------------------#
            #  Normalization on selected class  #
            #-----------------------------------#
            if widgets.radioButton_norm_d.isChecked():
                intens=data_filtered["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_filtered["Normalized_intensity"] = Intens_scaled
                    data_filtered = data_filtered.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_filtered["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue

            data_filtered.sample_name = item
            data_filtered.classe_selected = classe_selected
            self.read_param()
            frames.append(data_filtered)
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                    
                if widgets.stackedWidget_Kendrick_comp.currentIndex()==0: #KMD classic
                    x_data = frames['Kendrick nominal mass']
                    y_data = frames['Kendrick mass defect']
                    x_label = 'Kendrick nominal mass'
                    y_label = 'Kendrick mass defect'
                    
                    #-----------------------------------#
                    #  Color by intensity               #
                    #-----------------------------------#
                    if widgets.K_intensity_comp.isChecked():    
                        third_dimension = frames["Normalized_intensity"]
                    #-----------------------------------#
                    #  Color by oxygen                  #
                    #-----------------------------------#
                    if widgets.K_oxygen_comp.isChecked() :    
                        third_dimension = frames["O"]
                    #-----------------------------------#
                    #  Color by nitrogen                #
                    #-----------------------------------#
                    if widgets.K_nitrogen_comp.isChecked() :   
                        third_dimension = frames["N"]
                    #-----------------------------------#
                    #  Color by sulfur                  #
                    #-----------------------------------#
                    if widgets.K_sulfur_comp.isChecked() :   
                        third_dimension = frames["S"]
                        
                elif  widgets.stackedWidget_Kendrick_comp.currentIndex()==1: #Mass defect VS Nominal mass
                    x_data = frames['nominal_mass']
                    y_data = frames['mass_defect']
                    x_label = 'Nominal mass'
                    y_label = 'Mass defect'
                    
                    #-----------------------------------#
                    #  Color by intensity               #
                    #-----------------------------------#
                    if widgets.K_intensity_univ_comp.isChecked():    
                        third_dimension = frames["Normalized_intensity"]
                    #-----------------------------------#
                    #  Color by oxygen                  #
                    #-----------------------------------#
                    if widgets.K_oxygen_univ_comp.isChecked() :    
                        third_dimension = frames["O"]
                    #-----------------------------------#
                    #  Color by nitrogen                #
                    #-----------------------------------#
                    if widgets.K_nitrogen_univ_comp.isChecked() :   
                        third_dimension = frames["N"]
                    #-----------------------------------#
                    #  Color by sulfur                  #
                    #-----------------------------------#
                    if widgets.K_sulfur_univ_comp.isChecked() :   
                        third_dimension = frames["S"]
                
                
                plot_fun("scatter",x = x_data,y = y_data,d_color = third_dimension ,size = 1.5*dot_size*frames["Normalized_intensity"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)                  
                
                if widgets.KNM_min.text():
                    KNM_min = float(widgets.KNM_min.text())
                    plt.gca().set_xlim(left=KNM_min)
                if widgets.KNM_max.text():
                    KNM_max = float(widgets.KNM_max.text())
                    plt.gca().set_xlim(right=KNM_max)
                if widgets.KMD_min.text():
                    KMD_min = float(widgets.KMD_min.text())
                    plt.gca().set_ylim(bottom=KMD_min)
                if widgets.KMD_max.text():
                    KMD_max = float(widgets.KMD_max.text())
                    plt.gca().set_ylim(top=KMD_max)
                cbar = plt.colorbar()
                if widgets.K_intensity_univ.isChecked():
                    cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                if widgets.K_nitrogen_univ.isChecked():
                    cbar.set_label('Nitrogen number', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                if widgets.K_oxygen_univ.isChecked():
                    cbar.set_label('Oxygen number', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                if widgets.K_sulfur_univ.isChecked():
                    cbar.set_label('Sulfur number', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                cbar.ax.tick_params(labelsize=font_size-2)
                plt.suptitle(f'{y_label} vs {x_label}',fontsize=font_size+4,y=0.96,x=0.45)
                plt.xlabel(x_label, fontsize=font_size+4)
                plt.ylabel(y_label, fontsize=font_size+4)
                if 'molecular_formula' in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index]))
                else:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['m/z'].iloc[sel.target.index]))
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                
                plt.text(0.68,0.9,f'{frames.classe_selected}',horizontalalignment='right',
                         verticalalignment='center', transform = transf,fontsize=font_size+2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
        return data_filtered
    
    def envt_selector_compare(self,gif = False):
        """
        Selects the appropriate environmental variable to plot
        """
        self.read_param()
        if widgets.radio_ACOS_comp.isChecked():
            self.plot_ACOS_compare(gif)
        elif widgets.radio_MAI_comp.isChecked():
            self.plot_MAI_compare(gif)
        elif widgets.radio_MCR_comp.isChecked():
            self.plot_MCR_compare(gif)
            
    def plot_ACOS_compare(self,gif = False):
        """
        Average carbon oxydation plot
        """
        frames = []
        font_size = self.fontsize
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = widgets.list_classes_ACOS_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
                
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                    data_selected.columns.get_loc('count')+item_count*2+1].columns
        
        
        for item in sample_list:
            data_extract = data_selected.copy()
            nc=widgets.nc_box_comp.isChecked()


        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = self.compared_datas.df[index_classes]  
                
            data_extract.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_extract.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity
    
            
            if widgets.radio_color_intensity_ACOS_comp.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
                intens_for_size= data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc1_ACOS_comp.isChecked():
                third_dimension = data_extract["PC1"]
                third_dimension = third_dimension+1
                intens_for_size= data_extract["Normalized_intensity"]
            elif widgets.radio_color_pc2_ACOS_comp.isChecked():
                third_dimension = data_extract["PC2"]
                third_dimension = third_dimension+1
                intens_for_size= data_extract["Normalized_intensity"]
             
            
            Intens = third_dimension.values.astype(float).reshape(-1,1)
    
            if widgets.check_classic_ACOS_comp.isChecked():
                Intens= Intens
            if widgets.check_sqrt_ACOS_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_ACOS_comp.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract["point_size"]=intens_for_size
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)

            
    
    
            if nc==True:
                data_extract['OSc']=2*data_extract["O/C"]-data_extract["H/C"]-5*data_extract["N/C"]
            else:
                data_extract['OSc']=2*data_extract["O/C"]-data_extract["H/C"]


        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                size=data_extract["point_size"].copy()
                size=size.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    Size_scaled = min_max_scaler.fit_transform(size)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract["point_size"] = Size_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                    data_extract["point_size"]=1
                else :
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue


        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
            data_extract.classe_selected = classe_selected
            data_extract.sample_name = item
            frames.append(data_extract)
            self.read_param()
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                plot_fun("scatter",x=frames["C"],y=frames["OSc"],d_color=frames["Normalized_intensity"],size=self.d_size*frames["point_size"],dot_type=self.dot_type,edge=self.edge,cmap=self.color_map)
                plt.xlabel('#C', fontsize=self.fontsize+4)
                plt.ylabel('OSc', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                
                plt.gca().invert_xaxis()
                if widgets.x_min_ACOS_comp.text():
                    C_min = float(widgets.x_min_ACOS_comp.text())
                    plt.gca().set_xlim(right=C_min)
                if widgets.x_max_ACOS_comp.text():
                    C_max = float(widgets.x_max_ACOS_comp.text())
                    plt.gca().set_xlim(left=C_max)
                plt.text(0.68,0.9,f'{frames.classe_selected}',horizontalalignment='right',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_ACOS_comp.text():
                    ACOS_min = float(widgets.y_min_ACOS_comp.text())
                    plt.gca().set_ylim(bottom=ACOS_min)
                if widgets.y_max_ACOS_comp.text():
                    ACOS_max = float(widgets.y_max_ACOS_comp.text())
                    plt.gca().set_ylim(top=ACOS_max)
                plt.suptitle('Average carbon oxidation state vs #C',fontsize=font_size+4,y=0.97,x=0.45)
                cbar = plt.colorbar()
                cbar.set_label('Normalized Intensity', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size, color = self.cm_text_color)
                cbar.ax.tick_params(labelsize=font_size-2)
                if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                    plt.clim(0,1)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect("add", lambda sel: sel.annotation.set_text(frames['molecular_formula'].iloc[sel.target.index] +', #C = '+ str(frames['C'].iloc[sel.target.index]) +', OCs = ' + str(round(frames['OSc'].iloc[sel.target.index],2))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
    
    def plot_MAI_compare(self,gif = False):
        """
        Plot a Van Krevelen diagram with the modified aromaticity index as the color coding variable
        """
        frames = []
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = widgets.list_classes_MAI_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        font_size = self.fontsize
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
                
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                     data_selected.columns.get_loc('count')+item_count*2+1].columns
         
        for item in sample_list:
            data_extract = data_selected.copy()

            
                
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = self.compared_datas.df[index_classes]   
                
            if not 'S' in data_extract:
                data_extract['S']=0
            if not 'P' in data_extract:
                data_extract['P']=0
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
            
            data_extract.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_extract.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity

            Intens = data_extract["Normalized_intensity"].values.astype(float).reshape(-1,1) #astype(float) or crash!
            
    
            if widgets.check_classic_MAI_comp.isChecked():
                Intens= Intens
            if widgets.check_sqrt_MAI_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_MAI_comp.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
            
    
            if widgets.MAI_box_comp.isChecked():
                data_extract['AI']=(1+data_extract['C']-0.5*data_extract['O']-data_extract['S']-0.5*(data_extract['N']+data_extract['P']+data_extract['H']))/(data_extract['C']-0.5*data_extract['O']-data_extract['S']-data_extract['N']-data_extract['P'])
            else:
                data_extract['AI']=(1+data_extract['C']-data_extract['O']-data_extract['S']-0.5*(data_extract['N']+data_extract['P']+data_extract['H']))/(data_extract['C']-data_extract['O']-data_extract['S']-data_extract['N']-data_extract['P'])
            data_extract['AI'][data_extract['AI']<0]=0
            data_extract['AI'][data_extract['AI']>1]=1
    
            cond_1=pandas.Series(data_extract['AI']<=0.5) * pandas.Series(data_extract['AI']>=0)
            cond_2=pandas.Series(data_extract['AI']<=0.67) * pandas.Series(data_extract['AI']>0.5)
            cond_3=pandas.Series(data_extract['AI']<=1) * pandas.Series(data_extract['AI']>0.67)
    
    
    
        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(widgets, "Error", "No species to be displayed.")
                    continue
    
    
        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
    
            data_extract.classe_selected = classe_selected
            data_extract.cond_1 = cond_1.values
            data_extract.cond_2 = cond_2.values
            data_extract.cond_3 = cond_3.values
            data_extract.sample_name = item
            frames.append(data_extract)
            self.read_param()
            
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
    
                d1=frames[frames.cond_1]
                d2=frames[frames.cond_2]
                d3=frames[frames.cond_3]
                ax1=plt.scatter(d1["O/C"],d1["H/C"],c='#06a96a',s=self.d_size*d1["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax2=plt.scatter(d2["O/C"],d2["H/C"],c='#f39c1b',s=self.d_size*d2["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax3=plt.scatter(d3["O/C"],d3["H/C"],c='#de281b',s=self.d_size*d3["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                plt.xlabel('O/C', fontsize=self.fontsize+4)
                plt.ylabel('H/C', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                
        
                if widgets.x_min_MAI_comp.text():
                    C_min = float(widgets.x_min_MAI_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_MAI_comp.text():
                    C_max = float(widgets.x_max_MAI_comp.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(0.68,0.9,f'{frames.classe_selected}',horizontalalignment='right',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_MAI_comp.text():
                    MAI_min = float(widgets.y_min_MAI_comp.text())
                    plt.gca().set_ylim(bottom=MAI_min)
                if widgets.y_max_MAI_comp.text():
                    MAI_max = float(widgets.y_max_MAI_comp.text())
                    plt.gca().set_ylim(top=MAI_max)
                plt.suptitle('Van Krevelen diagram',fontsize=font_size+4,y=0.97,x=0.45)
        
                cmap = (matplotlib.colors.ListedColormap(['#06a96a','#f39c1b', '#de281b']))
                bounds = [0, 0.5, 0.67,1 ]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar=plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing='proportional',
                    orientation='vertical',
                )
                cbar.set_label('Aromaticity Index', labelpad=-3.3*(font_size), rotation=90,fontsize=font_size, color = "white")
                cbar.ax.tick_params(labelsize=font_size-2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
        
                if "m/z" in frames:
                    mplcursors.cursor(ax1,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d1['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d1['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d1['AI'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax2,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d2['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d2['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d2['AI'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax3,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d3['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d3['O/C'].iloc[sel.target.index].round(3)) +', (M)AI = ' + str(d3['AI'].iloc[sel.target.index].round(3))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
    
    def plot_MCR_compare(self,gif = False):
        """
        Plot a Van Krevelen diagram with the maximum carbonyl ratio as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        item_count = len(widgets.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = widgets.list_classes_MCR_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if widgets.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_list = data_selected.iloc[:,data_selected.columns.get_loc('count')+item_count+1:
                                    data_selected.columns.get_loc('count')+item_count*2+1].columns
        
        if not item_classes:
            return
        for item in sample_list:
            
            data_extract = data_selected.copy()
            
            if classe_selected == 'All':
                pass
            else:
                classes_index = self.compared_datas.classes[self.compared_datas.classes['variable'] == classe_selected]
                if 'x' in classe_selected:
                    index_classes = (self.compared_datas.df[classe_selected] == True)
                else:
                    index_classes = (self.compared_datas.df[self.compared_datas.heteroatoms.columns] == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]).all(1)
                data_extract = self.compared_datas.df[index_classes]   
                
            if not 'S' in data_extract:
                data_extract['S']=0
            if not 'P' in data_extract:
                data_extract['P']=0
    
        #-----------------------------#
        #  3rd dimension selection    #
        #-----------------------------#
    
            data_extract.drop(['Normalized_intensity'], axis = 1, inplace = True)
            data_extract.rename(columns = {item:'Normalized_intensity'},inplace = True) #item_name.csv => Normalized intensity

            Intens = data_extract["Normalized_intensity"].values.astype(float).reshape(-1,1) #astype(float) or crash!
            
    
            if widgets.check_classic_MCR_comp.isChecked():
                Intens= Intens
            if widgets.check_sqrt_MCR_comp.isChecked():
                Intens= np.sqrt(Intens)
            if widgets.check_log_MCR_comp.isChecked():
                Intens = np.log10(Intens+1e-10) #Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
    
            
    
    
            data_extract['MCR']=data_extract['DBE']/data_extract['O']
            data_extract['MCR'][data_extract['MCR']<0]=0
            data_extract['MCR'][data_extract['MCR']>1]=1
    
            cond_1=pandas.Series(data_extract['MCR']<=0.2) * pandas.Series(data_extract['MCR']>=0)
            cond_2=pandas.Series(data_extract['MCR']<=0.5) * pandas.Series(data_extract['MCR']>0.2)
            cond_3=pandas.Series(data_extract['MCR']<=0.9) * pandas.Series(data_extract['MCR']>0.5)
            cond_4=pandas.Series(data_extract['MCR']<=1) * pandas.Series(data_extract['MCR']>0.9)
    
    
    
        #-----------------------------------#
        #  Normalization                    #
        #-----------------------------------#
    
            if widgets.radioButton_norm_c.isChecked() or widgets.radioButton_norm_d.isChecked():
                intens=data_extract["Normalized_intensity"].copy()
                intens=intens.values.reshape(-1,1)
                if intens.shape[0]>1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract = data_extract.sort_values(by=["Normalized_intensity"], ascending=True)
                elif intens.shape[0]==1:
                    data_extract["Normalized_intensity"]=1
                else :
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue
    
    
        #-----------------------------------------#
        #  Normalization (end)                    #
        #-----------------------------------------#
    
            data_extract.classe_selected = classe_selected
            data_extract.cond_1 = cond_1.values
            data_extract.cond_2 = cond_2.values
            data_extract.cond_3 = cond_3.values
            data_extract.cond_4 = cond_4.values
            data_extract.sample_name = item
            frames.append(data_extract)
            self.read_param()
            
            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
    
    
                d1=frames[frames.cond_1]
                d2=frames[frames.cond_2]
                d3=frames[frames.cond_3]
                d4=frames[frames.cond_4]
                ax1=plt.scatter(d1["O/C"],d1["H/C"],c='#de281b',s=self.d_size*d1["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax2=plt.scatter(d2["O/C"],d2["H/C"],c='#f39c1b',s=self.d_size*d2["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax3=plt.scatter(d3["O/C"],d3["H/C"],c='#06a96a',s=self.d_size*d3["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                ax4=plt.scatter(d4["O/C"],d4["H/C"],c='#0f5fa8',s=self.d_size*d4["Normalized_intensity"],linewidths=0.7,edgecolors='black',alpha=0.7)
                plt.xlabel('O/C', fontsize=self.fontsize+4)
                plt.ylabel('H/C', fontsize=self.fontsize+4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                name = frames.sample_name
                name = name.replace("Rel_intens_","")
                name = name.replace(".csv","")
                name = name.replace(".xlsx","")
                plt.text(0.12,0.9,name,horizontalalignment='left',
                              verticalalignment='center',fontsize=font_size-1, transform = transf)
                
        
                if widgets.x_min_MCR_comp.text():
                    C_min = float(widgets.x_min_MCR_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if widgets.x_max_MCR_comp.text():
                    C_max = float(widgets.x_max_MCR_comp.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(0.68,0.9,f'{frames.classe_selected}',horizontalalignment='right',
                         verticalalignment='center',fontsize=font_size-1, transform = transf)
                if widgets.y_min_MCR_comp.text():
                    MCR_min = float(widgets.y_min_MCR_comp.text())
                    plt.gca().set_ylim(bottom=MCR_min)
                if widgets.y_max_MCR_comp.text():
                    MCR_max = float(widgets.y_max_MCR_comp.text())
                    plt.gca().set_ylim(top=MCR_max)
                plt.suptitle('Van Krevelen diagram',fontsize=font_size+4,y=0.97,x=0.45)
                cmap = (matplotlib.colors.ListedColormap(['#de281b','#f39c1b', '#06a96a','#0f5fa8']))
                bounds = [0,0.2, 0.5, 0.9,1 ]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar=plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing='proportional',
                    orientation='vertical',
                )
                cbar.set_label('Maximum carbonyl ratio', labelpad=-2.625*(font_size), rotation=90,fontsize=font_size)
                cbar.ax.tick_params(labelsize=font_size-2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
        
                if "m/z" in frames:
                    mplcursors.cursor(ax1,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d1['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d1['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d1['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax2,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d2['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d2['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d2['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax3,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d3['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d3['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d3['MCR'].iloc[sel.target.index].round(3))))
                    mplcursors.cursor(ax4,multiple=True).connect("add", lambda sel: sel.annotation.set_text(d4['molecular_formula'].iloc[sel.target.index] +', O/C = '+ str(d4['O/C'].iloc[sel.target.index].round(3)) +', MCR = ' + str(d4['MCR'].iloc[sel.target.index].round(3))))
        if gif == False:
            for i in frames:
                Anim(i)   
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000/self.fps)  
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(self.pos().x()+940,self.pos().y()+200,640, 545)
            writergif = PillowWriter(fps=self.fps) 
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
    
    
    def closeEvent(self, event):
        """
        Closes the GUI and all the plots
        """
        if self.settingsExit.value('ExitConfirm') == 'false':
            try :
                plt.close("all")
            except:
                pass
            try:
                if self.splitfinder:
                    self.splitfinder.close()
            except:
                pass
            event.accept()
        else  : 
            quit_msg = "No data will be saved. Confirm ?"
            reply = QMessageBox.question(self, 'Message',
                             quit_msg, QMessageBox.Yes, QMessageBox.No)
    
            if reply == QMessageBox.Yes:
                try :
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

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    app.exec()
