from modules.ui_functions import UIFunctions
import os
import numpy as np
import chemparse as cp
import math
from src.processing.merge_function import merge_file, merge_for_compare
from src.processing.merge_csv_from_same_spectrum import merge_Multicsv
from src.processing.fuse_replicates import fuse_replicates
from src.processing.merge_merged_function import merge_merged_file
from src.loading.loading_function import load_MS_file
from src.graphics.normalization_function import Normalize
from src.graphics.select_classe import Select_classe
from src.graphics.select_axes_VK import Select_Axes_VK, Select_Axes_VK_mol
from src.stats.HCA_function import plot_dendrogram
from src.stats.PCA_function import plot_pca
from src.stats.volcano_function import Make_Volcano
from src.processing.merge_unattributed import merge_non_attributed
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
from src.pyc2mc_ui import Ui_PyC2MC
from PyQt5.QtWidgets import QMessageBox, QLineEdit, QInputDialog, QTableWidgetItem
from matplotlib.animation import FuncAnimation, PillowWriter
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch
from venn import venn_diag, venn_sets
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
import imageio
from PIL import Image, ImageSequence
from IPython import display
from modules.plot_helpers import color_list, plot_fun
