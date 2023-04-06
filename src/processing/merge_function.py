################################
###Zone d'import des modules####
################################
import pandas
import os
from functools import reduce
import numpy as np
import chemparse
from ..loading.loading_function import load_MS_file

#################################################
###Définition de la fonction d'import des CSV####
#################################################
def merge_file(names,isotopes_dict):
        """
        This function is used to concatenate .csv files together in one unique file "merged".
        The merge is working using the molecular formulas
        
        Args: 
            names(dict): list of path of .csv to load and process.
            
        Return a pandas.DataFrame. 
        """
        data = {}
        filename = pandas.Series()
        sumformula = pandas.Series()
        if len(names) == 1:
            merged=load_MS_file(names)
        else:
            merged = pandas.DataFrame().astype('float') 
            n = 0
            while n < len(names):
                _, filename["%s" %n] = os.path.split(names[n])
                data["%s" %n] =  load_MS_file(names[n],isotopes_dict).df
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
            
            
            mz = pandas.DataFrame(index=range(len(sumformula)))
            mz['m/z']=0.0
            v=0
            ratio_mz = []
            while v < len(sumformula_splitted) :
                form=sumformula_splitted.iloc[v]
                mass = 0
                for atom in form.items():  
                    mass = mass + atom[1]*isotopes_dict[atom[0]]
                ratio_mz.append(mass)
                v=v+1
            mz['m/z'] = ratio_mz
            sumformula = sumformula.reset_index(drop=True)
        
            frames = [mz,sumformula_splitted,sumformula]
            merged = pandas.concat(frames, axis=1)
            merged['count'] = 0
            merged.rename(columns = {'sum formula':'molecular_formula'}, inplace = True)

            #####################################################################
            ### Boucle de regroupement des intensités pour chaque tableaux ######
            #####################################################################
            n = 0
            data_frames_abs_intens = []
            data_frames_rel_intens = []
            while n < len(names):
                data["%s" %n]["molecular_formula"] = data["%s" %n]["molecular_formula"].replace(' ','',regex = True)
                data_frames_abs_intens.append(data["%s" %n][["molecular_formula","absolute_intensity"]])
                data_frames_rel_intens.append(data["%s" %n][["molecular_formula","normalized_intensity"]])
                n = n+1
            
            
            #####################################################################
            ### Merge de toutes les intensités en fonction de la calc. m/z ######
            #####################################################################
        
            intens_abs_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_abs_intens).fillna(0)
            intens_rel_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_rel_intens).fillna(0)
            intens_abs_merged = intens_abs_merged.drop_duplicates(subset='molecular_formula')
            intens_rel_merged = intens_rel_merged.drop_duplicates(subset='molecular_formula')
            #################################
            ### Renommage des colonnes ######
            #################################
            n = 0
            while n < len(names):
                name_data = os.path.basename(names[n])
                if n < len(names):
                    intens_abs_merged.columns.values[n+1] = "Abs_intens_" + name_data
                    intens_rel_merged.columns.values[n+1] = "Rel_intens_" + name_data
                n = n+1
            
            ###################################################
            ### Merge final des intensités + SF + m/z #########
            ###################################################
            merged.set_index('molecular_formula',inplace=True)
            intens_abs_merged.set_index('molecular_formula',inplace=True)
            intens_rel_merged.set_index('molecular_formula',inplace=True)
            data_frames = [merged,intens_abs_merged,intens_rel_merged]
            merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames) #NaN si moins de 3 fichiers (!)
            merged.reset_index(inplace=True)
            
            ##########################################################
            ### Fonction pour compter les intensités non nulles ######
            ##########################################################
        
            n = merged.columns.get_loc('count')+1
            m = n + len(names)
            temp_count = merged.iloc[:,n:m]
            temp_count = temp_count.to_numpy().astype('float')
            merged['count'] = np.count_nonzero(temp_count,axis=1)
            intens_rel_merged.reset_index(inplace=True,drop = True)
            intens_rel_merged = pandas.DataFrame(intens_rel_merged).astype('float')
            merged['summed_intensity'] = intens_rel_merged.sum(axis=1)
            merged.sort_values('m/z',inplace=True)
            merged = merged.rename(columns = {'m/z':'calc. m/z'})
            merged.sort_values('summed_intensity',inplace=True)
    
        ########################
        ### Export en CSV ######
        ########################
        return merged
    
def merge_for_compare(data,name,isotopes_dict):
        """
        This function is used to concatenate on the file selected data of the List_compare widget together in one working dataset.
        The merge is working using the calculated mass-to-charge ratio
        
        Args: 
            data(dict) : Dictionnary of datasets imported from the List_compare widget items
            names(dict): Dictionnary of name of datasets imported from the List_compare widget items
            
        Return a pandas.DataFrame. 
        """
        sumformula = pandas.Series()
        for i in range(len(data)):
            sumformula = sumformula.append(data[i]['molecular_formula'])
                
        sumformula.name = 'sum formula'
        sumformula = sumformula.str
        sumformula = sumformula.replace(" ", "")        
        sumformula = sumformula.drop_duplicates()
        sumformula_splitted = [chemparse.parse_formula(formula) for formula in sumformula]                
        sumformula_splitted = pandas.DataFrame(list(sumformula_splitted))    
        sumformula_splitted.fillna(0, inplace = True)
        sumformula = sumformula.reset_index(drop=True)

        
        ##################################################
        ### Recalculating m/z ratio for homogeneity ######
        ##################################################
        
        
        mz = pandas.DataFrame(index=range(len(sumformula)))
        mz['m/z']=0.0
        v=0
        while v < len(sumformula_splitted) :
            form=sumformula_splitted.iloc[v]
            for atom in form.items():  
                mz['m/z'][v] = mz['m/z'][v] + atom[1]*isotopes_dict[atom[0]]
            v=v+1
        sumformula = sumformula.reset_index(drop=True)

        frames = [mz,sumformula_splitted,sumformula]
        merged = pandas.concat(frames, axis=1)
        merged['count'] = 0
        merged.rename(columns = {'sum formula':'molecular_formula'}, inplace = True)
        
        #####################################################################
        ### Boucle de regroupement des intensités pour chaque tableaux ######
        #####################################################################
        n = 0
        m = []
        data_frames_abs_intens = []
        data_frames_rel_intens = []
        data_frames_std_rel = []
        while n < len(data):
            data[n]["molecular_formula"] = data[n]["molecular_formula"].replace(' ','',regex = True)
            if "std_dev_rel" in data[n]:
                data_frames_abs_intens.append(data[n][["molecular_formula","absolute_intensity"]])
                data[n]['relative_intens'] = (data[n]['absolute_intensity']/sum(data[n]['absolute_intensity']))*100
                data_frames_rel_intens.append(data[n][["molecular_formula","relative_intens"]])
                data_frames_std_rel.append(data[n][["molecular_formula","std_dev_rel"]])
                m.append(n)
            else:    
                data_frames_abs_intens.append(data[n][["molecular_formula","absolute_intensity"]])
                data[n]['relative_intens'] = (data[n]['absolute_intensity']/sum(data[n]['absolute_intensity']))*100
                data_frames_rel_intens.append(data[n][["molecular_formula","relative_intens"]])
                data_frames_std_rel.append(data[n]["molecular_formula"])
            n = n+1
        
        
        #####################################################################
        ### Merge de toutes les intensités en fonction de la formule brute ?##
        #####################################################################
    
        intens_abs_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_abs_intens).fillna('0')
        intens_rel_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_rel_intens).fillna('0')
        if len(data_frames_std_rel) !=0:
            std_rel_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_std_rel).fillna('0')
            std_rel_merged = std_rel_merged.drop_duplicates(subset='molecular_formula')
        #################################
        intens_abs_merged = intens_abs_merged.drop_duplicates(subset='molecular_formula')
        intens_rel_merged = intens_rel_merged.drop_duplicates(subset='molecular_formula')
        ### Renommage des colonnes ######
        #################################
        n = 0
        c = 0
        while n < len(data):
            name_data = name[n]
            intens_abs_merged.columns.values[n+1] = "Abs_intens_" + str(name_data)
            intens_rel_merged.columns.values[n+1] = "Rel_intens_" + str(name_data)
            if n in m:
                std_rel_merged.columns.values[c+1] = "Std_rel_" + str(name_data)
                c = c+1
            n = n+1
        ###################################################
        ### Merge final des intensités + SF + m/z #########
        ###################################################
        merged.set_index('molecular_formula',inplace=True)
        intens_abs_merged.set_index('molecular_formula',inplace=True)
        intens_rel_merged.set_index('molecular_formula',inplace=True)
        if len(data_frames_std_rel) !=0:
            std_rel_merged.set_index('molecular_formula',inplace=True)
            data_frames = [merged,intens_abs_merged,intens_rel_merged,std_rel_merged]
        else:
            data_frames = [merged,intens_abs_merged,intens_rel_merged]
        merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames) #NaN si moins de 3 fichiers (!)
        merged.reset_index(inplace=True)
        
        ##########################################################
        ### Fonction pour compter les intensités non nulles ######
        ##########################################################
    
        n = merged.columns.get_loc('count')+1
        m = n + len(data)
        temp_count = merged.iloc[:,n:m]
        temp_count = temp_count.to_numpy().astype('float')
        merged['count'] = np.count_nonzero(temp_count,axis=1)
        intens_rel_merged.reset_index(inplace=True, drop = True)
        intens_rel_merged = pandas.DataFrame(intens_rel_merged).astype('float')
        merged['summed_intensity'] = intens_rel_merged.iloc[:,intens_rel_merged.columns != 'molecular_formula'].sum(axis=1)
        
        merged.sort_values('m/z',inplace=True)
        merged.sort_values('summed_intensity',inplace=True)
        merged.fillna(float(0),inplace = True)
        return merged
