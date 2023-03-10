
def Select_Axes_VK(x,y,data):
    """
    Selection of Axes for the View VK pannel

    Args:

        x (int): User choice for X axes

        y (int): User choice for Y axes
        
        data (DataFrame): Dataframe selected for the plot

        Return x_axes,y_axes,x_label,y_label
    """
    if x == 0:
        x_axes = data["O/C"]
        x_label = "O/C"
    elif x == 1:
        x_axes = data["N/C"]
        x_label = "N/C"
    elif x == 2:
        x_axes = data["S/C"]
        x_label = "S/C"
    elif x == 3:
        x_axes = data["H/C"]
        x_label = "H/C"
    elif x == 4:
        x_axes = data["m/z"]
        x_label = "m/z"
    if y == 0:
        y_axes = data["H/C"]
        y_label = "H/C"
    elif y == 1:
        y_axes = data["O/C"]
        y_label = "O/C"
    elif y == 2:
        y_axes = data["N/C"]
        y_label = "N/C"
    elif y == 3:
        y_axes = data["S/C"]
        y_label = "S/C"
    return x_axes,y_axes,x_label,y_label

def Select_Axes_VK_mol(x,y,data,data_inf_p,data_inf_n):
    """
    Selection of Axes for the Compare VK pannel

    Args:

        x (int): User choice for X axes

        y (int): User choice for Y axes
        
        data (DataFrame): Dataframe selected for the plot
        
        data_inf_p (DataFrame): Dataframe selected for the plot
        
        data_inf_n (DataFrame): Dataframe selected for the plot

        Return x_axes, x_axes_p, x_axes_n, y_axes ,y_axes_p,y_axes_n, x_label, y_label
    """
    if x == 0:
        x_axes = data["O/C"]
        x_axes_p = data_inf_p["O/C"]
        x_axes_n = data_inf_n["O/C"]
        x_label = "O/C"
    elif x == 1:
        x_axes = data["N/C"]
        x_axes_p = data_inf_p["N/C"]
        x_axes_n = data_inf_n["N/C"]
        x_label = "N/C"
    elif x == 2:
        x_axes = data["S/C"]
        x_axes_p = data_inf_p["S/C"]
        x_axes_n = data_inf_n["S/C"]
        x_label = "S/C"
    elif x == 3:
        x_axes = data["H/C"]
        x_axes_p = data_inf_p["H/C"]
        x_axes_n = data_inf_n["H/C"]
        x_label = "H/C"
    elif x == 4:
        x_axes = data["m/z"]
        x_axes_p = data_inf_p["m/z"]
        x_axes_n = data_inf_n["m/z"]
        x_label = "m/z"
    if y == 0:
        y_axes = data["H/C"]
        y_axes_p = data_inf_p["H/C"]
        y_axes_n = data_inf_n["H/C"]
        y_label = "H/C"
    elif y == 1:
        y_axes = data["O/C"]
        y_axes_p = data_inf_p["O/C"]
        y_axes_n = data_inf_n["O/C"]
        y_label = "O/C"
    elif y == 2:
        y_axes = data["N/C"]
        y_axes_p = data_inf_p["N/C"]
        y_axes_n = data_inf_n["N/C"]
        y_label = "N/C"
    elif y == 3:
        y_axes = data["S/C"]
        y_axes_p = data_inf_p["S/C"]
        y_axes_n = data_inf_n["S/C"]
        y_label = "S/C"
    return x_axes, x_axes_p, x_axes_n, y_axes ,y_axes_p,y_axes_n, x_label, y_label