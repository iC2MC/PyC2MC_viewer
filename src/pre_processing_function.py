import pandas as pd
from sklearn import preprocessing
import numpy as np
import statistics
import chemparse
import itertools

colors=['black','red','yellow','green','blue','purple','pink','silver','saddlebrown','orange','lawngreen','turquoise','fuschia','white','cyan','olive','teal']

def pre_processing(self):
    """
    Select and call the preprocessing functions adapted to the input data

    Returns :
        Returns self (Peak_list): A Peak_list class object containing
        preprocessed MS data.
    """
    
    if self.df_type == "Attributed" :
        classes,classes_concat,df,heteroatoms = split_classes(self.df,self.heteroatoms)
        df,dbe_both,C_both,N_both,O_both,S_both,dbe_odd,dbe_even = formating(df)
        self.df = df
        self.classes = classes
        self.classes_concat = classes_concat
        self.heteroatoms = heteroatoms
        self.dbe_both = dbe_both
        self.C_both = C_both
        self.N_both = N_both
        self.O_both = O_both
        self.S_both = S_both
        self.dbe_odd = dbe_odd
        self.dbe_even = dbe_even
        return self
    
    if self.df_type == "PyC2MC_merged":
        classes,classes_concat,df,heteroatoms,volc_data = split_classes_merged(self.df,self.heteroatoms,self.pca_data)
        df,dbe_both,C_both,N_both,O_both,S_both,dbe_odd,dbe_even = formating_merged(df)
        self.df = df
        self.classes = classes
        self.classes_concat = classes_concat
        self.heteroatoms = heteroatoms
        self.dbe_both = dbe_both
        self.C_both = C_both
        self.N_both = N_both
        self.O_both = O_both
        self.S_both = S_both
        self.dbe_odd = dbe_odd
        self.dbe_even = dbe_even
        self.volc_data = volc_data
        return self

    if self.df_type == 'PyC2MC_fusion':
        classes,classes_concat,df,heteroatoms = split_classes_fusionned(self.df,self.heteroatoms)
        df,dbe_both,C_both,N_both,O_both,S_both,dbe_odd,dbe_even = formating(df)
        self.df = df
        self.classes = classes
        self.classes_concat = classes_concat
        self.heteroatoms = heteroatoms
        self.dbe_both = dbe_both
        self.C_both = C_both
        self.N_both = N_both
        self.O_both = O_both
        self.S_both = S_both
        self.dbe_odd = dbe_odd
        self.dbe_even = dbe_even
        return self
    if self.df_type == "Peaklist":
        return self
    
    if self.df_type == "PyC2MC_merged_unattributed":
        volc_data = split_classes_merged_unattributed(self.df,self.pca_data)
        self.volc_data = volc_data
        return self

def split_classes(df,heteroatoms):
    """
    Preprocessing function for a simple attributed file

    Args:
        df (pandas.DataFrame): Dataframe containing data to be processed
        heteroatoms (pandas.DataFrame): Dataframe containing molecular formulae splitted by heteroelement

    Returns:
        classes (pandas.DataFrame): Dataframe containing informations on classes
            (Name, Total intensity, Nb peaks)
        classes_concat (pandas.Series): Series containing concatenated
            informations on classes (Name, Total intensity, Nb peaks)
        df (pandas.DataFrame): Dataframe containing all the data
        heteroatoms_saved (pandas.DataFrame)

    """

    if 'C' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('C', axis=1)
    if 'H' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('H', axis=1)
    heteroatoms = heteroatoms.drop_duplicates()
    heteroatoms_saved = heteroatoms
    total_intensity = sum(df["absolute_intensity"])
    n = 0
    classes = pd.DataFrame()
    while n < len(heteroatoms):
        index_classes = (df[heteroatoms.columns] == heteroatoms.iloc[n]).all(1)
        df_classe = df[index_classes]
        intensity_classes = sum(df_classe["absolute_intensity"])
        percent_value = intensity_classes/total_intensity*100
        nb_peaks=len(df_classe)
        classe_name_elements = heteroatoms.iloc[n]
        classe_name_elements = classe_name_elements[classe_name_elements != 0]
        m = 0
        classe_name = []
        while m < len(classe_name_elements):
            atom_name = str(classe_name_elements.index[m])
            value = str(int(classe_name_elements[m]))
            classe_name.append(atom_name + value)
            m = m+1
        classe_name = ''.join(classe_name)
        if classe_name == "":
            classe_name="CH"
        value=[percent_value,nb_peaks]
        classes[classe_name] = value
        n = n+1

    heteroatoms=list(heteroatoms.columns.values)
    n=len(heteroatoms)
    for i in range(1, len(heteroatoms)+1):
        for het_selected in itertools.combinations(heteroatoms, i):
            het_to_del=heteroatoms.copy()
            classe_name = ''
            for k in het_selected:
                het_to_del.remove(k)
                classe_name = classe_name + k + 'x'
            extract=df
            for h in het_to_del:
                extract=extract[extract[h]==0]
            for i in het_selected:
                extract=extract[extract[i]!=0]
            df_classe=extract
            nb_peaks=len(df_classe)
            intensity_classes = sum(df_classe["absolute_intensity"])
            percent_value = intensity_classes/total_intensity*100 #% intensité de la classe
            if  percent_value > 0  :
                value=[percent_value,nb_peaks]
                classes[classe_name] = value
                df[classe_name]=False
                df[classe_name].loc[df_classe.index]=True
    classes = classes.transpose()
    classes = classes.reset_index()
    names = ['variable','value','number']
    classes.columns = names
    classes = classes.sort_values(by=["value"], ascending=False)
    classes_concat = pd.DataFrame()
    classes_concat['classes'] = classes["variable"] +' '+ classes["number"].astype(int).astype(str) +' / '+ classes["value"].round(2).astype(str) + "%"
    return classes,classes_concat,df,heteroatoms_saved

def split_classes_merged(df,heteroatoms,pca_data):

    """
    Preprocessing function for a merged file

    Args:
        df (pandas.DataFrame): Dataframe contaiining data to be processed
        heteroatoms (pandas.DataFrame): Dataframe containing molecular formulae splitted by heteroelement

    Returns:
        classes (pandas.DataFrame): Dataframe containing informations on classes
            (Name, Mean total intensity, Std, Nb peaks, Mean intens and Nb peaks in each samples)
        classes_concat (pandas.Series): Series containing concatenated informations
        on classes (Name, Mean intensity, Std, Nb peaks
        df (pandas.DataFrame): Dataframe containing all the data
        heteroatoms_saved (pandas.DataFrame)

    """
    df['Normalized_intensity'] = df["summed_intensity"] / max(df['summed_intensity'])*100
    total_intensity = sum(df["summed_intensity"])
    if 'C' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('C', axis=1)
    if 'H' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('H', axis=1)

    heteroatoms = heteroatoms.drop_duplicates()
    heteroatoms_saved = heteroatoms
    n = 0
    classes = pd.DataFrame()
    n_sample = len(df.filter(like='Rel').columns)
    tot_percent = 0
    while n < len(heteroatoms):
        index_classes = (df[heteroatoms.columns] == heteroatoms.iloc[n]).all(1)
        data_classe = df[index_classes]
        rel_intens = data_classe.filter(like='Rel')
        temp_moyenne = []
        temp_nb = []
        p = 0
        while p < n_sample:
            temp_moyenne.append(sum(rel_intens.iloc[:,p].astype(float))*100/(total_intensity/n_sample))
            temp_nb.append(sum(rel_intens.iloc[:,p].astype(float) != 0))
            p = p+1
        percent_value = Average(temp_moyenne)
        std_rel=statistics.stdev(temp_moyenne)/Average(temp_moyenne)
        std_dev_classes = percent_value*std_rel
        nb_peaks=len(data_classe)
        classe_name_elements = heteroatoms.iloc[n]
        classe_name_elements = classe_name_elements[classe_name_elements != 0]
        m = 0
        classe_name = []
        while m < len(classe_name_elements):
            atom_name = str(classe_name_elements.index[m])
            value = str(int(classe_name_elements[m]))
            classe_name.append(atom_name + value)
            m = m+1
        classe_name = ''.join(classe_name)
        if classe_name == "":
            classe_name="CH"
        values = [percent_value,std_dev_classes,nb_peaks,temp_moyenne,temp_nb]
        classes[classe_name] = values
        tot_percent = tot_percent + percent_value
        n = n+1
    heteroatoms=list(heteroatoms.columns.values)
    n=len(heteroatoms)
    tot_percent=0
    for i in range(1, len(heteroatoms)+1):
        for het_selected in itertools.combinations(heteroatoms, i):
            het_to_del=heteroatoms.copy()
            classe_name = ''
            for k in het_selected:
                het_to_del.remove(k)
                classe_name = classe_name + k + 'x'
            extract=df
            for h in het_to_del:
                extract=extract[extract[h]==0]
            for i in het_selected:
                extract=extract[extract[i]!=0]
            data_classe=extract
            rel_intens = data_classe.filter(like='Rel')
            temp_moyenne = []
            temp_nb = []
            p = 0
            while p < n_sample:
                temp_moyenne.append(sum(rel_intens.iloc[:,p].astype(float))*100/(total_intensity/n_sample))
                temp_nb.append(sum(rel_intens.iloc[:,p].astype(float) != 0))
                p = p+1
            percent_value = Average(temp_moyenne)
            if percent_value > 0:
                std_rel=statistics.stdev(temp_moyenne)/Average(temp_moyenne)
                std_dev_classes = percent_value*std_rel
                nb_peaks=len(data_classe)
                values = [percent_value,std_dev_classes,nb_peaks,temp_moyenne,temp_nb]
                classes[classe_name] = values
                df[classe_name]=False
                df[classe_name].loc[data_classe.index]=True

            
            

            n = n+1
            

    ###################################################################        
    #Volcano data creation
    ###################################################################
    if 'PC1' in df.columns:
        classe_index = df.iloc[:,df.columns.get_loc('Normalized_intensity')+1:df.columns.get_loc('H/C')-1].copy()
    else:
        classe_index = df.iloc[:,df.columns.get_loc('Normalized_intensity')+1:].copy()
    
    
    n=0
    d = pd.DataFrame(index=np.arange(len(df)))
    d["family_color"]="X1"
    d["family_name"]="X2"
    
    for i in classe_index.columns:
        n=(n+1)%16
        d["family_color"].mask(classe_index[i],other=f'{colors[n]}',inplace=True)
        d["family_name"].mask(classe_index[i],other=f'{i}',inplace=True)
        
    d.replace('X1','black',inplace=True)
    d.replace('X2','CH',inplace=True)
    

    d["sum_formula"]=df['molecular_formula']
    if 'Na' in df:
        d["DBE"] = df["C"] - ((df["H"]+df["Na"])/2) + (df["N"]/2) + 1
    elif 'K' in df:
        d["DBE"] = df["C"] - ((df["H"]+df["K"])/2) + (df["N"]/2) + 1
    else:    
        d["DBE"] = df["C"] - ((df["H"])/2) + (df["N"]/2) + 1
    d["O/C"] = df["O"] / df["C"]
    
    volc_data=pd.concat([pca_data.copy(),d],axis=1)
    
    ###################################################################
    #End
    ###################################################################
    

    

    classes = classes.transpose()
    classes = classes.reset_index()
    names = ['variable','value','std_dev_rel','number','per_datas','per_datas_nb']
    classes.columns = names
    classes = classes.sort_values(by=["value"], ascending=False)
    classes_concat = pd.DataFrame()
    classes_concat['classes'] = classes["variable"] +' '+ classes["number"].astype(int).astype(str) +' / '+ classes["value"].astype(float).round(2).astype(str) + "%"+' / '+ classes["std_dev_rel"].astype(float).round(1).astype(str)+'%'
    return classes,classes_concat,df,heteroatoms_saved,volc_data

def split_classes_merged_unattributed(df,pca_data):
    volc_data = pca_data.copy()
    return volc_data

def split_classes_fusionned(df,heteroatoms):
    
    """
    Preprocessing function for a fusionned file

    Args:
        df (pandas.DataFrame): Dataframe contaiining data to be processed
        heteroatoms (pandas.DataFrame): Dataframe containing molecular formulae splitted by heteroelement

    Returns:
        classes (pandas.DataFrame): Dataframe containing informations on classes
            (Name, Mean total intensity, Std, Nb peaks, Mean intens and Nb peaks in each samples)
        classes_concat (pandas.Series): Series containing concatenated informations
        on classes (Name, Mean intensity, Std, Nb peaks
        df (pandas.DataFrame): Dataframe containing all the data
        heteroatoms_saved (pandas.DataFrame)

    """
    total_intensity = sum(df['normalized_intensity'])
    if 'C' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('C', axis=1)
    if 'H' in  heteroatoms.columns:
        heteroatoms =  heteroatoms.drop('H', axis=1)

    heteroatoms = heteroatoms.drop_duplicates()
    heteroatoms_saved = heteroatoms
    n = 0
    classes = pd.DataFrame()
    n_sample = len(df.filter(like='Rel').columns)
    tot_percent = 0
    while n < len(heteroatoms):
        index_classes = (df[heteroatoms.columns] == heteroatoms.iloc[n]).all(1)
        data_classe = df[index_classes]
        rel_intens = data_classe.filter(like='Rel')
        temp_moyenne = []
        temp_nb = []
        p = 0
        while p < n_sample:
            temp_moyenne.append(sum(rel_intens.iloc[:,p].astype(float))*100/total_intensity)
            temp_nb.append(sum(rel_intens.iloc[:,p].astype(float) != 0))
            p = p+1
        percent_value = Average(temp_moyenne)
        if len(temp_moyenne) > 0  and percent_value > 0 :
            std_rel=statistics.stdev(temp_moyenne)/Average(temp_moyenne)
            std_dev_classes = percent_value*std_rel
            nb_peaks=len(data_classe)
            classe_name_elements = heteroatoms.iloc[n]
            classe_name_elements = classe_name_elements[classe_name_elements != 0]
            m = 0
            classe_name = []
            while m < len(classe_name_elements):
                atom_name = str(classe_name_elements.index[m])
                value = str(int(classe_name_elements[m]))
                classe_name.append(atom_name + value)
                m = m+1
            classe_name = ''.join(classe_name)
            if classe_name == "":
                classe_name="CH"
            values = [percent_value,std_dev_classes,nb_peaks,temp_moyenne,temp_nb]
            classes[classe_name] = values
            tot_percent = tot_percent + percent_value
        else : pass
        n = n+1
    
    heteroatoms=list(heteroatoms.columns.values)
    n=len(heteroatoms)
    tot_percent=0
    for i in range(1, len(heteroatoms)+1):
        for het_selected in itertools.combinations(heteroatoms, i):
            het_to_del=heteroatoms.copy()
            classe_name = ''
            for k in het_selected:
                het_to_del.remove(k)
                classe_name = classe_name + k + 'x'
            extract=df
            for h in het_to_del:
                extract=extract[extract[h]==0]
            for i in het_selected:
                extract=extract[extract[i]!=0]
            data_classe=extract
            rel_intens = data_classe.filter(like='Rel')
            temp_moyenne = []
            temp_nb = []
            p = 0
            while p < n_sample:
                temp_moyenne.append(sum(rel_intens.iloc[:,p].astype(float))*100/(total_intensity))
                temp_nb.append(sum(rel_intens.iloc[:,p].astype(float) != 0))
                p = p+1
            percent_value = Average(temp_moyenne)
            if percent_value > 0:
                std_rel=statistics.stdev(temp_moyenne)/Average(temp_moyenne)
                std_dev_classes = percent_value*std_rel
                nb_peaks=len(data_classe)
                values = [percent_value,std_dev_classes,nb_peaks,temp_moyenne,temp_nb]
                classes[classe_name] = values
                df[classe_name]=False
                df[classe_name].loc[data_classe.index]=True
                tot_percent = tot_percent + percent_value
            else: pass

            n = n+1
    classes = classes.transpose()
    classes = classes.reset_index()
    names = ['variable','value','std_dev_rel','number','per_datas','per_datas_nb']
    classes.columns = names
    classes = classes.sort_values(by=["value"], ascending=False)
    classes_concat = pd.DataFrame()
    classes_concat['classes'] = classes["variable"] +' '+ classes["number"].astype(int).astype(str) +' / '+ classes["value"].astype(float).round(2).astype(str) + "%"+' / '+ classes["std_dev_rel"].astype(float).round(1).astype(str)+'%'
    return classes,classes_concat,df,heteroatoms_saved

def formating_merged(df):
        df["H/C"] = df["H"] / df["C"]
        if 'O' in df:
            df["O/C"] = df["O"] / df["C"]
        if 'N' in df:
            df["N/C"] = df["N"] / df["C"]
        if 'S' in df:
            df["S/C"] = df["S"] / df["C"]
            
        if 'Na' in df:
            df["DBE"] = df["C"] - ((df["H"]+df["Na"])/2) + (df["N"]/2) + 1
        elif 'K' in df:
            df["DBE"] = df["C"] - ((df["H"]+df["K"])/2) + (df["N"]/2) + 1
        else:    
            df["DBE"] = df["C"] - ((df["H"])/2) + (df["N"]/2) + 1
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        dbe_both = dict()
        dbe_odd = dict()
        dbe_even = dict()

        C_both = dict()
        O_both = dict()
        N_both = dict()
        S_both = dict()

        all_DBE = df.DBE.drop_duplicates()
        tot_int = sum(df["summed_intensity"])
        for i in range(len(all_DBE)):
            intensity_DBE = 100*sum(df["summed_intensity"].loc[df.DBE == all_DBE.values[i]])/tot_int
            if  intensity_DBE:
                dbe_both[i] = [intensity_DBE]
                if all_DBE.values[i].is_integer():
                    dbe_odd[i] = [intensity_DBE]
                else :
                    dbe_even[i] = [intensity_DBE]
        if "C" in df:
            all_C = df.C.drop_duplicates()
            for i in range(len(all_C)):
                intensity_C = 100*sum(df["summed_intensity"].loc[df.C == all_C.values[i]])/tot_int
                if  intensity_C  :
                    C_both[i] = [intensity_C]
        if "N" in df:
            all_N = df.N.drop_duplicates()
            for i in range(len(all_N)):
                intensity_N = 100*sum(df["summed_intensity"].loc[df.N == all_N.values[i]])/tot_int
                if  intensity_N  :
                    N_both[i] = [intensity_N]
        if "O" in df:
            all_O = df.O.drop_duplicates()
            for i in range(len(all_O)):
                intensity_O = 100*sum(df["summed_intensity"].loc[df.O == all_O.values[i]])/tot_int
                if  intensity_O  :
                    O_both[i] = [intensity_O]
        if "S" in df:
            all_S = df.S.drop_duplicates()
            for i in range(len(all_S)):
                intensity_S = 100*sum(df["summed_intensity"].loc[df.S == all_S.values[i]])/tot_int
                if  intensity_S  :
                    S_both[i] = [intensity_S]

        dbe_both=pd.DataFrame.from_dict(dbe_both)
        C_both=pd.DataFrame.from_dict(C_both)
        N_both=pd.DataFrame.from_dict(N_both)
        O_both=pd.DataFrame.from_dict(O_both)
        S_both=pd.DataFrame.from_dict(S_both)
        dbe_odd=pd.DataFrame.from_dict(dbe_odd)
        dbe_even=pd.DataFrame.from_dict(dbe_even)
        return df,dbe_both,C_both,N_both,O_both,S_both,dbe_odd,dbe_even



def formating(df):
    
    df["Normalized_intensity"] = df["normalized_intensity"]
    if 'H' in df:
        df["H/C"] = df["H"] / df["C"]
    else:
        df['H'] = 0
    if 'O' in df:
        df["O/C"] = df["O"] / df["C"]
    if 'N' in df:
        df["N/C"] = df["N"] / df["C"]
    else:
        df['N'] = 0
    if 'S' in df:
        df["S/C"] = df["S"] / df["C"]
        
    if 'Na' in df:
        df["DBE"] = df["C"] - ((df["H"]+df["Na"])/2) + (df["N"]/2) + 1
    elif 'K' in df:
        df["DBE"] = df["C"] - ((df["H"]+df["K"])/2) + (df["N"]/2) + 1
    else:    
        df["DBE"] = df["C"] - ((df["H"])/2) + (df["N"]/2) + 1
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    dbe_both = dict()
    dbe_odd = dict()
    dbe_even = dict()

    C_both = dict()
    O_both = dict()
    N_both = dict()
    S_both = dict()
    all_DBE = df.DBE.drop_duplicates()
    for i in range(len(all_DBE)):
        intensity_DBE = sum(df["Normalized_intensity"].loc[df.DBE == all_DBE.values[i]])
        if  intensity_DBE  :
            dbe_both[i] = [intensity_DBE]
            if all_DBE.values[i].is_integer():
                dbe_odd[i] = [intensity_DBE]
            else :
                dbe_even[i] = [intensity_DBE]

    if "C" in df:
        all_C = df.C.drop_duplicates()
        for i in range(len(all_C)):
            intensity_C = sum(df["Normalized_intensity"].loc[df.C == all_C.values[i]])
            if  intensity_C  :
                C_both[i] = [intensity_C]
    if "N" in df:
        all_N = df.N.drop_duplicates()
        for i in range(len(all_N)):
            intensity_N = sum(df["Normalized_intensity"].loc[df.N == all_N.values[i]])
            if  intensity_N  :
                N_both[i] = [intensity_N]
    if "O" in df:
        all_O = df.O.drop_duplicates()
        for i in range(len(all_O)):
            intensity_O = sum(df["Normalized_intensity"].loc[df.O == all_O.values[i]])
            if  intensity_O  :
                O_both[i] = [intensity_O]
    if "S" in df:
        all_S = df.S.drop_duplicates()
        for i in range(len(all_S)):
            intensity_S = sum(df["Normalized_intensity"].loc[df.S == all_S.values[i]])
            if  intensity_S  :
                S_both[i] = [intensity_S]
    dbe_both=pd.DataFrame.from_dict(dbe_both)
    C_both=pd.DataFrame.from_dict(C_both)
    N_both=pd.DataFrame.from_dict(N_both)
    O_both=pd.DataFrame.from_dict(O_both)
    S_both=pd.DataFrame.from_dict(S_both)
    dbe_odd=pd.DataFrame.from_dict(dbe_odd)
    dbe_even=pd.DataFrame.from_dict(dbe_even)
    return df,dbe_both,C_both,N_both,O_both,S_both,dbe_odd,dbe_even

def Average(lst):
    if len(lst)!=0:
        return sum(lst) / len(lst)
    else:
        return 0