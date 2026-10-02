from modules.controller_dependencies import *

class DataViewsMixin:
    def distrib_pannel(self):
        """
        Enables GUI elements in the View->Overview->Distribution panel
        """
        x_axes = self.ui.list_distribution.currentRow()
        if x_axes == 0:
            self.ui.groupBox_18.setEnabled(True)
        if x_axes == 1:
            self.ui.groupBox_18.setEnabled(False)
            self.ui.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 2:
            self.ui.groupBox_18.setEnabled(False)
            self.ui.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 3:
            self.ui.groupBox_18.setEnabled(False)
            self.ui.radio_both_intens_vs_DBE.setChecked(True)
        if x_axes == 4:
            self.ui.groupBox_18.setEnabled(False)
            self.ui.radio_both_intens_vs_DBE.setChecked(True)

    def distribution_compare_pannel(self):
        """
        Enables GUI elements in the Compare->Overview->Distribution panel
        """
        x_axes = self.ui.list_distribution_compare.currentRow()
        if x_axes == 0:
            self.ui.groupBox_37.setEnabled(True)
        if x_axes == 1:
            self.ui.groupBox_37.setEnabled(False)
            self.ui.radio_both_DBE_compare.setChecked(True)
        if x_axes == 2:
            self.ui.groupBox_37.setEnabled(False)
            self.ui.radio_both_DBE_compare.setChecked(True)
        if x_axes == 3:
            self.ui.groupBox_37.setEnabled(False)
            self.ui.radio_both_DBE_compare.setChecked(True)
        if x_axes == 4:
            self.ui.groupBox_37.setEnabled(False)
            self.ui.radio_both_DBE_compare.setChecked(True)

    def split_classes(self):
        """
        Identifies chemical classes and PCA coeficient (if any) of the loaded Peak_list class and activates relevants GUI elements
        """

        self.ui.list_classes_DBE.clear()
        self.ui.list_classes_mass_spec.clear()
        self.ui.list_classes_error.clear()
        self.ui.list_classes_VK.clear()
        self.ui.list_classes_Kendrick.clear()
        self.ui.list_classes_Kendrick_univ.clear()
        self.ui.list_classes_distrib.clear()
        self.ui.list_classes_ACOS.clear()
        self.ui.list_classes_MAI.clear()
        self.ui.list_classes_MCR.clear()
        self.ui.list_classes_ACOS_comp.clear()
        self.ui.list_classes_MAI_comp.clear()
        self.ui.list_classes_MCR_comp.clear()
        items = self.ui.list_loaded_file.selectedItems()
        if not items:
            return
        item = items[0]
        self.data = item.data(self.USERDATA_ROLE)
        n = 0
        if self.data.df_type == "PyC2MC_merged":
            self.ui.stackedWidget_overview.setCurrentWidget(self.ui.page_composition)
            self.ui.radio_composition.setChecked(True)
            self.ui.radio_error_plots.setEnabled(False)
            self.ui.radio_distributions.setEnabled(True)
            self.ui.radio_mass_spectrum.setEnabled(False)
            self.ui.K_nitrogen.setEnabled(True)
            self.ui.K_oxygen.setEnabled(True)
            self.ui.K_sulfur.setEnabled(True)
            self.ui.btn_kendricks.setEnabled(True)

        elif self.data.df_type == "PyC2MC_fusion":
            self.ui.stackedWidget_overview.setCurrentWidget(self.ui.page_composition)
            self.ui.radio_composition.setChecked(True)
            self.ui.radio_error_plots.setEnabled(False)
            self.ui.radio_distributions.setEnabled(True)
            self.ui.radio_mass_spectrum.setEnabled(True)
            self.ui.K_nitrogen.setEnabled(True)
            self.ui.K_oxygen.setEnabled(True)
            self.ui.K_sulfur.setEnabled(True)
            self.ui.btn_kendricks.setEnabled(True)

        elif self.data.df_type == "Peaklist":
            self.ui.stackedWidget_overview.setCurrentWidget(self.ui.page_mass_spectrum)
            self.ui.btn_overview.setEnabled(True)
            self.ui.btn_EV.setEnabled(False)
            self.ui.radio_composition.setEnabled(False)
            self.ui.radio_mass_spectrum.setChecked(True)
            self.ui.radio_error_plots.setEnabled(False)
            self.ui.radio_distributions.setEnabled(False)
            self.ui.btn_DBE.setEnabled(False)
            self.ui.btn_van_krevelen.setEnabled(False)
            self.ui.K_nitrogen.setEnabled(False)
            self.ui.K_oxygen.setEnabled(False)
            self.ui.K_sulfur.setEnabled(False)
            self.ui.btn_kendricks.setEnabled(True)
            self.buttonColor()
            return
        elif self.data.df_type == "PyC2MC_merged_unattributed":
            self.ui.plot_button_view.setEnabled(False)
            self.ui.plot_compare.setEnabled(False)
            self.ui.plot_compare_GIF.setEnabled(False)
            return

        if "PC1" in self.data.df:
            self.ui.radio_color_pc1.show()
            self.ui.radio_color_pc2.show()
            self.ui.radio_color_pc1_comp.show()
            self.ui.radio_color_pc2_comp.show()
            self.ui.radio_color_pc1_VK.show()
            self.ui.radio_color_pc2_VK.show()
            self.ui.radio_color_pc1_VK_comp.show()
            self.ui.radio_color_pc2_VK_comp.show()
            self.ui.radio_color_pc1_ACOS.show()
            self.ui.radio_color_pc2_ACOS.show()
            self.ui.radio_color_pc1_ACOS_comp.show()
            self.ui.radio_color_pc2_ACOS_comp.show()
            self.ui.K_PC1.show()
            self.ui.K_PC2.show()
            self.ui.radio_color_pc1.setEnabled(True)
            self.ui.radio_color_pc2.setEnabled(True)
            self.ui.radio_color_pc1_comp.setEnabled(True)
            self.ui.radio_color_pc2_comp.setEnabled(True)
            self.ui.radio_color_pc1_VK.setEnabled(True)
            self.ui.radio_color_pc2_VK.setEnabled(True)
            self.ui.radio_color_pc1_VK_comp.setEnabled(True)
            self.ui.radio_color_pc2_VK_comp.setEnabled(True)
            self.ui.radio_color_pc1_ACOS.setEnabled(True)
            self.ui.radio_color_pc2_ACOS.setEnabled(True)
            self.ui.radio_color_pc1_ACOS_comp.setEnabled(True)
            self.ui.radio_color_pc2_ACOS_comp.setEnabled(True)
            self.ui.K_PC1.setEnabled(True)
            self.ui.K_PC2.setEnabled(True)
            self.ui.K_nitrogen.setEnabled(True)
            self.ui.K_oxygen.setEnabled(True)
            self.ui.K_sulfur.setEnabled(True)
            self.ui.btn_kendricks.setEnabled(True)

        else:
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
            self.ui.radio_color_intensity_2.setChecked(True)
            self.ui.radio_color_intensity_3.setChecked(True)
            self.ui.K_nitrogen.setEnabled(True)
            self.ui.K_oxygen.setEnabled(True)
            self.ui.K_sulfur.setEnabled(True)
            self.ui.btn_kendricks.setEnabled(True)

        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_DBE.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_VK.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_Kendrick.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_Kendrick_univ.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_mass_spec.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_distrib.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_ACOS.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_MAI.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_MCR.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_error.addItem(item_classes)

        while n < len(self.data.classes):
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_DBE.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_VK.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_Kendrick.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_Kendrick_univ.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_mass_spec.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_distrib.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_ACOS.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_MAI.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_MCR.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_ACOS_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_MAI_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_MCR_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.data.classes_concat.iloc[n, 0]
            )
            item_classes.setData(self.USERDATA_ROLE, self.data.classes.iloc[n, 0])
            self.ui.list_classes_error.addItem(item_classes)
            n = n + 1
        self.ui.list_classes_distrib.setCurrentRow(0)
        self.ui.list_classes_error.setCurrentRow(0)

    def split_classes_merged(self):
        """
        Identifies chemical classes and PCA coeficient (if any) of the loaded Peak_list class and activates relevants GUI elements (for a merged file)
        """
        self.ui.list_sample_1.clear()
        self.ui.list_sample_2.clear()
        self.ui.volc_color_classes.setEnabled(True)
        self.ui.volc_color_dbe.setEnabled(True)
        self.ui.volc_color_oc.setEnabled(True)
        self.ui.list_sample_1_stats.clear()
        self.ui.list_sample_2_stats.clear()
        item_file = self.ui.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        if data_selected.df_type == "PyC2MC_merged":
            volc_data = data_selected.volc_data
            volc_data.columns = volc_data.columns.str.replace(".csv", "")
            volc_data.columns = volc_data.columns.str.replace("Rel_intens_", "")
            self.volc_data = volc_data
            n = 2
            while n < len(volc_data.columns) - 5:
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                self.ui.list_sample_1.addItem(item_sample)
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                self.ui.list_sample_2.addItem(item_sample)
                n = n + 1
        elif data_selected.df_type == "PyC2MC_merged_unattributed":
            self.ui.volc_color_classes.setEnabled(False)
            self.ui.volc_color_dbe.setEnabled(False)
            self.ui.volc_color_oc.setEnabled(False)
            self.ui.volc_color_mz.setChecked(True)
            volc_data = data_selected.volc_data
            volc_data.columns = volc_data.columns.str.replace("Rel_intens_", "")
            self.volc_data = volc_data
            n = 2
            while n < len(volc_data.columns):
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                self.ui.list_sample_1.addItem(item_sample)
                item_sample = QtWidgets.QListWidgetItem(volc_data.columns[n])
                self.ui.list_sample_2.addItem(item_sample)
                n = n + 1

        # Add samples in FC calc samples list
        # Remove useless info in names
        nb_sample = (
            int(
                (
                    data_selected.df.columns.get_loc("Normalized_intensity")
                    - data_selected.df.columns.get_loc("count")
                )
                / 2
            )
            - 1
        )
        name_data = data_selected.df.iloc[
            :,
            data_selected.df.columns.get_loc("count")
            + nb_sample
            + 1 : data_selected.df.columns.get_loc("count")
            + nb_sample * 2
            + 1,
        ]
        name_data.columns = name_data.columns.str.replace(".csv", "")
        name_data.columns = name_data.columns.str.replace(".xlsx", "")
        name_data.columns = name_data.columns.str.replace("Rel_intens_", "")

        # add items in lists
        n = 0
        while n < len(name_data.columns):
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            self.ui.list_sample_1_stats.addItem(item_sample)
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            self.ui.list_sample_2_stats.addItem(item_sample)
            n = n + 1

    def save_file(self):
        """
        Export chemical classes data of the selected file to .csv
        """

        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        msgBox = QMessageBox()
        msgBox.setText("Save datasets or save classes ?")
        msgBox.setWindowTitle("Boîte de dialogue")
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonYes = msgBox.button(QMessageBox.Yes)
        buttonYes.setText("Datasets")
        buttonNo = msgBox.button(QMessageBox.No)
        buttonNo.setText("Classes")
        choice = msgBox.exec_()
        if choice == QMessageBox.Yes:
            save_name, okPressed = QInputDialog.getText(
                self, "Save Name", "Your name:", QLineEdit.Normal, ""
            )
            os.chdir(save_path)
            # data_selected.df.to_csv(save_name +".csv",index = False)
            self.write_csv_df(save_path, save_name + ".csv", data_selected.df)
        elif choice == QMessageBox.No:
            save_name, okPressed = QInputDialog.getText(
                self, "Save Name", "Your name:", QLineEdit.Normal, ""
            )
            os.chdir(save_path)
            # data_selected.df.to_csv(save_name +".csv",index = False)
            if data_selected.df_type == "Attributed":

                def weighted_average_m1(to_mean, norm_I):
                    numerator = sum([x * y for x, y in zip(to_mean, norm_I)])
                    denominator = sum(norm_I)
                    return round(numerator / denominator, 2)

                classes = data_selected.classes.copy()
                classes["Mean DBE"] = 0
                for classe in classes.variable:
                    temp = Select_classe(
                        classe,
                        data_selected.df,
                        data_selected.heteroatoms,
                        data_selected.classes,
                    )
                    mean_DBE = weighted_average_m1(
                        temp["DBE"], temp["normalized_intensity"]
                    )
                    classes["Mean DBE"][classes.variable == classe] = mean_DBE
                self.write_csv_df(save_path, save_name + ".csv", classes)
            else:
                self.write_csv_df(save_path, save_name + ".csv", data_selected.classes)
