import pandas as pd
import numpy as np
from scipy import stats
"""
Created on Fri Mar 10 09:21:18 2023

@author: J1065380
"""

def Make_Volcano(volc_data,list_samp_1,list_samp_2):
    volc_data['Mean_int_1']=volc_data[list_samp_1].mean(axis=1) #Mean intensities in sample 1
    volc_data['Mean_int_2']=volc_data[list_samp_2].mean(axis=1) #Mean intensities in sample 2
    volc_data["fc"]=pd.DataFrame(np.log2(volc_data['Mean_int_2']/volc_data['Mean_int_1'])) #Calculates log2(FC) values
    volc_data['p']=stats.ttest_ind(volc_data[list_samp_1],volc_data[list_samp_2],axis=1)[1].tolist() #Calculates p-values
    ####
    #Excluding infinite and NaN values (attribution in neither of the sample)
    volc_data['fc'].fillna(2e20,inplace=True)
    p_inf=(volc_data['fc'] >1e20).tolist()
    n_inf=(volc_data['fc'] <-1e20).tolist()

    inf_index=[i or j for i, j in zip(n_inf,p_inf)]
    volc_data.drop(index=volc_data.index[inf_index],inplace=True,axis=0)
    
    ####
    return volc_data, str(volc_data.shape[0])