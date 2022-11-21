import pandas
from functools import reduce
import numpy as np
import os


 
def merge_non_attributed(names,tol):
    """
    This function is used to concatenate non attributed .asc files from DataAnalysis.
    The merge is working using the mass-to-charge ratio with a given tolerance in Dalton
    
    Args: 
        names(list): Dictionnary of name of datasets to import
        tol(tuple(float)): value of the tolerance in Dalton applied for the merging
    Return a pandas.DataFrame. 
    """
    data = list()
    data_name = list()
    for i in names[0]:
        filename = str(os.path.basename(i))
        data_name.append(filename) #isole le nom du fichier et l'ajoute à une liste
        temp_data = pandas.read_csv(filename, delim_whitespace=True,
                         names=["m/z", "I"],
                         usecols=(0, 1), dtype=np.float64)
        temp_data['Rel_intens'] = (temp_data['I']/sum(temp_data['I']))*100
        data.append(temp_data)   
        
    # merged = reduce(lambda  left,right: pandas.merge_asof(left,right,on=['m/z'],tolerance=tol[0]), data).fillna('0') 
    temp_merged = data[0]
    for i in range(len(names[0])-1):
        left = temp_merged.copy()
        right = data[i+1]
        right = right.assign(idx=np.arange(right.shape[0]))
        temp_merged = (pandas.merge_asof(left,right, on='m/z',direction='nearest',tolerance=tol[0]))
        temp_merged = temp_merged.merge(right, on='idx', how='outer',suffixes=('_l','_r'))
        temp_merged = temp_merged.assign(mz=lambda x:x['m/z_l'].fillna(x['m/z_r']))
        if i<1:
            temp_merged = temp_merged.assign(I_y=lambda x:x['I_y'].fillna(x['I']))
            temp_merged = temp_merged.assign(Rel_intens_y=lambda x:x['Rel_intens_y'].fillna(x['Rel_intens']))
        else:
            temp_merged = temp_merged.assign(I_y=lambda x:x['I_l'].fillna(x['I_r']))
            temp_merged = temp_merged.assign(Rel_intens_y=lambda x:x['Rel_intens_l'].fillna(x['Rel_intens_r']))
        temp_merged = temp_merged.rename(columns={'mz':'m/z','I_y':f'I_{i}','Rel_intens_y':f'Rel_intens_{i}'})
        if i<1:
            temp_merged = temp_merged.drop(['m/z_l','m/z_r','idx','I','Rel_intens'], axis=1)
        else:
            temp_merged = temp_merged.drop(['m/z_l','m/z_r','idx','I_l','Rel_intens_l','I_r','Rel_intens_r'], axis=1)
        temp_merged = temp_merged.sort_values('m/z')
        temp_merged = temp_merged.reset_index(drop = True).fillna(0)
    
    ### 
    #Move m/z column at the end of 'merged'
    merged = temp_merged
    mz= merged['m/z']
    merged.drop('m/z',axis = 1,inplace = True)
    merged['m/z'] = mz
    ###
    
    n = 0
    colum_names = list()
    colum_names.append('m/z')
    colum_names.append('count')
    abs_name = list()
    rel_name = list()
    for name in data_name:
        name = name.replace('.asc','')
        merged.columns.values[n] = "Abs_intens_" + name
        merged.columns.values[n+1] = "Rel_intens_" + name 
        abs_name.append('Abs_intens_' + name)
        rel_name.append('Rel_intens_' + name)
        n = n+2   
    colum_names = [*colum_names,*abs_name,*rel_name]          
    temp_count = merged.filter(like='Rel').to_numpy().astype('float')  
    merged['count'] = np.count_nonzero(temp_count,axis=1)
    merged = merged.reindex(colum_names,axis = 1)
    return merged
