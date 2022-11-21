import pandas as pd
def Pre_treatment_petroOrg(filename):
    
    """
    Pre-treat the Petro Org files to ensure compatibility with the loading function.

    Returns :
        Returns data (Dataframe): Containd Petro Org data
    """
    
    loaded_xls = pd.read_excel(filename,sheet_name=None,skiprows=(2))
    try:
        del loaded_xls['Combined R. Abundances']
        del loaded_xls['General']
        del loaded_xls['No Hit']
        data = pd.concat(loaded_xls,axis=0)
        start = data.columns.get_loc('Molecular Formula')
        end = data.columns.get_loc('H/C')
        i = 1
        list_to_drop = []
        while i < end-start-1:
            temp_header = data.iloc[0,start+i]
            data.rename(columns={data.columns[start+i+1]:temp_header},inplace=True)
            list_to_drop.append(start+i)
            i = i+2
        data.drop(data.columns[list_to_drop],axis=1,inplace=True)  
        if '13C' in data.columns:
            data = data[data['13C'] == 0]
            data = data.drop('13C',axis = 1)
    except:
        data = pd.concat(loaded_xls,axis=0)
        start = data.columns.get_loc('Molecular Formula')
        end = data.columns.get_loc('H/C')
        i = 1
        list_to_drop = []
        while i < end-start-1:
            temp_header = data.iloc[0,start+i]
            data.rename(columns={data.columns[start+i+1]:temp_header},inplace=True)
            list_to_drop.append(start+i)
            i = i+2
        data.drop(data.columns[list_to_drop],axis=1,inplace=True) 
        if '13C' in data.columns:
            data = data[data['13C'] == 0]
            data = data.drop('13C',axis = 1)
    return data