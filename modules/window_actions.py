from modules.controller_dependencies import *

class WindowActionsMixin:
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
            self.click_count = self.click_count + 1
            if time.time() - self.start_counter > 1.5:
                self.start_counter = False
                self.click_count = []
                return
            if self.click_count == 5:
                try:
                    easter()
                except:
                    return

        else:
            self.start_counter = time.time()
            self.click_count = 1

    def write_csv_df(self, path, filename, df):
        # Give the filename you wish to save the file to
        pathfile = os.path.normpath(os.path.join(path, filename))

        # Use this function to search for any files which match your filename
        files_present = os.path.isfile(pathfile)
        # if no matching files, write to csv, if there are matching files, print statement
        if not files_present:
            df.to_csv(pathfile, sep=";", index=False)
            QMessageBox.about(self, "FYI box", "Your file was correctly saved.")
        else:
            overwrite_msg = "A file with this name already exist in this directory. Would you like to overwrite it ?"
            overwrite = QMessageBox.question(
                self, "Message", overwrite_msg, QMessageBox.Yes, QMessageBox.No
            )
            if overwrite == QMessageBox.Yes:
                try:
                    df.to_csv(pathfile, sep=";", index=False)
                    QMessageBox.about(self, "FYI box", "Your file was correctly saved.")
                except:
                    msg = "A problem occured. Check if the file to replace is open."
                    reply = QMessageBox.information(
                        self, "Message", msg, QMessageBox.Ok, QMessageBox.Ok
                    )
                    return
            elif overwrite == QMessageBox.No:
                new_filename, okPressed = QInputDialog.getText(
                    self, "Save Name", "Name of the merged file: ", QLineEdit.Normal, ""
                )
                self.write_csv_df(path, new_filename + ".csv", df)
            else:
                msg = "Not a valid input. Data is NOT saved!\n"
                reply = QMessageBox.information(
                    self, "Message", msg, QMessageBox.Ok, QMessageBox.Ok
                )

    def about(self, last_modified):
        """
        Links the github page in a new window
        """
        link_git = "https://github.com/iC2MC/PyC2MC_viewer"
        email = "maxime.sueur1@univ-rouen.fr"
        link_preprint = "https://doi.org/10.1021/jasms.2c00323"
        msg = (
            "PyC2MC Viewer: a FTMS data visualization software. <br><br>\
            Want to improve the application ? Join us on <a href='%s'>GitHub</a> <br><br> \
            When using PyC2MC, please cite our <a href='%s'>article</a>. <br><br>\
            Version modified on %s <br><br> \
            GUI based on PyDracula by Wanderson M. Pimenta."
            % (link_git, link_preprint, self.last_modified)
        )
        reply = QMessageBox.information(
            self, "Message", msg, QMessageBox.Ok, QMessageBox.Ok
        )

    def colorTab(self, tab):
        """
        CHANGES THE COLOR OF THE ACTIVE  TAB
        """
        if hasattr(self, "bak_view"):
            self.ui.btn_view.setStyleSheet(self.bak_view)
            self.ui.btn_compare.setStyleSheet(self.bak_comp)
            self.ui.btn_stats.setStyleSheet(self.bak_stats)

        self.bak_view = self.ui.btn_view.styleSheet()
        self.bak_comp = self.ui.btn_compare.styleSheet()
        self.bak_stats = self.ui.btn_stats.styleSheet()

        if tab == "View":
            self.ui.btn_view.setStyleSheet(
                self.bak_view
                + "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}"
            )
        elif tab == "Compare":
            self.ui.btn_compare.setStyleSheet(
                self.bak_comp
                + "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}"
            )
        elif tab == "Stats":
            self.ui.btn_stats.setStyleSheet(
                self.bak_stats
                + "QPushButton {border-right: 1.5px solid rgb(208,208,208);border-bottom: 1.5px solid rgb(208,208,208)}"
            )

    def buttonColor(self):
        """
        CHANGES THE COLOR OF THE LAST BUTTON CLICKED
        """

        btn = self.sender()
        if btn.objectName() == "list_loaded_file":  # Exception for peaklists:
            btn = self.ui.btn_kendricks
        if hasattr(self, "btn_bak"):
            self.btn_bak.setStyleSheet(self.style_backup)
        self.style_backup = btn.styleSheet()
        if btn.objectName() == "btn_settings":  # Exception to keep the icon
            btn.setStyleSheet(
                "QPushButton {background-color:  rgb(200,200,200);\n"
                + self.style_backup
                + "}"
            )
            self.colorTab("")
        else:
            btn.setStyleSheet(
                "QPushButton {background-color:  rgb(208,208,208);\n"
                + self.style_backup
                + "}"
            )
        self.btn_bak = btn

    def KMD_ext_label_update(self):
        if self.ui.mz_extraction.isChecked() == True:
            self.ui.label_3.setText("m/z")
        else:
            self.ui.label_3.setText("KMD")

    def resizeEvent(self, event):
        """
        Update Size Grips
        """
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        """
        SET DRAG POS WINDOW
        """
        self.dragPos = event.globalPos()

    def viewPlot(self):
        """
        Select plot to draw from View tab
        """
        ind = self.ui.choose_plot_stacked.currentIndex()

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

    def viewGif(self):
        """
        Select plot to draw from View tab
        """
        ind = self.ui.choose_plot_stacked.currentIndex()
        if ind == 0:
            self.overview(gif=True)
        elif ind == 1:
            self.plot_DBE(gif=True)
        elif ind == 2:
            self.plot_VK(gif=True)
        elif ind == 3:
            self.plot_Kendrick(gif=True)
        elif ind == 4:
            self.envt_selector(gif=True)

    def comparePlot(self):
        """
        Select plot to draw from Compare tab
        """
        ind = self.ui.Compare_stacked_widget.currentIndex()

        if ind == 0:  # overview
            ind_bis = self.ui.stackedWidget_overview_compare.currentIndex()
            if ind_bis == 0:
                self.plot_composition_compare()
            elif ind_bis == 1:
                self.plot_distrib_compare()
            elif ind_bis == 2:
                self.plot_spectrum_compare()

        elif ind == 1:  # FC
            ind_bis = self.ui.stackedWidget_FC.currentIndex()
            if ind_bis == 0:
                self.plot_molecular_carto_DBE()
            elif ind_bis == 1:
                self.plot_molecular_carto_VK()
            elif ind_bis == 2:
                self.plot_molecular_carto_KMD()
            elif ind_bis == 3:
                self.plot_molecular_carto_MD()

        elif ind == 2:  # DBE
            self.plot_DBE_compare()

        elif ind == 3:  # VK
            self.plot_VK_compare()

        elif ind == 4:  # KMD
            self.plot_KMD_compare()

        elif ind == 5:  # EV variables
            self.envt_selector_compare()

    def comparePlotGIF(self):
        """
        Select plot to draw from Compare tab
        """
        ind = self.ui.Compare_stacked_widget.currentIndex()

        if ind == 0:
            ind_bis = self.ui.stackedWidget_overview_compare.currentIndex()
            if ind_bis == 0:
                self.plot_composition_compare()
            elif ind_bis == 1:
                self.plot_distrib_compare(gif=True)
            elif ind_bis == 2:
                self.plot_spectrum_compare()

        elif ind == 1:
            ind_bis = self.ui.stackedWidget_FC.currentIndex()
            if ind_bis == 0:
                self.plot_molecular_carto_DBE(gif=True)
            elif ind_bis == 1:
                self.plot_molecular_carto_VK(gif=True)

        elif ind == 2:  # DBE
            self.plot_DBE_compare(gif=True)

        elif ind == 3:  # VK
            self.plot_VK_compare(gif=True)

        elif ind == 4:  # KMD
            self.plot_KMD_compare(gif=True)

        elif ind == 5:  # EV variables
            self.envt_selector_compare(gif=True)

    def statsPlot(self):
        """
        Select plot to draw from Stats tab
        """
        ind = self.ui.stats_stacked_widget.currentIndex()

        if ind == 0:
            self.venn()
        elif ind == 1:
            self.plot_PCA()
        elif ind == 2:
            self.plot_HCA()
        elif ind == 3:
            self.volcano()
        elif ind == 4:
            sub_ind = self.ui.stackedWidget_FC_stats.currentIndex()
            if sub_ind == 0:
                self.pl_comp_KMD()
            elif sub_ind == 1:
                self.pl_comp_MD()

    def btn_enabling(self):
        """
        Enables every GUI button (acts as a GUI reset).
        """
        self.ui.btn_stats.setEnabled(True)
        self.ui.btn_overview.setEnabled(True)
        self.ui.btn_DBE.setEnabled(True)
        self.ui.btn_EV.setEnabled(True)
        self.ui.btn_van_krevelen.setEnabled(True)
        self.ui.plot_button_view.setEnabled(True)
        self.ui.plot_compare.setEnabled(True)
        self.ui.plot_compare_GIF.setEnabled(True)
        self.ui.radio_composition.setEnabled(True)
        self.ui.radio_error_plots.setEnabled(True)
        self.ui.radio_distributions.setEnabled(True)
        self.ui.radio_mass_spectrum.setEnabled(True)

    def colormap(self):
        """
        Reads the colormap parameter in the GUI.
        """
        cmp = self.ui.list_color_map.currentItem()
        self.color_map = cmp.text()
        white_text_cm = ["viridis", "cividis", "plasma"]

        if cmp.text() in white_text_cm:
            self.cm_text_color = "white"
        else:
            self.cm_text_color = "black"
