# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 14:33:14 2023

@author: J1065380
"""

def Select_classe(classe_selected,df,heteroatoms,classes):
    if classe_selected == 'All':
        pass
    else:
        classes_index = classes[classes['variable'] == classe_selected]
        if 'x' in classe_selected:
            index_classes = (df[classe_selected] == True)
        else:
            index_classes = (df[heteroatoms.columns] == heteroatoms.iloc[classes_index.index[0]]).all(1)
        df = df[index_classes]
    return df