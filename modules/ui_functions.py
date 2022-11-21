# ///////////////////////////////////////////////////////////////
#
#
# ///////////////////////////////////////////////////////////////

# MAIN FILE
# ///////////////////////////////////////////////////////////////
from main import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# GLOBALS
# ///////////////////////////////////////////////////////////////
GLOBAL_STATE = False
GLOBAL_TITLE_BAR = True

class UIFunctions(MainWindow):
    # MAXIMIZE/RESTORE
    # ///////////////////////////////////////////////////////////////
    def maximize_restore(self):
        global GLOBAL_STATE
        status = GLOBAL_STATE
        if status == False:
            self.showMaximized()
            GLOBAL_STATE = True
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            self.ui.maximizeRestoreAppBtn.setToolTip("Restore")
            self.ui.maximizeRestoreAppBtn.setStyleSheet("QPushButton{\nbackground: url(:/icons/images/icons/icon_maximize.png)  no-repeat center center;\n}\nQPushButton:hover {\n	background-color: rgb(0,56,94);\n}\nQPushButton:pressed {	\n	background-color: rgb(195,221,240);\n	color: black;\n}")
            self.ui.frame_size_grip.hide()
            self.left_grip.hide()
            self.right_grip.hide()
            self.top_grip.hide()
            self.bottom_grip.hide()
        else:
            GLOBAL_STATE = False
            self.showNormal()
            self.resize(self.width()+1, self.height()+1)
            self.ui.appMargins.setContentsMargins(10, 10, 10, 10)
            self.ui.maximizeRestoreAppBtn.setToolTip("Maximize")
            self.ui.maximizeRestoreAppBtn.setStyleSheet("QPushButton{\nbackground: url(:/icons/images/icons/icon_restore.png)  no-repeat center center;\n}\nQPushButton:hover {\n	background-color: rgb(0,56,94);\n}\nQPushButton:pressed {	\n	background-color: rgb(195,221,240);\n	color: black;\n}")
            self.ui.frame_size_grip.show()
            self.left_grip.show()
            self.right_grip.show()
            self.top_grip.show()
            self.bottom_grip.show()

    # RETURN STATUS
    # ///////////////////////////////////////////////////////////////
    def returStatus(self):
        return GLOBAL_STATE

    # SET STATUS
    # ///////////////////////////////////////////////////////////////
    def setStatus(self, status):
        global GLOBAL_STATE
        GLOBAL_STATE = status


    # TOGGLE SETTINGS BOX
    # ///////////////////////////////////////////////////////////////       
    def toggleSettingsBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.ui.settingsMenu.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            standard = 0
            height = self.ui.bgApp.height()

            # GET BTN STYLE
            style = self.ui.settingsTopBtn.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend

            else:
                widthExtended = standard

        UIFunctions.start_box_animation(self, width, height, "settings")
            
    # TOGGLE PROCESS BOX
    # ///////////////////////////////////////////////////////////////       
    def toggleProcessBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.ui.processMenu.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            standard = 0
            height = self.ui.bgApp.height()

            # GET BTN STYLE
            style = self.ui.btn_process.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend

            else:
                widthExtended = standard

        UIFunctions.start_box_animation(self, width, height, "process")
    # TOGGLE VIEW BOX
    # ///////////////////////////////////////////////////////////////
    def toggleViewBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.ui.viewMenu.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            standard = 0
            height = self.ui.bgApp.height()

            # GET BTN STYLE
            style = self.ui.btn_view.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend

            else:
                widthExtended = standard

        UIFunctions.start_box_animation(self, width, height, "view")
        
    # TOGGLE COMPARE BOX
    # ///////////////////////////////////////////////////////////////
    def toggleCompareBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.ui.compareMenu.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            standard = 0
            height = self.ui.bgApp.height()

            # GET BTN STYLE
            style = self.ui.btn_compare.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend

            else:
                widthExtended = standard

        UIFunctions.start_box_animation(self, width, height, "compare")
        
    # TOGGLE STATS BOX
    # ///////////////////////////////////////////////////////////////
    def toggleStatsBox(self, enable):
        if enable:
            # GET WIDTH
            width = self.ui.statsMenu.width()
            maxExtend = Settings.LEFT_BOX_WIDTH
            standard = 0
            height = self.ui.bgApp.height()

            # GET BTN STYLE
            style = self.ui.btn_stats.styleSheet()

            # SET MAX WIDTH
            if width == 0:
                widthExtended = maxExtend

            else:
                widthExtended = standard

        UIFunctions.start_box_animation(self, width, height, "stats")

    
        
    def start_box_animation(self, left_box_width, height, direction):
        right_width = 0
        left_width = 0 
        init_time = 20
        #Init every width
        ##Settings 
        self.settings = QPropertyAnimation(self.ui.settingsMenu, b"size")
        self.settings.setDuration(init_time)
        self.settings.setStartValue(QSize(self.ui.settingsMenu.width(),self.ui.settingsMenu.height()))
        self.settings.setEndValue(QSize(0,self.ui.settingsMenu.height()))
        self.settings.setEasingCurve(QEasingCurve.InOutQuart)
        self.settings.start()
        ##Process
        self.process = QPropertyAnimation(self.ui.processMenu, b"size")
        self.process.setDuration(init_time)
        self.process.setStartValue(QSize(self.ui.processMenu.width(),self.ui.processMenu.height()))
        self.process.setEndValue(QSize(0,self.ui.processMenu.height()))
        self.process.setEasingCurve(QEasingCurve.InOutQuart)
        self.process.start()
        ##View
        self.view = QPropertyAnimation(self.ui.viewMenu, b"size")
        self.view.setDuration(init_time)
        self.view.setStartValue(QSize(self.ui.viewMenu.width(),self.ui.viewMenu.height()))
        self.view.setEndValue(QSize(0,self.ui.viewMenu.height()))
        self.view.setEasingCurve(QEasingCurve.InOutQuart)
        self.view.start()
        
        ##Compare
        self.compare = QPropertyAnimation(self.ui.compareMenu, b"size")
        self.compare.setDuration(init_time)
        self.compare.setStartValue(QSize(self.ui.compareMenu.width(),self.ui.compareMenu.height()))
        self.compare.setEndValue(QSize(0,self.ui.compareMenu.height()))
        self.compare.setEasingCurve(QEasingCurve.InOutQuart)
        self.compare.start()
        
        ##Stats
        self.stats = QPropertyAnimation(self.ui.statsMenu, b"size")
        self.stats.setDuration(init_time)
        self.stats.setStartValue(QSize(self.ui.statsMenu.width(),self.ui.statsMenu.height()))
        self.stats.setEndValue(QSize(0,self.ui.statsMenu.height()))
        self.stats.setEasingCurve(QEasingCurve.InOutQuart)
        self.stats.start()
        
        
        
        # Check values
        if direction == "settings":
            if left_box_width == 0 :
                left_width = 240
            else:
                left_width = 0
            self.left_box = QPropertyAnimation(self.ui.settingsMenu, b"size")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(QSize(left_box_width,height))
            self.left_box.setEndValue(QSize(left_width,height))
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)
            self.left_box.start()  
        if direction == "process":
            if left_box_width == 0 :
                left_width = 240
            else:
                left_width = 0
            self.left_box = QPropertyAnimation(self.ui.processMenu, b"size")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(QSize(left_box_width,height))
            self.left_box.setEndValue(QSize(left_width,height))
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)
            self.left_box.start()   
            
        if direction == "view":
            if left_box_width == 0 :
                left_width = 240
            else:
                left_width = 0
            self.left_box = QPropertyAnimation(self.ui.viewMenu, b"size")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(QSize(left_box_width,height))
            self.left_box.setEndValue(QSize(left_width,height))
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)
            self.left_box.start()       
                
        if direction == "compare":
            if left_box_width == 0 :
                left_width = 240
            else:
                left_width = 0
            self.left_box = QPropertyAnimation(self.ui.compareMenu, b"size")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(QSize(left_box_width,height))
            self.left_box.setEndValue(QSize(left_width,height))
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)
            self.left_box.start()  
        
        if direction == "stats":
            if left_box_width == 0 :
                left_width = 240
            else:
                left_width = 0
            self.left_box = QPropertyAnimation(self.ui.statsMenu, b"size")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(QSize(left_box_width,height))
            self.left_box.setEndValue(QSize(left_width,height))
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart)
            self.left_box.start() 
     

 
        


    # SELECT/DESELECT MENU
    # ///////////////////////////////////////////////////////////////
    # SELECT
    def selectMenu(getStyle):
        select = getStyle + Settings.MENU_SELECTED_STYLESHEET
        return select

    # DESELECT
    def deselectMenu(getStyle):
        deselect = getStyle.replace(Settings.MENU_SELECTED_STYLESHEET, "")
        return deselect

    # START SELECTION
    def selectStandardMenu(self, widget):
        for w in self.ui.topMenu.findChildren(QPushButton):
            if w.objectName() == widget:
                w.setStyleSheet(UIFunctions.selectMenu(w.styleSheet()))

    # RESET SELECTION
    def resetStyle(self, widget):
        for w in self.ui.topMenu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(UIFunctions.deselectMenu(w.styleSheet()))

    # IMPORT THEMES FILES QSS/CSS
    # ///////////////////////////////////////////////////////////////
    def theme(self, file, useCustomTheme):
        if useCustomTheme:
            str = open(file, 'r').read()
            self.ui.styleSheet.setStyleSheet(str)

    # START - GUI DEFINITIONS
    # ///////////////////////////////////////////////////////////////
    def uiDefinitions(self):
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, lambda: UIFunctions.maximize_restore(self))
        self.ui.titleRightInfo.mouseDoubleClickEvent = dobleClickMaximizeRestore


        # RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.ui.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        # MINIMIZE
        self.ui.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())

        # MAXIMIZE/RESTORE
        self.ui.maximizeRestoreAppBtn.clicked.connect(lambda: UIFunctions.maximize_restore(self))

        # CLOSE APPLICATION
        self.ui.closeAppBtn.clicked.connect(lambda: self.close())
        
        # CUSTOM GRIPS
        self.left_grip = CustomGrip(self, Qt.LeftEdge, True)
        self.right_grip = CustomGrip(self, Qt.RightEdge, True)
        self.top_grip = CustomGrip(self, Qt.TopEdge, True)
        self.bottom_grip = CustomGrip(self, Qt.BottomEdge, True)
        

    def resize_grips(self):
        self.left_grip.setGeometry(0, 10, 10, self.height())
        self.right_grip.setGeometry(self.width() - 10, 10, 10, self.height())
        self.top_grip.setGeometry(0, 0, self.width(), 10)
        self.bottom_grip.setGeometry(0, self.height() - 10, self.width(), 10)

    # ///////////////////////////////////////////////////////////////
    # END - GUI DEFINITIONS
