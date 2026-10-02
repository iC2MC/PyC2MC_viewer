from modules.controller_dependencies import *

class MolecularMapsMixin:
    def plot_molecular_carto_DBE(self, gif=False):
        """
        DBE vs C# plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
            plt.close("all")
        sample_1 = self.ui.list_compare_sample_1.currentRow()
        sample_2 = self.ui.list_compare_sample_2.currentRow()
        n_sample = max(self.compared_datas.df["count"])
        if self.ui.radio_fold_rel.isChecked():
            fold_intens_1 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            leg_1 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
        self.compared_datas.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)
        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df["fc"].fillna(2e20, inplace=True)
        p_inf = (self.compared_datas.df["fc"] > 1e20).tolist()
        n_inf = (self.compared_datas.df["fc"] < -1e20).tolist()
        data_inf_pos = self.compared_datas.df[:][p_inf].copy()
        data_inf_neg = self.compared_datas.df[:][n_inf].copy()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        ###

        item_classes = self.ui.list_classes_DBE_compare.selectedItems()
        if not item_classes:
            return

        for item in item_classes:
            data_extract = self.compared_datas.df.drop(
                index=self.compared_datas.df.index[inf_index], axis=0
            ).copy()

            classe_selected = item.data(self.USERDATA_ROLE)

            data_extract = data_extract.sort_values(by=["fc"], ascending=False)
            Intens = data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ].values.reshape(-1, 1)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ] = Intens_scaled
            if classe_selected == "All":
                pass
            else:
                classes_index = self.compared_datas.classes[
                    self.compared_datas.classes["variable"] == classe_selected
                ]
                if "x" in classe_selected:
                    index_classes = self.compared_datas.df[classe_selected] == True
                else:
                    index_classes = (
                        self.compared_datas.df[self.compared_datas.heteroatoms.columns]
                        == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]
                    ).all(1)
                data_extract = data_extract[index_classes]
                data_inf_neg = data_inf_neg[index_classes]
                data_inf_pos = data_inf_pos[index_classes]

            dbe_text = "Even and odd ions"
            if self.ui.radio_even_DBE_compare_2.isChecked():
                data_extract = data_extract.loc[
                    np.where(data_extract["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 1
                ]
                data_inf_neg = data_inf_neg.loc[
                    np.where(data_inf_neg["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 1
                ]
                data_inf_pos = data_inf_pos.loc[
                    np.where(data_inf_pos["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 1
                ]
                dbe_text = "Even ions"
            elif self.ui.radio_odd_DBE_compare_2.isChecked():
                data_extract = data_extract.loc[
                    np.where(data_extract["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 0
                ]
                data_inf_neg = data_inf_neg.loc[
                    np.where(data_inf_neg["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 0
                ]
                data_inf_pos = data_inf_pos.loc[
                    np.where(data_inf_pos["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 0
                ]
                dbe_text = "Odd ions"

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)
            if Intens != []:
                min_max_scaler = preprocessing.MinMaxScaler()
                Intens_scaled = min_max_scaler.fit_transform(Intens)
            else:
                Intens_scaled = Intens
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["fc", "Normalized_intensity"], ascending=[False, True]
            )

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
                if self.ui.CheckBox_size_fc.isChecked():
                    size = self.d_size * frames.data_extract.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_neg = self.d_size * frames.data_inf_neg.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_pos = self.d_size * frames.data_inf_pos.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_2,
                    ].astype(float)
                else:
                    size = self.d_size
                    size_inf_neg = self.d_size
                    size_inf_pos = self.d_size

                if self.ui.fc_all_dbe.isChecked():
                    plot_fun(
                        "scatter",
                        x=frames.data_inf_neg["C"],
                        y=frames.data_inf_neg["DBE"],
                        d_color="#a84ca4",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_neg,
                    )
                    plot_fun(
                        "scatter",
                        x=frames.data_inf_pos["C"],
                        y=frames.data_inf_pos["DBE"],
                        d_color="#0070c0",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_pos,
                    )
                # plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = size)
                plt.scatter(
                    frames.data_extract["C"],
                    frames.data_extract["DBE"],
                    s=size,
                    c=frames.data_extract["fc"],
                    vmin=-8,
                    vmax=8,
                    cmap="RdYlGn",
                    edgecolor="black",
                    linewidths=0.7,
                )

                if self.ui.C_min_DBE_compare.text():
                    C_min = float(self.ui.C_min_DBE_compare.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.C_max_DBE_compare.text():
                    C_max = float(self.ui.C_max_DBE_compare.text())
                    plt.gca().set_xlim(right=C_max)

                if self.ui.DBE_min_DBE_compare.text():
                    DBE_min = float(self.ui.DBE_min_DBE_compare.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if self.ui.DBE_max_DBE_compare.text():
                    DBE_max = float(self.ui.DBE_max_DBE_compare.text())
                    plt.gca().set_ylim(top=DBE_max)
                if self.ui.CheckBox_hap_compare.isChecked():
                    plt.axline((13, 9), (19, 14), color="red", linestyle=(0, (5, 5)))
                if self.ui.CheckBox_fulle_compare.isChecked():
                    plt.axline((0, 1), (2, 3), color="black", linestyle=(0, (5, 5)))
                plt.suptitle(
                    "DBE vs #C (fold change)", fontsize=font_size + 4, y=0.97, x=0.45
                )

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
                        "log2(FC)",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=16,
                    )

                plt.xlabel("#C", fontsize=self.fontsize + 4)
                plt.ylabel("DBE", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                plt.text(
                    0.13,
                    0.9,
                    frames.classe_selected,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=self.fontsize - 1,
                )

                plt.text(
                    0.75,
                    0.9,
                    dbe_text,
                    horizontalalignment="right",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=self.fontsize - 1,
                )

                if self.ui.fc_all_dbe.isChecked():
                    legend_elements = [
                        Patch(
                            facecolor="#a84ca4",
                            edgecolor="k",
                            label=leg_1 + " exclusive",
                        ),
                        Patch(
                            facecolor="#0070c0",
                            edgecolor="k",
                            label=leg_2 + " exclusive",
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
                            frames.data_extract["molecular_formula"].iloc[
                                sel.target.index
                            ]
                            + ", #C = "
                            + str(frames.data_extract["C"].iloc[sel.target.index])
                            + ", DBE = "
                            + str(frames.data_extract["DBE"].iloc[sel.target.index])
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

    def plot_molecular_carto_VK(self, gif=False):
        """
        Van Krevelen plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_1 = self.ui.list_compare_sample_1.currentRow()
        sample_2 = self.ui.list_compare_sample_2.currentRow()
        n_sample = max(self.compared_datas.df["count"])

        if self.ui.radio_fold_rel.isChecked():
            fold_intens_1 = self.compared_datas.df.iloc[
                :,
                self.compared_datas.df.columns.get_loc("count")
                + max(self.compared_datas.df["count"])
                + 1
                + sample_1,
            ].astype(float)
            fold_intens_2 = self.compared_datas.df.iloc[
                :,
                self.compared_datas.df.columns.get_loc("count")
                + max(self.compared_datas.df["count"])
                + 1
                + sample_2,
            ].astype(float)
            leg_1 = str(fold_intens_1.name)
            leg_2 = str(fold_intens_2.name)
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Rel_intens_", "")
            leg_2 = leg_2.replace("Rel_intens_", "")
        else:
            fold_intens_1 = self.compared_datas.df.iloc[
                :, self.compared_datas.df.columns.get_loc("count") + 1 + sample_1
            ].astype(float)
            fold_intens_2 = self.compared_datas.df.iloc[
                :, self.compared_datas.df.columns.get_loc("count") + 1 + sample_2
            ].astype(float)
            leg_1 = str(fold_intens_1.name)
            leg_2 = str(fold_intens_2.name)
            leg_1 = leg_1.replace(".csv", "")
            leg_2 = leg_2.replace(".csv", "")
            leg_1 = leg_1.replace(".xlsx", "")
            leg_2 = leg_2.replace(".xlsx", "")
            leg_1 = leg_1.replace("Abs_intens_", "")
            leg_2 = leg_2.replace("Abs_intens_", "")

        self.compared_datas.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)
        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df["fc"].fillna(2e20, inplace=True)
        p_inf = (self.compared_datas.df["fc"] > 1e20).tolist()
        n_inf = (self.compared_datas.df["fc"] < -1e20).tolist()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        data_inf_p = self.compared_datas.df[:][p_inf]
        data_inf_n = self.compared_datas.df[:][n_inf]
        item_classes = self.ui.list_classes_VK_compare.selectedItems()
        if not item_classes:
            return
        for item in item_classes:
            data_extract = self.compared_datas.df.drop(
                index=self.compared_datas.df.index[inf_index], axis=0
            ).copy()
            classe_selected = item.data(self.USERDATA_ROLE)
            data_extract["Normalized_intensity"] = self.compared_datas.df["fc"]
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )
            if classe_selected == "All":
                pass
            else:
                classes_index = self.compared_datas.classes[
                    self.compared_datas.classes["variable"] == classe_selected
                ]
                if "x" in classe_selected:
                    index_classes = self.compared_datas.df[classe_selected] == True
                else:
                    index_classes = (
                        self.compared_datas.df[self.compared_datas.heteroatoms.columns]
                        == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]
                    ).all(1)
                data_extract = data_extract[index_classes]
                data_inf_p = data_inf_p[index_classes]
                data_inf_n = data_inf_n[index_classes]
            x_axes = self.ui.list_VK_x_2.currentRow()
            y_axes = self.ui.list_VK_y_2.currentRow()

            x_axes, x_axes_p, x_axes_n, y_axes, y_axes_p, y_axes_n, x_label, y_label = (
                Select_Axes_VK_mol(x_axes, y_axes, data_extract, data_inf_p, data_inf_n)
            )

            if self.ui.font_size.text():
                font_size = float(self.ui.font_size.text())
            if self.ui.checkBox_old_figures.isChecked():
                if plt.get_fignums():
                    plt.close("all")
            # if len(data_extract) == 0:
            #     QMessageBox.about(self, "FYI box", f"Something went wrong trying to display {classe_selected}'s data \nNo common attributions")
            #     continue
            data = pandas.DataFrame()
            data.data_extract = data_extract
            data.x_axes = x_axes
            data.y_axes = y_axes
            data.x_axes_n = x_axes_n
            data.y_axes_n = y_axes_n
            data.x_axes_p = x_axes_p
            data.y_axes_p = y_axes_p
            data.classe_selected = classe_selected
            data.data_inf_n = data_inf_n
            data.data_inf_p = data_inf_p
            frames.append(data)

            def Anim(frames, x_label, y_label):
                if gif == False:
                    fig = plt.figure()
                    transf = fig.transFigure
                else:
                    Figure.clear()
                    transf = Figure.transFigure
                self.read_param()
                self.read_param()
                if self.ui.CheckBox_size_fc_vk.isChecked():
                    size = self.d_size * frames.data_extract.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_neg = self.d_size * frames.data_inf_n.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_pos = self.d_size * frames.data_inf_p.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_2,
                    ].astype(float)
                else:
                    size = self.d_size
                    size_inf_neg = self.d_size
                    size_inf_pos = self.d_size

                if self.ui.fc_all_vk.isChecked():
                    plot_fun(
                        "scatter",
                        x=frames.x_axes_n,
                        y=frames.y_axes_n,
                        d_color="purple",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_neg,
                    )
                    plot_fun(
                        "scatter",
                        x=frames.x_axes_p,
                        y=frames.y_axes_p,
                        d_color="blue",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_pos,
                    )

                plot_fun(
                    "scatter",
                    x=frames.x_axes,
                    y=frames.y_axes,
                    d_color=frames.data_extract["Normalized_intensity"],
                    dot_type=self.dot_type,
                    edge=self.edge,
                    cmap="RdYlGn",
                    size=size,
                )

                if self.ui.x_min_VK_compare.text():
                    C_min = float(self.ui.x_min_VK_compare.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_VK_compare.text():
                    C_max = float(self.ui.x_max_VK_compare.text())
                    plt.gca().set_xlim(right=C_max)
                if self.ui.y_min_VK_compare.text():
                    y_min = float(self.ui.y_min_VK_compare.text())
                    plt.gca().set_ylim(bottom=y_min)
                if self.ui.y_max_VK_compare.text():
                    y_max = float(self.ui.y_max_VK_compare.text())
                    plt.gca().set_ylim(top=y_max)
                plt.suptitle("Van Krevelen (fold change)", fontsize=20, y=0.97, x=0.45)
                if len(data.data_extract) != 0:
                    cbar = plt.colorbar(
                        ticks=[
                            min(frames.data_extract["Normalized_intensity"]),
                            max(frames.data_extract["Normalized_intensity"]),
                        ]
                    )
                    cbar.ax.set_yticklabels(
                        [leg_1, leg_2],
                        fontsize=font_size - 2,
                        weight="bold",
                        rotation=-45,
                    )  # vertically oriented colorbar
                    cbar.set_label(
                        "log2(FC)",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                    )
                plt.xlabel(x_label, fontsize=font_size + 4)
                plt.ylabel(y_label, fontsize=font_size + 4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                plt.text(
                    0.13,
                    0.9,
                    frames.classe_selected,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=self.fontsize - 1,
                )

                if self.ui.fc_all_vk.isChecked():
                    legend_elements = [
                        Patch(
                            facecolor="purple",
                            edgecolor="k",
                            label=leg_1 + " exclusive",
                        ),
                        Patch(
                            facecolor="blue", edgecolor="k", label=leg_2 + " exclusive"
                        ),
                    ]
                    plt.legend(handles=legend_elements, fontsize=font_size - 4)
                mngr = plt.get_current_fig_manager()
                mngr.window.setGeometry(
                    self.pos().x() + 640, self.pos().y() + 200, 800, 680
                )
                mplcursors.cursor(multiple=True).connect(
                    "add",
                    lambda sel: sel.annotation.set_text(
                        frames.data_extract["molecular_formula"].iloc[sel.target.index]
                        + ", "
                        + str(x_label)
                        + " : "
                        + str(round(frames.x_axes.iloc[sel.target.index], 4))
                        + ", "
                        + str(y_label)
                        + " = "
                        + str(round(frames.y_axes.iloc[sel.target.index], 4))
                    ),
                )

        if gif == False:
            for i in frames:
                Anim(i, x_label, y_label)
            plt.show()
        else:
            Figure = plt.figure()
            plt.show()
            anim_created = FuncAnimation(
                Figure,
                Anim,
                frames,
                farg=(
                    x_label,
                    y_label,
                ),
                interval=1000 / self.fps,
            )
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(
                self.pos().x() + 940, self.pos().y() + 200, 800, 680
            )
            writergif = PillowWriter(fps=self.fps)
            anim_created.save("animation.gif", writer=writergif)
            plt.ion()

    def plot_molecular_carto_KMD(self, gif=False):
        """
        KMD plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
            plt.close("all")
        sample_1 = self.ui.list_compare_sample_1.currentRow()
        sample_2 = self.ui.list_compare_sample_2.currentRow()
        n_sample = max(self.compared_datas.df["count"])
        if self.ui.radio_fold_rel_KMD.isChecked():
            fold_intens_1 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            leg_1 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
        self.compared_datas.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)

        # KMD calculation
        if self.ui.edit_mass_motif_compare.text():
            repetive_unit_mass = float(self.ui.edit_mass_motif_compare.text())
            nominal_unit = round(repetive_unit_mass)
        self.compared_datas.df["Kendrick mass"] = self.compared_datas.df["m/z"] * (
            nominal_unit / repetive_unit_mass
        )
        self.compared_datas.df["Kendrick nominal mass"] = round(
            self.compared_datas.df["m/z"]
        )

        if self.ui.round_up_compare.isChecked():
            self.compared_datas.df["Kendrick nominal mass"] = self.compared_datas.df[
                "Kendrick mass"
            ].apply(np.ceil)
        elif self.ui.round_closest_compare.isChecked():
            self.compared_datas.df["Kendrick nominal mass"] = round(
                self.compared_datas.df["Kendrick mass"]
            )
        self.compared_datas.df["Kendrick mass defect"] = (
            self.compared_datas.df["Kendrick nominal mass"]
            - self.compared_datas.df["Kendrick mass"]
        )

        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df["fc"].fillna(2e20, inplace=True)
        p_inf = (self.compared_datas.df["fc"] > 1e20).tolist()
        n_inf = (self.compared_datas.df["fc"] < -1e20).tolist()
        data_inf_pos = self.compared_datas.df[:][p_inf].copy()
        data_inf_neg = self.compared_datas.df[:][n_inf].copy()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        ###

        item_classes = self.ui.list_classes_KMD_compare.selectedItems()
        if not item_classes:
            return

        for item in item_classes:
            data_extract = self.compared_datas.df.drop(
                index=self.compared_datas.df.index[inf_index], axis=0
            ).copy()

            classe_selected = item.data(self.USERDATA_ROLE)

            data_extract = data_extract.sort_values(by=["fc"], ascending=False)
            Intens = data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ].values.reshape(-1, 1)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ] = Intens_scaled
            if classe_selected == "All":
                pass
            else:
                classes_index = self.compared_datas.classes[
                    self.compared_datas.classes["variable"] == classe_selected
                ]
                if "x" in classe_selected:
                    index_classes = self.compared_datas.df[classe_selected] == True
                else:
                    index_classes = (
                        self.compared_datas.df[self.compared_datas.heteroatoms.columns]
                        == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]
                    ).all(1)
                data_extract = data_extract[index_classes]
                data_inf_neg = data_inf_neg[index_classes]
                data_inf_pos = data_inf_pos[index_classes]

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)
            if Intens != []:
                min_max_scaler = preprocessing.MinMaxScaler()
                Intens_scaled = min_max_scaler.fit_transform(Intens)
            else:
                Intens_scaled = Intens
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["fc", "Normalized_intensity"], ascending=[False, True]
            )

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
                if self.ui.CheckBox_size_fc_kmd.isChecked():
                    size = self.d_size * frames.data_extract.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_neg = self.d_size * frames.data_inf_neg.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_pos = self.d_size * frames.data_inf_pos.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_2,
                    ].astype(float)
                else:
                    size = self.d_size
                    size_inf_neg = self.d_size
                    size_inf_pos = self.d_size

                if self.ui.fc_all_kmd.isChecked():
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

                if self.ui.x_min_KMD_compare.text():
                    x_min = float(self.ui.x_min_KMD_compare.text())
                    plt.gca().set_xlim(left=x_min)
                if self.ui.x_max_KMD_compare.text():
                    x_max = float(self.ui.x_max_KMD_compare.text())
                    plt.gca().set_xlim(right=x_max)

                if self.ui.y_min_KMD_compare.text():
                    y_min = float(self.ui.y_min_KMD_compare.text())
                    plt.gca().set_ylim(bottom=y_min)
                if self.ui.y_max_KMD_compare.text():
                    y_max = float(self.ui.y_max_KMD_compare.text())
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
                        "log2(FC)",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=16,
                    )

                plt.xlabel("Nominal mass", fontsize=self.fontsize + 4)
                plt.ylabel("KMD", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                plt.text(
                    0.13,
                    0.9,
                    frames.classe_selected,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=self.fontsize - 1,
                )

                if self.ui.fc_all_kmd.isChecked():
                    legend_elements = [
                        Patch(
                            facecolor="#a84ca4",
                            edgecolor="k",
                            label=leg_1 + " exclusive",
                        ),
                        Patch(
                            facecolor="#0070c0",
                            edgecolor="k",
                            label=leg_2 + " exclusive",
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
                            frames.data_extract["molecular_formula"].iloc[
                                sel.target.index
                            ]
                            + ", m/z = "
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

    def plot_molecular_carto_MD(self, gif=False):
        """
        KMD plot for the compare menu
        """
        frames = []
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked() and plt.get_fignums():
            plt.close("all")
        sample_1 = self.ui.list_compare_sample_1.currentRow()
        sample_2 = self.ui.list_compare_sample_2.currentRow()
        n_sample = max(self.compared_datas.df["count"])
        if self.ui.radio_fold_rel_md.isChecked():
            fold_intens_1 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            fold_intens_2 = (
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_2,
                ]
                .values.astype(float)
                .copy()
                .reshape(-1, 1)
            )
            leg_1 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
                    + 1
                    + sample_1,
                ].name
            )
            leg_2 = str(
                self.compared_datas.df.iloc[
                    :,
                    self.compared_datas.df.columns.get_loc("count")
                    + max(self.compared_datas.df["count"])
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
        self.compared_datas.df["fc"] = np.log2(fold_intens_2 / fold_intens_1)

        # MD calculation
        nominal_mass = round(self.compared_datas.df["m/z"])
        mass_defect = self.compared_datas.df["m/z"] - nominal_mass
        self.compared_datas.df["nominal_mass"] = nominal_mass
        self.compared_datas.df["mass_defect"] = mass_defect

        ####
        # Excluding infinite and NaN values (attribution in neither of the sample)
        self.compared_datas.df["fc"].fillna(2e20, inplace=True)
        p_inf = (self.compared_datas.df["fc"] > 1e20).tolist()
        n_inf = (self.compared_datas.df["fc"] < -1e20).tolist()
        data_inf_pos = self.compared_datas.df[:][p_inf].copy()
        data_inf_neg = self.compared_datas.df[:][n_inf].copy()
        inf_index = [i or j for i, j in zip(n_inf, p_inf)]
        ###

        item_classes = self.ui.list_classes_MD_compare.selectedItems()
        if not item_classes:
            return

        for item in item_classes:
            data_extract = self.compared_datas.df.drop(
                index=self.compared_datas.df.index[inf_index], axis=0
            ).copy()

            classe_selected = item.data(self.USERDATA_ROLE)

            data_extract = data_extract.sort_values(by=["fc"], ascending=False)
            Intens = data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ].values.reshape(-1, 1)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract.iloc[
                :, self.compared_datas.df.columns.get_loc("summed_intensity") - 2
            ] = Intens_scaled
            if classe_selected == "All":
                pass
            else:
                classes_index = self.compared_datas.classes[
                    self.compared_datas.classes["variable"] == classe_selected
                ]
                if "x" in classe_selected:
                    index_classes = self.compared_datas.df[classe_selected] == True
                else:
                    index_classes = (
                        self.compared_datas.df[self.compared_datas.heteroatoms.columns]
                        == self.compared_datas.heteroatoms.iloc[classes_index.index[0]]
                    ).all(1)
                data_extract = data_extract[index_classes]
                data_inf_neg = data_inf_neg[index_classes]
                data_inf_pos = data_inf_pos[index_classes]

            Intens = data_extract["Normalized_intensity"].values.reshape(-1, 1)
            if Intens != []:
                min_max_scaler = preprocessing.MinMaxScaler()
                Intens_scaled = min_max_scaler.fit_transform(Intens)
            else:
                Intens_scaled = Intens
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["fc", "Normalized_intensity"], ascending=[False, True]
            )

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
                if self.ui.CheckBox_size_fc_md.isChecked():
                    size = self.d_size * frames.data_extract.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_neg = self.d_size * frames.data_inf_neg.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_1,
                    ].astype(float)
                    size_inf_pos = self.d_size * frames.data_inf_pos.iloc[
                        :,
                        self.compared_datas.df.columns.get_loc("summed_intensity")
                        - (n_sample)
                        + sample_2,
                    ].astype(float)
                else:
                    size = self.d_size
                    size_inf_neg = self.d_size
                    size_inf_pos = self.d_size

                if self.ui.fc_all_md.isChecked():
                    plot_fun(
                        "scatter",
                        x=frames.data_inf_neg["nominal_mass"],
                        y=frames.data_inf_neg["mass_defect"],
                        d_color="#a84ca4",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_neg,
                    )
                    plot_fun(
                        "scatter",
                        x=frames.data_inf_pos["nominal_mass"],
                        y=frames.data_inf_pos["mass_defect"],
                        d_color="#0070c0",
                        dot_type=self.dot_type,
                        edge=self.edge,
                        size=size_inf_pos,
                    )
                # plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlGn",size = size)
                plt.scatter(
                    frames.data_extract["nominal_mass"],
                    frames.data_extract["mass_defect"],
                    s=size,
                    c=frames.data_extract["fc"],
                    vmin=-8,
                    vmax=8,
                    cmap="RdYlGn",
                    edgecolor="black",
                    linewidths=0.7,
                )

                if self.ui.x_min_MD_compare.text():
                    x_min = float(self.ui.x_min_MD_compare.text())
                    plt.gca().set_xlim(left=x_min)
                if self.ui.x_max_MD_compare.text():
                    x_max = float(self.ui.x_max_MD_compare.text())
                    plt.gca().set_xlim(right=x_max)

                if self.ui.y_min_MD_compare.text():
                    y_min = float(self.ui.y_min_MD_compare.text())
                    plt.gca().set_ylim(bottom=y_min)
                if self.ui.y_max_MD_compare.text():
                    y_max = float(self.ui.y_max_MD_compare.text())
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
                        "log2(FC)",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=16,
                    )

                plt.xlabel("Nominal mass", fontsize=self.fontsize + 4)
                plt.ylabel("Mass defect", fontsize=self.fontsize + 4)
                plt.xticks(fontsize=self.fontsize)
                plt.yticks(fontsize=self.fontsize)
                plt.text(
                    0.13,
                    0.9,
                    frames.classe_selected,
                    horizontalalignment="left",
                    verticalalignment="center",
                    transform=transf,
                    fontsize=self.fontsize - 1,
                )

                if self.ui.fc_all_md.isChecked():
                    legend_elements = [
                        Patch(
                            facecolor="#a84ca4",
                            edgecolor="k",
                            label=leg_1 + " exclusive",
                        ),
                        Patch(
                            facecolor="#0070c0",
                            edgecolor="k",
                            label=leg_2 + " exclusive",
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
                            frames.data_extract["molecular_formula"].iloc[
                                sel.target.index
                            ]
                            + ", m/z = "
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

    def plot_DBE_compare(self, gif=False):
        """
        DBE vs C# plots
        """

        frames = []
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = self.ui.list_classes_DBE_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")

        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns
        for item in sample_list:
            if not item_classes:
                return
            if "PC1" in data_selected:
                self.ui.radio_color_pc1_comp.show()
                self.ui.radio_color_pc2_comp.show()
            data_extract = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#
            data_extract.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_extract.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            Intens = (
                data_extract["Normalized_intensity"].values.astype(float).reshape(-1, 1)
            )  # astype(float) or crash!
            if self.ui.check_classic_comp.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_comp.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )

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

            if self.ui.radio_even_DBE_comp.isChecked():
                data_extract = data_extract.loc[
                    np.where(data_extract["DBE"].apply(lambda x: x.is_integer()), 0, 1)
                    == 1
                ]
                dbe_text = "Even ions"
            elif self.ui.radio_odd_DBE_comp.isChecked():
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

            if self.ui.radio_color_intensity_comp.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc1_comp.isChecked():
                third_dimension = data_extract["PC1"]
            elif self.ui.radio_color_pc2_comp.isChecked():
                third_dimension = data_extract["PC2"]
            elif self.ui.radio_color_O_comp.isChecked():
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

                if self.ui.C_min_DBE_comp.text():
                    C_min = float(self.ui.C_min_DBE_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.C_max_DBE_comp.text():
                    C_max = float(self.ui.C_max_DBE_comp.text())
                    plt.gca().set_xlim(right=C_max)
                else:
                    C_max = data_selected.df["C"][data_selected.df["C"].idxmax()]
                if self.ui.DBE_min_DBE_comp.text():
                    DBE_min = float(self.ui.DBE_min_DBE_comp.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if self.ui.DBE_max_DBE_comp.text():
                    DBE_max = float(self.ui.DBE_max_DBE_comp.text())
                    plt.gca().set_ylim(top=DBE_max)
                else:
                    DBE_max = frames["DBE"][frames["DBE"].idxmax()]
                if self.ui.CheckBox_hap_comp.isChecked():
                    plt.axline(
                        (13, 8.57), (19, 12.95), color="red", linestyle=(0, (5, 5))
                    )
                if self.ui.CheckBox_fulle_comp.isChecked():
                    plt.axline((0, 1), (2, 3), color="black", linestyle=(0, (5, 5)))
                plt.suptitle(
                    f"{frames.classe_selected}", fontsize=font_size + 4, y=0.95, x=0.45
                )
                cbar = plt.colorbar()
                if self.ui.radio_color_intensity_comp.isChecked():
                    cbar.set_label(
                        "Normalized Intensity",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc1_comp.isChecked():
                    cbar.set_label(
                        "PC1",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc2_comp.isChecked():
                    cbar.set_label(
                        "PC2",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )

                cbar.ax.tick_params(labelsize=font_size - 2)
                if self.ui.radio_color_pc1_comp.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC1"]), np.max(data_selected.df["PC1"])
                    )
                elif self.ui.radio_color_pc2_comp.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC2"]), np.max(data_selected.df["PC2"])
                    )
                plt.xlabel("#C", fontsize=font_size + 4)
                plt.ylabel("DBE", fontsize=font_size + 4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                name = frames.sample_name
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                plt.text(
                    0.12,
                    0.9,
                    name,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
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

    def plot_VK_compare(self, gif=False):
        """
        Van Krevelen plot
        """

        frames = []
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = self.ui.list_classes_VK_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        self.read_param()
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns
        for item in sample_list:
            if not item_classes:
                return
            if "PC1" in data_selected:
                self.ui.radio_color_pc1_VK_comp.show()
                self.ui.radio_color_pc2_VK_comp.show()

            data_filtered = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            data_filtered.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_filtered.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            Intens = (
                data_filtered["Normalized_intensity"]
                .values.astype(float)
                .reshape(-1, 1)
            )  # astype(float) or crash!
            if self.ui.check_classic_vk_comp.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_vk_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_vk_comp.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value, log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled

            dot_size = self.d_size
            x_axes = self.ui.list_VK_x_comp.currentRow()
            y_axes = self.ui.list_VK_y_comp.currentRow()

            # Tests the presence of sulfur
            if x_axes == 2 or y_axes == 3:
                try:
                    test = data_filtered["S/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(
                        self,
                        "Error",
                        "No sulfur in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.",
                    )
            # Tests the presence of oxygen
            if x_axes == 0 or y_axes == 1:
                try:
                    test = data_filtered["O/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(
                        self,
                        "Error",
                        "No oxygen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.",
                    )
            # Tests the presence of nitrogen
            if x_axes == 1 or y_axes == 2:
                try:
                    test = data_filtered["N/C"]
                    del test
                except:
                    x_axes = 3
                    y_axes = 0
                    QMessageBox.about(
                        self,
                        "Error",
                        "No nitrogen in the selected data, (H/C)=f[(H/C)] will be plotted instead to avoid crash.",
                    )

            # Tests the presence of hydrogen
            if x_axes == 3 or y_axes == 0:
                try:
                    test = data_filtered["H/C"]
                    del test
                except:
                    QMessageBox.about(self, "Error", "No hydrogen in the selected data")
                    continue

            (
                x_axes,
                y_axes,
                x_label,
                y_label,
            ) = Select_Axes_VK(x_axes, y_axes, data_filtered)

            if self.ui.radio_color_pc1_VK_comp.isChecked():
                third_dimension = data_filtered["PC1"]
            elif self.ui.radio_color_pc2_VK_comp.isChecked():
                third_dimension = data_filtered["PC2"]
            elif self.ui.radio_color_O_vk_comp.isChecked():
                third_dimension = data_filtered["O"]
            else:
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
                frames.sort_values(
                    by=["third_dimension", "Normalized_intensity"],
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

                if self.ui.x_min_VK_comp.text():
                    C_min = float(self.ui.x_min_VK_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_VK_comp.text():
                    C_max = float(self.ui.x_max_VK_comp.text())
                    plt.gca().set_xlim(right=C_max)
                if self.ui.y_min_VK_comp.text():
                    DBE_min = float(self.ui.y_min_VK_comp.text())
                    plt.gca().set_ylim(bottom=DBE_min)
                if self.ui.y_max_VK_comp.text():
                    DBE_max = float(self.ui.y_max_VK_comp.text())
                    plt.gca().set_ylim(top=DBE_max)
                plt.suptitle(
                    f"{frames.classe_selected}", fontsize=font_size + 4, y=0.95, x=0.45
                )
                cbar = plt.colorbar()
                if self.ui.radio_color_intensity_comp_2.isChecked():
                    cbar.set_label(
                        "Normalized Intensity",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc1_VK_comp.isChecked():
                    cbar.set_label(
                        "PC1",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_pc2_VK_comp.isChecked():
                    cbar.set_label(
                        "PC2",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                elif self.ui.radio_color_O_vk_comp.isChecked():
                    cbar.set_label(
                        "#O",
                        labelpad=-2.625 * (font_size),
                        rotation=90,
                        fontsize=font_size,
                        color=self.cm_text_color,
                    )
                cbar.ax.tick_params(labelsize=font_size - 2)
                if self.ui.radio_color_pc1_VK_comp.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC1"]), np.max(data_selected.df["PC1"])
                    )
                elif self.ui.radio_color_pc2_VK_comp.isChecked():
                    plt.clim(
                        np.min(data_selected.df["PC2"]), np.max(data_selected.df["PC2"])
                    )
                plt.xlabel(frames.x_label, fontsize=font_size + 4)
                plt.ylabel(frames.y_label, fontsize=font_size + 4)
                plt.xticks(fontsize=font_size)
                plt.yticks(fontsize=font_size)
                name = frames.sample_name
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                plt.text(
                    0.12,
                    0.9,
                    name,
                    horizontalalignment="left",
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
                            + ", "
                            + str(x_label)
                            + " : "
                            + str(round(x_axes.iloc[sel.target.index], 4))
                            + ", "
                            + str(y_label)
                            + " = "
                            + str(round(y_axes.iloc[sel.target.index], 4))
                        ),
                    )
                if (
                    self.ui.checkBox_vk_area_comp.isChecked()
                    and self.ui.list_VK_x_comp.currentRow() == 0
                    and self.ui.list_VK_y_comp.currentRow() == 0
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

    def plot_KMD_compare(self, gif=False):
        """
        Classic Kendrick plots
        """

        frames = []
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")

        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns
        self.read_param()
        dot_size = self.d_size
        font_size = self.fontsize
        if self.ui.stackedWidget_Kendrick_comp.currentIndex() == 0:  # KMD classic
            item_classes = self.ui.list_classes_Kendrick_comp.selectedItems()[0]
        elif self.ui.stackedWidget_Kendrick_comp.currentIndex() == 1:  # MD
            item_classes = self.ui.list_classes_Kendrick_univ_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)

        #### KMD & MD vs m/z ####

        if not item_classes:
            return

        for item in sample_list:
            data_filtered = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            # KMD calculation
            if self.ui.edit_motif_comp.text():
                edit_repetive_unit = self.ui.edit_motif_comp.text()
            if self.ui.edit_mass_motif_comp.text():
                repetive_unit_mass = float(self.ui.edit_mass_motif_comp.text())
                nominal_unit = round(repetive_unit_mass)
            data_filtered["Kendrick mass"] = data_filtered["m/z"] * (
                nominal_unit / repetive_unit_mass
            )
            data_filtered["Kendrick nominal mass"] = round(data_filtered["m/z"])

            if self.ui.roundUp_comp.isChecked():
                data_filtered["Kendrick nominal mass"] = data_filtered[
                    "Kendrick mass"
                ].apply(np.ceil)
            elif self.ui.roundClosest_comp.isChecked():
                data_filtered["Kendrick nominal mass"] = round(
                    data_filtered["Kendrick mass"]
                )
            data_filtered["Kendrick mass defect"] = (
                data_filtered["Kendrick nominal mass"] - data_filtered["Kendrick mass"]
            )

            data_filtered.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_filtered.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            Intens = (
                data_filtered["Normalized_intensity"]
                .values.astype(float)
                .reshape(-1, 1)
            )  # astype(float) or crash!
            if self.ui.classic_intens_K_comp.isChecked():
                Intens = Intens
            if self.ui.sqrt_intens_K_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.log_intens_K_comp.isChecked():
                Intens = np.log10(Intens + 1e-10)
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_filtered["Normalized_intensity"] = Intens_scaled
            data_filtered = data_filtered.sort_values(
                by=["Normalized_intensity"], ascending=True
            )

            nominal_mass = round(data_filtered["m/z"])
            mass_defect = data_filtered["m/z"] - nominal_mass
            data_filtered["nominal_mass"] = nominal_mass
            data_filtered["mass_defect"] = mass_defect

            # -----------------------------------#
            #  Normalization on selected class  #
            # -----------------------------------#
            if self.ui.radioButton_norm_d.isChecked():
                data_filtered["Normalized_intensity"], error = Normalize(
                    data_filtered["Normalized_intensity"]
                )
                if error == 1:
                    QMessageBox.about(
                        self,
                        "Error",
                        f"No species to be displayed for the class : {classe_selected}.",
                    )
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

                if (
                    self.ui.stackedWidget_Kendrick_comp.currentIndex() == 0
                ):  # KMD classic
                    x_data = frames["Kendrick nominal mass"]
                    y_data = frames["Kendrick mass defect"]
                    x_label = "Kendrick nominal mass"
                    y_label = "Kendrick mass defect"

                if self.ui.stackedWidget_Kendrick_comp.currentIndex() == 0:
                    x_data = frames["Kendrick nominal mass"]
                    y_data = frames["Kendrick mass defect"]
                    x_label = "Kendrick nominal mass"
                    y_label = "Kendrick mass defect"
                elif self.ui.stackedWidget_Kendrick_comp.currentIndex() == 1:
                    x_data = frames["nominal_mass"]
                    y_data = frames["mass_defect"]
                    x_label = "Nominal mass"
                    y_label = "Mass defect"

                color_options = {
                    "K_intensity_comp": "Normalized_intensity",
                    "K_oxygen_comp": "O",
                    "K_nitrogen_comp": "N",
                    "K_sulfur_comp": "S",
                    "K_intensity_univ_comp": "Normalized_intensity",
                    "K_oxygen_univ_comp": "O",
                    "K_nitrogen_univ_comp": "N",
                    "K_sulfur_univ_comp": "S",
                }
                try:
                    third_dimension = None
                    for option, column_name in color_options.items():
                        if getattr(self.ui, option).isChecked():
                            third_dimension = frames[column_name]
                            break
                    plot_fun(
                        "scatter",
                        x=x_data,
                        y=y_data,
                        d_color=third_dimension,
                        size=1.5 * dot_size * frames["Normalized_intensity"],
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
                    if self.ui.K_intensity_univ.isChecked():
                        cbar.set_label(
                            "Normalized Intensity",
                            labelpad=-2.625 * (font_size),
                            rotation=90,
                            fontsize=font_size,
                            color=self.cm_text_color,
                        )
                    if self.ui.K_nitrogen_univ.isChecked():
                        cbar.set_label(
                            "Nitrogen number",
                            labelpad=-2.625 * (font_size),
                            rotation=90,
                            fontsize=font_size,
                            color=self.cm_text_color,
                        )
                    if self.ui.K_oxygen_univ.isChecked():
                        cbar.set_label(
                            "Oxygen number",
                            labelpad=-2.625 * (font_size),
                            rotation=90,
                            fontsize=font_size,
                            color=self.cm_text_color,
                        )
                    if self.ui.K_sulfur_univ.isChecked():
                        cbar.set_label(
                            "Sulfur number",
                            labelpad=-2.625 * (font_size),
                            rotation=90,
                            fontsize=font_size,
                            color=self.cm_text_color,
                        )
                    cbar.ax.tick_params(labelsize=font_size - 2)
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
                    name = frames.sample_name
                    name = name.replace("Rel_intens_", "")
                    name = name.replace(".csv", "")
                    name = name.replace(".xlsx", "")
                    plt.text(
                        0.12,
                        0.9,
                        name,
                        horizontalalignment="left",
                        verticalalignment="center",
                        fontsize=font_size - 1,
                        transform=transf,
                    )

                    plt.text(
                        0.68,
                        0.9,
                        f"{frames.classe_selected}",
                        horizontalalignment="right",
                        verticalalignment="center",
                        transform=transf,
                        fontsize=font_size + 2,
                    )
                    if gif == False:
                        mngr = plt.get_current_fig_manager()
                        mngr.window.setGeometry(
                            self.pos().x() + 940, self.pos().y() + 200, 640, 545
                        )
                except:
                    QMessageBox.about(
                        self, "Error", "This heteroatom is not in datasets"
                    )
                    pass

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
        return data_filtered

    def envt_selector_compare(self, gif=False):
        """
        Selects the appropriate environmental variable to plot
        """
        self.read_param()
        try:
            if self.ui.radio_ACOS_comp.isChecked():
                self.plot_ACOS_compare(gif)
            elif self.ui.radio_MAI_comp.isChecked():
                self.plot_MAI_compare(gif)
            elif self.ui.radio_MCR_comp.isChecked():
                self.plot_MCR_compare(gif)
        except:
            pass

    def plot_ACOS_compare(self, gif=False):
        """
        Average carbon oxydation plot
        """
        frames = []
        font_size = self.fontsize
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = self.ui.list_classes_ACOS_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")

        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns

        for item in sample_list:
            data_extract = data_selected.copy()
            nc = self.ui.nc_box_comp.isChecked()

            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#
            data_extract = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            data_extract.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_extract.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            if self.ui.radio_color_intensity_ACOS_comp.isChecked():
                third_dimension = data_extract["Normalized_intensity"]
                intens_for_size = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc1_ACOS_comp.isChecked():
                third_dimension = data_extract["PC1"]
                third_dimension = third_dimension + 1
                intens_for_size = data_extract["Normalized_intensity"]
            elif self.ui.radio_color_pc2_ACOS_comp.isChecked():
                third_dimension = data_extract["PC2"]
                third_dimension = third_dimension + 1
                intens_for_size = data_extract["Normalized_intensity"]

            Intens = third_dimension.values.astype(float).reshape(-1, 1)

            if self.ui.check_classic_ACOS_comp.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_ACOS_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_ACOS_comp.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract["point_size"] = intens_for_size
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )

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
                name = frames.sample_name
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                plt.text(
                    0.12,
                    0.9,
                    name,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )

                plt.gca().invert_xaxis()
                if self.ui.x_min_ACOS_comp.text():
                    C_min = float(self.ui.x_min_ACOS_comp.text())
                    plt.gca().set_xlim(right=C_min)
                if self.ui.x_max_ACOS_comp.text():
                    C_max = float(self.ui.x_max_ACOS_comp.text())
                    plt.gca().set_xlim(left=C_max)
                plt.text(
                    0.68,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="right",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_ACOS_comp.text():
                    ACOS_min = float(self.ui.y_min_ACOS_comp.text())
                    plt.gca().set_ylim(bottom=ACOS_min)
                if self.ui.y_max_ACOS_comp.text():
                    ACOS_max = float(self.ui.y_max_ACOS_comp.text())
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
                        self.pos().x() + 940, self.pos().y() + 200, 640, 545
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

    def plot_MAI_compare(self, gif=False):
        """
        Plot a Van Krevelen diagram with the modified aromaticity index as the color coding variable
        """
        frames = []
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = self.ui.list_classes_MAI_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        font_size = self.fontsize
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")

        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns

        for item in sample_list:
            data_extract = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )

            if not "S" in data_extract:
                data_extract["S"] = 0
            if not "P" in data_extract:
                data_extract["P"] = 0
            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            data_extract.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_extract.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            Intens = (
                data_extract["Normalized_intensity"].values.astype(float).reshape(-1, 1)
            )  # astype(float) or crash!

            if self.ui.check_classic_MAI_comp.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_MAI_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_MAI_comp.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
            )

            if self.ui.MAI_box_comp.isChecked():
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
                name = frames.sample_name
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                plt.text(
                    0.12,
                    0.9,
                    name,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )

                if self.ui.x_min_MAI_comp.text():
                    C_min = float(self.ui.x_min_MAI_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_MAI_comp.text():
                    C_max = float(self.ui.x_max_MAI_comp.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(
                    0.68,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="right",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_MAI_comp.text():
                    MAI_min = float(self.ui.y_min_MAI_comp.text())
                    plt.gca().set_ylim(bottom=MAI_min)
                if self.ui.y_max_MAI_comp.text():
                    MAI_max = float(self.ui.y_max_MAI_comp.text())
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

    def plot_MCR_compare(self, gif=False):
        """
        Plot a Van Krevelen diagram with the maximum carbonyl ratio as the color coding variable
        """
        frames = []
        font_size = self.fontsize
        item_count = len(self.ui.list_loaded_file_compare.selectedItems())
        data_selected = self.compared_datas.df.copy()
        item_classes = self.ui.list_classes_MCR_comp.selectedItems()[0]
        classe_selected = item_classes.data(self.USERDATA_ROLE)
        if self.ui.checkBox_old_figures.isChecked():
            if plt.get_fignums():
                plt.close("all")
        sample_list = data_selected.iloc[
            :,
            data_selected.columns.get_loc("count")
            + item_count
            + 1 : data_selected.columns.get_loc("count")
            + item_count * 2
            + 1,
        ].columns

        if not item_classes:
            return
        for item in sample_list:
            data_extract = Select_classe(
                classe_selected,
                data_selected,
                self.compared_datas.heteroatoms,
                self.compared_datas.classes,
            )
            if not "S" in data_extract:
                data_extract["S"] = 0
            if not "P" in data_extract:
                data_extract["P"] = 0

            # -----------------------------#
            #  3rd dimension selection    #
            # -----------------------------#

            data_extract.drop(["Normalized_intensity"], axis=1, inplace=True)
            data_extract.rename(
                columns={item: "Normalized_intensity"}, inplace=True
            )  # item_name.csv => Normalized intensity

            Intens = (
                data_extract["Normalized_intensity"].values.astype(float).reshape(-1, 1)
            )  # astype(float) or crash!

            if self.ui.check_classic_MCR_comp.isChecked():
                Intens = Intens
            if self.ui.check_sqrt_MCR_comp.isChecked():
                Intens = np.sqrt(Intens)
            if self.ui.check_log_MCR_comp.isChecked():
                Intens = np.log10(
                    Intens + 1e-10
                )  # Avoid having a null value log(0)=error math
            min_max_scaler = preprocessing.MinMaxScaler()
            Intens_scaled = min_max_scaler.fit_transform(Intens)
            data_extract["Normalized_intensity"] = Intens_scaled
            data_extract = data_extract.sort_values(
                by=["Normalized_intensity"], ascending=True
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
                name = frames.sample_name
                name = name.replace("Rel_intens_", "")
                name = name.replace(".csv", "")
                name = name.replace(".xlsx", "")
                plt.text(
                    0.12,
                    0.9,
                    name,
                    horizontalalignment="left",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )

                if self.ui.x_min_MCR_comp.text():
                    C_min = float(self.ui.x_min_MCR_comp.text())
                    plt.gca().set_xlim(left=C_min)
                if self.ui.x_max_MCR_comp.text():
                    C_max = float(self.ui.x_max_MCR_comp.text())
                    plt.gca().set_xlim(right=C_max)
                plt.text(
                    0.68,
                    0.9,
                    f"{frames.classe_selected}",
                    horizontalalignment="right",
                    verticalalignment="center",
                    fontsize=font_size - 1,
                    transform=transf,
                )
                if self.ui.y_min_MCR_comp.text():
                    MCR_min = float(self.ui.y_min_MCR_comp.text())
                    plt.gca().set_ylim(bottom=MCR_min)
                if self.ui.y_max_MCR_comp.text():
                    MCR_max = float(self.ui.y_max_MCR_comp.text())
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
