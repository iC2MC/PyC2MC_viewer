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
def merge_merged_file(names,isotopes_dict):
        """
        This function is used to concatenate fusionned of merged files together in one unique file "merged".
        The merge is working using the molecular formula
        
        Args: 
            names(dict): list of path of files to load and process.
            
        Return a pandas.DataFrame.    
        """
        temp_data_fused = {}
        temp_data_merged = {}
        filename = pandas.Series()
        sumformula = pandas.Series()
        
        if len(names[0]) == 1:
            merged=pandas.read_csv(open(names[0][0]), sep=',|;', encoding="utf-8")
        else:
            merged = pandas.DataFrame().astype('float') 
            n = 0
            f = 0 #Counter for fused files
            m = 0 #Counter for merged files
            while n < len(names[0]):
                _, filename["%s" %n] = os.path.split(names[0][n])
                temp = load_MS_file(names[0][n],isotopes_dict)
                if temp.df_type == 'PyC2MC_fusion':
                    temp_data_fused["%s" %f] = temp.df
                    f = f + 1
                elif temp.df_type == 'PyC2MC_merged':
                    temp_data_merged["%s" %m] = temp.df
                    m = m + 1
                n = n + 1
            if f != 0 and m != 0 :
                raise TypeError
            elif f != 0:
                temp_data = temp_data_fused
                n_files = f
            elif m != 0:
                temp_data = temp_data_merged
                n_files = m
            for n in range(n_files):
                sumformula = sumformula.append(temp_data["%s" %n]['molecular_formula'])     
            
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
            if m !=0:    
                n = 0
                n_samples = 0
                data_frames_abs_intens = []
                data_frames_rel_intens = []
                while n < len(names[0]):
                    filter_col_abs = [col for col in temp_data["%s" %n] if 'Abs_intens' in col]
                    filter_col_abs.append('molecular_formula')
                    filter_col_rel = [col for col in temp_data["%s" %n] if 'Rel_intens' in col]
                    filter_col_rel.append('molecular_formula')
                    data_frames_abs_intens.append(temp_data["%s" %n][filter_col_abs])
                    data_frames_rel_intens.append(temp_data["%s" %n][filter_col_rel])
                    n_samples = n_samples + len(filter_col_abs) - 1
                    n = n+1
            elif f !=0:    
                n = 0
                n_samples = 0
                data_frames_abs_intens = []
                data_frames_rel_intens = []
                while n < len(names[0]):
                    data_frames_abs_intens.append(temp_data["%s" %n][["molecular_formula","absolute_intensity"]])
                    data_frames_rel_intens.append(temp_data["%s" %n][["molecular_formula","normalized_intensity"]])
                    n = n+1
                n_samples = n
            ###############################################################################
            ### Merge de toutes les intensités en fonction de la formule moleculaire ######
            ###############################################################################
        
            intens_abs_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_abs_intens).fillna('0')
            intens_rel_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['molecular_formula'], how='outer'), data_frames_rel_intens).fillna('0')
            intens_abs_merged = intens_abs_merged.drop_duplicates(subset='molecular_formula')
            intens_rel_merged = intens_rel_merged.drop_duplicates(subset='molecular_formula')
            #################################
            ### Renommage des colonnes ######
            #################################
            if f != 0:
                n = 0
                while n < len(names[0]):
                    name_data = os.path.basename(names[0][n])
                    if n < len(names[0]):
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
            m = n + n_samples
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
    

