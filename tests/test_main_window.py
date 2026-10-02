import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import QtCore, QtWidgets
import matplotlib.pyplot as plt

import main


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.settings_directory = tempfile.TemporaryDirectory()
        QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
        QtCore.QSettings.setPath(
            QtCore.QSettings.IniFormat,
            QtCore.QSettings.UserScope,
            self.settings_directory.name,
        )
        defaults = [
            ("def", "def", "false"),
            ("ExitConfirm", "ExitConfirm", "false"),
            ("Minimize", "Minimize", "true"),
            ("FontSize", "DotSize", "130"),
            ("FontSize", "FontSize", "16"),
            ("SaveDPI", "SaveDPI", "300"),
            ("FPS", "FPS", "2"),
            ("DotType", "DotType", "size_and_color"),
            ("Colormap", "Colormap", "viridis"),
            ("Edge", "Edge", "true"),
            ("Normalization", "Normalization", "all"),
        ]
        for group, key, value in defaults:
            settings = QtCore.QSettings("PyC2MC", group)
            settings.setValue(key, value)
            settings.sync()

    def tearDown(self):
        self.settings_directory.cleanup()

    def test_window_keeps_existing_ui_and_domain_actions(self):
        window = main.MainWindow()
        self.addCleanup(window.close)

        self.assertEqual(window.windowTitle(), "PyC2MC Viewer Edition")
        self.assertIsInstance(window.ui, main.Ui_MainWindow)
        self.assertGreater(len(window.ui.__dict__), 1000)

        for name in ("btn_split", "btn_settings", "btn_compare", "btn_stats"):
            self.assertEqual(getattr(window.ui, name).objectName(), name)

        for name in (
            "load_file_method",
            "merge_files",
            "plot_DBE",
            "plot_VK",
            "plot_PCA",
            "plot_ACOS_compare",
            "plot_molecular_carto_DBE",
        ):
            self.assertTrue(callable(getattr(window, name)))

    def test_controller_methods_are_grouped_by_domain(self):
        domains = (
            (main.AppFunctions, "setThemeHack"),
            (main.WindowActionsMixin, "start_splitfinder"),
            (main.FileOperationsMixin, "load_file_method"),
            (main.DataViewsMixin, "split_classes"),
            (main.PlotsMixin, "plot_DBE"),
            (main.ComparisonMixin, "plot_ACOS"),
            (main.MolecularMapsMixin, "plot_molecular_carto_DBE"),
        )
        for mixin, method_name in domains:
            with self.subTest(mixin=mixin.__name__):
                self.assertIn(method_name, mixin.__dict__)

    def test_plot_helper_keeps_histogram_behavior(self):
        self.addCleanup(plt.close, "all")

        result = main.plot_fun("histo", [1, 2], [3, 4])

        self.assertIs(result, plt)
        self.assertEqual(len(plt.gca().patches), 2)


if __name__ == "__main__":
    unittest.main()