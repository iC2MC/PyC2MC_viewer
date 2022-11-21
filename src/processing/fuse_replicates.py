import pandas
import os
from functools import reduce
import numpy as np
import chemparse
from ..loading.loading_function import load_MS_file


def fuse_replicates(names,replicates):
    """
    Special merging process only keeping the species found in at least a defined number of analysis

    Args:

        names (str): Filenames to be loaded, provided by a Qt.FileDialog box.

        replicates (int): Minimal number of analyses where a species has to be found to be merged

        save_name(str): Output file name ['savename'.csv]
    """
    temp_data = {}
    data = {}
    filename = pandas.Series()
    sumformula = pandas.Series()
    mz = pandas.Series()

    if len(names[0]) == 1:
        merged=load_MS_file(names[0][0]).df
    else:
        merged = pandas.DataFrame().astype('float')
        n = 0
        while n < len(names[0]):
            _, filename["%s" %n] = os.path.split(names[0][n])
            try : temp_data["%s" %n] =  load_MS_file(names[0][n]).df
            except : temp_data["%s" %n] =  load_MS_file(names[0][n]).df
            
            temp_data["%s" %n] = temp_data["%s" %n].sort_values(by=["normalized_intensity"], ascending=True)
            temp_data["%s" %n]['relative_intens'] = (temp_data["%s" %n]['normalized_intensity']/sum(temp_data["%s" %n]['normalized_intensity']))*100
            data["%s" %n] = pandas.DataFrame(temp_data["%s" %n])
            sumformula = sumformula.append(data["%s" %n]['molecular_formula'])
            mz = mz.append(data["%s" %n]['m/z'])
            n = n+1
            

        sumformula = sumformula.drop_duplicates()
        sumformula.name = 'molecular_formula'
        sumformula = sumformula.str
        sumformula = sumformula.replace(" ", "")
        sumformula_splitted = [chemparse.parse_formula(formula) for formula in sumformula]
        sumformula_splitted = pandas.DataFrame(list(sumformula_splitted))
        sumformula_splitted.fillna(0, inplace = True)
        sumformula_splitted = sumformula_splitted.astype(int)
        sumformula = sumformula.reset_index(drop=True)
        mz = mz.drop_duplicates()
        mz.name = 'm/z'
        mz = mz.reset_index(drop = True)

        frames = [mz,sumformula_splitted,sumformula]
        merged = pandas.concat(frames, axis=1)
        merged['count'] = 0
        #####################################################################
        ### Boucle de regroupement des intensités pour chaque tableaux ######
        #####################################################################
        n = 0
        data_frames_abs_intens = []
        data_frames_rel_intens = []
        while n < len(names[0]):
            data_frames_abs_intens.append(data["%s" %n][["m/z","absolute_intensity"]])
            data_frames_rel_intens.append(data["%s" %n][["m/z","relative_intens"]])
            n = n+1

        #####################################################################
        ### Merge de toutes les intensités en fonction de la calc. m/z ######
        #####################################################################

        intens_abs_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['m/z'], how='outer'), data_frames_abs_intens).fillna('0')
        intens_rel_merged = reduce(lambda  left,right: pandas.merge(left,right,on=['m/z'], how='outer'), data_frames_rel_intens).fillna('0')
        intens_abs_merged = intens_abs_merged.drop_duplicates(subset='m/z')
        intens_rel_merged = intens_rel_merged.drop_duplicates(subset='m/z')

        #################################
        ### Renommage des colonnes ######
        #################################
        n = 0
        while n < len(names[0]):
            name_data = os.path.basename(names[0][n])
            if n < len(names[0]):
                intens_abs_merged.columns.values[n+1] = "Abs_intens_" + name_data
                intens_rel_merged.columns.values[n+1] = "Rel_intens_" + name_data
            n = n+1


        #################################
        ### Calcul des moyennes    ######
        #################################

        mean_abs = intens_abs_merged.iloc[:,1:].astype('float').mean(axis=1).copy()
        mean_abs = pandas.DataFrame(mean_abs).astype('float')
        mean_abs['m/z'] = intens_abs_merged['m/z']

        mean_rel = intens_rel_merged.iloc[:,1:].astype('float').mean(axis=1).copy()
        mean_rel = pandas.DataFrame(mean_rel).astype('float')
        mean_rel['m/z'] = intens_rel_merged['m/z']

        ###################################################
        ### Merge final des intensités + SF + m/z #########
        ###################################################
        merged.set_index('m/z',inplace=True)
        intens_abs_merged.set_index('m/z',inplace=True)
        intens_rel_merged.set_index('m/z',inplace=True)
        mean_abs.set_index('m/z',inplace=True)
        mean_rel.set_index('m/z',inplace=True)
        data_frames = [merged,intens_abs_merged,intens_rel_merged,mean_abs,mean_rel]
        merged = reduce(lambda  left,right: pandas.merge(left,right,on=['m/z'], how='outer'), data_frames) #NaN si moins de 3 fichiers (!)
        merged.reset_index(inplace=True)

        ##########################################################
        ### Fonction pour compter les intensités non nulles ######
        ##########################################################

        n = merged.columns.get_loc('count')+1
        m = n + len(names[0])
        temp_count = merged.iloc[:,n:m]
        temp_count = temp_count.to_numpy().astype('float')
        merged['count'] = np.count_nonzero(temp_count,axis=1)
        merged = merged.rename(columns = {'m/z':'calc. m/z'})
        merged = merged.rename(columns = {'0_x':'Abs_intens','0_y':'Rel_intens'})
        merged = merged[merged["count"] >= replicates]
    ########################
    ### Export en CSV ######
    ########################
    return merged


