from modules.controller_dependencies import *

class FileOperationsMixin:
    def clear_loaded_list(self):
        """
        Clears the loaded files lists
        """
        self.ui.list_loaded_file.clear()
        self.ui.list_loaded_file_2.clear()
        self.ui.list_loaded_file_compare.clear()
        self.ui.list_compare_sample_1.clear()
        self.ui.list_compare_sample_2.clear()
        self.ui.list_sample_1_stats.clear()
        self.ui.list_sample_2_stats.clear()
        self.ui.list_classes_mass_spec_comp.clear()
        self.ui.list_classes_distrib_compare.clear()
        self.ui.list_classes_DBE_compare.clear()
        self.ui.list_classes_VK_compare.clear()
        self.ui.list_classes_DBE_comp.clear()
        self.ui.list_classes_VK_comp.clear()
        self.ui.list_classes_Kendrick_comp.clear()
        self.ui.list_classes_Kendrick_univ_comp.clear()
        try:
            plt.close("all")
        except:
            pass

    def load_file_method(self):
        """
        Prepares the GUI and call the Loading_function
        """
        self.ui.list_classes_DBE.clear()
        self.ui.list_classes_mass_spec.clear()
        self.ui.list_classes_error.clear()
        self.ui.list_classes_VK.clear()
        self.ui.list_classes_Kendrick.clear()
        self.ui.list_classes_Kendrick_univ.clear()
        self.ui.pbar.show()
        type_color = {
            "PyC2MC_fusion": "#dd324d",
            "Peaklist": "#2d6bad",
            "Attributed": "#f0a23e",
            "PyC2MC_merged": "#42d66a",
            "PyC2MC_merged_unattributed": "#bfb0b7",
        }
        p = 0
        # Get the filepath
        filepath, _ = QtWidgets.QFileDialog.getOpenFileNames(
            caption="Choose one result file or more to import",
            filter="Results files (*.csv;*.asc;*.xlsx;*.xls)",
        )
        if not filepath:
            self.ui.pbar.hide()
            return
        path_old = os.getcwd()
        n = 0
        self.ui.pbar.setValue(p)

        while n < len(filepath):
            p = (n + 1) / len(filepath) * 100

            path_to_file = os.path.dirname(filepath[n])
            filename = str(os.path.basename(filepath[n]))
            # read data and create data frame
            os.chdir(path_to_file)
            try:
                dataframe = load_MS_file(filename, self.isotopes_dict)
            except Exception as err:
                QMessageBox.about(
                    self,
                    "FYI box",
                    f"A problem has occured with the following file: '{filename}', error is : {err}",
                )
                n = n + 1
                if n < len(filepath):
                    p = (n + 1) / len(filepath) * 100

                    path_to_file = os.path.dirname(filepath[n])
                    filename = str(os.path.basename(filepath[n]))
                    os.chdir(path_to_file)
                    try:
                        dataframe = load_MS_file(filename, self.isotopes_dict)
                    except Exception as err:
                        QMessageBox.about(
                            self,
                            "FYI box",
                            f"A problem has occured with the following file: '{filename}', error is : {err}",
                        )
            pass

            try:
                test_var = dataframe.df
                del test_var
            except:
                return

            if dataframe.df_type == "Error":
                QMessageBox.about(
                    self,
                    "FYI box",
                    f".xlsx files should only come from CERES processing, '{filename}' isn't such a file",
                )
                dataframe.df = pandas.DataFrame()
                pass
            os.chdir(path_old)

            ###-----------------------------------------------------------###
            # Display the dataframe(s) item(s) in the appropriate GUI lists #
            ###-----------------------------------------------------------###

            if dataframe.df_type == "PyC2MC_merged":
                if (
                    "std_dev_rel" in dataframe.df
                ):  # Fused replicates file (specific merging type)
                    # create items with text = filename for every appropriate Qlist (view and compare)
                    item = QtWidgets.QListWidgetItem(filename)
                    item_2 = QtWidgets.QListWidgetItem(filename + " ")
                    # Attribute data loaded to the items
                    item.setData(self.USERDATA_ROLE, dataframe)
                    item_2.setData(self.USERDATA_ROLE, dataframe)
                    # Display items in their respective Qlist
                    self.ui.list_loaded_file_compare.addItem(item)
                    self.ui.list_loaded_file.addItem(item_2)
                    # Set the color of the item for better identification
                    i = self.ui.list_loaded_file.count() - 1
                    j = self.ui.list_loaded_file_compare.count() - 1
                    qcolor = QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                    qcolor.setAlphaF(0.3)
                    self.ui.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
                    self.ui.list_loaded_file.item(i).setBackground(QColor(qcolor))

                else:  # Classical Merged file
                    # create items with text = filename for every appropriate Qlist (view and stats)
                    item = QtWidgets.QListWidgetItem(filename)
                    item_2 = QtWidgets.QListWidgetItem(filename + " ")
                    # Attribute data loaded to the items
                    item.setData(self.USERDATA_ROLE, dataframe)
                    item_2.setData(self.USERDATA_ROLE, dataframe)
                    # Display items in their respective Qlist
                    self.ui.list_loaded_file.addItem(item)
                    self.ui.list_loaded_file_2.addItem(item_2)
                    # Set the color of the item for better identification
                    i = self.ui.list_loaded_file.count() - 1
                    j = self.ui.list_loaded_file_2.count() - 1
                    qcolor = QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                    qcolor.setAlphaF(0.3)
                    self.ui.list_loaded_file.item(i).setBackground(QColor(qcolor))
                    self.ui.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
            elif dataframe.df_type == "PyC2MC_merged_unattributed":
                item = QtWidgets.QListWidgetItem(filename)
                # Attribute data loaded to the items
                item.setData(self.USERDATA_ROLE, dataframe)
                # Display items in their respective Qlist
                self.ui.list_loaded_file_2.addItem(item)
                # Set the color of the item for better identification
                j = self.ui.list_loaded_file_2.count() - 1
                qcolor = QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                qcolor.setAlphaF(0.3)
                self.ui.list_loaded_file_2.item(j).setBackground(QColor(qcolor))

            elif dataframe.df_type == "Peaklist":
                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                self.ui.list_loaded_file.addItem(item)

                i = self.ui.list_loaded_file.count() - 1
                qcolor = QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                qcolor.setAlphaF(0.3)
                self.ui.list_loaded_file.item(i).setBackground(QColor(qcolor))

            elif dataframe.df_type == "Error":
                pass

            else:  # simply attributed data
                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                self.ui.list_loaded_file.addItem(item)

                item = QtWidgets.QListWidgetItem(filename)
                item.setData(self.USERDATA_ROLE, dataframe)
                self.ui.list_loaded_file_compare.addItem(item)

                i = self.ui.list_loaded_file.count() - 1
                j = self.ui.list_loaded_file_compare.count() - 1
                qcolor = QColor(type_color[item.data(self.USERDATA_ROLE).df_type])
                qcolor.setAlphaF(0.3)
                self.ui.list_loaded_file_compare.item(j).setBackground(QColor(qcolor))
                self.ui.list_loaded_file.item(i).setBackground(QColor(qcolor))
            self.ui.pbar.setValue(int(p))
            n = n + 1

        self.latest_path = os.path.dirname(filepath[n - 1])

        self.ui.pbar.setValue(int(p))
        self.ui.pbar.hide()

    def merge_files(self):
        """
        Calls the Merge Function and load the newly created .csv in the GUI
        """

        self.ui.pbar.show()
        i = 0
        self.ui.pbar.setValue(int(i))
        try:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileNames(
                filter="Results files (*.csv;*.asc;*.xlsx;*.xls)"
            )
            names = []
            n = 0
            while n < len(filepath):
                i = (n + 1) / len(filepath) * 100
                self.ui.pbar.setValue(int(i))

                filename = str(os.path.basename(filepath[n]))
                names.append(filename)
                n = n + 1
            path_to_file = os.path.dirname(filepath[0])
            os.chdir(path_to_file)
            path_old = os.getcwd()

        except:
            path_old = os.getcwd()
            return
        if len(names) == 1:
            QMessageBox.about(
                self,
                "FYI box",
                "Only one file was selected ! Please, select several files.",
            )
            self.ui.pbar.hide()
            return
        save_name, okPressed = QInputDialog.getText(
            self, "Save Name", "Your name:", QLineEdit.Normal, ""
        )
        if okPressed and save_name != "":
            try:
                self.merged_data = merge_file(names, self.isotopes_dict)
            except:
                self.ui.pbar.hide()
                QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
                return
        else:
            self.ui.pbar.hide()
            QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
            return

        # os.chdir(path_to_file)
        # self.merged_data.to_csv(save_name +".csv",index = False)
        self.write_csv_df(path_to_file, save_name + ".csv", self.merged_data)
        filename = save_name + ".csv"
        dataframe = load_MS_file(filename, self.isotopes_dict)
        os.chdir(path_old)

        self.ui.pbar.hide()

        # Load the created merged file
        item = QtWidgets.QListWidgetItem(filename)
        item_2 = QtWidgets.QListWidgetItem(filename + " ")
        # Attribute data loaded to the items
        item.setData(self.USERDATA_ROLE, dataframe)
        item_2.setData(self.USERDATA_ROLE, dataframe)
        # Display items in their respective Qlist
        self.ui.list_loaded_file.addItem(item)
        self.ui.list_loaded_file_2.addItem(item_2)
        # Set the color of the item for better identification
        i = self.ui.list_loaded_file.count() - 1
        j = self.ui.list_loaded_file_2.count() - 1
        qcolor = QColor("#42d66a")
        qcolor.setAlphaF(0.3)
        self.ui.list_loaded_file.item(i).setBackground(QColor(qcolor))
        self.ui.list_loaded_file_2.item(j).setBackground(QColor(qcolor))

    def fusion_replicats(self):
        """
        Calls the Fusion_Replicats and load the newly created .csv in the GUI
        """
        self.ui.pbar.show()
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(
                filter="Results files (*.csv;*.asc;*.xls;*.xlsx)"
            )
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
        except:
            return
        try:
            replicats_tuple = QInputDialog.getInt(
                self,
                "Extraction of species common to x replicates",
                "Species must be found in at least x samples : ",
                min=1,
                max=len(names[0]),
            )
        except:
            QMessageBox.about(self, "FYI box", "Aborted")
        save_name, okPressed = QInputDialog.getText(
            self, "Filename and save name", "Your name:", QLineEdit.Normal, ""
        )
        i = 50
        self.ui.pbar.setValue(i)
        replicats = replicats_tuple[0]
        if okPressed and save_name != "":
            try:
                self.merged_data = fuse_replicates(names, replicats, self.isotopes_dict)
            except:
                self.ui.pbar.hide()
                QMessageBox.about(self, "FYI box", "Error, no files merged")
        self.write_csv_df(path_to_file, save_name + ".csv", self.merged_data)
        os.chdir(path_old)
        self.ui.pbar.hide()

    def merge_merged_files(self):
        """
        Calls the Merge_merged_files function and load the newly created .csv in the GUI
        """
        self.ui.pbar.show()
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(
                filter="Results files (*.csv)"
            )
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
            save_name, okPressed = QInputDialog.getText(
                self, "Save Name", "Your name:", QLineEdit.Normal, ""
            )
        except:
            return
        i = 50
        self.ui.pbar.setValue(i)
        if okPressed and save_name != "":
            try:
                self.merged_data = merge_merged_file(names, self.isotopes_dict)
            except:
                self.ui.pbar.hide()
                QMessageBox.about(
                    self, "FYI box", "You can only merge the same type of file"
                )
                return
        # os.chdir(path_to_file)
        # self.merged_data.to_csv(save_name +".csv",index = False)
        self.write_csv_df(path_to_file, save_name + ".csv", self.merged_data)

        os.chdir(path_old)
        self.ui.pbar.hide()

    def merge_Multicsv(
        self,
    ):  # Merged files from sequential attribution (Obritrap only) (To update ?)

        self.ui.pbar.show()
        i = 0
        self.ui.pbar.setValue(i)
        try:
            filepath, _ = QtWidgets.QFileDialog.getOpenFileNames(
                filter="Results files (*.csv;*.asc;*.xlsx;*.xls)"
            )
            names = []
            n = 0
            while n < len(filepath):
                i = (n + 1) / len(filepath) * 100
                self.ui.pbar.setValue(i)

                filename = str(os.path.basename(filepath[n]))
                names.append(filename)
                n = n + 1
            path_to_file = os.path.dirname(filepath[0])
            os.chdir(path_to_file)
            path_old = os.getcwd()

        except:
            path_old = os.getcwd()
            return
        if len(names) == 1:
            QMessageBox.about(
                self,
                "FYI box",
                "Only one file was selected ! Please, select several files.",
            )
            self.ui.pbar.hide()
            return

        save_name, okPressed = QInputDialog.getText(
            self, "Save Name", "Name of the merged file:", QLineEdit.Normal, ""
        )

        i = 50
        self.ui.pbar.setValue(i)
        try:
            if okPressed and save_name != "":
                self.ui.merged_data = merge_Multicsv(names)
        except:
            QMessageBox.about(self, "FYI box", "An error has occurred")
            self.ui.pbar.hide()
            return
        os.chdir(path_to_file)
        self.write_csv_df(path_to_file, save_name + ".csv", self.ui.merged_data)

        os.chdir(path_old)
        self.ui.pbar.hide()

    def merge_unattributed_files(self):
        """
        Calls the Merge Function for unnatributed data and load the newly created .csv in the GUI
        """
        self.ui.pbar.show()
        i = 0
        self.ui.pbar.setValue(i)
        try:
            names = QtWidgets.QFileDialog.getOpenFileNames(
                filter="Raw files (*.asc; *.csv)"
            )
            path_old = os.getcwd()
            path_to_file = os.path.dirname(names[0][0])
            os.chdir(path_to_file)
            tol = QInputDialog.getDouble(
                self,
                "Choose the Tolerance for merging",
                "Tolerance in ppm (min = 0.01 max : 50): ",
                value=1,
                min=0.001,
                max=50,
                decimals=2,
            )[0]
            min_rel_int, ok = QInputDialog.getDouble(
                self,
                "Choose Minimum Rel. Int. value",
                "Do you want to set a lower limit for the relative intensity ? \nCancel if you don't.",
                value=0.1,
                min=0,
                max=50,
                decimals=3,
            )
            if not ok:
                min_rel_int = None
            save_name, okPressed = QInputDialog.getText(
                self, "Save Name", "Your name:", QLineEdit.Normal, ""
            )

        except:
            path_old = os.getcwd()
            return
        if okPressed and save_name != "":
            try:
                self.merged_data = merge_non_attributed(
                    names,
                    tol,
                    min_rel_intens=min_rel_int,
                    callback=self.ui.pbar.setValue,
                )
            except:
                self.ui.pbar.hide()
                QMessageBox.about(self, "FYI box", "Impossible to merge selected files")
                return
        else:
            self.ui.pbar.hide()
            QMessageBox.about(self, "FYI box", "No or wrong saving name")
            return
        try:
            self.write_csv_df(path_to_file, save_name + ".csv", self.merged_data)

            filename = save_name + ".csv"
            dataframe = load_MS_file(filename, self.isotopes_dict)
            os.chdir(path_old)
            self.ui.pbar.hide()

            # Load the created merged file
            item_2 = QtWidgets.QListWidgetItem(filename + " ")
            # Attribute data loaded to the items
            item_2.setData(self.USERDATA_ROLE, dataframe)
            # Display items in their respective Qlist
            self.ui.list_loaded_file_2.addItem(item_2)
            # Set the color of the item for better identification
            j = self.ui.list_loaded_file_2.count() - 1
            qcolor = QColor("#bfb0b7")
            qcolor.setAlphaF(0.3)
            self.ui.list_loaded_file_2.item(j).setBackground(QColor(qcolor))
        except:
            self.ui.pbar.hide()
            QMessageBox.about(
                self, "FYI box", "An error occurs during the saving of your file"
            )
            return

    def read_param(self):
        """
        Reads graphic paramaters from the GUI
        """
        if self.ui.radio_size_and_color.isChecked():
            self.dot_type = "sc"
        elif self.ui.radio_color.isChecked():
            self.dot_type = "c"
        elif self.ui.radio_size.isChecked():
            self.dot_type = "s"

        self.d_size = float(self.ui.dot_size.text())
        self.fontsize = float(self.ui.font_size.text())
        self.edge = self.ui.CheckBox_edge.isChecked()
        self.para_dict = {
            "dt": self.dot_type,
            "ds": self.d_size,
            "fs": self.fontsize,
            "cm": self.color_map,
        }

        self.fps = float(self.ui.gif_fps.text())
        matplotlib.rcParams["savefig.dpi"] = self.ui.saveDPI.text()
