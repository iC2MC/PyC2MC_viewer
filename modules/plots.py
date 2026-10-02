from modules.controller_dependencies import *

class PlotsMixin:
    def overview(self, gif=False):
        """
        Plotting function in the overview panel
        """
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        self.read_param()
        font_size = self.fontsize

        ##############
        # Composition
        ##############

        if self.ui.radio_composition.isChecked():
            if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
                plt.close("all")

            item_classes = self.ui.list_loaded_file.selectedItems()
            if not item_classes:
                return

            fig, ax = plt.subplots()

            for item_class in item_classes:
                data_selected = item_class.data(self.USERDATA_ROLE)
                data = data_selected.classes

                if "count" in data_selected.df:
                    capsize = 5
                    if self.ui.radio_classes.isChecked():
                        data = data[~data["variable"].str.contains("x")]

                    if self.ui.edit_min_intensity_classes.text():
                        min_intens_classes = float(
                            self.ui.edit_min_intensity_classes.text()
                        )
                        if self.ui.radio_classes.isChecked():
                            data = data[data["value"] > min_intens_classes]
                        else:
                            data = data[data["variable"].str.contains("x")]
                            if "CH" in data_selected.classes["variable"].values:
                                data = data.append(
                                    data_selected.classes[
                                        data_selected.classes["variable"].str.contains(
                                            "CH"
                                        )
                                    ]
                                )
                            data = data[data["value"] > min_intens_classes]

                    data = data.sort_values("value", ascending=False).reset_index(
                        drop=True
                    )
                    if self.ui.radio_comp_int.isChecked():
                        y_label = "Relative intensity (%)"
                        ax.bar(
                            data["variable"],
                            data["value"],
                            yerr=data["std_dev_rel"],
                            align="center",
                            ecolor="black",
                            capsize=capsize,
                        )
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                f"{data['variable'].iloc[sel.target.index]}: Rel. Intensity  = {round(data['value'].iloc[sel.target.index],2)}%, std deviation = {round(data['std_dev_rel'].iloc[sel.target.index],2)}%"
                            ),
                        )
                    elif self.ui.radio_comp_nb.isChecked():
                        y_label = "Number of attribution (%)"
                        ax.bar(data["variable"], data["number"])
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                f"{data['variable'].iloc[sel.target.index]}: Count  = {int(data['number'].iloc[sel.target.index])}"
                            ),
                        )
                else:
                    if self.ui.radio_classes.isChecked():
                        data = data[~data["variable"].str.contains("x")]

                    if self.ui.edit_min_intensity_classes.text():
                        min_intens_classes = float(
                            self.ui.edit_min_intensity_classes.text()
                        )
                        if not self.ui.radio_classes.isChecked():
                            data_temp = data[data["variable"].str.contains("x")]
                            data = data_temp.append(
                                data[data["variable"].str.contains("CH")]
                            )

                        data = data[data["value"] > min_intens_classes]

                    if self.ui.radio_comp_int.isChecked():
                        data = data.sort_values("value", ascending=False).reset_index(
                            drop=True
                        )
                        ax.bar(data["variable"], data["value"])
                        y_label = "Relative intensity (%)"
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                f"{data['variable'].iloc[sel.target.index]}: Rel. Intensity  = {round(data['value'].iloc[sel.target.index],2)}%"
                            ),
                        )
                    elif self.ui.radio_comp_nb.isChecked():
                        data["number"] = (
                            data["number"].div(data["number"].sum(axis=0)) * 100
                        )
                        data = data.sort_values("number", ascending=False).reset_index(
                            drop=True
                        )
                        ax.bar(data["variable"], data["number"])
                        y_label = "Number of attribution (%)"
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                f"{data['variable'].iloc[sel.target.index]}: Nb. Attrib.  = {int(data['number'].iloc[sel.target.index])}%"
                            ),
                        )

            plt.suptitle("Heteroatom class distribution", fontsize=font_size + 2)
            plt.ylabel(f"{y_label}", fontsize=font_size + 2)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 640, 545
            )
            plt.xticks(fontsize=font_size)
            plt.yticks(fontsize=font_size)
            plt.show()

        ##############
        # Error
        ##############

        elif self.ui.radio_error_plots.isChecked():
            dot_size = self.d_size
            data_selected = item.data(self.USERDATA_ROLE)
            frames = []
            item_classes = self.ui.list_classes_error.selectedItems()
            if not item_classes:
                return
            if self.ui.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            for item in item_classes:
                classe_selected = item.data(self.USERDATA_ROLE)
                data_extract = Select_classe(
                    classe_selected,
                    data_selected.df,
                    data_selected.heteroatoms,
                    data_selected.classes,
                )

                # -----------------------------------#
                #  Normalization on displayed data  #
                # -----------------------------------#

                if (
                    self.ui.radioButton_norm_d.isChecked()
                    or self.ui.radioButton_norm_c.isChecked()
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
                #  Normalization on displayed data (end)  #
                # -----------------------------------------#
                self.read_param()

                data_extract = data_extract.sort_values(
                    by=["Normalized_intensity"], ascending=True
                )
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
                    if self.ui.radio_ppm.isChecked():

                        x_data = frames["m/z"]
                        y_data = frames["err_ppm"]
                        third_dim = frames["Normalized_intensity"]

                        plot_fun(
                            "scatter",
                            x=x_data,
                            y=y_data,
                            d_color=third_dim,
                            size=(dot_size) * third_dim,
                            dot_type=self.dot_type,
                            edge=self.edge,
                            cmap=self.color_map,
                        )

                        if self.ui.mz_min.text():
                            mz_min = float(self.ui.mz_min.text())
                            plt.gca().set_xlim(left=mz_min)
                        if self.ui.mz_max.text():
                            mz_max = float(self.ui.mz_max.text())
                            plt.gca().set_xlim(right=mz_max)
                        if self.ui.error_min.text():
                            error_min = float(self.ui.error_min.text())
                            plt.gca().set_ylim(bottom=error_min)
                        if self.ui.error_max.text():
                            error_max = float(self.ui.error_max.text())
                            plt.gca().set_ylim(top=error_max)
                        if self.ui.font_size.text():
                            font_size = float(self.ui.font_size.text())
                        plt.suptitle(
                            f"{frames.classe_selected}",
                            fontsize=font_size + 4,
                            y=0.95,
                            x=0.5,
                        )
                        cbar = plt.colorbar()
                        cbar.set_label(
                            "Normalized Intensity",
                            labelpad=-2.625 * (font_size),
                            rotation=90,
                            fontsize=font_size,
                            color=self.cm_text_color,
                        )
                        plt.xlabel("m/z", fontsize=font_size + 2)
                        plt.ylabel("Error (ppm)", fontsize=font_size + 2)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(
                                self.pos().x() + 940, self.pos().y() + 200, 640, 545
                            )
                        if "m/z" in frames:
                            mplcursors.cursor(multiple=True).connect(
                                "add",
                                lambda sel: sel.annotation.set_text(
                                    frames["molecular_formula"].iloc[sel.target.index]
                                ),
                            )

                    ### Box plot ###

                    elif self.ui.radio_boxplot.isChecked():

                        plt.boxplot(frames["err_ppm"])
                        if self.ui.font_size.text():
                            font_size = float(self.ui.font_size.text())
                        plt.suptitle(
                            f"{frames.classe_selected}",
                            fontsize=font_size + 4,
                            y=0.95,
                            x=0.5,
                        )
                        plt.ylabel("Error (ppm)", fontsize=font_size)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        yaxes = plt.gca().yaxis
                        yaxes.offsetText.set_fontsize(font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(
                                self.pos().x() + 940, self.pos().y() + 200, 640, 545
                            )

                    ### bar plot  ###
                    else:

                        lst_error = []
                        min_error = min(frames["err_ppm"])
                        max_error = max(frames["err_ppm"])
                        n_bin = 50
                        error_range = (
                            max(frames["err_ppm"]) + abs(min(frames["err_ppm"]))
                        ) / (
                            n_bin + 1
                        )  # Calculates error range and divides it into 50 sections
                        if self.ui.radio_histo.isChecked():
                            Data = frames.groupby(
                                pandas.cut(
                                    frames["err_ppm"],
                                    np.arange(min_error, max_error, error_range),
                                )
                            ).sum()
                        elif self.ui.radio_histo_2.isChecked():
                            Data = frames.groupby(
                                pandas.cut(
                                    frames["err_ppm"],
                                    np.arange(min_error, max_error, error_range),
                                )
                            ).count()
                        # Creates the 20 sections and determines errors value for each
                        for i in range(len(Data["err_ppm"])):
                            lst_error.append(
                                min_error + (error_range / 2) + i * error_range
                            )
                        # Mean error list
                        d = {"col1": lst_error, "col2": Data["absolute_intensity"]}
                        df = pandas.DataFrame(data=d)
                        plt.bar(df["col1"], df["col2"], width=1 / n_bin)
                        if self.ui.error_min.text():
                            error_min = float(self.ui.error_min.text())
                            plt.gca().set_xlim(left=error_min)
                        if self.ui.error_max.text():
                            error_max = float(self.ui.error_max.text())
                            plt.gca().set_xlim(right=error_max)
                        if self.ui.font_size.text():
                            font_size = float(self.ui.font_size.text())
                        plt.suptitle(
                            f"{frames.classe_selected}",
                            fontsize=font_size + 4,
                            y=0.97,
                            x=0.5,
                        )
                        plt.title("error distribution", fontsize=font_size + 2)
                        plt.xlabel("Errors", fontsize=font_size)
                        if self.ui.radio_histo.isChecked():
                            plt.ylabel("Summed intensities (a.u)", fontsize=font_size)
                        elif self.ui.radio_histo_2.isChecked():
                            plt.ylabel("Number", fontsize=font_size)
                        plt.xticks(fontsize=font_size)
                        plt.yticks(fontsize=font_size)
                        yaxes = plt.gca().yaxis
                        yaxes.offsetText.set_fontsize(font_size)
                        if gif == False:
                            mngr = plt.get_current_fig_manager()
                            mngr.window.setGeometry(
                                self.pos().x() + 940, self.pos().y() + 200, 640, 545
                            )
                        mplcursors.cursor(multiple=True).connect(
                            "add",
                            lambda sel: sel.annotation.set_text(
                                "Intensity = "
                                + str(format(df["col2"].iloc[sel.target.index], ".1E"))
                            ),
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

        ##############
        # Spectra
        ##############

        elif self.ui.radio_mass_spectrum.isChecked():
            if self.ui.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            fig = plt.figure()
            item_file = self.ui.list_loaded_file.selectedItems()
            if not item_file:
                return
            item = item_file[0]
            data_selected = item.data(self.USERDATA_ROLE)
            leg = list()
            if data_selected.df_type == "Peaklist":
                item_classes = []
                classe_selected = "All"
                data_filtered = data_selected.df
                plt.stem(
                    data_filtered["m/z"],
                    data_filtered["absolute_intensity"],
                    linefmt="black",
                    markerfmt=" ",
                    basefmt="k",
                )

            else:
                item_classes = self.ui.list_classes_mass_spec.selectedItems()
                if not item_classes:
                    item_classes = [self.ui.list_classes_mass_spec.item(0)]
                for i in range(len(item_classes)):

                    classe_selected = item_classes[i].data(self.USERDATA_ROLE)
                    data_filtered = Select_classe(
                        classe_selected,
                        data_selected.df,
                        data_selected.heteroatoms,
                        data_selected.classes,
                    )
                    third_dimension = data_filtered["Normalized_intensity"]
                    Intens = third_dimension.values.reshape(-1, 1)
                    min_max_scaler = preprocessing.MinMaxScaler()
                    Intens_scaled = min_max_scaler.fit_transform(Intens)
                    data_filtered["Normalized_intensity"] = Intens_scaled
                    data_filtered = data_filtered.sort_values(
                        by=["Normalized_intensity"], ascending=True
                    )
                    c = color_list[(i + 1) % 10 - 1]
                    patch = mpatches.Patch(color=c, label=item_classes[i].text())
                    leg.append(patch)
                    plt.stem(
                        data_filtered["m/z"],
                        data_filtered["absolute_intensity"],
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
            cursor = mplcursors.cursor(multiple=True)

            @cursor.connect("add")
            def on_add(sel):
                sel.annotation.set(position=(0, 20), anncoords="offset points")

            plt.xticks(fontsize=font_size)
            plt.yticks(fontsize=font_size)
            yaxes = plt.gca().yaxis
            yaxes.offsetText.set_fontsize(font_size)
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 640, self.pos().y() + 200, 640, 545
            )
            plt.show()

        ##############
        # Distrib
        ##############

        elif self.ui.radio_distributions.isChecked():

            self.read_param()
            font_size = self.fontsize
            frames = []
            item_file = self.ui.list_loaded_file.selectedItems()
            if not item_file:
                return
            item = item_file[0]
            data_selected = item.data(self.USERDATA_ROLE)

            item_classes = self.ui.list_classes_distrib.selectedItems()
            if not item_classes:
                return
            if self.ui.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            if self.ui.radio_dist_int.isChecked():
                y_label = "Relative intensity (%)"
                y_title = "Relative intensity"
            else:
                y_label = "Number of attribution (%)"
                y_title = "Number of attribution"

            for item in item_classes:
                classe_selected = item.data(self.USERDATA_ROLE)
                data_extract = Select_classe(
                    classe_selected,
                    data_selected.df,
                    data_selected.heteroatoms,
                    data_selected.classes,
                )
                data_extract.classe_selected = classe_selected
                frames.append(data_extract)

                def Anim(frames, data_selected):
                    pr1 = False
                    if gif == False:
                        fig = plt.figure()
                        transf = fig.transFigure
                    else:
                        Figure.clear()
                        transf = Figure.transFigure
                    x_axes = self.ui.list_distribution.currentRow()

                    if x_axes == 0:  # DBE

                        x_label = "DBE"
                        bar_color = "grey"

                        dbe_both = dict()
                        dbe_odd = dict()
                        dbe_even = dict()
                        m = float(-0.5)
                        while m <= max(frames.DBE):
                            index_DBE = frames.DBE == m
                            data_DBE = frames[index_DBE]
                            intensity_DBE = (
                                sum(data_DBE["Normalized_intensity"])
                                * 100
                                / sum(data_selected.df["Normalized_intensity"])
                            )
                            number_DBE = len(data_DBE)
                            if intensity_DBE:
                                dbe_both[m] = [intensity_DBE, number_DBE]
                                if m.is_integer():
                                    dbe_odd[m] = [intensity_DBE, number_DBE]
                                else:
                                    dbe_even[m] = [intensity_DBE, number_DBE]
                            m = m + 0.5

                        if self.ui.radio_even_intens_vs_DBE.isChecked():
                            dbe = dbe_even
                            dbe_text = "Even ions"
                            w = 1
                        elif self.ui.radio_odd_intens_vs_DBE.isChecked():
                            dbe = dbe_odd
                            dbe_text = "Odd ions"
                            w = 1
                        elif self.ui.radio_both_intens_vs_DBE.isChecked():
                            dbe = dbe_both
                            dbe_text = "Even and odd ions"
                            w = 0.5
                            pr1 = True

                        dbe = pandas.DataFrame.from_dict(dbe)
                        x = dbe.columns
                        try:
                            if self.ui.radio_dist_int.isChecked():
                                y = dbe.values.tolist()[0]
                            elif self.ui.radio_dist_nb.isChecked():
                                y = dbe.values.tolist()[1]
                        except IndexError:
                            QMessageBox.about(
                                self,
                                "Error",
                                f"No species to be displayed for the selected parity",
                            )
                            return

                    elif x_axes == 1:  # C
                        x_label = "#C"
                        bar_color = "grey"
                        C_both = dict()
                        m = float(1)
                        while m <= max(frames.C):
                            index_C = frames.C == m
                            data_C = frames[index_C]
                            intensity_C = (
                                sum(data_C["Normalized_intensity"])
                                * 100
                                / sum(data_selected.df["Normalized_intensity"])
                            )
                            number_C = len(data_C)
                            if intensity_C:
                                C_both[m] = [intensity_C, number_C]
                            m = m + 1
                        C_both = pandas.DataFrame.from_dict(C_both)
                        dbe_text = "Even and odd ions"
                        w = 1
                        x = C_both.columns
                        if self.ui.radio_dist_int.isChecked():
                            y = C_both.values.tolist()[0]
                        elif self.ui.radio_dist_nb.isChecked():
                            y = C_both.values.tolist()[1]

                    elif x_axes == 2:
                        x_label = "#N"
                        bar_color = "blue"
                        w = 1
                        N_both = dict()
                        m = int(0)
                        while m <= max(frames.N):
                            index_N = frames.N == m
                            data_N = frames[index_N]
                            intensity_N = (
                                sum(data_N["Normalized_intensity"])
                                * 100
                                / sum(data_selected.df["Normalized_intensity"])
                            )
                            number_N = len(data_N)
                            if intensity_N:
                                N_both[m] = [intensity_N, number_N]
                            m = m + 1
                        N_both = pandas.DataFrame.from_dict(N_both)
                        dbe_text = "Even and odd ions"
                        x = N_both.columns
                        if self.ui.radio_dist_int.isChecked():
                            y = N_both.values.tolist()[0]
                        elif self.ui.radio_dist_nb.isChecked():
                            y = N_both.values.tolist()[1]

                    elif x_axes == 3:
                        x_label = "#O"
                        bar_color = "red"
                        w = 1
                        O_both = dict()
                        m = int(0)
                        while m <= max(frames.O):
                            index_O = frames.O == m
                            data_O = frames[index_O]
                            intensity_O = (
                                sum(data_O["Normalized_intensity"])
                                * 100
                                / sum(data_selected.df["Normalized_intensity"])
                            )
                            number_O = len(data_O)
                            if intensity_O:
                                O_both[m] = [intensity_O, number_O]
                            m = m + 1
                        O_both = pandas.DataFrame.from_dict(O_both)
                        dbe_text = "Even and odd ions"
                        x = O_both.columns
                        if self.ui.radio_dist_int.isChecked():
                            y = O_both.values.tolist()[0]
                        elif self.ui.radio_dist_nb.isChecked():
                            y = O_both.values.tolist()[1]

                    elif x_axes == 4:
                        x_label = "#S"
                        bar_color = "yellow"
                        w = 1
                        S_both = dict()
                        m = int(0)
                        while m <= max(frames.S):
                            index_S = frames.S == m
                            data_S = frames[index_S]
                            intensity_S = (
                                sum(data_S["Normalized_intensity"])
                                * 100
                                / sum(data_selected.df["Normalized_intensity"])
                            )
                            number_S = len(data_S)
                            if intensity_S:
                                S_both[m] = [intensity_S, number_S]
                            m = m + 1
                        S_both = pandas.DataFrame.from_dict(S_both)
                        dbe_text = "Even and odd ions"
                        x = S_both.columns
                        if self.ui.radio_dist_int.isChecked():
                            y = S_both.values.tolist()[0]
                        elif self.ui.radio_dist_nb.isChecked():
                            y = S_both.values.tolist()[1]

                    total_attrib = ""
                    if self.ui.radio_dist_nb.isChecked():
                        if pr1 == False:
                            total_attrib = f". Tot.nb. = {int(sum(y))}"
                        y = (np.array(y) * 100 / sum(y)).tolist()

                    if pr1:
                        dbe_odd = pandas.DataFrame.from_dict(dbe_odd)
                        dbe_even = pandas.DataFrame.from_dict(dbe_even)

                        x_odd = dbe_odd.columns
                        x_even = dbe_even.columns
                        if self.ui.radio_dist_int.isChecked():
                            try:
                                y_odd = dbe_odd.values.tolist()[0]
                            except:
                                y_odd = []
                            try:
                                y_even = dbe_even.values.tolist()[0]
                            except:
                                y_even = []
                            tot_odd = ""
                            tot_even = ""
                        elif self.ui.radio_dist_nb.isChecked():
                            try:
                                y_odd = dbe_odd.values.tolist()[1]
                            except:
                                y_odd = []
                            tot_odd = f"(Nb={int(sum(y_odd))})"
                            y_odd = (np.array(y_odd) * 100 / sum(y_odd)).tolist()
                            try:
                                y_even = dbe_even.values.tolist()[1]
                            except:
                                y_even = []
                            tot_even = f"(Nb={int(sum(y_even))})"
                            y_even = (np.array(y_even) * 100 / sum(y_even)).tolist()

                        plt.bar(
                            x_odd,
                            y_odd,
                            width=0.5,
                            color="dodgerblue",
                            edgecolor="black",
                            linewidth=2,
                        )
                        plt.bar(
                            x_even,
                            y_even,
                            width=0.5,
                            color="orangered",
                            edgecolor="black",
                            linewidth=2,
                        )
                        legend_elements = [
                            Patch(
                                facecolor="dodgerblue",
                                edgecolor="k",
                                label="Odd" + tot_odd,
                            ),
                            Patch(
                                facecolor="orangered",
                                edgecolor="k",
                                label="Even" + tot_even,
                            ),
                        ]
                        plt.legend(handles=legend_elements, fontsize=font_size - 4)
                    else:
                        plt.bar(
                            x,
                            y,
                            width=w,
                            color=bar_color,
                            edgecolor="black",
                            linewidth=2,
                        )

                    title = f"{y_title} vs {x_label}"
                    plt.suptitle(f"{title}", fontsize=font_size + 4, y=0.98, x=0.45)
                    plt.xlabel(x_label, fontsize=font_size + 2)
                    plt.ylabel(y_label, fontsize=font_size + 2)
                    cursor = mplcursors.cursor(multiple=True)

                    @cursor.connect("add")
                    def on_add(sel):
                        x, y, width, height = (
                            sel.artist[sel.target.index].get_bbox().bounds
                        )
                        if self.ui.radio_dist_nb.isChecked():
                            txt = "Nb. Attrib."
                        else:
                            txt = "Rel. Intens."
                        sel.annotation.set(
                            text=f"DBE: {x+width/2,0}; {txt}: {round(height,4)}%",
                            position=(0, 20),
                            anncoords="offset points",
                        )
                        sel.annotation.xy = (x + width / 2, y + height)

                    plt.xticks(fontsize=font_size)
                    plt.yticks(fontsize=font_size)
                    if self.ui.Int_vs_DBE_min.text():
                        C_min = float(self.ui.Int_vs_DBE_min.text())
                        plt.gca().set_xlim(left=C_min)
                    if self.ui.Int_vs_DBE_max.text():
                        C_max = float(self.ui.Int_vs_DBE_max.text())
                        plt.gca().set_xlim(right=C_max)
                    if gif == False:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(
                            self.pos().x() + 940, self.pos().y() + 200, 640, 545
                        )
                    plt.text(
                        0.68,
                        0.9,
                        dbe_text + total_attrib,
                        horizontalalignment="center",
                        verticalalignment="center",
                        transform=transf,
                        fontsize=font_size + 2,
                    )
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
                for i in frames:
                    Anim(i, data_selected)
                plt.show()
            else:
                Figure = plt.figure()
                plt.show()
                anim_created = FuncAnimation(
                    Figure,
                    Anim,
                    frames,
                    fargs=(data_selected,),
                    interval=1000 / self.fps,
                )
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(
                    self.pos().x() + 940, self.pos().y() + 200, 640, 545
                )
                writergif = PillowWriter(fps=self.fps)
                anim_created.save("animation.gif", writer=writergif)
                plt.ion()

    def plot_DBE(self, gif=False):
        """
        DBE vs C# plots
        """

        frames = []
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        item_classes = self.ui.list_classes_DBE.selectedItems()
        if not item_classes:
            return
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        for item in item_classes:
            classe_selected = item.data(self.USERDATA_ROLE)

            if "PC1" in data_selected.df:
                self.ui.radio_color_pc1.show()
                self.ui.radio_color_pc2.show()

            data = data_selected.df.copy()
            data_extract = Select_classe(
                classe_selected, data, data_selected.heteroatoms, data_selected.classes
            )
            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)
            if self.ui.check_classic.isChecked():
                Intens = Intens
            if self.ui.check_sqrt.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled

            # -----------------------------------#
            #  Normalization on selected class  #
            # -----------------------------------#

            if self.ui.radioButton_norm_c.isChecked():
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
            #  Normalization on selected class (end)  #
            # -----------------------------------------#

            if self.ui.radio_even_DBE.isChecked():
                data_extract = data_extract.loc[
                    np.where(data_extract["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 1
                ]
                dbe_text = "Even ions"
            elif self.ui.radio_odd_DBE.isChecked():
                data_extract = data_extract.loc[
                    np.where(data_extract["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 0
                ]
                dbe_text = "Odd ions"
            else:
                dbe_text = "Even and odd ions"
            if self.ui.dot_size.text():
                dot_size = float(self.ui.dot_size.text())
            if self.ui.font_size.text():
                font_size = float(self.ui.font_size.text())

            # -----------------------------------#
            #  Normalization on displayed data  #
            # -----------------------------------#

            if self.ui.radioButton_norm_d.isChecked():
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
            #  Normalization on displayed data (end)  #
            # -----------------------------------------#
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )
            if self.ui.radio_color_intensity_2.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc1.isChecked():
                third_dimension = data_extract["PC1"]
            elif self.ui.radio_color_pc2.isChecked():
                third_dimension = data_extract["PC2"]
            elif self.ui.radio_color_O.isChecked():
                third_dimension = data_extract["O"]
            elif self.ui.radio_color_N.isChecked():
                third_dimension = data_extract["N"]
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
                frames.sort_values(
                    by=["third_dimension", "Normalized_intensity"],
                    ascending=[True, True],
                    inplace=True,
                )
                plot_fun(
                    "scatter",
                    x=frames["C"],
                    y=frames["DBE"],
                    d_color=frames["third_dimension"],
                    size=dot_size * frames["Normalized_intensity"],
                    dot_type=self.dot_type,
                    edge=self.edge,
                    cmap=self.color_map,
                )

                if self.ui.C_min_DBE.text():
                    C_min = float(self.ui.C_min_DBE.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.C_max_DBE.text():
                    C_max = float(self.ui.C_max_DBE.text())
                    plt.gca().set_xlim(right=C_max)
                else:
                    C_max = data_selected.df["C"][data_selected.df["C"].idxmax()]
                if self.ui.DBE_min_DBE.text():
                    DBE_min = float(self.ui.DBE_min_DBE.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if self.ui.DBE_max_DBE.text():
                    DBE_max = float(self.ui.DBE_max_DBE.text())
                    plt.gca().set_ylim(top=DBE_max)
                else:
                    DBE_max = frames["DBE"][frames["DBE"].idxmax()]
                if self.ui.CheckBox_hap.isChecked():
                    plt.axline(
                        (13, 8.57), (19, 12.95), color="red", linestyle=(0, (5, 5))
                    )
                if self.ui.CheckBox_fulle.isChecked():
                    plt.axline((0, 1), (2, 3), color="black", linestyle=(0, (5, 5)))
                plt.suptitle(
                    f"{frames.classe_selected}", fontsize=font_size + 4, y=0.95, x=0.45
                )
                cbar = plt.colorbar()
                if self.ui.radio_color_intensity_2.isChecked():
                    cbar.set_label(
                        "Normalized Intensity",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc1.isChecked():
                    cbar.set_label(
                        "PC1",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc2.isChecked():
                    cbar.set_label(
                        "PC2",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )

                cbar.ax.tick_params(labelsize=font_size - 2)
                if self.ui.radio_color_pc1.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC1"]), np.max(data_selected.df["PC1"])
                    )
                elif self.ui.radio_color_pc2.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC2"]), np.max(data_selected.df["PC2"])
                    )
                plt.xlabel("#C", fontsize=font_size + 4)
                plt.ylabel("DBE", fontsize=font_size + 4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                plt.text(
                    0.68,
                    0.9,
                    dbe_text,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
                    )
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            frames["molecular_formula"].iloc[sel.target.index]
                            + ", #C = "
                            + str(frames["C"].iloc[sel.target.index])
                            + ", DBE = "
                            + str(frames["DBE"].iloc[sel.target.index])
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

    def plot_VK(self, gif=False):
        """
        Van Krevelen plot
        """

        frames = []
        item_file = self.ui.list_loaded_file.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)

        item_classes = self.ui.list_classes_VK.selectedItems()
        if not item_classes:
            return
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")

        for item in item_classes:
            classe_selected = item.data(self.USERDATA_ROLE)
            data = data_selected.df.copy()
            data_filtered = Select_classe(
                classe_selected, data, data_selected.heteroatoms, data_selected.classes
            )
            Intens = data_filtered["Normalized_intensity"].values.reshape(-1, 1)
            if self.ui.check_classic_vk.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_vk.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_vk.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value, log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled

            dot_size = self.d_size
            x_axes = self.ui.list_VK_x.currentRow()
            y_axes = self.ui.list_VK_y.currentRow()

            element_list = ["O/C", "N/C", "S/C", "H/C"]
            element_present = False
            for i in [x_axes, y_axes]:
                if i < len(element_list):
                    if element_list[i] not in data_filtered.columns:
                        QMessageBox.about(
                            self,
                            "Error",
                            f"No {element_list[i][0]} in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.",
                        )
                        x_axes, y_axes = 3, 0
                        element_present = True
            if not element_present and ("H/C" not in data_filtered.columns):
                QMessageBox.about(self, "Error", "No hydrogen in the selected data")

            (
                x_axes,
                y_axes,
                x_label,
                y_label,
            ) = Select_Axes_VK(x_axes, y_axes, data_filtered)

            if self.ui.radio_color_pc1_VK.isChecked():
                third_dimension = data_filtered["PC1"]
            elif self.ui.radio_color_pc2_VK.isChecked():
                third_dimension = data_filtered["PC2"]
            elif self.ui.radio_color_O_vk.isChecked():
                third_dimension = data_filtered["O"]
            elif self.ui.radio_color_N_vk.isChecked():
                third_dimension = data_filtered["N"]
            elif self.ui.radio_color_mz_vk.isChecked():
                third_dimension = data_filtered["m/z"]
            else:
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
                frames.sort_values(
                    by=["Normalized_intensity", "third_dimension"],
                    ascending=[True, True],
                    inplace=True,
                )

                plot_fun(
                    "scatter",
                    x=frames["x_axes"],
                    y=frames["y_axes"],
                    d_color=frames["third_dimension"],
                    size=dot_size * frames["Normalized_intensity"],
                    dot_type=self.dot_type,
                    edge=self.edge,
                    cmap=self.color_map,
                )

                if self.ui.x_min_VK.text():
                    C_min = float(self.ui.x_min_VK.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_VK.text():
                    C_max = float(self.ui.x_max_VK.text())
                    plt.gca().set_xlim(right=C_max)
                if self.ui.y_min_VK.text():
                    DBE_min = float(self.ui.y_min_VK.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if self.ui.y_max_VK.text():
                    DBE_max = float(self.ui.y_max_VK.text())
                    plt.gca().set_ylim(top=DBE_max)
                plt.suptitle(
                    f"{frames.classe_selected}", fontsize=font_size + 4, y=0.95, x=0.45
                )
                cbar = plt.colorbar()
                if self.ui.radio_color_intensity_3.isChecked():
                    cbar.set_label(
                        "Normalized Intensity",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc1_VK.isChecked():
                    cbar.set_label(
                        "PC1",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc2_VK.isChecked():
                    cbar.set_label(
                        "PC2",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_O_vk.isChecked():
                    cbar.set_label(
                        "#O",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_N_vk.isChecked():
                    cbar.set_label(
                        "#N",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                cbar.ax.tick_params(labelsize=font_size - 2)
                if self.ui.radio_color_pc1_VK.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC1"]), np.max(data_selected.df["PC1"])
                    )
                elif self.ui.radio_color_pc2_VK.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC2"]), np.max(data_selected.df["PC2"])
                    )
                plt.xlabel(frames.x_label, fontsize=font_size + 4)
                plt.ylabel(frames.y_label, fontsize=font_size + 4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                if gif == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
                    )
                if "m/z" in frames:
                    mplcursors.cursor(multiple=True).connect(
                        "add",
                        lambda sel: sel.annotation.set_text(
                            frames["molecular_formula"].iloc[sel.target.index]
                            + ", "
                            + str(x_label)
                            + " : "
                            + str(round(frames["x_axes"].iloc[sel.target.index], 4))
                            + ", "
                            + str(y_label)
                            + " = "
                            + str(round(frames["y_axes"].iloc[sel.target.index], 4))
                        ),
                    )

                if (
                    self.ui.checkBox_vk_area.isChecked()
                    and self.ui.list_VK_x.currentRow() == 0
                    and self.ui.list_VK_y.currentRow() == 0
                ):
                    border_width = 4
                    alpha = 1
                    patches = [
                        {
                            "left": 0.51,
                            "bottom": 1.52,
                            "width": 0.19,
                            "height": 0.5,
                            "color": "orange",
                            "label": "Amino sugars",
                        },
                        {
                            "left": 0.71,
                            "bottom": 1.52,
                            "width": 0.3,
                            "height": 0.8,
                            "color": "green",
                            "label": "Carbohydrates",
                        },
                        {
                            "left": 0.31,
                            "bottom": 0.51,
                            "width": 0.5,
                            "height": 0.99,
                            "color": "purple",
                            "label": "Lignin",
                        },
                        {
                            "left": 0,
                            "bottom": 1.72,
                            "width": 0.29,
                            "height": 0.6,
                            "color": "blue",
                            "label": "Lipids",
                        },
                        {
                            "left": 0,
                            "bottom": 0,
                            "width": 0.8,
                            "height": 0.49,
                            "color": "black",
                            "label": "Condensed Hydrocarbons",
                        },
                        {
                            "left": 0,
                            "bottom": 0.51,
                            "width": 0.29,
                            "height": 1.19,
                            "color": "red",
                            "label": "Unsaturated Hydrocarbons",
                        },
                        {
                            "left": 0.31,
                            "bottom": 1.52,
                            "width": 0.19,
                            "height": 0.49,
                            "color": "brown",
                            "label": "Proteins",
                        },
                    ]
                    patches_rects = []
                    for patch in patches:
                        rect = mpatches.Rectangle(
                            (patch["left"], patch["bottom"]),
                            patch["width"],
                            patch["height"],
                            fill=False,
                            color=patch["color"],
                            linewidth=border_width,
                            alpha=alpha,
                        )
                        patches_rects.append(rect)
                        plt.gca().add_patch(rect)
                    patches_labels = [
                        mpatches.Patch(color=patch["color"], label=patch["label"])
                        for patch in patches
                    ]
                    plt.legend(handles=patches_labels)

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

    def plot_PCA(self):
        """
        Principal component analysis (plot only)
        """

        if self.ui.radio_PCPC2.isChecked():
            axes = 0  # PC1PC2
        elif self.ui.radio_PC2PC3.isChecked():
            axes = 1  # PC2PC3
        elif self.ui.radio_PC1PC3.isChecked():
            axes = 2  # PC1PC3
        elif self.ui.radio_3D.isChecked():
            axes = 3  # PC1PC3
        if self.ui.PCA_ALL.isChecked():
            pca_on = "all"
        elif self.ui.PCA_COMMON.isChecked():
            pca_on = "common"
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        if not self.ui.lineEdit_n_component.text():
            n_comp = 5
        else:
            n_comp = int(self.ui.lineEdit_n_component.text())

        item_file = self.ui.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        pca_data = data_selected.pca_data
        # mz = data_selected.mass
        n_formula, n_ech = pca_data.shape
        n_ech = n_ech - 2
        if (
            int(self.ui.lineEdit_n_component.text()) > n_ech
            or int(self.ui.lineEdit_n_component.text()) < 3
        ):
            QMessageBox.about(
                self,
                "FYI box",
                "Number of component must be comprised between 3 and the number of compared samples, i.e. "
                + str(n_ech)
                + " in this case.",
            )
            return
        self.read_param()
        data_old = list(data_selected.df)
        score_coef, first_comps = plot_pca(
            pca_data, axes, n_comp, pca_on, para_dict=self.para_dict
        )
        data_selected.df.columns = data_old
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x() + 640, self.pos().y() + 200, 640, 545)
        self.data_with_coef = pandas.merge(
            left=data_selected.df, right=score_coef, left_on="m/z", right_on="m/z"
        )
        self.data_with_coef = self.data_with_coef.rename(columns={"m/z": "calc. m/z"})
        self.ui.save_button_pca_coef.setEnabled(True)
        self.ui.lineEdit_exp_var_3.setText(str(round(first_comps, 2)) + "%")

    def save_pca_coef(self):
        """
        Saves the PCA coefficient in a .csv file
        """

        save_path = QtWidgets.QFileDialog.getExistingDirectory()
        if save_path == "":
            return
        save_name, okPressed = QInputDialog.getText(
            self, "Save Name", "Your name:", QLineEdit.Normal, ""
        )
        if save_name == "":
            return

        self.write_csv_df(save_path, save_name + ".csv", self.data_with_coef)

    def plot_HCA(self):
        """
        Hierachical cluster analysis (plot only)
        """
        fig = plt.figure()
        item_file = self.ui.list_loaded_file_2.selectedItems()
        if not item_file:
            return
        item = item_file[0]
        data_selected = item.data(self.USERDATA_ROLE)
        hca_data = data_selected.pca_data.filter(like="Rel")
        hca_data = hca_data.transpose()
        model = AgglomerativeClustering(distance_threshold=True, n_clusters=None)
        labelist = hca_data.index.values.tolist()
        for i in range(len(labelist)):
            labelist[i] = labelist[i].replace("Rel_intens_", "")
            labelist[i] = labelist[i].replace(".csv", "")
        ##set intensity##
        if self.ui.hca_intensity_classic.isChecked():
            hca_data = hca_data
        if self.ui.hca_intensity_sqrt.isChecked():
            hca_data = np.sqrt(hca_data)
        ##set orientation##
        if self.ui.hca_orientation_left.isChecked():
            orientation = "left"
            plt.xlabel("Euclidean distance")
            val = 0
        if self.ui.hca_orientation_top.isChecked():
            orientation = "top"
            plt.ylabel("Euclidean distance")
            val = 90
        model = model.fit(hca_data)
        plt.title("Hierarchical Clustering Dendrogram")
        plot_dendrogram(
            model,
            truncate_mode="lastp",
            p=len(hca_data.index.values),
            labels=labelist,
            orientation=orientation,
        )
        mngr = plt.get_current_fig_manager()
        plt.xticks(rotation=val)
        mngr.window.setGeometry(self.pos().x() + 640, self.pos().y() + 200, 640, 545)
        plt.show()
        plt.tight_layout()

    def volcano(self):
        """
        Volcano plots
        """
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        font_size = int(self.ui.font_size.text())
        dot_size = int(self.ui.dot_size.text())
        volc_data = self.volc_data.copy()  # Retrieves data

        list_samp_1 = []  # Sample 1 selection
        for i in self.ui.list_sample_1.selectedItems():
            list_samp_1.append(i.text())

        list_samp_2 = []  # Sample 2 selection
        for j in self.ui.list_sample_2.selectedItems():
            list_samp_2.append(j.text())

        volc_data, string = Make_Volcano(volc_data, list_samp_1, list_samp_2)
        self.ui.lineEdit_tot_spec_volc.setText(string)

        try:
            min_fc = min(volc_data["fc"])
            max_fc = max(volc_data["fc"])
        except:
            QMessageBox.about(self, "FYI box", "No data selected.")
            return
        ####

        self.ui.lineEdit_comp_spec_volc.setText(str(volc_data.shape[0]))
        volc_data.sort_values(by="fc", inplace=True)
        volc_data["p"] = -np.log10(volc_data["p"])
        plt.figure()
        if self.ui.cb_significancy_volc.isChecked():
            if self.ui.cb_005.isChecked():
                pmin = 0.05
            if self.ui.cb_001.isChecked():
                pmin = 0.01
            if self.ui.cb_0001.isChecked():
                pmin = 0.001
        else:
            pmin = 100
        if (
            self.ui.cb_005.isChecked() == False
            and self.ui.cb_001.isChecked() == False
            and self.ui.cb_0001.isChecked() == False
        ):
            pmin = 100
        if self.ui.cb_fc_lim.isChecked():
            fcmin = 1
        else:
            fcmin = 0

        if not self.ui.cb_volc_color.isChecked():
            grey_data_fc = volc_data.drop(volc_data[abs(volc_data["fc"]) > fcmin].index)
            volc_data = pandas.concat([grey_data_fc, volc_data]).drop_duplicates(
                keep=False
            )

            grey_data_p = volc_data.drop(
                volc_data[volc_data["p"] > -np.log10(pmin)].index
            )
            volc_data = pandas.concat([grey_data_p, volc_data]).drop_duplicates(
                keep=False
            )

            grey_data_all = pandas.concat([grey_data_p, grey_data_fc]).drop_duplicates()

            scatter = plot_fun(
                "scatter",
                grey_data_all["fc"],
                grey_data_all["p"],
                d_color="grey",
                alpha=0.5,
            )

        if self.ui.volc_color_classes.isChecked():
            if self.ui.cb_volc_sort.isChecked():
                volc_data.sort_values("family_name", inplace=True)
            for fam in volc_data["family_name"].drop_duplicates():
                plt_ind = volc_data["family_name"] == fam
                to_plot = volc_data[plt_ind]
                scatter = plt.scatter(
                    to_plot["fc"],
                    to_plot["p"],
                    s=dot_size * 0.75,
                    c=to_plot["family_color"].astype(str),
                    label=fam,
                    edgecolor="black",
                    linewidths=0.75,
                    alpha=0.8,
                )
        elif self.ui.volc_color_dbe.isChecked():
            if self.ui.cb_volc_sort.isChecked():
                volc_data.sort_values("DBE", inplace=True)
            scatter = plot_fun(
                "scatter",
                volc_data["fc"],
                volc_data["p"],
                d_color=volc_data["DBE"],
                cmap=self.color_map,
            )
            cbar = plt.colorbar()
            cbar.set_label(
                "DBE",
                labelpad=-2.4 * (font_size),
                rotation=90,
                fontsize=font_size,
                color=self.cm_text_color,
            )
            cbar.ax.tick_params(labelsize=font_size - 2)

        elif self.ui.volc_color_mz.isChecked():
            if self.ui.cb_volc_sort.isChecked():
                volc_data.sort_values("m/z", inplace=True)
            scatter = plot_fun(
                "scatter",
                volc_data["fc"],
                volc_data["p"],
                d_color=volc_data["m/z"],
                cmap=self.color_map,
            )
            cbar = plt.colorbar()
            cbar.set_label(
                "m/z",
                labelpad=-3 * (font_size),
                rotation=90,
                fontsize=font_size,
                color=self.cm_text_color,
            )
            cbar.ax.tick_params(labelsize=font_size - 2)

        elif self.ui.volc_color_oc.isChecked():
            if self.ui.cb_volc_sort.isChecked():
                volc_data.sort_values("O/C", inplace=True)
            scatter = plot_fun(
                "scatter",
                volc_data["fc"],
                volc_data["p"],
                d_color=volc_data["O/C"],
                cmap=self.color_map,
            )
            cbar = plt.colorbar()
            cbar.set_label(
                "O/C",
                labelpad=-3.15 * (font_size),
                rotation=90,
                fontsize=font_size,
                color=self.cm_text_color,
            )
            cbar.ax.tick_params(labelsize=font_size - 2)

        if self.ui.cb_significancy_volc.isChecked():
            if self.ui.cb_005.isChecked():
                plt.axline(
                    (-1, -np.log10(0.05)),
                    (1, -np.log10(0.05)),
                    color="black",
                    ls=(0, (5, 5)),
                    lw=0.8,
                )
                plt.text(
                    max_fc * 1.05,
                    -np.log10(0.05),
                    "*",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                )
            if self.ui.cb_001.isChecked():
                plt.axline(
                    (-1, -np.log10(0.01)),
                    (1, -np.log10(0.01)),
                    color="black",
                    ls=(0, (5, 5)),
                    lw=0.8,
                )
                plt.text(
                    max_fc * 1.03,
                    -np.log10(0.01),
                    "**",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                )
            if self.ui.cb_0001.isChecked():
                plt.axline(
                    (-1, -np.log10(0.001)),
                    (1, -np.log10(0.001)),
                    color="black",
                    ls=(0, (5, 5)),
                    lw=0.8,
                )
                plt.text(
                    max_fc * 1.01,
                    -np.log10(0.001),
                    "***",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                )
        if self.ui.cb_fc_lim.isChecked():
            plt.axline((-1, 0), (-1, 1), color="black", ls=(0, (5, 5)), lw=0.8)
            plt.axline((1, 0), (1, 1), color="black", ls=(0, (5, 5)), lw=0.8)

        plt.xlabel("log2(fold change)", fontsize=font_size - 1)
        plt.ylabel("-log10(p-value)", fontsize=font_size - 1)
        plt.suptitle(
            f"Left :{list_samp_1} \nRight :{list_samp_2}",
            fontsize=font_size * 0.5,
            y=0.95,
            x=0.1,
            horizontalalignment="left",
        )
        plt.legend(fontsize=font_size - 4)
        try:
            volc_data["sum_formula"]
            mplcursors.cursor(multiple=True).connect(
                "add",
                lambda sel: sel.annotation.set_text(
                    volc_data["sum_formula"].iloc[sel.target.index]
                ),
            )
        except:
            try:
                mplcursors.cursor(multiple=True).connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        volc_data["m/z"].iloc[sel.target.index]
                    ),
                )
            except:
                return

        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(self.pos().x() + 640, self.pos().y() + 200, 640, 545)
        plt.show()
