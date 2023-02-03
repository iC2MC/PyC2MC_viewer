################################
###Zone d'import des modules####
################################
import pandas
import os
from functools import reduce
import numpy as np
import chemparse
from ..loading.loading_function import load_MS_file



def merge_Multicsv(names):
    
    """
    This function is used to concatenate .csv files obtained from a same spectrum in an unique file.
    The merge is working using the molecular
    
    Args: 
        names(dict): list of path of .csv to load and process.
        
    Return a pandas.DataFrame. 
    """
    
    data = {}
    filename = pandas.Series()
    sumformula = pandas.Series()
    
    if len(names[0]) == 1:
        merged=pandas.read_csv(open(names[0][0]), sep=',|;', encoding="utf-8")
    else:
        merged = pandas.DataFrame().astype('float') 
        n = 0
        while n < len(names):
            _, filename["%s" %n] = os.path.split(names[n])
            data["%s" %n] =  load_MS_file(names[n]).df
            data["%s" %n] = data["%s" %n].iloc[:,0:5]
            data["%s" %n] = data["%s" %n].drop('normalized_intensity',axis=1)
            sumformula = sumformula.append(data["%s" %n]['molecular_formula'])
            n = n+1
        
        sumformula.name = 'sum formula'
        sumformula = sumformula.str
        sumformula = sumformula.replace(" ", "")
        sumformula = sumformula.drop_duplicates()
        sumformula_splitted = [chemparse.parse_formula(formula) for formula in sumformula]                
        sumformula_splitted = pandas.DataFrame(list(sumformula_splitted))    
        sumformula_splitted.fillna(0, inplace = True)
        
        ##################################################
        ### Recalculating m/z ratio for homogeneity ######
        ##################################################
        
        
        dict_data={'C': 12,'H':1.007825,'N':14.003074,'O':15.994915,'S':31.972072,'Cl':34.968853,'Si':27.976928,'P':30.9737634\
        ,'V':50.943963,'K':39.0983,'Na':22.989769,'Li':7.016005,'Cu':62.929599,'Ni':57.935347,'F':18.998403,'B':11.009305, 'Zn':63.92915, 'Br':78.91834}
        mz = pandas.DataFrame(index=range(len(sumformula)))
        mz['m/z']=0.0
        v=0
        ratio_mz = []
        while v < len(sumformula_splitted) :
            form=sumformula_splitted.iloc[v]
            mass = 0
            for atom in form.items():  
                mass = mass + atom[1]*dict_data[atom[0]]
            ratio_mz.append(mass)
            v=v+1
        
        merged = pandas.concat(data, axis=0)      
        merged = merged.drop_duplicates(subset='molecular_formula')
        


        
        
    return merged