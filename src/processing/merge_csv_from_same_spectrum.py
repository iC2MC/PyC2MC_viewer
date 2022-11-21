################################
###Zone d'import des modules####
################################
import pandas
import os
from functools import reduce
import numpy as np
import chemparse

###Fonction de merge de fichier csv provenant d'un même spectre###


#################################################
###Définition de la fonction d'import des CSV####
#################################################

def merge_Multicsv(names):
    temp_data = {}
    data = {}
    filename = pandas.Series()
    mz = pandas.Series()
    Intensity = pandas.Series()
    Deltappm = pandas.Series()
    sumformula = pandas.Series()
    
    if len(names[0]) == 1:
        merged=pandas.read_csv(open(names[0][0]), sep=',|;', encoding="utf-8")
    else:
        merged = pandas.DataFrame().astype('float') 
        n = 0
        while n < len(names[0]):
            _, filename["%s" %n] = os.path.split(names[0][n])
            try : temp_data["%s" %n] =  pandas.read_csv(open(names[0][n]), sep=',|;', encoding="utf-8")
            except : temp_data["%s" %n] =  pandas.read_csv(names[0][n], sep=',', encoding="utf-8", header=5)
            
            temp_data["%s" %n].dropna(subset=['Delta (ppm)'], inplace = True)   
            temp_data["%s" %n] = temp_data["%s" %n].sort_values('m/z', ascending=True)
            temp_data["%s" %n].reset_index(drop = True, inplace = True)
            dict_data={'C': 12,'H':1.007825,'N':14.003074,'O':15.994915,'S':31.972072,'Cl':34.968853,'Si':27.976928,'P':30.9737634\
            ,'V':50.943963,'Li':7.016005,'Cu':62.929599,'Ni':57.935347,'F':18.998403,'B':11.009305, 'Zn':63.92915, 'Mo':97.90541}
            f=0
            while f < len(temp_data["%s" %n]): 
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('³²S','S')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('⁶⁴Zn','Zn')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('⁹²Mo','Mo')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₀','0')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₁','1')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₂','2')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₃','3')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₄','4')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₅','5')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₆','6')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₇','7')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₈','8')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₉','9')
               temp_data["%s" %n]['Composition'][f] = temp_data["%s" %n]['Composition'][f].replace('₉','9')
               f=f+1    
            temp_data["%s" %n]['formulas'] = [chemparse.parse_formula(formula) for formula in temp_data["%s" %n]['Composition']]
            df = pandas.DataFrame(list(temp_data["%s" %n]['formulas']))
            df.index=temp_data["%s" %n].index
            df.fillna(0,inplace = True)
            df = df.astype(int)
            temp_data["%s" %n] = temp_data["%s" %n].join(df)
            temp_data["%s" %n]['mass']=0.0
            v=0
            while v < len(temp_data["%s" %n]['Composition']) :
                form=chemparse.parse_formula(temp_data["%s" %n]['Composition'][v])
                for atom in form:  
                    temp_data["%s" %n]['mass'][v] = temp_data["%s" %n]['mass'][v] + form[atom]*dict_data[atom]
                v=v+1
            temp_data["%s" %n] = temp_data["%s" %n].rename(columns={'Intensity':'Observed Intens','mass':'calc. m/z','Delta (ppm)':'err ppm', 'Composition':'sum formula'})
            temp_data["%s" %n] = temp_data["%s" %n].loc[:, ~temp_data["%s" %n].columns.str.contains('^Unnamed')]                        
            data["%s" %n] = pandas.DataFrame(temp_data["%s" %n])
            mz = mz.append(data["%s" %n]['calc. m/z'])
            Intensity = Intensity.append(data["%s" %n]['Observed Intens'])
            sumformula = sumformula.append(data["%s" %n]['sum formula'])
            Deltappm = Deltappm.append(data["%s" %n]['err ppm'])
            n = n+1
    
     
    sumformula.name = 'sum formula'
    sumformula = sumformula.replace(" ", "") 
    mz.name = 'calc. m/z'
    Intensity.name = 'Observed Intens'
    Deltappm.name = 'err ppm'
    frames = [mz,Intensity,Deltappm,sumformula]
    merged = pandas.concat(frames, axis=1)
    merged['formulas'] = [chemparse.parse_formula(formula) for formula in merged['sum formula']]
    merged = merged.sort_values(by=["calc. m/z"], ascending=True)
    merged.reset_index(drop = True, inplace = True)
    sumformula_splitted = pandas.DataFrame(list(merged['formulas'])) 
    sumformula_splitted.fillna(0, inplace = True)
    sumformula_splitted = sumformula_splitted.astype(int)
    merged = merged.join(sumformula_splitted)
    merged=merged.drop(columns="formulas")

        
        
    return merged