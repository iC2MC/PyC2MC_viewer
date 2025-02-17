import pandas
from functools import reduce
import numpy as np
import os
from time import time
from src.loading.loading_function import load_MS_file


 
def merge_non_attributed(names:str, tol:float, min_rel_intens:float = None, callback: callable = None):
    """
    This function is used to concatenate non attributed .asc files from DataAnalysis.
    The merge is working using the mass-to-charge ratio with a given tolerance in Dalton
    
    Args: 
        names(list): Dictionnary of name of datasets to import
        tol(float): value of the tolerance in ppm (1e-6)
        min_rel_intens(float): Lower limit for relative intensity, allows to roughly filter noise 
        callback (callable): callback function 
    Return a pandas.DataFrame. 
    """
    start_time = time()
    data = list()
    data_name = list()
    for i in names[0]:
        filename = str(os.path.basename(i))
        data_name.append(filename) #isole le nom du fichier et l'ajoute à une liste
        temp_data: pandas.DataFrame = load_MS_file(filename).df[["m/z","absolute_intensity"]]
        temp_data.rename(columns={"m/z":"mz", "absolute_intensity":"I"},inplace=True)
        temp_data['Rel_intens'] = (temp_data['I']/sum(temp_data['I']))*100
        if min_rel_intens is not None:
            temp_data = temp_data[temp_data['Rel_intens'] >= min_rel_intens]
        
        temp_data.sort_values("mz",inplace = True,ignore_index= True)
        data.append(temp_data)   
        
    # merged = reduce(lambda  left,right: pandas.merge_asof(left,right,on=['mz'],tolerance=tol[0]), data).fillna('0') 
    temp_merged = data[0]
    for i in range(len(names[0])-1):
        left = temp_merged.copy()
        right = data[i+1]
        right = right.assign(idx=np.arange(right.shape[0]))
        # create a df with species within tolerance:
        #dynamic tolerance, row by row:
        left['tolerance'] = left['mz'] * tol*1e-6
        
        temp_merged = pandas.DataFrame()
        for n, row in left.iterrows():
            tolerance = row['tolerance']
            temp = pandas.merge_asof(
                left=pandas.DataFrame([row]),
                right=right,
                on='mz',
                tolerance=tolerance,
                direction='nearest'
            )
            temp_merged = pandas.concat([temp_merged, temp], ignore_index=True)
            
            if callback != None:
                progress = 100 *((i)/(len(names[0])-1) + n/(len(left)*(len(names[0])-1)))
                callback(progress)
            
        temp_merged.drop("tolerance", inplace= True, axis = 1)
    
        # add missing species from the right member
        temp_merged = temp_merged.merge(right, on='idx', how='outer',suffixes=('_l','_r'))
        # fill NaN values with 0
        temp_merged = temp_merged.assign(mz=lambda x:x['mz_l'].fillna(x['mz_r']))
        if i<1:
            temp_merged = temp_merged.assign(I_y=lambda x:x['I_y'].fillna(x['I']))
            temp_merged = temp_merged.assign(Rel_intens_y=lambda x:x['Rel_intens_y'].fillna(x['Rel_intens']))
        else:
            temp_merged = temp_merged.assign(I_y=lambda x:x['I_l'].fillna(x['I_r']))
            temp_merged = temp_merged.assign(Rel_intens_y=lambda x:x['Rel_intens_l'].fillna(x['Rel_intens_r']))
        temp_merged = temp_merged.rename(columns={'mz':'mz','I_y':f'I_{i}','Rel_intens_y':f'Rel_intens_{i}'})
        if i<1:
            temp_merged = temp_merged.drop(['mz_l','mz_r','idx','I','Rel_intens'], axis=1)
        else:
            temp_merged = temp_merged.drop(['mz_l','mz_r','idx','I_l','Rel_intens_l','I_r','Rel_intens_r'], axis=1)
        temp_merged = temp_merged.sort_values('mz')
        temp_merged = temp_merged.reset_index(drop = True).fillna(0)
        
            
    
    ### 
    #Move mz column at the end of 'merged'
    merged = temp_merged
    mz= merged['mz']
    merged.drop('mz',axis = 1,inplace = True)
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
    print(f"Done in : {time()-start_time}s")
    return merged
