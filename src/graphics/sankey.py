from matplotlib.sankey import Sankey

def Create_Sankey(data_classes):
    data_class_x = data_classes[data_classes['variable'].str.contains("x")]
    data_class_rest = data_classes[~data_classes['variable'].str.contains("x")]
    sankey_plot = Sankey()
    for index,row in data_class_x.iterrows():
        sankey_plot.add(flows=row[1],
                   labels=row[0],
                   orientations=0)
