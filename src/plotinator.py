import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def to_array(serie):
    """ transforms a pandas.Series to numpy.array"""
    return serie.values


def scatter_plot(x, y, fig = None, ax = None, **kwargs):
    """
    Generic matplotlib scatter plot initializing method.
        
    Args:
        x (numpy.array): contains the x-axis data.
        y (numpy.array): contains the y-axis data.
        fig (matplotlib.pyplot.figure): figure specifications.
        ax (matplotlib.pyplot.subplot): subplot axis.
        
    Returns a matplotlib.pyplot.subplot ax from the scatter kind.
    """
    if fig is None:
        fig = plt.figure(figsize=(8,8)) #TODO: Define plot dimensions
    if ax is None:    
        ax = plt.subplot(1,1,1)
    
    ax.scatter(x, y, **kwargs)
        
    return ax
    

def stem_plot(x, y, fig = None, ax = None, **kwargs):
    """
    Generic matplotlib stem plot initializing method.
    
    Args:
        x (numpy.array): contains the x-axis data.
        y (numpy.array): contains the y-axis data.
        fig (matplotlib.pyplot.figure): figure specifications.
        ax (matplotlib.pyplot.subplot): subplot axis.
    
    Returns a matplotlib.pyplot.subplot ax from the stem kind.
    """
    if fig is None:
        fig = plt.figure(figsize=(8,8)) #TODO: Define plot dimensions
    if ax is None:    
        ax = plt.subplot(1,1,1)

    ax.stem(x, y, markerfmt ="", basefmt = "", **kwargs)
    
    return ax
    
def bar_plot(x, y, fig = None, ax = None, **kwargs):
    """
    Generic matplotlib bar plot initializing method.
    
    Args:
        x (numpy.array): contains the x-axis data.
        y (numpy.array): contains the y-axis data.
        fig (matplotlib.pyplot.figure): figure specifications.
        ax (matplotlib.pyplot.subplot): subplot axis.
    
    Returns a matplotlib.pyplot.subplot ax from the bar kind.
    """
    if fig is None:
        fig = plt.figure(figsize=(8,8)) #TODO: Define plot dimensions
    if ax is None:    
        ax = plt.subplot(1,1,1)

    ax.bar(x, y, align="center", **kwargs)
    
    return ax
    
    