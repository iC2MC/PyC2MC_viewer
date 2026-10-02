import matplotlib.pyplot as plt

def plot_fun(
    kind,
    x,
    y,
    d_color="blue",
    dot_type="sc",
    cmap="jet",
    edge=True,
    size=100,
    b_width=1,
    error_data=0,
    stem_color="",
    e_color="k",
    bar_color="grey",
    alpha=1,
):
    """
    Built-in plot function

    Args
    ----------
    kind : str
        Plot type : "scatter", "spectrum", "histo".
    x : Pandas.Series
        Data of x-axis.
    y : Pandas.Series
        Data of y-axis.
    d_color : str, optional
        Points color. The default is 'blue'.
    dot_type : str, optional
        Points size and color based on 3rd dimension ? : "sc" size and color, "s" size only , "c" color only. The default is "sc".
    cmap : str, optional
        Color map definition. The default is "jet".
    edge : bool, optional
        Enable points edge. The default is True.
    size : int, optional
        Set the points size scale. The default is 100.
    b_width : int, optional
        Set the bar width for bar and histo plots. The default is 1.
    error_data : Pandas.Series, optional
        Error bars data for bar and histo plots. The default is 0.
    stem_color : str, optional
        Stem color for spectrum plots. The default is ''.
    e_color : str, optional
        Edge color. The default is 'k'.

    Returns
    -------
    plt : Figure
        Figure object

    """
    # Dot type ?
    if dot_type == "sc":
        color = d_color
        d_size = size
    elif dot_type == "s":
        color = "blue"
        d_size = size
    elif dot_type == "c":
        color = d_color
        d_size = size / color
    # Edge ?
    if edge == True:
        e = 0.7
    elif edge == False:
        e = 0
    # Plot type ?
    if (
        kind == "scatter"
    ):  # Scatter plot for DBE, Van krevelen, Kendricks and ppm vs mz plots.
        plt.scatter(
            x,
            y,
            s=d_size,
            c=color,
            cmap=cmap,
            edgecolor=e_color,
            linewidths=e,
            alpha=alpha,
        )
        return plt

    elif kind == "spectrum":  # Stem plot for mass spectrum
        plt.stem(x, y, stem_color, markerfmt=" ", basefmt="k")
        return plt

    elif (
        kind == "histo"
    ):  # Bar diagram for composition, error distribution, DBE distribution (solo and merged),
        plt.bar(
            x,
            y,
            yerr=error_data,
            width=b_width * 0.05,
            color=bar_color,
            align="center",
            ecolor="black",
            capsize=1 / (len(x)),
        )
        return plt

color_list = [
    "#000000",  # Black
    "#FF0000",  # Red
    "#0000FF",  # Blue
    "#15B01A",  # Light green
    "#800080",  # Purple
    "#008000",  # Forest green
    "#FFA500",  # Orange
    "#DC143C",  # Crimson
    "#00FFFF",  # Cyan
    "#FFFF00",
]  # Yellow
