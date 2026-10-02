from modules.controller_dependencies import *

class ComparisonMixin:
    def pl_comp_KMD(self, gif=False):
        """
        KMD plot for the stats menu
        """

        item_file = self.ui.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
            plt.close("all")
        sample_1 = self.ui.list_sample_1_stats.currentRow()
        sample_2 = self.ui.list_sample_2_stats.currentRow()
        n_sample = (
            int(
                (
                    data_selected.df.columns.get_loc("Normalized_intensity")
                    - data_selected.df.columns.get_loc("count")
                )
                / 2
            )
            - 1
        )
        if self.ui.radio_fold_rel_KMD_stats.isChecked():
            fold_intens_1 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            min_max_scaler = preprocessing.MinMaxScaler()
            fold_intens_1 = min_max_scaler.fit_transform(fold_intens_1)
            fold_intens_2 = min_max_scaler.fit_transform(fold_intens_2)

            leg_1 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ].name
            )
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Rel_intens_", "")
            leg_2 = leg_2.replace("Rel_intens_", "")
        else:
            fold_intens_1 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            leg_1 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ].name
            )
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Rel_intens_", "")
            leg_2 = leg_2.replace("Rel_intens_", "")
        data_selected.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)
        data_selected.df["summed_intensity"] = fold_intens_1 + fold_intens_2
        # KMD calculation
        if self.ui.edit_mass_motif_stats.text():
            repetive_unit_mass = float(self.ui.edit_mass_motif_stats.text())
            nominal_unit = round(repetive_unit_mass)
        data_selected.df["Kendrick mass"] = data_selected.df["m/z"] * (
            nominal_unit / repetive_unit_mass
        )
        data_selected.df["Kendrick nominal mass"] = round(data_selected.df["m/z"])

        if self.ui.round_up_stats.isChecked():
            data_selected.df["Kendrick nominal mass"] = data_selected.df[
                "Kendrick mass"
            ].apply(np.ceil)
        elif self.ui.round_closest_stats.isChecked():
            data_selected.df["Kendrick nominal mass"] = round(
                data_selected.df["Kendrick mass"]
            )
        data_selected.df["Kendrick mass defect"] = (
            data_selected.df["Kendrick nominal mass"]
            - data_selected.df["Kendrick mass"]
        )

        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        data_selected.df["fc"].fillna(2e20, inplace=True)
        p_inf = (data_selected.df["fc"] > 1e20).tolist()
        n_inf = (data_selected.df["fc"] < -1e20).tolist()
        data_inf_pos = data_selected.df[:][p_inf].copy()
        data_inf_neg = data_selected.df[:][n_inf].copy()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        ###

        data_extract = data_selected.df.drop(
            index=data_selected.df.index[inf_index], axis=0
        ).copy()
        data_extract = data_extract.sort_values(by=["fc"], ascending=False)
        Intens = data_extract.iloc[
            :, data_selected.df.columns.get_loc("summed_intensity") - 2
        ].values.reshape(-1, 1)
        min_max_scaler = preprocessing.MinMaxScaler()
        Intens_scaled = min_max_scaler.fit_transform(Intens)
        data_extract.iloc[
            :, data_selected.df.columns.get_loc("summed_intensity") - 2
        ] = Intens_scaled
        data_extract = data_extract.sort_values(
            by=["fc", "summed_intensity"], ascending=[False, True]
        )

        data = pandas.DataFrame()
        data.data_extract = data_extract
        data.data_inf_neg = data_inf_neg
        data.data_inf_pos = data_inf_pos
        frames.append(data)

        def Anim(frames):
            if gif == False:
                fig = plt.figure()
                transf = fig.transFigure
            else:
                Figure.clear()
                transf = Figure.transFigure
            self.read_param()
            if self.ui.CheckBox_size_fc_kmd_stats.isChecked():
                size = self.d_size * frames.data_extract.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_1,
                ].astype(float)
                size_inf_neg = self.d_size * frames.data_inf_neg.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_1,
                ].astype(float)
                size_inf_pos = self.d_size * frames.data_inf_pos.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_2,
                ].astype(float)
            else:
                size = self.d_size
                size_inf_neg = self.d_size
                size_inf_pos = self.d_size

            if self.ui.fc_all_kmd_stats.isChecked():
                plot_fun(
                    "scatter",
                    x=frames.data_inf_neg["Kendrick nominal mass"],
                    y=frames.data_inf_neg["Kendrick mass defect"],
                    d_color="#a84ca4",
                    dot_type=self.dot_type,
                    edge=self.edge,
                    size=size_inf_neg,
                )
                plot_fun(
                    "scatter",
                    x=frames.data_inf_pos["Kendrick nominal mass"],
                    y=frames.data_inf_pos["Kendrick mass defect"],
                    d_color="#0070c0",
                    dot_type=self.dot_type,
                    edge=self.edge,
                    size=size_inf_pos,
                )
            # plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = size)
            plt.scatter(
                frames.data_extract["Kendrick nominal mass"],
                frames.data_extract["Kendrick mass defect"],
                s=size,
                c=frames.data_extract["fc"],
                vmin=-8,
                vmax=8,
                cmap="RdYlGn",
                edgecolor="black",
                linewidths=0.7,
            )

            if self.ui.x_min_KMD_stats.text():
                x_min = float(self.ui.x_min_KMD_stats.text())
                plt.gca().set_xlim(left=x_min)
            if self.ui.x_max_KMD_stats.text():
                x_max = float(self.ui.x_max_KMD_stats.text())
                plt.gca().set_xlim(right=x_max)

            if self.ui.y_min_KMD_stats.text():
                y_min = float(self.ui.y_min_KMD_stats.text())
                plt.gca().set_ylim(bottom=y_min)
            if self.ui.y_max_KMD_stats.text():
                y_max = float(self.ui.y_max_KMD_stats.text())
                plt.gca().set_ylim(top=y_max)

            if len(data.data_extract) != 0:
                cbar = plt.colorbar(ticks=[-8, 8])
                cbar.ax.set_yticklabels(
                    [leg_1, leg_2],
                    fontsize=font_size - 2,
                    weight="bold",
                    rotation=90,
                    va="center",
                )  # vertically oriented colorbar
                cbar.set_label(
                    "log2(FC)", labelpad=-2.625 * (font_size), rotation=90, fontsize=16
                )

            plt.xlabel("Nominal mass", fontsize=self.fontsize + 4)
            plt.ylabel("KMD", fontsize=self.fontsize + 4)
            plt.xticks(fontsize=self.fontsize)
            plt.yticks(fontsize=self.fontsize)

            if self.ui.fc_all_kmd_stats.isChecked():
                legend_elements = [
                    Patch(
                        facecolor="#a84ca4", edgecolor="k", label=leg_1 + " exclusive"
                    ),
                    Patch(
                        facecolor="#0070c0", edgecolor="k", label=leg_2 + " exclusive"
                    ),
                ]
                plt.legend(handles=legend_elements, fontsize=font_size - 4)
            if gif == False:
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(
                    self.pos().x() + 940, self.pos().y() + 200, 800, 680
                )
            if "m/z" in frames.data_extract:
                mplcursors.cursor(multiple=True).connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        "m/z = "
                        + str(frames.data_extract["m/z"].iloc[sel.target.index])
                    ),
                )

        if gif == False:
            for i in frames:
                Anim(i)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 800, 680
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def pl_comp_MD(self, gif=False):
        """
        KMD plot for the stats menu
        """

        item_file = self.ui.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
            plt.close("all")
        sample_1 = self.ui.list_sample_1_stats.currentRow()
        sample_2 = self.ui.list_sample_2_stats.currentRow()
        n_sample = max(data_selected.df["count"])
        if self.ui.radio_fold_rel_md_stats.isChecked():
            fold_intens_1 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            min_max_scaler = preprocessing.MinMaxScaler()
            fold_intens_1 = min_max_scaler.fit_transform(fold_intens_1)
            fold_intens_2 = min_max_scaler.fit_transform(fold_intens_2)

            leg_1 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ].name
            )
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Rel_intens_", "")
            leg_2 = leg_2.replace("Rel_intens_", "")
        else:
            fold_intens_1 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            leg_1 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                data_selected.df.iloc[
                    :,
                    data_selected.df.columns.get_loc("count")
                    + max(data_selected.df["count"])
                    + 1
                    + sample_2,
                ].name
            )
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Rel_intens_", "")
            leg_2 = leg_2.replace("Rel_intens_", "")
        data_selected.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)
        data_selected.df["summed_intensity"] = fold_intens_1 + fold_intens_2
        # MD calculation
        nominal_mass = round(data_selected.df["m/z"])
        mass_defect = data_selected.df["m/z"] - nominal_mass
        data_selected.df["nominal_mass"] = nominal_mass
        data_selected.df["mass_defect"] = mass_defect

        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        data_selected.df["fc"].fillna(2e20, inplace=True)
        p_inf = (data_selected.df["fc"] > 1e20).tolist()
        n_inf = (data_selected.df["fc"] < -1e20).tolist()
        data_inf_pos = data_selected.df[:][p_inf].copy()
        data_inf_neg = data_selected.df[:][n_inf].copy()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        ###

        data_extract = data_selected.df.drop(
            index=data_selected.df.index[inf_index], axis=0
        ).copy()
        data_extract = data_extract.sort_values(by=["fc"], ascending=False)
        Intens = data_extract.iloc[
            :, data_selected.df.columns.get_loc("summed_intensity") - 2
        ].values.reshape(-1, 1)
        min_max_scaler = preprocessing.MinMaxScaler()
        Intens_scaled = min_max_scaler.fit_transform(Intens)
        data_extract.iloc[
            :, data_selected.df.columns.get_loc("summed_intensity") - 2
        ] = Intens_scaled
        data_extract = data_extract.sort_values(
            by=["fc", "summed_intensity"], ascending=[False, True]
        )

        data = pandas.DataFrame()
        data.data_extract = data_extract
        data.data_inf_neg = data_inf_neg
        data.data_inf_pos = data_inf_pos
        frames.append(data)

        def Anim(frames):
            if gif == False:
                fig = plt.figure()
                transf = fig.transFigure
            else:
                Figure.clear()
                transf = Figure.transFigure
            self.read_param()
            if self.ui.CheckBox_size_fc_md_stats.isChecked():
                size = self.d_size * frames.data_extract.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_1,
                ].astype(float)
                size_inf_neg = self.d_size * frames.data_inf_neg.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_1,
                ].astype(float)
                size_inf_pos = self.d_size * frames.data_inf_pos.iloc[
                    :,
                    data_selected.df.columns.get_loc("summed_intensity")
                    - (n_sample)
                    + sample_2,
                ].astype(float)
            else:
                size = self.d_size
                size_inf_neg = self.d_size
                size_inf_pos = self.d_size

            if self.ui.fc_all_md_stats.isChecked():
                plot_fun(
                    "scatter",
                    x=frames.data_inf_neg["Kendrick nominal mass"],
                    y=frames.data_inf_neg["Kendrick mass defect"],
                    d_color="#a84ca4",
                    dot_type=self.dot_type,
                    edge=self.edge,
                    size=size_inf_neg,
                )
                plot_fun(
                    "scatter",
                    x=frames.data_inf_pos["Kendrick nominal mass"],
                    y=frames.data_inf_pos["Kendrick mass defect"],
                    d_color="#0070c0",
                    dot_type=self.dot_type,
                    edge=self.edge,
                    size=size_inf_pos,
                )
            # plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = size)
            plt.scatter(
                frames.data_extract["Kendrick nominal mass"],
                frames.data_extract["Kendrick mass defect"],
                s=size,
                c=frames.data_extract["fc"],
                vmin=-8,
                vmax=8,
                cmap="RdYlGn",
                edgecolor="black",
                linewidths=0.7,
            )

            if self.ui.x_min_MD_stats.text():
                x_min = float(self.ui.x_min_MD_stats.text())
                plt.gca().set_xlim(left=x_min)
            if self.ui.x_max_MD_stats.text():
                x_max = float(self.ui.x_max_MD_stats.text())
                plt.gca().set_xlim(right=x_max)

            if self.ui.y_min_MD_stats.text():
                y_min = float(self.ui.y_min_MD_stats.text())
                plt.gca().set_ylim(bottom=y_min)
            if self.ui.y_max_MD_stats.text():
                y_max = float(self.ui.y_max_MD_stats.text())
                plt.gca().set_ylim(top=y_max)

            if len(data.data_extract) != 0:
                cbar = plt.colorbar(ticks=[-8, 8])
                cbar.ax.set_yticklabels(
                    [leg_1, leg_2],
                    fontsize=font_size - 2,
                    weight="bold",
                    rotation=90,
                    va="center",
                )  # vertically oriented colorbar
                cbar.set_label(
                    "log2(FC)", labelpad=-2.625 * (font_size), rotation=90, fontsize=16
                )

            plt.xlabel("Nominal mass", fontsize=self.fontsize + 4)
            plt.ylabel("Mass defect", fontsize=self.fontsize + 4)
            plt.xticks(fontsize=self.fontsize)
            plt.yticks(fontsize=self.fontsize)

            if self.ui.fc_all_kmd_stats.isChecked():
                legend_elements = [
                    Patch(
                        facecolor="#a84ca4", edgecolor="k", label=leg_1 + " exclusive"
                    ),
                    Patch(
                        facecolor="#0070c0", edgecolor="k", label=leg_2 + " exclusive"
                    ),
                ]
                plt.legend(handles=legend_elements, fontsize=font_size - 4)
            if gif == False:
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(
                    self.pos().x() + 940, self.pos().y() + 200, 800, 680
                )
            if "m/z" in frames.data_extract:
                mplcursors.cursor(multiple=True).connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        "m/z = "
                        + str(frames.data_extract["m/z"].iloc[sel.target.index])
                    ),
                )

        if gif == False:
            for i in frames:
                Anim(i)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 800, 680
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def kendrick_motif_calculation(self):
        """
        Returns the mass of the selected repetitive unit
        """

        formula = self.ui.edit_motif.text()  # Retrieves text from "edit_motif"

        form = cp.parse_formula(formula)  # Creates a dict with symbols and mass

        try:
            mass = 0  # Initialisation
            for atom in form:  # Loop
                mass = mass + form[atom] * self.isotopes_dict[atom]
        except:
            QMessageBox.about(self, "FYI box", "Upper case only.")

        self.ui.edit_mass_motif.setText(str(mass))  # Modify text in "mass_motif"

    def kendrick_motif_compare_calculation(self):
        """
        Returns the mass of the selected repetitive unit
        """

        formula = self.ui.edit_motif_compare.text()  # Retrieves text from "edit_motif"

        form = cp.parse_formula(formula)  # Creates a dict with symbols and mass

        try:
            mass = 0  # Initialisation
            for atom in form:  # Loop
                mass = mass + form[atom] * self.isotopes_dict[atom]
        except:
            QMessageBox.about(self, "FYI box", "Upper case only.")

        self.ui.edit_mass_motif_compare.setText(
            str(mass)
        )  # Modify text in "mass_motif"

    def kendrick_motif_stats_calculation(self):
        """
        Returns the mass of the selected repetitive unit
        """

        formula = self.ui.edit_motif_stats.text()  # Retrieves text from "edit_motif"

        form = cp.parse_formula(formula)  # Creates a dict with symbols and mass

        try:
            mass = 0  # Initialisation
            for atom in form:  # Loop
                mass = mass + form[atom] * self.isotopes_dict[atom]
        except:
            QMessageBox.about(self, "FYI box", "Upper case only.")

        self.ui.edit_mass_motif_stats.setText(str(mass))  # Modify text in "mass_motif"

    def plot_Kendrick(self, gif=False):
        """
        Classic Kendrick plots and extracting series
        """

        frames = []
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        data_filtered = data_selected.df
        if data_selected.df_type == "PyC2MC_merged":
            data_filtered = data_filtered.rename(
                columns={"summed_intensity": "normalized_intensity"}
            )
        data_filtered = data_filtered.sort_values(
            by=["normalized_intensity"], ascending=True
        )
        self.read_param()
        dot_size = self.d_size
        font_size = self.fontsize
        if self.ui.edit_mass_motif.text():
            repetive_unit_mass = float(self.ui.edit_mass_motif.text())
            nominal_unit = round(repetive_unit_mass)

        if self.ui.stackedWidget_Kendrick.currentIndex() == 0:  # KMD classic
            item_classes = self.ui.list_classes_Kendrick.selectedItems()
        elif self.ui.stackedWidget_Kendrick.currentIndex() == 2:  # MD
            item_classes = self.ui.list_classes_Kendrick_univ.selectedItems()
        #### KMD extract ####
        if self.ui.stackedWidget_Kendrick.currentIndex() == 1:
            tol_per = float(self.ui.Extract_tol.text())
            if self.ui.set_intensity_KMD.text():
                intens_KMD = float(self.ui.set_intensity_KMD.text())
                data_filtered = data_filtered[
                    data_filtered.normalized_intensity >= intens_KMD
                ]

            if "mz" in data_filtered:
                data_filtered["Kendrick mass"] = data_filtered["mz"] * (
                    nominal_unit / repetive_unit_mass
                )
            elif "count" in data_filtered:
                data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                    nominal_unit / repetive_unit_mass
                )
            elif "m/z" in data_filtered:
                data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                    nominal_unit / repetive_unit_mass
                )

            if self.ui.roundUp.isChecked():
                data_filtered["Kendrick nominal mass"] = data_filtered[
                    "Kendrick mass"
                ].apply(np.ceil)
            elif self.ui.roundClosest.isChecked():
                data_filtered["Kendrick nominal mass"] = round(
                    data_filtered["Kendrick mass"]
                )

            data_filtered["Kendrick mass defect"] = (
                data_filtered["Kendrick nominal mass"] - data_filtered["Kendrick mass"]
            )

            if data_selected.df_type == "PyC2MC_merged":
                data_filtered = data_filtered.rename(
                    columns={"summed_intensity": "normalized_intensity"}
                )
            # Determination of the number of series (1 to 6):
            data_filtered["id"] = 0  # Colors species of interest
            n_series = 0
            list_mass = []
            self.kendrickSeries = pandas.DataFrame()
            list_series = [
                self.ui.series_1,
                self.ui.series_2,
                self.ui.series_3,
                self.ui.series_4,
                self.ui.series_5,
                self.ui.series_6,
                self.ui.series_7,
            ]
            list_series_index = []
            list_color = [
                self.ui.comboBox_1.currentText(),
                self.ui.comboBox_2.currentText(),
                self.ui.comboBox_3.currentText(),
                self.ui.comboBox_4.currentText(),
                self.ui.comboBox_5.currentText(),
                self.ui.comboBox_6.currentText(),
                self.ui.comboBox_7.currentText(),
            ]
            for n in range(7):
                if list_series[n].text():
                    n_series = n_series + 1
                    list_mass.append(list_series[n].text())
                    list_series_index.append(n)
            if n_series == 0:
                QMessageBox.about(self, "FYI box", "No series to look for ...")
                return

            for j in list_series_index:

                if self.ui.mz_extraction.isChecked():
                    try:
                        m = float(list_series[j].text())
                    except:
                        QMessageBox.about(
                            self,
                            "FYI box",
                            "Only use digits and dots for m/z or KMD values (no comma !)",
                        )
                        return
                    rep_pattern = repetive_unit_mass
                    nominal_pattern = round(rep_pattern)
                    km = m * (nominal_pattern / rep_pattern)

                try:
                    m = float(list_series[j].text())
                except:
                    QMessageBox.about(
                        self,
                        "FYI box",
                        "Only use digits and dots for m/z values (no comma !)",
                    )
                    return

                if self.ui.mz_extraction.isChecked() == True:
                    rep_pattern = repetive_unit_mass
                    nominal_pattern = round(rep_pattern)
                    km = m * (nominal_pattern / rep_pattern)
                    if self.ui.roundUp.isChecked():
                        nkm = math.ceil(km)
                    elif self.ui.roundClosest.isChecked():
                        nkm = round(km)
                    kmd = nkm - km
                    tol = abs(kmd) * tol_per / 100  # tolerance attribution

                    n = 0
                    l = 0
                    i = 0
                    lst = [round(m)]
                    m_plus = m
                    while m_plus <= max(data_filtered["m/z"]):
                        m_plus = m_plus + rep_pattern
                        if self.ui.roundUp.isChecked():
                            nkm = math.ceil(km)
                        elif self.ui.roundClosest.isChecked():
                            nkm = round(km)
                        kmd = nkm - km

                        l = 0
                        i = 0
                        lst = [round(m)]
                        m_plus = m
                        while m_plus <= max(data_filtered["m/z"]):
                            m_plus = m_plus + rep_pattern
                            if self.ui.roundUp.isChecked():
                                i = math.ceil(m_plus * (nominal_pattern / rep_pattern))
                            elif self.ui.roundClosest.isChecked():
                                i = round(m_plus * (nominal_pattern / rep_pattern))
                            lst.append(i)
                        m_moins = m
                        while m_moins >= min(data_filtered["m/z"]):
                            m_moins = m_moins - rep_pattern
                            if self.ui.roundUp.isChecked():
                                i = math.ceil(m_moins * (nominal_pattern / rep_pattern))
                            elif self.ui.roundClosest.isChecked():
                                i = round(m_moins * (nominal_pattern / rep_pattern))
                            lst.append(i)
                        lst.sort()
                        data_filtered.sort_values("m/z", ascending=True, inplace=True)
                        data_filtered = data_filtered.reset_index(drop=True)
                        for kmd_exp in data_filtered["Kendrick mass defect"]:
                            if kmd_exp >= kmd - tol and kmd_exp <= kmd + tol:
                                for o in lst:
                                    if o == data_filtered["Kendrick nominal mass"][l]:
                                        data_filtered.at[l, "id"] = j + 1
                            l = l + 1

                if self.ui.KMD_Extraction.isChecked():
                    try:
                        kmd = float(list_series[j].text())
                    except:
                        QMessageBox.about(
                            self,
                            "FYI box",
                            "Only use digits and dots for KMD values (no comma !)",
                        )
                        return

                    tol = abs(kmd) * tol_per / 100  # tolerance attribution
                    n = 0
                    data_filtered.sort_values("m/z", ascending=True, inplace=True)
                    data_filtered = data_filtered.reset_index(drop=True)
                    for o in data_filtered["Kendrick mass defect"]:
                        if o >= kmd - tol and o <= kmd + tol:
                            data_filtered.at[n, "id"] = j + 1
                        n = n + 1

            d = {
                "col1": data_filtered["Kendrick nominal mass"],
                "col2": data_filtered["Kendrick mass defect"],
                "normalized_intensity": data_filtered["normalized_intensity"],
                "id": data_filtered["id"],
                "m/z": data_filtered["m/z"],
            }
            df = pandas.DataFrame(data=d)
            df = df.sort_values("normalized_intensity", ascending=True)
            if self.ui.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            fig = plt.figure()
            if self.ui.checkBox_extract_only.isChecked() == False:
                plt.scatter(
                    df["col1"],
                    df["col2"],
                    color=[0, 0, 0, 0.1],
                    s=df["normalized_intensity"] * dot_size / 100,
                )
            for k in list_series_index:
                d_series = data_filtered[data_filtered["id"] == k + 1]
                plt.scatter(
                    d_series["Kendrick nominal mass"],
                    d_series["Kendrick mass defect"],
                    color=list_color[k],
                    s=(d_series["normalized_intensity"]) * dot_size / 100,
                    edgecolors="black",
                )

            plt.clim(0, n_series)

            if self.ui.KNM_min.text():
                KNM_min = float(self.ui.KNM_min.text())
                plt.gca().set_xlim(left=KNM_min)
            if self.ui.KNM_max.text():
                KNM_max = float(self.ui.KNM_max.text())
                plt.gca().set_xlim(right=KNM_max)
            if self.ui.KMD_min.text():
                KMD_min = float(self.ui.KMD_min.text())
                plt.gca().set_ylim(bottom=KMD_min)
            if self.ui.KMD_max.text():
                KMD_max = float(self.ui.KMD_max.text())
                plt.gca().set_ylim(top=KMD_max)
            plt.xlabel("Kendrick nominal mass")
            plt.ylabel("Kendrick mass defect")
            mplcursors.cursor(multiple=True).connect(
                "add",
                lambda sel: sel.annotation.set_text(
                    d_series["m/z"].iloc[sel.target.index]
                ),
            )
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            plt.show()
            self.kendrickSeries = data_filtered[data_filtered["id"] != 0]
            return

        #### KMD & MD vs m/z ####
        else:
            if not item_classes:
                item_classes = ["Unatributed"]

            for item in item_classes:
                data_filtered = data_selected.df.copy()
                if item == "Unatributed":
                    classe_selected = ""
                    pass
                else:
                    classe_selected = item.data(self.USERDATA_ROLE)
                    if classe_selected == "All":
                        pass
                    elif "x" in classe_selected:
                        index_classes = data_filtered[classe_selected] == True
                        data_filtered = data_filtered[index_classes]
                    else:
                        classes_index = data_selected.classes[
                            data_selected.classes["variable"] == classe_selected
                        ]
                        index_classes = (
                            data_filtered[data_selected.heteroatoms.columns]
                            == data_selected.heteroatoms.iloc[classes_index.index[0]]
                        ).all(1)
                        data_filtered = data_filtered[index_classes]

                # KMD calculation
                if self.ui.edit_motif.text():
                    edit_repetive_unit = self.ui.edit_motif.text()
                if self.ui.edit_mass_motif.text():
                    repetive_unit_mass = float(self.ui.edit_mass_motif.text())
                    nominal_unit = round(repetive_unit_mass)
                if "mz" in data_filtered:
                    data_filtered["Kendrick mass"] = data_filtered["mz"] * (
                        nominal_unit / repetive_unit_mass
                    )
                    data_filtered["Kendrick nominal mass"] = round(data_filtered["m/z"])
                elif "count" in data_filtered:
                    data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                        nominal_unit / repetive_unit_mass
                    )
                    data_filtered["Kendrick nominal mass"] = round(data_filtered["m/z"])
                elif "m/z" in data_filtered:
                    data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                        nominal_unit / repetive_unit_mass
                    )
                    data_filtered["Kendrick nominal mass"] = round(data_filtered["m/z"])

                if self.ui.roundUp.isChecked():
                    data_filtered["Kendrick nominal mass"] = data_filtered[
                        "Kendrick mass"
                    ].apply(np.ceil)
                elif self.ui.roundClosest.isChecked():
                    data_filtered["Kendrick nominal mass"] = round(
                        data_filtered["Kendrick mass"]
                    )
                data_filtered["Kendrick mass defect"] = (
                    data_filtered["Kendrick nominal mass"]
                    - data_filtered["Kendrick mass"]
                )
                if data_selected.df_type == "PyC2MC_merged":
                    data_filtered = data_filtered.rename(
                        columns={"summed_intensity": "normalized_intensity"}
                    )

                if data_selected.df_type == "PyC2MC_merged":
                    data_filtered = data_filtered.rename(
                        columns={"summed_intensity": "normalized_intensity"}
                    )
                if self.ui.classic_intens_K.isChecked():
                    Intens = data_filtered["normalized_intensity"].copy()
                if self.ui.sqrt_intens_K.isChecked():
                    Intens = data_filtered["normalized_intensity"].copy()
                    Intens = np.sqrt(Intens)
                if self.ui.log_intens_K.isChecked():
                    Intens = np.log10(
                        data_filtered["normalized_intensity"].copy() + 1e-10
                    )
                    Intens = (Intens - Intens.min()) / (Intens.max() - Intens.min())
                data_filtered["normalized_intensity"] = Intens
                data_filtered = data_filtered.sort_values(
                    by=["normalized_intensity"], ascending=True
                )
                if self.ui.set_intensity_KMD.text():
                    intens_KMD = float(self.ui.set_intensity_KMD.text())
                    data_filtered = data_filtered[
                        data_filtered.normalized_intensity >= intens_KMD
                    ]

                nominal_mass = round(data_filtered["m/z"])
                mass_defect = data_filtered["m/z"] - nominal_mass
                data_filtered["nominal_mass"] = nominal_mass
                data_filtered["mass_defect"] = mass_defect

                # -----------------------------------#
                #  Normalization on selected class  #
                # -----------------------------------#
                if self.ui.radioButton_norm_d.isChecked():
                    data_filtered["normalized_intensity"], error = Normalize(
                        data_filtered["normalized_intensity"]
                    )
                    if error == 1:
                        QMessageBox.about(
                            self,
                            "Error",
                            f"No species to be displayed for the class : {classe_selected}.",
                        )
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

                    if (
                        self.ui.stackedWidget_Kendrick.currentIndex() == 0
                    ):  # KMD classic
                        x_data = "Kendrick nominal mass"
                        y_data = "Kendrick mass defect"
                        x_label = "Kendrick nominal mass"
                        y_label = "Kendrick mass defect"

                        # -----------------------------------#
                        #  Color by intensity               #
                        # -----------------------------------#
                        if self.ui.K_intensity.isChecked():
                            frames["third_dimension"] = frames["normalized_intensity"]
                            c_label = "Normalized Intensity"

                        # -----------------------------------#
                        #  Color by oxygen                  #
                        # -----------------------------------#
                        if self.ui.K_oxygen.isChecked():
                            frames["third_dimension"] = frames["O"]
                            c_label = "Oxygen number"
                        # -----------------------------------#
                        #  Color by nitrogen                #
                        # -----------------------------------#
                        if self.ui.K_nitrogen.isChecked():
                            frames["third_dimension"] = frames["N"]
                            c_label = "Nitrogen number"

                        # -----------------------------------#
                        #  Color by sulfur                  #
                        # -----------------------------------#
                        if self.ui.K_sulfur.isChecked():
                            frames["third_dimension"] = frames["S"]
                            c_label = "Sulfur number"

                        # -----------------------------------#
                        #  Color by PC1                 #
                        # -----------------------------------#
                        if self.ui.K_PC1.isChecked():
                            frames["third_dimension"] = frames["PC1"]
                            c_label = "PC1"

                        # -----------------------------------#
                        #  Color by PC2                #
                        # -----------------------------------#
                        if self.ui.K_PC2.isChecked():
                            frames["third_dimension"] = frames["PC2"]
                            c_label = "PC2"

                    elif (
                        self.ui.stackedWidget_Kendrick.currentIndex() == 2
                    ):  # Mass defect VS Nominal mass
                        x_data = "nominal_mass"
                        y_data = "mass_defect"
                        x_label = "Nominal mass"
                        y_label = "Mass defect"

                        # -----------------------------------#
                        #  Color by intensity               #
                        # -----------------------------------#
                        if self.ui.K_intensity_univ.isChecked():
                            frames["third_dimension"] = frames["normalized_intensity"]
                            c_label = "Normalized Intensity"

                        # -----------------------------------#
                        #  Color by oxygen                  #
                        # -----------------------------------#
                        if self.ui.K_oxygen_univ.isChecked():
                            frames["third_dimension"] = frames["O"]
                            c_label = "Oxygen number"

                        # -----------------------------------#
                        #  Color by nitrogen                #
                        # -----------------------------------#
                        if self.ui.K_nitrogen_univ.isChecked():
                            frames["third_dimension"] = frames["N"]
                            c_label = "Nitrogen number"

                        # -----------------------------------#
                        #  Color by sulfur                  #
                        # -----------------------------------#
                        if self.ui.K_sulfur_univ.isChecked():
                            frames["third_dimension"] = frames["S"]
                            c_label = "Sulfur number"

                        # -----------------------------------#
                        #  Color by PC1                 #
                        # -----------------------------------#
                        if self.ui.K_PC1.isChecked():
                            frames["third_dimension"] = frames["PC1"]
                            c_label = "PC1"

                        # -----------------------------------#
                        #  Color by PC2                #
                        # -----------------------------------#
                        if self.ui.K_PC2.isChecked():
                            frames["third_dimension"] = frames["PC2"]
                            c_label = "PC2"

                    frames.sort_values(
                        by=["normalized_intensity", "third_dimension"],
                        ascending=[True, True],
                        inplace=True,
                    )

                    plot_fun(
                        "scatter",
                        x=frames[x_data],
                        y=frames[y_data],
                        d_color=frames["third_dimension"],
                        size=1.5 * dot_size * frames["normalized_intensity"],
                        dot_type=self.dot_type,
                        edge=self.edge,
                        cmap=self.color_map,
                    )

                    if self.ui.KNM_min.text():
                        KNM_min = float(self.ui.KNM_min.text())
                        plt.gca().set_xlim(left=KNM_min)
                    if self.ui.KNM_max.text():
                        KNM_max = float(self.ui.KNM_max.text())
                        plt.gca().set_xlim(right=KNM_max)
                    if self.ui.KMD_min.text():
                        KMD_min = float(self.ui.KMD_min.text())
                        plt.gca().set_ylim(bottom=KMD_min)
                    if self.ui.KMD_max.text():
                        KMD_max = float(self.ui.KMD_max.text())
                        plt.gca().set_ylim(top=KMD_max)
                    cbar = plt.colorbar()
                    cbar.ax.tick_params(labelsize=font_size - 2)
                    cbar.set_label(
                        c_label,
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )

                    plt.suptitle(
                        f"{y_label} vs {x_label}",
                        fontsize=font_size + 4,
                        y=0.96,
                        x=0.45,
                    )
                    plt.xlabel(x_label, fontsize=font_size + 4)
                    plt.ylabel(y_label, fontsize=font_size + 4)
                    if "molecular_formula" in frames:
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                frames["molecular_formula"].iloc[sel.target.index]
                            ),
                        )
                    else:
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                frames["m/z"].iloc[sel.target.index]
                            ),
                        )
                    plt.xticks(fontsize=font_size)
                    plt.yticks(fontsize=font_size)
                    plt.text(
                        0.12,
                        0.9,
                        f"{frames.classe_selected}",
                        horizontalalignment="left",
                        verticalalignment="center",
                        transform=transf,
                        fontsize=font_size + 2,
                    )
                    if gif == False:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(
                            self.pos().x() + 940, self.pos().y() + 200, 640, 545
                        )

            if gif == False:
                for i in frames:
                    Anim(i)
                plt.show()
            else:
                Figure = plt.figure()
                plt.show()
                anim_created = FuncAnimation(
                    Figure, Anim, frames, interval=1000 / self.fps
                )
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(
                    self.pos().x() + 940, self.pos().y() + 200, 640, 545
                )
                writergif = PillowWriter(fps=self.fps)
                anim_created.save("animation.gif", writer=writergif)
                plt.ion()
            return data_filtered

    def deformulation(self, gif=False):

        ###Load the csv containing the info and KMD values to identify
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            caption="Choose the file containing the info about the species to identify",
            filter="Results files (*.csv)",
        )
        if not filepath:
            return
        path_old = os.getcwd()
        def_info = pandas.read_csv(filepath, delimiter=(";"))
        if len(def_info.columns) != 2:
            def_info = pandas.read_csv(filepath, delimiter=(","))
            if len(def_info.columns) != 2:
                QMessageBox.about(
                    self, "Error box", "Input file doesn't have the required format."
                )
        ###

        ###Load data and read GUI parameters
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        data_filtered = data_selected.df
        if data_selected.df_type == "PyC2MC_merged":
            data_filtered = data_filtered.rename(
                columns={"summed_intensity": "normalized_intensity"}
            )
        data_filtered = data_filtered.sort_values(
            by=["normalized_intensity"], ascending=True
        )
        if self.ui.checkBox_int_filter_extract.isChecked():
            intens_KMD = float(self.ui.set_intensity_KMD.text())
            data_filtered = data_filtered[
                data_filtered.normalized_intensity >= intens_KMD
            ]
        self.read_param()
        dot_size = self.d_size
        font_size = self.fontsize
        tol_per = float(self.ui.Extract_tol.text())
        if self.ui.edit_mass_motif.text():
            repetive_unit_mass = float(self.ui.edit_mass_motif.text())
            nominal_unit = round(repetive_unit_mass)

        if "mz" in data_filtered:
            data_filtered["Kendrick mass"] = data_filtered["mz"] * (
                nominal_unit / repetive_unit_mass
            )
        elif "count" in data_filtered:
            data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                nominal_unit / repetive_unit_mass
            )
        elif "m/z" in data_filtered:
            data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                nominal_unit / repetive_unit_mass
            )

        if self.ui.roundUp.isChecked():
            data_filtered["Kendrick nominal mass"] = data_filtered[
                "Kendrick mass"
            ].apply(np.ceil)
        elif self.ui.roundClosest.isChecked():
            data_filtered["Kendrick nominal mass"] = round(
                data_filtered["Kendrick mass"]
            )

        data_filtered["Kendrick mass defect"] = (
            data_filtered["Kendrick nominal mass"] - data_filtered["Kendrick mass"]
        )
        ###

        ###Attribution
        data_filtered["id"] = 0  # Colors for species of interest

        self.kendrickSeries = pandas.DataFrame()
        list_kmd = def_info.iloc[:, 1].to_list()
        list_cmpd = def_info.iloc[:, 0].to_list()
        n_series = len(list_kmd)

        if n_series == 0:
            QMessageBox.about(self, "FYI box", "No species to look for ...")
            return

        list_series_index = [*range(n_series)]
        list_color = color_list[-9:] * (1 + n_series // 8)
        list_color = list_color[:n_series]

        matching_series = []
        for j in list_series_index:

            kmd_defo = list_kmd[j]
            tol = abs(kmd_defo) * tol_per / 100  # tolerance attribution
            l = 0  # row number of matching specie
            lst = []

            data_filtered.sort_values("m/z", ascending=True, inplace=True)
            data_filtered = data_filtered.reset_index(drop=True)
            for kmd_exp in data_filtered["Kendrick mass defect"]:
                if kmd_exp >= kmd_defo - tol and kmd_exp <= kmd_defo + tol:
                    lst.append(data_filtered["m/z"][l])
                    data_filtered.at[l, "id"] = (
                        j + 1
                    )  # increment id columns to register that this specie was found when looking for the jth KMD
                    if j not in matching_series:
                        matching_series.append(
                            j
                        )  # add the serie's index to a list in case of a match
                l = l + 1
        ###

        ###Plot
        d = {
            "col1": data_filtered["Kendrick nominal mass"],
            "col2": data_filtered["Kendrick mass defect"],
            "normalized_intensity": data_filtered["normalized_intensity"],
            "id": data_filtered["id"],
            "m/z": data_filtered["m/z"],
        }
        df = pandas.DataFrame(data=d)
        df = df.sort_values("normalized_intensity", ascending=True)
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        fig = plt.figure()
        if self.ui.checkBox_extract_only.isChecked() == False:
            plt.scatter(
                df["col1"],
                df["col2"],
                color=[0, 0, 0, 0.1],
                s=df["normalized_intensity"] * dot_size / 100,
            )
        for k in list_series_index:
            d_series = data_filtered[data_filtered["id"] == k + 1]
            plt.scatter(
                d_series["Kendrick nominal mass"],
                d_series["Kendrick mass defect"],
                color=list_color[k],
                s=(d_series["normalized_intensity"]) * dot_size / 100,
                edgecolors="black",
            )

        plt.clim(0, n_series)
        if self.ui.KNM_min.text():
            KNM_min = float(self.ui.KNM_min.text())
            plt.gca().set_xlim(left=KNM_min)
        if self.ui.KNM_max.text():
            KNM_max = float(self.ui.KNM_max.text())
            plt.gca().set_xlim(right=KNM_max)
        if self.ui.KMD_min.text():
            KMD_min = float(self.ui.KMD_min.text())
            plt.gca().set_ylim(bottom=KMD_min)
        if self.ui.KMD_max.text():
            KMD_max = float(self.ui.KMD_max.text())
            plt.gca().set_ylim(top=KMD_max)
        plt.xlabel("Kendrick nominal mass")
        plt.ylabel("Kendrick mass defect")
        temp_leg = list_cmpd.copy()
        leg = [temp_leg[i] for i in matching_series]
        if self.ui.checkBox_extract_only.isChecked() == False:
            leg.insert(0, "Background")
        plt.gca().legend(leg, fontsize=font_size - 4)

        mplcursors.cursor(
            multiple=True
        )  # .connect("add", lambda sel: sel.annotation.set_text(target))
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x() + 940, self.pos().y() + 200, 640, 545)
        plt.show()
        ###
        ###Prepare data for saving
        series = data_filtered[data_filtered["id"] != 0]
        total_int = data_filtered["normalized_intensity"].sum()
        deform_results = pandas.DataFrame(
            columns=["Group", "m/z ratio", "Rel. intensity (%)"]
        )
        for i in range(n_series):
            cmpd_id = list_cmpd[i]
            cmpd_mz = (data_filtered["m/z"][data_filtered["id"] == i + 1]).to_list()
            cmpd_int = (
                data_filtered["normalized_intensity"][data_filtered["id"] == i + 1]
            ).sum()
            cmpd_int = cmpd_int * 100 / total_int
            temp = pandas.DataFrame(
                {
                    "Group": cmpd_id,
                    "m/z ratio": [cmpd_mz],
                    "Rel. intensity (%)": cmpd_int,
                }
            )
            deform_results = pandas.concat([deform_results, temp])
        self.deformulation_results = deform_results
        return

    def save_deformulation(self):
        ###Export as csv
        save = QMessageBox.question(
            self,
            "Message",
            "Do you want to save the results in a .csv file ?",
            QMessageBox.Yes,
            QMessageBox.No,
        )
        if save == QMessageBox.Yes:
            save_path = QtWidgets.QFileDialog.getExistingDirectory()
            save_name, okPressed = QInputDialog.getText(
                self, "Save Name", "Your name:", QLineEdit.Normal, ""
            )
            if save_name != "" and save_path != "":
                self.write_csv_df(
                    save_path, save_name + ".csv", self.deformulation_results
                )
            else:
                QMessageBox.about(
                    self,
                    "Error box",
                    "Either the save path or the  file name is missing.",
                )
                return
        else:
            return

    def clear_series(self):
        """
        Clears m/z values in the KMD extraction panel
        """

        list_series = [
            self.ui.series_1,
            self.ui.series_2,
            self.ui.series_3,
            self.ui.series_4,
            self.ui.series_5,
            self.ui.series_6,
            self.ui.series_7,
            self.ui.series_8,
            self.ui.series_9,
            self.ui.series_10,
        ]
        for n in range(10):
            list_series[n].setText("")

    def save_kendrick_series(self):
        """
        Save the extracted series in a .csv file
        """

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        save_name, okPressed = QInputDialog.getText(
            self, "Save Name", "Your name:", QLineEdit.Normal, ""
        )
        if save_name != "" and save_path != "":
            # os.chdir(save_path)
            # self.kendrickSeries.to_csv(save_name +".csv",index = False)
            self.write_csv_df(save_path, save_name + ".csv", self.kendrickSeries)

        else:
            QMessageBox.about(
                self, "Error box", "Either the save path or the  file name is missing."
            )
            return

    def envt_selector(self, gif=False):
        """
        Selects the appropriate environmental variable to plot
        """
        self.read_param()
        if self.ui.radio_ACOS.isChecked():
            self.plot_ACOS(gif)
        elif self.ui.radio_MAI.isChecked():
            self.plot_MAI(gif)
        elif self.ui.radio_MCR.isChecked():
            self.plot_MCR(gif)

    def plot_ACOS(self, gif):
        """
        Average carbon oxydation plot
        """
        frames = []
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        item_classes = self.ui.list_classes_ACOS.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)
            nc = self.ui.nc_box.isChecked()

            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            if self.ui.radio_color_intensity_ACOS.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
                intens_for_size = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc1_ACOS.isChecked():
                third_dimension = data_extract["PC1"]
                third_dimension = third_dimension + 1
                intens_for_size = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc2_ACOS.isChecked():
                third_dimension = data_extract["PC2"]
                third_dimension = third_dimension + 1
                intens_for_size = data_extract["Normalized_intensity"]
            Intens = third_dimension.values.reshape(-1, 1)

            if self.ui.check_classic_ACOS.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_ACOS.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_ACOS.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )
            data_extract = Select_classe(
                classe_selected,
                data_selected.df,
                data_selected.heteroatoms,
                data_selected.classes,
            )
            data_extract["point_size"] = intens_for_size

            if nc == True:
                data_extract["OSc"] = (
                    2 * data_extract["O/C"]
                    - data_extract["H/C"]
                    - 5 * data_extract["N/C"]
                )
            else:
                data_extract["OSc"] = 2 * data_extract["O/C"] - data_extract["H/C"]

            # -----------------------------------#
            #  Normalization                    #
            # -----------------------------------#

            if (
                self.ui.radioButton_norm_c.isChecked()
                or self.ui.radioButton_norm_d.isChecked()
            ):
                intens = data_extract["Normalized_intensity"].copy()
                intens = intens.values.reshape(-1, 1)
                size = data_extract["point_size"].copy()
                size = size.values.reshape(-1, 1)
                if intens.shape[0] > 1:
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(intens)
                    Size_scaled = min_max_scaler.fit_transform(size)
                    data_extract["Normalized_intensity"] = Intens_scaled
                    data_extract["point_size"] = Size_scaled
                    data_extract = data_extract.sort_values(
                        by=["Normalized_intensity"], ascending=True
                    )
                elif intens.shape[0] == 1:
                    data_extract["Normalized_intensity"] = 1
                    data_extract["point_size"] = 1
                else:
                    QMessageBox.about(self, "Error", "No species to be displayed.")
                    continue

            # -----------------------------------------#
            #  Normalization (end)                    #
            # -----------------------------------------#
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
                plot_fun(
                    "scatter",
                    x=frames["C"],
                    y=frames["OSc"],
                    d_color=frames["Normalized_intensity"],
                    size=self.d_size * frames["point_size"],
                    dot_type=self.dot_type,
                    edge=self.edge,
                    cmap=self.color_map,
                )
                plt.xlabel("#C", fontsize=self.fontsize + 4)
                plt.ylabel("OSc", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)

                plt.gca().invert_xaxis()
                if self.ui.x_min_ACOS.text():
                    C_min = float(self.ui.x_min_ACOS.text())
                    plt.gca().set_xlim(right=C_min)
                if self.ui.x_max_ACOS.text():
                    C_max = float(self.ui.x_max_ACOS.text())
                    plt.gca().set_xlim(left=C_max)
                plt.text(
                    0.12,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_ACOS.text():
                    ACOS_min = float(self.ui.y_min_ACOS.text())
                    plt.gca().set_ylim(bottom=ACOS_min)
                if self.ui.y_max_ACOS.text():
                    ACOS_max = float(self.ui.y_max_ACOS.text())
                    plt.gca().set_ylim(top=ACOS_max)
                plt.suptitle(
                    "Average carbon oxidation state vs #C",
                    fontsize=font_size + 4,
                    y=0.97,
                    x=0.45,
                )
                cbar = plt.colorbar()
                cbar.set_label(
                    "Normalized Intensity",
                    labelpad=-2.625 * (font_size),
                    rotation=90,
                    fontsize=font_size,
                    color=self.cm_text_color,
                )
                cbar.ax.tick_params(labelsize=font_size - 2)
                if (
                    self.ui.radioButton_norm_c.isChecked()
                    or self.ui.radioButton_norm_d.isChecked()
                ):
                    plt.clim(0, 1)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 1000, 437
                    )
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            frames["molecular_formula"].iloc[sel.target.index]
                            + ", #C = "
                            + str(frames["C"].iloc[sel.target.index])
                            + ", OCs = "
                            + str(round(frames["OSc"].iloc[sel.target.index], 2))
                        ),
                    )

        if gif == False:
            for i in frames:
                Anim(i)
                plt.tight_layout()
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()

            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 1000, 437
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()
            plt.tight_layout()

    def plot_MAI(self, gif):
        """
        Plot a Van Krevelen diagram with the modified aromaticity index as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        item_classes = self.ui.list_classes_MAI.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)

            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)

            if self.ui.check_classic_MAI.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_MAI.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_MAI.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = Select_classe(
                classe_selected,
                data_selected.df,
                data_selected.heteroatoms,
                data_selected.classes,
            )
            if not "S" in data_extract:
                data_extract["S"] = 0
            if not "P" in data_extract:
                data_extract["P"] = 0
            if self.ui.MAI_box.isChecked():
                data_extract["AI"] = (
                    1
                    + data_extract["C"]
                    - 0.5 * data_extract["O"]
                    - data_extract["S"]
                    - 0.5 * (data_extract["N"] + data_extract["P"] + data_extract["H"])
                ) / (
                    data_extract["C"]
                    - 0.5 * data_extract["O"]
                    - data_extract["S"]
                    - data_extract["N"]
                    - data_extract["P"]
                )
            else:
                data_extract["AI"] = (
                    1
                    + data_extract["C"]
                    - data_extract["O"]
                    - data_extract["S"]
                    - 0.5 * (data_extract["N"] + data_extract["P"] + data_extract["H"])
                ) / (
                    data_extract["C"]
                    - data_extract["O"]
                    - data_extract["S"]
                    - data_extract["N"]
                    - data_extract["P"]
                )
            data_extract["AI"][data_extract["AI"] < 0] = 0
            data_extract["AI"][data_extract["AI"] > 1] = 1

            cond_1 = pandas.Series(data_extract["AI"] <= 0.5) * pandas.Series(
                data_extract["AI"] >= 0
            )
            cond_2 = pandas.Series(data_extract["AI"] <= 0.67) * pandas.Series(
                data_extract["AI"] > 0.5
            )
            cond_3 = pandas.Series(data_extract["AI"] <= 1) * pandas.Series(
                data_extract["AI"] > 0.67
            )

            # -----------------------------------#
            #  Normalization                    #
            # -----------------------------------#

            if (
                self.ui.radioButton_norm_c.isChecked()
                or self.ui.radioButton_norm_d.isChecked()
            ):
                data_extract["Normalized_intensity"], error = Normalize(
                    data_extract["Normalized_intensity"]
                )
                if error == 1:
                    QMessageBox.about(
                        self,
                        "Error",
                        f"No species to be displayed for the class : {classe_selected}.",
                    )
                    continue

            # -----------------------------------------#
            #  Normalization (end)                    #
            # -----------------------------------------#

            data_extract.classe_selected = classe_selected
            data_extract.cond_1 = cond_1.values
            data_extract.cond_2 = cond_2.values
            data_extract.cond_3 = cond_3.values
            frames.append(data_extract)
            self.read_param()
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )

            def Anim(frames):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure

                d1 = frames[frames.cond_1]
                d2 = frames[frames.cond_2]
                d3 = frames[frames.cond_3]
                ax1 = plt.scatter(
                    d1["O/C"],
                    d1["H/C"],
                    c="#06a96a",
                    s=self.d_size * d1["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                ax2 = plt.scatter(
                    d2["O/C"],
                    d2["H/C"],
                    c="#f39c1b",
                    s=self.d_size * d2["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                ax3 = plt.scatter(
                    d3["O/C"],
                    d3["H/C"],
                    c="#de281b",
                    s=self.d_size * d3["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                plt.xlabel("O/C", fontsize=self.fontsize + 4)
                plt.ylabel("H/C", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)

                if self.ui.x_min_MAI.text():
                    C_min = float(self.ui.x_min_MAI.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_MAI.text():
                    C_max = float(self.ui.x_max_MAI.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(
                    0.12,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_MAI.text():
                    MAI_min = float(self.ui.y_min_MAI.text())
                    plt.gca().set_ylim(bottom=MAI_min)
                if self.ui.y_max_MAI.text():
                    MAI_max = float(self.ui.y_max_MAI.text())
                    plt.gca().set_ylim(top=MAI_max)
                plt.suptitle(
                    "Van Krevelen diagram", fontsize=font_size + 4, y=0.97, x=0.45
                )

                cmap = matplotlib.colors.ListedColormap(
                    ["#06a96a", "#f39c1b", "#de281b"]
                )
                bounds = [0, 0.5, 0.67, 1]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar = plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing="proportional",
                    orientation="vertical",
                )
                cbar.set_label(
                    "Aromaticity Index",
                    labelpad=-3.3 * (font_size),
                    rotation=90,
                    fontsize=font_size,
                    color="white",
                )
                cbar.ax.tick_params(labelsize=font_size - 2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
                    )

                if "m/z" in frames:
                    mplcursors.cursor(ax1, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d1["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d1["O/C"].iloc[sel.target.index].round(3))
                            + ", (M)AI = "
                            + str(d1["AI"].iloc[sel.target.index].round(3))
                        ),
                    )
                    mplcursors.cursor(ax2, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d2["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d2["O/C"].iloc[sel.target.index].round(3))
                            + ", (M)AI = "
                            + str(d2["AI"].iloc[sel.target.index].round(3))
                        ),
                    )
                    mplcursors.cursor(ax3, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d3["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d3["O/C"].iloc[sel.target.index].round(3))
                            + ", (M)AI = "
                            + str(d3["AI"].iloc[sel.target.index].round(3))
                        ),
                    )

        if gif == False:
            for i in frames:
                Anim(i)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_MCR(self, gif):
        """
        Plot a Van Krevelen diagram with the maximum carbonyl ratio as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        item_classes = self.ui.list_classes_MCR.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = data_selected.df.copy()
            classe_selected = item.data(self.USERDATA_ROLE)

            if not "S" in data_extract:
                data_extract["S"] = 0
            if not "P" in data_extract:
                data_extract["P"] = 0

            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)

            if self.ui.check_classic_MCR.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_MCR.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_MCR.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )
            data_extract = Select_classe(
                classe_selected,
                data_selected.df,
                data_selected.heteroatoms,
                data_selected.classes,
            )
            data_extract["MCR"] = data_extract["DBE"] / data_extract["O"]
            data_extract["MCR"][data_extract["MCR"] < 0] = 0
            data_extract["MCR"][data_extract["MCR"] > 1] = 1

            cond_1 = pandas.Series(data_extract["MCR"] <= 0.2) * pandas.Series(
                data_extract["MCR"] >= 0
            )
            cond_2 = pandas.Series(data_extract["MCR"] <= 0.5) * pandas.Series(
                data_extract["MCR"] > 0.2
            )
            cond_3 = pandas.Series(data_extract["MCR"] <= 0.9) * pandas.Series(
                data_extract["MCR"] > 0.5
            )
            cond_4 = pandas.Series(data_extract["MCR"] <= 1) * pandas.Series(
                data_extract["MCR"] > 0.9
            )

            # -----------------------------------#
            #  Normalization                    #
            # -----------------------------------#

            if (
                self.ui.radioButton_norm_c.isChecked()
                or self.ui.radioButton_norm_d.isChecked()
            ):
                data_extract["Normalized_intensity"], error = Normalize(
                    data_extract["Normalized_intensity"]
                )
                if error == 1:
                    QMessageBox.about(
                        self,
                        "Error",
                        f"No species to be displayed for the class : {classe_selected}.",
                    )
                    continue

            # -----------------------------------------#
            #  Normalization (end)                    #
            # -----------------------------------------#

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

                d1 = frames[frames.cond_1]
                d2 = frames[frames.cond_2]
                d3 = frames[frames.cond_3]
                d4 = frames[frames.cond_4]
                ax1 = plt.scatter(
                    d1["O/C"],
                    d1["H/C"],
                    c="#de281b",
                    s=self.d_size * d1["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                ax2 = plt.scatter(
                    d2["O/C"],
                    d2["H/C"],
                    c="#f39c1b",
                    s=self.d_size * d2["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                ax3 = plt.scatter(
                    d3["O/C"],
                    d3["H/C"],
                    c="#06a96a",
                    s=self.d_size * d3["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                ax4 = plt.scatter(
                    d4["O/C"],
                    d4["H/C"],
                    c="#0f5fa8",
                    s=self.d_size * d4["Normalized_intensity"],
                    linewidths=0.7,
                    edgecolors="black",
                    alpha=0.7,
                )
                plt.xlabel("O/C", fontsize=self.fontsize + 4)
                plt.ylabel("H/C", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)

                if self.ui.x_min_MCR.text():
                    C_min = float(self.ui.x_min_MCR.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_MCR.text():
                    C_max = float(self.ui.x_max_MCR.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(
                    0.12,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_MCR.text():
                    MCR_min = float(self.ui.y_min_MCR.text())
                    plt.gca().set_ylim(bottom=MCR_min)
                if self.ui.y_max_MCR.text():
                    MCR_max = float(self.ui.y_max_MCR.text())
                    plt.gca().set_ylim(top=MCR_max)
                plt.suptitle(
                    "Van Krevelen diagram", fontsize=font_size + 4, y=0.97, x=0.45
                )
                cmap = matplotlib.colors.ListedColormap(
                    ["#de281b", "#f39c1b", "#06a96a", "#0f5fa8"]
                )
                bounds = [0, 0.2, 0.5, 0.9, 1]
                norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
                cbar = plt.colorbar(
                    matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm),
                    boundaries=bounds,
                    ticks=bounds,
                    spacing="proportional",
                    orientation="vertical",
                )
                cbar.set_label(
                    "Maximum carbonyl ratio",
                    labelpad=-2.625 * (font_size),
                    rotation=90,
                    fontsize=font_size,
                    color="white",
                )
                cbar.ax.tick_params(labelsize=font_size - 2)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
                    )

                if "m/z" in frames:
                    mplcursors.cursor(ax1, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d1["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d1["O/C"].iloc[sel.target.index].round(3))
                            + ", MCR = "
                            + str(d1["MCR"].iloc[sel.target.index].round(3))
                        ),
                    )
                    mplcursors.cursor(ax2, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d2["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d2["O/C"].iloc[sel.target.index].round(3))
                            + ", MCR = "
                            + str(d2["MCR"].iloc[sel.target.index].round(3))
                        ),
                    )
                    mplcursors.cursor(ax3, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d3["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d3["O/C"].iloc[sel.target.index].round(3))
                            + ", MCR = "
                            + str(d3["MCR"].iloc[sel.target.index].round(3))
                        ),
                    )
                    mplcursors.cursor(ax4, multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            d4["molecular_formula"].iloc[sel.target.index]
                            + ", O/C = "
                            + str(d4["O/C"].iloc[sel.target.index].round(3))
                            + ", MCR = "
                            + str(d4["MCR"].iloc[sel.target.index].round(3))
                        ),
                    )

        if gif == False:
            for i in frames:
                Anim(i)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def venn(self):
        """
        Group molecular formula (or m/z ratio) to plot a Venn diagram.
        Groups are called sets.
        """

        # Select display mode
        if self.ui.radio_count.isChecked():
            disp = "{size}"
        elif self.ui.radio_percentage.isChecked():
            disp = "{percentage:.1f} %"
        # Select colormap
        color_map = self.ui.color.text()

        self.ui.list_sets.clear()
        # Loads and store data in "data_selected" :
        item = self.ui.list_loaded_file_2.selectedItems()
        item = item[0]
        if not item:
            return
        df = pandas.DataFrame()
        data_selected = item.data(self.USERDATA_ROLE)
        data_selected = data_selected.df
        inde = pandas.Series(data_selected["m/z"])
        data_venn = data_selected.set_index("m/z")
        filename = item.text().split(".")  # Determines set's name ("xxx.csv" -> "xxx")
        n_heteroatoms = data_venn.columns.get_loc("count")
        n_ech = data_venn["count"].max()  # n file= max(count)
        if n_ech < 2 or n_ech > 6:
            QMessageBox.about(
                self, "FYI box", "Number of samples to compare must be between 2 and 6"
            )
            return
        for i in range(n_ech):
            df[i] = inde
        df = df.set_index(df[0])
        data_venn = data_venn.iloc[
            :, n_heteroatoms + 1 : n_heteroatoms + 1 + n_ech
        ]  # extracts intensity values

        # -----------------------------------------------------------------------------------
        # Creates a dataframe of the same dimensions as data_venn but filled with m/z
        # Mandatory since df.where was changed since last pandas version
        # -----------------------------------------------------------------------------------

        index_values = pandas.DataFrame(
            {"a": data_venn.index.values}, index=data_venn.index.values
        )
        index_df = index_values.copy()
        index_df.set_index("a", inplace=True)
        for i in range(data_venn.shape[1]):
            index_df = pandas.concat([index_df, index_values], axis=1)

        # -------
        # End
        # -------

        data_venn = data_venn.where(
            data_venn.eq(0), index_df.values
        )  # Replaces non-null values by their corresponding index
        dict_venn = {}

        for columnName, columnData in data_venn.iteritems():
            dict_venn[columnName] = set(columnData)

        venn_diag(
            dict_venn, fmt=disp, cmap=color_map
        ).figure.show()  # Plots using Venn.py (fonction venn_diag)
        sets = venn_sets(
            dict_venn
        )  # EXctractiong and storage of data using Venn.py (fonction venn_sets)

        logic = []
        for i in range(1, 2**n_ech):
            logic.append(bin(i)[2:].zfill(n_ech))

        for b in logic:
            self.ui.list_sets.addItem(str(b))
        plt.show
        plt.tight_layout()
        # Variables globalization
        self.sets_all = sets
        self.sets_names = logic
        self.data_complete = data_selected
        self.ui.Save_Sets_Button.setEnabled(True)

    def select_set_venn(self):
        """
        Display values for the selected set
        """

        item_selected = self.ui.list_sets.currentItem().text()
        data_se = self.data_complete
        data_se = data_se.loc[data_se["m/z"].isin(self.sets_all[item_selected])]
        data_se = data_se["m/z"].sort_values(ascending=True)

        self.ui.set_content.setColumnCount(1)
        self.ui.set_content.setRowCount(len(data_se))
        x = 0
        for i in data_se.index:
            self.ui.set_content.setItem(x, 0, QTableWidgetItem(str(data_se[i])))
            x = x + 1

    def save_sets_venn(self):
        """
        Saves sets under a .xlsx file
        """

        # Progress bar#
        self.ui.pbar.setMaximum(len(self.sets_names))
        value_pb_1 = 0
        self.ui.pbar.setValue(value_pb_1)
        # \Progress bar#

        path = QtWidgets.QFileDialog.getExistingDirectory()
        if path == "":
            return
        filename, okPressed = QInputDialog.getText(
            self, "Save Name", "Your name:", QLineEdit.Normal, ""
        )
        if filename == "":
            return
        os.chdir(path)
        filename = filename + ".xlsx"
        data = self.data_complete

        for columnName, content in data.iteritems():  # drops columns Nx Ox Sx etc ..
            if len(columnName) == 2 and "x" in columnName:
                data = data.drop(columnName, axis=1)
        with pandas.ExcelWriter(filename) as writer:
            for s in self.sets_names:
                df = data.loc[data["m/z"].isin(self.sets_all[s])]
                df.set_index("m/z", inplace=True)
                df.sort_index(ascending=True, inplace=True)
                names_dict = {"m/z": "calc. m/z"}
                df = df.rename(columns=names_dict)
                df.to_excel(writer, sheet_name=str(s))
                # Progress Bar#
                value_pb_1 = value_pb_1 + 1
                self.ui.pbar.setValue(value_pb_1)
                # \Progress bar#
                self.ui.pbar.hide()
        QMessageBox.about(self, "FYI box", "Your file was correctly saved.")

    def plot_composition_compare(self):
        """
        Composition plots for the compare menu (Chemical family)
        """
        self.read_param()
        font_size = self.fontsize
        try:
            self.compared_datas
        except:
            QMessageBox.about(self, "FYI box", "Please select several data files.")
            return
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        if self.ui.font_size.text():
            font_size = float(self.ui.font_size.text())
        fig, ax = plt.subplots()
        if self.ui.radio_classes_compare.isChecked():
            if self.ui.edit_min_intensity_classes_compare.text():
                min_intens_classes = float(
                    self.ui.edit_min_intensity_classes_compare.text()
                )
                classes = self.compared_datas.classes[
                    ~self.compared_datas.classes["variable"].str.contains("x")
                ]
                classes = classes[classes["value"] > min_intens_classes]
            else:
                classes = self.compared_datas.classes[
                    ~self.compared_datas.classes["variable"].str.contains("x")
                ]
        else:
            if self.ui.edit_min_intensity_classes_compare.text():
                min_intens_classes = float(
                    self.ui.edit_min_intensity_classes_compare.text()
                )
                classes = self.compared_datas.classes[
                    self.compared_datas.classes["variable"].str.contains("x")
                ]
                ch = self.compared_datas.classes[
                    self.compared_datas.classes["variable"].str.contains("CH")
                ]
                classes = classes.append(ch)
                classes = classes[classes["value"] > min_intens_classes]
            else:
                classes = self.compared_datas.classes[
                    self.compared_datas.classes["variable"].str.contains("x")
                ]
                ch = self.compared_datas.classes[
                    self.compared_datas.classes["variable"].str.contains("CH")
                ]
                classes = classes.append(ch)
        classes = classes.sort_values("value", ascending=False)
        classes = classes.reset_index(drop=True)
        if self.ui.radio_classes_grouped.isChecked():
            capsize = 5
            if self.ui.radio_comp_int_compare.isChecked():
                ax.bar(
                    classes["variable"],
                    classes["value"],
                    yerr=classes["std_dev_rel"],
                    align="center",
                    ecolor="black",
                    capsize=capsize,
                )
                plt.ylabel("Relative intensity (%)", fontsize=font_size + 2)
            elif self.ui.radio_comp_nb_compare.isChecked():
                ax.bar(classes["variable"], classes["number"])
                plt.ylabel("Number of attribution", fontsize=font_size + 2)
            plt.suptitle("Heteroatom class distribution", fontsize=font_size + 2)
            plt.xticks(fontsize=font_size, rotation=45)
            plt.yticks(fontsize=font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            plt.show()
        elif self.ui.radio_one_by_one.isChecked():
            capsize = 5
            leg = list(classes.variable.values)
            wid = float(self.ui.compo_compare_width.text())
            gap = float(self.ui.compo_compare_gap.text())
            y_max = int(len(classes.per_datas[0]))

            data_comp = pandas.DataFrame(
                columns=range(len(leg)), index=self.name.values()
            )
            leg_raw = self.name.values()
            leg_2 = []
            for name in leg_raw:
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                leg_2.append(name)

            if self.ui.radio_comp_int_compare.isChecked():
                for y in range(y_max):
                    for i in range(len(leg)):
                        data_comp.iloc[y, i] = classes.per_datas[i][y]
                plt.ylabel("Relative intensity (%)", fontsize=font_size + 2)

            elif self.ui.radio_comp_nb_compare.isChecked():
                for y in range(y_max):
                    for i in range(len(leg)):
                        data_comp.iloc[y, i] = classes.per_datas_nb[i][y]
                data_comp = data_comp.div(data_comp.sum(axis=1), axis=0) * 100
                plt.ylabel("Number of attribution (%)", fontsize=font_size + 2)

            for y in range(y_max):
                ab = np.array(data_comp.columns) - gap * (
                    0.5 - ((y + 1) / (y_max + 1))
                ) / (y_max + 1)
                plt.bar(
                    ab,
                    data_comp.iloc[y, :],
                    width=(0.14 * wid) / (y_max + 1),
                    color=color_list[y % 9],
                )
            plt.gca().legend(leg, fontsize=font_size - 4)

            ax.set_xticks(range(len(leg)))
            ax.set_xticklabels(leg)
            cursor = mplcursors.cursor(multiple=True)

            @cursor.connect("add")
            def on_add(sel):
                x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
                if self.ui.radio_comp_int_compare.isChecked():
                    txt = "Rel.Int."
                else:
                    txt = "Number of attributions"
                sel.annotation.set(
                    text=f"{txt} : {round(height,4)}%",
                    position=(0, 20),
                    anncoords="offset points",
                )
                sel.annotation.xy = (x + width / 2, y + height)

            plt.gca().legend(leg_2, fontsize=font_size - 4)
            plt.suptitle("Heteroatom class distribution", fontsize=font_size + 2)
            plt.xticks(fontsize=font_size, rotation=45)
            plt.yticks(fontsize=font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            plt.show()

    def plot_distrib_compare(self, gif=False):
        """
        Distribution plots for the compare menu
        """

        self.read_param()
        font_size = self.fontsize
        frames = []
        item_classes = self.ui.list_classes_distrib_compare.selectedItems()
        if not item_classes:
            return
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        if self.ui.radio_dist_int_comp.isChecked():
            y_label = "Relative Intensity %"
            y_legend = "Rel. Intens"
        else:
            y_label = "Number of attributions %"
            y_legend = "Number of attributions"
        for classe_selected in item_classes:
            classe_selected = classe_selected.data(self.USERDATA_ROLE)
            data = Select_classe(
                classe_selected,
                self.compared_datas.df,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            if len(data) == 0:
                QMessageBox.about(
                    self, "FYI box", f"Nothing to display for {classe_selected} class."
                )
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

                x_axes = self.ui.list_distribution_compare.currentRow()
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                plt.ylabel(f"{y_label}", fontsize=font_size + 2)
                x_axes = self.ui.list_distribution_compare.currentRow()
                nb_sample = (
                    int(
                        (
                            frames.columns.get_loc("Normalized_intensity")
                            - frames.columns.get_loc("count")
                        )
                        / 2
                    )
                    - 1
                )

                ###
                if x_axes == 0:  # DBE
                    dbe_both_m = pandas.DataFrame()
                    index_dbe_both_m = list()
                    dbe_odd_m = pandas.DataFrame()
                    dbe_even_m = pandas.DataFrame()
                    m = -0.5
                    while m < max(frames.DBE):
                        index_dbe_both_m.append(m)
                        m = m + 0.5
                    dbe_exp = frames.DBE
                    intens = frames.iloc[
                        :,
                        frames.columns.get_loc("count")
                        + nb_sample
                        + 1 : frames.columns.get_loc("count")
                        + nb_sample * 2
                        + 1,
                    ]  # stocke les intensités relatives des échantillons
                    df = pandas.concat([dbe_exp, intens], axis=1)
                    for y in index_dbe_both_m:
                        index_DBE_m = df.DBE == y
                        data_DBE_m = df[index_DBE_m].astype(float)
                        dbe_sum_m = pandas.DataFrame()
                        for i in range(nb_sample):
                            intensity_DBE_m = sum(data_DBE_m.iloc[:, 1 + i])
                            count_DBE_m = np.count_nonzero(data_DBE_m.iloc[:, 1 + i])
                            if self.ui.radio_dist_int_comp.isChecked():
                                dbe_sum_m[i] = [intensity_DBE_m]
                            else:
                                dbe_sum_m[i] = [count_DBE_m]
                        dbe_both_m[y] = list(dbe_sum_m.values[0])
                        if y.is_integer():
                            dbe_odd_m[y] = list(dbe_sum_m.values[0])
                        else:
                            dbe_even_m[y] = list(dbe_sum_m.values[0])

                    dbe_both_m.index = list(
                        data_DBE_m.columns[1:]
                    )  # Remplace l'index par le nom de l'échantillon
                    dbe_odd_m.index = list(data_DBE_m.columns[1:])
                    dbe_even_m.index = list(data_DBE_m.columns[1:])
                    if self.ui.radio_even_DBE_compare.isChecked():
                        data_DBE_m = dbe_even_m
                        dbe_text = "Even ions"
                    elif self.ui.radio_odd_DBE_compare.isChecked():
                        data_DBE_m = dbe_odd_m
                        dbe_text = "Odd ions"
                    elif self.ui.radio_both_DBE_compare.isChecked():
                        data_DBE_m = dbe_both_m
                        dbe_text = "Both parity"
                    leg_raw = list(data_DBE_m.index.values)
                    leg = []
                    for name in leg_raw:
                        name = name.replace("Rel_intens_", "")
                        name = name.replace(".csv", "")
                        name = name.replace(".xlsx", "")
                        leg.append(name)

                    x_label = "DBE"
                    y_max = len(data_DBE_m)
                    to_plt = data_DBE_m

                elif x_axes == 1:  # C
                    dbe_text = "Even and odd ions"
                    C_both = pandas.DataFrame()
                    intens = frames.iloc[
                        :,
                        frames.columns.get_loc("count")
                        + nb_sample
                        + 1 : frames.columns.get_loc("count")
                        + nb_sample * 2
                        + 1,
                    ]  # stocke les intensités relatives des échantillons
                    if "C" in frames:
                        all_C = frames.C.drop_duplicates()
                        df = pandas.concat([frames.C, intens], axis=1)
                        for y in all_C:
                            index_C_m = df.C == y
                            data_C_m = df[index_C_m].astype(float)
                            C_sum_m = pandas.DataFrame()
                            for i in range(nb_sample):
                                intensity_C_m = sum(data_C_m.iloc[:, 1 + i])
                                count_C_m = np.count_nonzero(data_C_m.iloc[:, 1 + i])
                                if self.ui.radio_dist_int_comp.isChecked():
                                    C_sum_m[i] = [intensity_C_m]
                                else:
                                    C_sum_m[i] = [count_C_m]
                            C_both[y] = list(C_sum_m.values[0])

                        C_both.index = list(data_C_m.columns[1:])
                        leg_raw = list(C_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_", "")
                            name = name.replace(".csv", "")
                            name = name.replace(".xlsx", "")
                            leg.append(name)
                        y_max = len(C_both)
                        x_label = "#C"
                        to_plt = C_both

                elif x_axes == 2:
                    dbe_text = "Even and odd ions"
                    N_both = pandas.DataFrame()
                    intens = frames.iloc[
                        :,
                        frames.columns.get_loc("count")
                        + nb_sample
                        + 1 : frames.columns.get_loc("count")
                        + nb_sample * 2
                        + 1,
                    ]  # stocke les intensités relatives des échantillons
                    if "N" in frames:
                        all_N = frames.N.drop_duplicates()
                        df = pandas.concat([frames.N, intens], axis=1)
                        for y in all_N:
                            index_N_m = df.N == y
                            data_N_m = df[index_N_m].astype(float)
                            N_sum_m = pandas.DataFrame()
                            for i in range(nb_sample):
                                intensity_N_m = sum(data_N_m.iloc[:, 1 + i])
                                count_N_m = np.count_nonzero(data_N_m.iloc[:, 1 + i])
                                if self.ui.radio_dist_int_comp.isChecked():
                                    N_sum_m[i] = [intensity_N_m]
                                else:
                                    N_sum_m[i] = [count_N_m]

                            N_both[y] = list(N_sum_m.values[0])

                        N_both.index = list(data_N_m.columns[1:])
                        leg_raw = list(N_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_", "")
                            name = name.replace(".csv", "")
                            name = name.replace(".xlsx", "")
                            leg.append(name)
                        y_max = len(N_both)
                        x_label = "#N"
                        to_plt = N_both

                elif x_axes == 3:
                    dbe_text = "Even and odd ions"
                    O_both = pandas.DataFrame()
                    intens = frames.iloc[
                        :,
                        frames.columns.get_loc("count")
                        + nb_sample
                        + 1 : frames.columns.get_loc("count")
                        + nb_sample * 2
                        + 1,
                    ]  # stocke les intensités relatives des échantillons
                    if "O" in frames:
                        all_O = frames.O.drop_duplicates()
                        df = pandas.concat([frames.O, intens], axis=1)
                        for y in all_O:
                            index_O_m = df.O == y
                            data_O_m = df[index_O_m].astype(float)
                            O_sum_m = pandas.DataFrame()
                            for i in range(nb_sample):
                                intensity_O_m = sum(data_O_m.iloc[:, 1 + i])
                                count_O_m = np.count_nonzero(data_O_m.iloc[:, 1 + i])
                                if self.ui.radio_dist_int_comp.isChecked():
                                    O_sum_m[i] = [intensity_O_m]
                                else:
                                    O_sum_m[i] = [count_O_m]
                            O_both[y] = list(O_sum_m.values[0])

                        O_both.index = list(data_O_m.columns[1:])
                        leg_raw = list(O_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_", "")
                            name = name.replace(".csv", "")
                            name = name.replace(".xlsx", "")
                            leg.append(name)
                        y_max = len(O_both)
                        x_label = "#O"
                        to_plt = O_both

                elif x_axes == 4:
                    dbe_text = "Even and odd ions"
                    S_both = pandas.DataFrame()
                    intens = frames.iloc[
                        :,
                        frames.columns.get_loc("count")
                        + nb_sample
                        + 1 : frames.columns.get_loc("count")
                        + nb_sample * 2
                        + 1,
                    ]  # stocke les intensités relatives des échantillons
                    if "S" in frames:
                        all_S = frames.S.drop_duplicates()
                        df = pandas.concat([frames.S, intens], axis=1)
                        for y in all_S:
                            index_S_m = df.S == y
                            data_S_m = df[index_S_m].astype(float)
                            S_sum_m = pandas.DataFrame()
                            for i in range(nb_sample):
                                intensity_S_m = sum(data_S_m.iloc[:, 1 + i])
                                count_S_m = np.count_nonzero(data_S_m.iloc[:, 1 + i])
                                if self.ui.radio_dist_int_comp.isChecked():
                                    S_sum_m[i] = [intensity_S_m]
                                else:
                                    S_sum_m[i] = [count_S_m]
                            S_both[y] = list(S_sum_m.values[0])

                        S_both.index = list(data_S_m.columns[1:])
                        leg_raw = list(S_both.index.values)
                        leg = []
                        for name in leg_raw:
                            name = name.replace("Rel_intens_", "")
                            name = name.replace(".csv", "")
                            name = name.replace(".xlsx", "")
                            leg.append(name)
                        y_max = len(S_both)
                        x_label = "#S"
                        to_plt = S_both

                wid = float(self.ui.Distrib_compare_width.text())
                gap = float(self.ui.Distrib_compare_gap.text())

                if (
                    self.ui.radio_dist_nb_comp.isChecked()
                ):  # Normalize number of attribution
                    to_plt = to_plt.div(to_plt.sum(axis=1), axis=0) * 100

                for y in range(y_max):  # y_max = number of samples
                    ab = np.array(to_plt.columns) - gap * (
                        0.5 - ((y + 1) / (y_max + 1))
                    ) / (y_max + 1)
                    plt.bar(
                        ab,
                        to_plt.iloc[y, :],
                        width=(0.14 * wid) / (y_max + 1),
                        color=color_list[y % 9],
                    )
                # Plot parameters :
                plt.gca().legend(leg, fontsize=font_size - 4)
                if self.ui.x_compare_min.text():
                    x_min = float(self.ui.x_compare_min.text())
                    plt.gca().set_xlim(left=x_min)
                if self.ui.x_compare_max.text():
                    x_max = float(self.ui.x_compare_max.text())
                    plt.gca().set_xlim(right=x_max)
                plt.xlabel(x_label, fontsize=font_size + 2)
                plt.suptitle(
                    f"{y_legend} vs {x_label}", fontsize=font_size + 4, y=0.98, x=0.45
                )
                plt.text(
                    0.88,
                    0.9,
                    dbe_text,
                    horizontalalignment="right",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=font_size,
                )
                plt.text(
                    0.12,
                    0.9,
                    frames.classe_selected,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=font_size,
                )
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
                    )
                cursor = mplcursors.cursor(multiple=True)

                @cursor.connect("add")
                def on_add(sel):
                    x, y, width, height = sel.artist[sel.target.index].get_bbox().bounds
                    sel.annotation.set(
                        text=f"{y_legend}: {round(height,4)}%",
                        position=(0, 20),
                        anncoords="offset points",
                    )
                    sel.annotation.xy = (x + width / 2, y + height)

        if gif == False:
            for i in frames:
                Anim(i)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(Figure, Anim, frames, interval=1000 / self.fps)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_spectrum_compare(self):
        """
        Plots mass spectrum in the compare menu
        """
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        fig = plt.figure()

        data_selected = self.compared_datas

        item_classes = self.ui.list_classes_mass_spec_comp.selectedItems()
        if not item_classes:
            return
        leg = list()
        for i in range(len(item_classes)):
            classe_selected = item_classes[i].data(self.USERDATA_ROLE)
            data_filtered = Select_classe(
                classe_selected,
                data_selected.df,
                data_selected.heteroatoms,
                data_selected.classes,
            )
            data_filtered = data_filtered.sort_values(
                by=["summed_intensity"], ascending=True
            )
            c = color_list[(i + 1) % 10 - 1]
            patch = mpatches.Patch(color=c, label=item_classes[i].text())
            leg.append(patch)
            plt.stem(
                data_filtered["m/z"],
                data_filtered["summed_intensity"],
                linefmt=c,
                markerfmt=" ",
                basefmt="k",
            )
        if self.ui.mz_min_2.text():
            mz_min_2 = float(self.ui.mz_min_2.text())
            plt.gca().set_xlim(left=mz_min_2)
        if self.ui.mz_max_2.text():
            mz_max_2 = float(self.ui.mz_max_2.text())
            plt.gca().set_xlim(right=mz_max_2)
        if self.ui.intens_min.text():
            intens_min = float(self.ui.intens_min.text())
            plt.gca().set_ylim(bottom=intens_min)
        if self.ui.intens_max.text():
            intens_max = float(self.ui.intens_max.text())
            plt.gca().set_ylim(top=intens_max)
        if self.ui.font_size.text():
            font_size = float(self.ui.font_size.text())
        plt.gca().legend(handles=leg, fontsize=font_size - 2)
        plt.xlabel("m/z", fontsize=font_size + 2, style="italic")
        plt.ylabel("Intensity", fontsize=font_size + 2)
        plt.xticks(fontsize=font_size)
        plt.yticks(fontsize=font_size)
        yaxes = plt.gca().yaxis
        yaxes.offsetText.set_fontsize(font_size)
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x() + 940, self.pos().y() + 200, 640, 545)
        plt.show()

    def compare_calculation(self):
        """
        Creates an in-line merged file with the samples selected in the compare menu
        """

        self.ui.plot_compare.setEnabled(False)
        self.ui.plot_compare_GIF.setEnabled(False)
        self.ui.status_compare.setStyleSheet(
            "background-color: rgb(255, 150, 0); border-radius: 12px; color: white"
        )
        self.ui.status_compare.setText("Operating")
        data = {}
        self.name = {}
        compare_items = self.ui.list_loaded_file_compare.selectedItems()
        if not compare_items or len(compare_items) < 2:
            self.ui.status_compare.setStyleSheet(
                "background-color: rgb(220, 0, 3); border-radius: 12px; color: white"
            )
            self.ui.status_compare.setText("No Files")
            return

        else:
            self.ui.pbar.show()
            v = int(0)
            self.ui.pbar.setValue(int(v))
            for i in range(len(compare_items)):
                item = compare_items[i].data(self.USERDATA_ROLE)
                self.name[i] = compare_items[i].text()
                data[i] = pandas.DataFrame(item.df)
                v = 50 * (i + 1) / len(compare_items)
                self.ui.pbar.setValue(int(v))

            compared_datas = merge_for_compare(data, self.name, self.isotopes_dict)
            self.ui.pbar.setValue(int(75))
            self.compared_datas = load_MS_file(compared_datas, self.isotopes_dict)
            self.ui.pbar.setValue(int(90))
        self.ui.status_compare.setStyleSheet(
            "background-color: rgb(50, 150, 0); border-radius: 12px; color: white"
        )
        self.ui.status_compare.setText("Ready")
        self.ui.pbar.setValue(int(100))
        self.ui.pbar.hide()
        self.split_classes_compare()

    def split_classes_compare(self):
        if self.ui.status_compare.text() != "Ready":
            return

        self.ui.list_classes_mass_spec_comp.clear()
        self.ui.list_classes_distrib_compare.clear()
        self.ui.list_classes_DBE_compare.clear()
        self.ui.list_classes_VK_compare.clear()
        self.ui.list_classes_DBE_comp.clear()
        self.ui.list_classes_VK_comp.clear()
        self.ui.list_classes_Kendrick_comp.clear()
        self.ui.list_classes_Kendrick_univ_comp.clear()
        self.ui.list_classes_KMD_compare.clear()
        self.ui.list_classes_MD_compare.clear()

        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_mass_spec_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_distrib_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_DBE_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_VK_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_DBE_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_VK_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_Kendrick_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_Kendrick_univ_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_ACOS_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_MAI_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_MCR_comp.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_KMD_compare.addItem(item_classes)
        item_classes = QtWidgets.QListWidgetItem("All")
        item_classes.setData(self.USERDATA_ROLE, "All")
        self.ui.list_classes_MD_compare.addItem(item_classes)
        n = 0
        while n < len(self.compared_datas.classes):
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_mass_spec_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_distrib_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_DBE_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_VK_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_DBE_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_VK_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_Kendrick_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_Kendrick_univ_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_ACOS_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_MAI_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_MCR_comp.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_KMD_compare.addItem(item_classes)
            item_classes = QtWidgets.QListWidgetItem(
                self.compared_datas.classes_concat.iloc[n, 0]
            )
            item_classes.setData(
                self.USERDATA_ROLE, self.compared_datas.classes.iloc[n, 0]
            )
            self.ui.list_classes_MD_compare.addItem(item_classes)
            n = n + 1
        self.ui.plot_compare.setEnabled(True)
        self.ui.plot_compare_GIF.setEnabled(True)
        self.ui.list_classes_distrib_compare.setCurrentRow(0)
        self.ui.list_compare_sample_1.clear()
        self.ui.list_compare_sample_2.clear()
        self.ui.list_sample_1_stats.clear()
        self.ui.list_sample_2_stats.clear()
        name_data = self.compared_datas.df.iloc[
            :,
            self.compared_datas.df.columns.get_loc("count")
            + max(self.compared_datas.df["count"])
            + 1 : self.compared_datas.df.columns.get_loc("count")
            + max(self.compared_datas.df["count"]) * 2
            + 1,
        ]
        name_data.columns = name_data.columns.str.replace(".csv", "")
        name_data.columns = name_data.columns.str.replace(".xlsx", "")
        name_data.columns = name_data.columns.str.replace("Rel_intens_", "")
        n = 0
        if "PC1" in self.compared_datas.df:
            self.ui.radio_color_pc1_comp.show()
            self.ui.radio_color_pc1_comp.setEnabled(True)
            self.ui.radio_color_pc2_comp.show()
            self.ui.radio_color_pc2_comp.setEnabled(True)
            self.ui.radio_color_pc1_VK_comp.show()
            self.ui.radio_color_pc1_VK_comp.setEnabled(True)
            self.ui.radio_color_pc2_VK_comp.show()
            self.ui.radio_color_pc2_VK_comp.setEnabled(True)
            self.ui.radio_color_pc1_ACOS_comp.show()
            self.ui.radio_color_pc1_ACOS_comp.setEnabled(True)
            self.ui.radio_color_pc2_ACOS_comp.show()
            self.ui.radio_color_pc2_ACOS_comp.setEnabled(True)

        else:
            self.ui.radio_color_pc1_comp.hide()
            self.ui.radio_color_pc1_comp.setEnabled(False)
            self.ui.radio_color_pc2_comp.hide()
            self.ui.radio_color_pc2_comp.setEnabled(False)
            self.ui.radio_color_pc1_VK_comp.hide()
            self.ui.radio_color_pc1_VK_comp.setEnabled(False)
            self.ui.radio_color_pc2_VK_comp.hide()
            self.ui.radio_color_pc2_VK_comp.setEnabled(False)
            self.ui.radio_color_pc1_ACOS_comp.hide()
            self.ui.radio_color_pc1_ACOS_comp.setEnabled(False)
            self.ui.radio_color_pc2_ACOS_comp.hide()
            self.ui.radio_color_pc2_ACOS_comp.setEnabled(False)

        while n < len(name_data.columns):
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            self.ui.list_compare_sample_1.addItem(item_sample)
            item_sample = QtWidgets.QListWidgetItem(name_data.columns[n])
            self.ui.list_compare_sample_2.addItem(item_sample)
            n = n + 1
        self.ui.list_classes_DBE_compare.setCurrentRow(0)
        self.ui.list_classes_VK_compare.setCurrentRow(0)
        self.ui.list_classes_DBE_comp.setCurrentRow(0)
        self.ui.list_classes_VK_comp.setCurrentRow(0)
        self.ui.list_classes_Kendrick_comp.setCurrentRow(0)
        self.ui.list_classes_Kendrick_univ_comp.setCurrentRow(0)
        self.ui.list_classes_KMD_compare.setCurrentRow(0)
        self.ui.list_classes_MD_compare.setCurrentRow(0)
