import pandas as pd
from src.pre_processing_function import pre_processing
import chemparse
from src.pre_treatment_petroOrg import Pre_treatment_petroOrg

def load_MS_file(filename,isotopes_dict):
    """
    Global loading data method. Recognize file type and calls the appropriate function(s)
    
    Args:
        filename (path): Directory of the file.
        
    Returns data (Peak_list): A Peak_list class object containing raw or
    preprocessed MS data.
    """
    
    
    
    if type(filename) != str :
        data=Peak_list.from_inline_merged(filename)
        data = pre_processing(data)
        return data

    if filename.endswith('.asc'):
        data = Peak_list.from_asc(filename)
        return data

    if filename.endswith('.csv'):
        data = load_csv_file(filename)
        data = pre_processing(data)
        if not data :
            return filename
        return data
    
    if filename.endswith('xlsx'):
        data = load_xlsx_file(filename)
        if data.df_type == 'Error':
            return data
        data = pre_processing(data)
        return data

    if filename.endswith('.pks'):
        #data = Peak_list.from_pks(filename)
        return data
    if filename.endswith('.xls'):
        data = Pre_treatment_petroOrg(filename)
        data = Peak_list.from_petroOrg(data)
        data = pre_processing(data)
        return data


def load_csv_file(filename):
    """
    CSV file loading method for raw or attributted data.
    
    Args:
        filename (path): Directory of the file.
        
    Returns data (pandas.DataFrame): pre-formatted dataset
    """
    header = get_header_csv(filename)
    if header == 2: # Particular attributed csv file from PetroOrg
        data_df = pd.read_csv(filename, skiprows = 2,header=None,sep=',|;',encoding="utf-8", engine='python')
        data = Peak_list.from_csv_petroOrg(data_df)
    else:    
        data_df = pd.read_csv(filename, header = header,sep=',|;',encoding="utf-8", engine='python')
        if "#" in data_df: # non-attributed csv file from DA
            data = Peak_list.from_csv_raw(data_df)
        elif "Observed Intens" in data_df: #attributed CSV file from DA
            data = Peak_list.from_csv_data_analysis(data_df)
        elif "count" in data_df:
            if 'summed_intensity' in data_df : #merged file
                data = Peak_list.from_merged(data_df)
            elif 'Rel_intens' in data_df : #fusionned replicates
                data = Peak_list.from_fusionned(data_df)
            else : #merged non attributed from DA
                data = Peak_list.from_merged_unattributed(data_df)
        elif "SPECTRUM - MS" in data_df: #Qual browser ( orbi with special header)
            data_df = pd.read_csv(filename, header = 6,sep=',|;',encoding="utf-8", engine='python')
            data = Peak_list.from_csv_orbitrap(data_df)
        elif "Relative" in data_df:
            if "Delta (ppm)" in data_df: # attributed orbitrap csv file
                data = Peak_list.from_csv_orbitrap(data_df)
            else: # non-attributed orbitrap csv file
                data = Peak_list.from_csv_raw_orbitrap(data_df)
        elif "Flags" in data_df: #Frestyle export w/o attributions
            data = Peak_list.from_csv_raw_orbitrap(data_df)
        elif "H/C" in data_df:
            data = Peak_list.from_csv_saved(data_df)
        else: # other file
            data = Peak_list.from_csv_other(data_df)


    return data

def load_xlsx_file(filename):
    """
    xlsx file loading method for raw or attributted data.
    
    Args:
        filename (path): Directory of the file.
        
    Returns data (pandas.DataFrame): pre-formatted dataset
    """
    header = get_header_xlsx(filename)
    data_df = pd.read_excel(filename, skiprows = header)
    if 'ROI' in data_df: #CERES processing file
        data = Peak_list.from_CERES(data_df)
    else:
        data = Peak_list.from_file(data_df)
    return data
     
def get_header_csv(filename):

    """
    Search if exists a header in the csv file.
    """
    try:
        df2 = pd.read_csv(filename, nrows = 5)
        del df2
        return 0
    except:
        try:
            df2 = pd.read_csv(filename, nrows = 2)
            del df2
            return 5
        except:
            return 2
    
def get_header_xlsx(filename):

    """
    Search if exists a header in the xlsx file.
    
    Args:
        filename (path): Directory of the file.
    """
    try:
        df2 = pd.read_excel(filename, nrows = 5)
        del df2
        return 0
    except:
        return 5




class Peak_list:
    """
    Inside this class it is defined all the attributes for the Raw Data.

    . attribute: mass

        m/z calc. column of the data DataFrame.

    . attribute: observed_intensity

        Experimental intensity.

    . attribute: normalized_intensity

        Normalized inensity value in (%)

    . attribute: df

        DataFrame containing the file information.

    . attribute: dt_type

        String containing the type of loaded file (DataAnalysis, Xcalibur...)

    """

    def __init__(self, data,df_type,heteroatoms = 'None' ,pca_data = 'None'):
        """
        Instance method for the RawData class.

        Args:
            data (pandas.DataFrame): it is a pandas DataFrame that contains the
                mass and intensity values from a mass spectrum, which has not
                been attributed yet.
            df_type (str): Origin of the file loaded (DataAnalysis, Xcalibur...)

        """

        self.mass = data['m/z'].values #values converts it into numpy array
        if df_type != 'PyC2MC_merged' and df_type != 'PyC2MC_merged_unattributed':
            self.absolute_intensity = data['absolute_intensity']
            self.normalized_intensity = data['normalized_intensity']
        self.heteroatoms = heteroatoms
        self.df_type = df_type
        self.pca_data = pca_data
        self.df = data

    @classmethod
    def from_file(cls, filename):
        """
        Initialize the Peak_list class for an unsopported file
        """
        del filename
        df = pd.DataFrame(columns=['m/z','absolute_intensity','normalized_intensity'])
        heteroatoms = None
        pca_data = None
        df_type = 'Error'
        return cls(df,df_type,heteroatoms,pca_data)
    


    @classmethod
    def from_asc(cls, filename, **kwargs):
        """
        Initialize the Peak_list class for a non-attributed asc file.

        Args:
            filename (path): Directory of the file.
            kwargs: kwargs from pandas.read_csv() method.

        Returns an object of the class RawData
        """
        names = ['m/z',
                 'absolute_intensity',
                 'S/N ratio']
        df = pd.read_csv(filename, delim_whitespace=(True), names=names,
                         **kwargs)
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df_type = 'Peaklist'
        return cls(df,df_type)

    @classmethod
    def from_csv_raw(cls, df):
        """
        Initialize the Peak_list class for a non-attributed csv file.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        names = ['#',
                 'm/z',
                 'absolute_intensity']
        df.columns = names
        df = df.drop('#',axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df_type = 'Peaklist'
        return cls(df,df_type)

    @classmethod
    def from_csv_raw_orbitrap(cls,df):
        """
        Initialize the Peak_list class for a non-attributed csv file (orbitrap).

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        df = df.iloc[:,[0,1]]
        names = ['m/z',
                 'absolute_intensity']
        df.columns = names
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df_type = 'Peaklist'
        return cls(df,df_type)

    @classmethod
    def from_csv_data_analysis(cls, df_initial):
        """
        Initialize the Peak_list class for a non-attributed csv file.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        names_dict = {'calc. m/z':'m/z','Observed Intens':'absolute_intensity', 'err ppm': 'err_ppm',
                      'sum formula':'molecular_formula'}
        df_initial = df_initial.rename(columns=names_dict)
        df_initial = df_initial.loc[:, ~df_initial.columns.str.contains('^Unnamed')]
        index_nan = df_initial[df_initial['C'].isnull()].index
        if len(index_nan) != 0:
            for index in index_nan:
                df_initial = df_initial.drop(labels = index)
                df_initial = df_initial.reset_index(drop=True)
        df = pd.DataFrame().astype('Float')
        temp = df_initial[df_initial.columns[df_initial.columns.get_loc('molecular_formula'):]]
        df = pd.concat([df,df_initial['m/z'],df_initial['absolute_intensity'],df_initial['err_ppm']],axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values*100/ \
            df["absolute_intensity"].values.max()
        df = df.reindex(['m/z','absolute_intensity','normalized_intensity','err_ppm'],axis = 1)
        df = pd.concat([df,temp],axis=1)
        df['molecular_formula'] = df['molecular_formula'].replace(' ','',regex = True)
        heteroatoms = df[df.columns[df.columns.get_loc('molecular_formula')+1:len(df.columns)]]
        if "N" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('H')+1,"N",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('H')+1,"N",0)
        if "O" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('N')+1,"O",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('N')+1,"O",0)
        if "S" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('O')+1,"S",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('O')+1,"S",0)
        df_type = 'Attributed'
        return cls(df,df_type,heteroatoms)
    
    @classmethod
    def from_csv_other(cls, df_initial):
        """
        Initialize the Peak_list class for an attributed csv file not coming from a compatible software.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        columns = df_initial.columns
        names_list = ('m/z','absolute_intensity','err_ppm','molecular_formula')
        names_dict = dict(zip(columns,names_list))
        
        df_initial = df_initial.rename(columns=names_dict)
        df_initial = df_initial.loc[:, ~df_initial.columns.str.contains('^Unnamed')]
        df = pd.DataFrame().astype('Float')
        temp = df_initial[df_initial.columns[df_initial.columns.get_loc('molecular_formula'):]]
        df = pd.concat([df,df_initial['m/z'],df_initial['absolute_intensity'],df_initial['err_ppm']],axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values*100/ \
            df["absolute_intensity"].values.max()
        df = df.reindex(['m/z','absolute_intensity','normalized_intensity','err_ppm'],axis = 1)
        df = pd.concat([df,temp],axis=1)
        df['molecular_formula'] = df['molecular_formula'].replace(' ','',regex = True)
        heteroatoms = pd.DataFrame(list([chemparse.parse_formula(formula) for formula in df['molecular_formula']]))
        heteroatoms.fillna(0,inplace = True)
        heteroatoms = heteroatoms.astype(int)
        
        if "N" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('H')+1,"N",0)
        if "O" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('N')+1,"O",0)
        if "S" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('O')+1,"S",0)
        df=df.join(heteroatoms)
        df_type = 'Attributed'
        return cls(df,df_type,heteroatoms)

    @classmethod
    def from_csv_saved(cls, df_initial):
        """
        Initialize the Peak_list class for an attributed csv file not coming from a compatible software.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        
        df_initial = df_initial.loc[:, ~df_initial.columns.str.contains('^Unnamed')]
        df = df_initial
        heteroatoms = pd.DataFrame(list([chemparse.parse_formula(formula) for formula in df['molecular_formula']]))
        heteroatoms.fillna(0,inplace = True)
        heteroatoms = heteroatoms.astype(int)
        if "N" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('H')+1,"N",0)
            if "N" not in df.columns:
                df.insert(df.columns.get_loc('H')+1,"N",0)
        if "O" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('N')+1,"O",0)
            if "O" not in df.columns:
                df.insert(df.columns.get_loc('N')+1,"O",0)
        if "S" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('O')+1,"S",0)
            if "S" not in df.columns:
                df.insert(df.columns.get_loc('O')+1,"S",0)
        df_type = 'Attributed'
        return cls(df,df_type,heteroatoms)


    @classmethod
    def from_csv_orbitrap(cls, df):
        """
        Initialize the Peak_list class for a non-attributed csv orbitrap file.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        names_dict = {'Relative':'normalized_intensity','Intensity':'absolute_intensity'
                      ,'Delta (ppm)':'err_ppm','Composition':'molecular_formula'}
        df.dropna(subset=['Delta (ppm)'], inplace = True)
        df.reset_index(drop = True, inplace = True)
        df = df.loc[:, ~df.columns.str.contains('Segment Number')]
        df = df.loc[:, ~df.columns.str.contains('Flags')]
        df = df.loc[:, ~df.columns.str.contains('RDB equiv')]
        dict_data={'C': 12,'H':1.007825,'N':14.003074,'O':15.994915,'S':31.972072,'Cl':34.968853,'Si':27.976928,'P':30.9737634\
        ,'V':50.943963,'K':39.0983,'Na':22.989769,'Li':7.016005,'Cu':62.929599,'Ni':57.935347,'F':18.998403,'Ca':39.962590863,'B':11.009305, 'Zn':63.92915, 'Br':78.91834}
        df['Composition'] = df['Composition'].replace(['³²S','₀','₁','₂','₃','₄','₅','₆','₇','₈','₉',' '],
                                                      ['S','0','1','2','3','4','5','6','7','8','9',''],regex=True)
        heteroatoms = pd.DataFrame(list([chemparse.parse_formula(formula) for formula in df['Composition']]))
        heteroatoms.fillna(0,inplace = True)
        heteroatoms = heteroatoms.astype(int)
        if "N" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('H')+1,"N",0)
        if "O" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('N')+1,"O",0)
        if "S" not in heteroatoms.columns:
            heteroatoms.insert(heteroatoms.columns.get_loc('O')+1,"S",0)
        df['m/z']=0.0
        v = 0
        ratio_mz = []
        while v < len(df['Composition']) :
            mass = 0
            form=chemparse.parse_formula(df['Composition'][v])
            for atom in form:  
                mass = mass + form[atom]*dict_data[atom]
            ratio_mz.append(mass)
            v=v+1
        df['m/z'] = ratio_mz
        df = df.rename(columns=names_dict)
        df = df.reindex(['m/z','absolute_intensity','normalized_intensity','err_ppm','molecular_formula'],axis = 1)
        df=df.join(heteroatoms)
        df_type='Attributed'
        return cls(df,df_type,heteroatoms)


    @classmethod
    def from_merged(cls, df):
        """
        Initialize the Peak_list class for a PyC2MC merged csv file.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class Peak_list.
        """
        df[df.columns[df.columns.get_loc('calc. m/z')+1:df.columns.get_loc('count')]] = \
            df[df.columns[df.columns.get_loc('calc. m/z')+1:df.columns.get_loc('count')]].astype(int)
        heteroatoms = df[df.columns[df.columns.get_loc('calc. m/z')+1:df.columns.get_loc('count')]]
        
        if "N" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('H')+1,"N",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('H')+1,"N",0)
        if "O" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('N')+1,"O",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('N')+1,"O",0)
        if "S" not in heteroatoms.columns:
            df.insert(df.columns.get_loc('O')+1,"S",0)
            heteroatoms.insert(heteroatoms.columns.get_loc('O')+1,"S",0)
            
        
        names_dict = {'calc. m/z':'m/z','sum formula':'molecular_formula'}
        df = df.rename(columns=names_dict)
        pca_data = pd.DataFrame(df[['count','m/z']]).join(df.filter(like='Rel'))
        df_type = 'PyC2MC_merged'

        return cls(df,df_type,heteroatoms,pca_data)
    
    @classmethod
    def from_merged_unattributed(cls, df):
        """
        Initialize the Peak_list class for a PyC2MC merged csv file from unattributed datas.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class Peak_list.
        """
        heteroatoms = None
        pca_data = pd.DataFrame(df[['count','m/z']]).join(df.filter(like='Rel_'))
        df_type = 'PyC2MC_merged_unattributed'
    
        return cls(df,df_type,heteroatoms,pca_data)
    @classmethod
    def from_inline_merged(cls, df):
        """
        Initialize the Peak_list class for an inline PyC2MC merged dataset.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class Peak_list.
        """
        df[df.columns[df.columns.get_loc('m/z')+1:df.columns.get_loc('count')]] = \
            df[df.columns[df.columns.get_loc('m/z')+1:df.columns.get_loc('count')]].astype(int)
        heteroatoms = df[df.columns[df.columns.get_loc('m/z')+1:df.columns.get_loc('count')]]
        pca_data = df.filter(like='Rel')
        df_type = 'PyC2MC_merged'
        return cls(df,df_type,heteroatoms,pca_data)

    @classmethod
    def from_fusionned(cls,df):
        """
        Initialize the Peak_list class for a PyC2MC fusionned replicates file

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class Peak_list.
        """
        heteroatoms = df[df.columns[df.columns.get_loc('calc. m/z')+1:df.columns.get_loc('count')-1]]
        names_dict = {'calc. m/z':'m/z','sum formula':'molecular_formula','Rel_intens':'normalized_intensity','Abs_intens':'absolute_intensity'}
        df = df.rename(columns=names_dict)
        df_type = 'PyC2MC_fusion'
        return cls(df,df_type,heteroatoms)
    
    
    
    
    @classmethod
    def from_CERES(cls,df_initial):
        """
        Initialize the Peak_list class for a csv file exported from CERES processing.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the csv file
                information.

        Returns an object of the class RawData.
        """
        Atoms_mass = {'C': 12,'H':1.007825,'N':14.003074,'O':15.994915,'S':31.972072,'Cl':34.968853,'Si':27.976928,'P':30.9737634\
        ,'V':50.943963,'K':39.0983,'Na':22.989769,'Li':7.016005,'Cu':62.929599,'Ni':57.935347,'F':18.998403,'B':11.009305,'Ca':39.962590863, 'Zn':63.92915, 'Br':78.91834}
        
        mol_form =''
        mass = 0
        heteroatoms = df_initial[df_initial.columns[df_initial.columns.get_loc('maximum_intensity')+1:df_initial.columns.get_loc('DBE')]]
        het_for_formula = heteroatoms.copy()

        for atom in het_for_formula:
            mol_form = mol_form + ' ' + atom + het_for_formula[atom].astype(str) 
            mol_form = mol_form.replace(atom +'0','',regex = True)
        df_initial['molecular_formula'] = mol_form
        names_dict = {'mz':'m/z','summed_intensity':'absolute_intensity', 'error_ppm': 'err_ppm'}
        df_initial = df_initial.rename(columns=names_dict)
        df_initial = df_initial.loc[:, ~df_initial.columns.str.contains('^Unnamed')]
        df = pd.DataFrame().astype('Float')
        temp = df_initial[df_initial.columns[df_initial.columns.get_loc('molecular_formula'):]]
        df = pd.concat([df,df_initial['m/z'],df_initial['absolute_intensity'],df_initial['err_ppm']],axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df = df.reindex(['m/z','absolute_intensity','normalized_intensity','err_ppm'],axis = 1)
        df = pd.concat([df,temp],axis=1)
        df['molecular_formula'] = df['molecular_formula'].replace(' ','',regex = True)
        df_type = 'Attributed'
        df=df.join(heteroatoms)
        for atom in heteroatoms:
             mass = mass + Atoms_mass[atom]*heteroatoms[atom].astype(int) 
        df['m/z'] = mass
        return cls(df,df_type,heteroatoms)


    @classmethod
    def from_pks(cls, filename, **kwargs):
        """
        Open a non-attributed pks file.

        Args:
            filename (path): Directory of the file.
            kwargs: kwargs from pandas.read_csv() method.

        Returns an object of the class RawData.
        """

        del filename
        df = None
        df_type = None
        return cls(df,df_type)
    
    @classmethod
    def from_petroOrg(cls, df_initial):
        """
        Initialize the Peak_list class for a attributed xls file from petroOrg.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the xls file
                information.

        Returns an object of the class RawData.
        """
        mol_form = ""
        names_dict = {'Theor. Mass':'m/z','Rel. Abundance':'absolute_intensity', ' Error': 'err_ppm'}
        start = df_initial.columns.get_loc('DBE')
        end = df_initial.columns.get_loc('H/C')
        het_for_formula = df_initial.iloc[:,start+2:end]

        for atom in het_for_formula:
            mol_form = mol_form + ' ' + atom + het_for_formula[atom].astype(str) 
            mol_form = mol_form.replace(atom +'0','',regex = True)
        df_initial['molecular_formula'] = mol_form    
        df_initial = df_initial.rename(columns=names_dict)
        df = pd.DataFrame().astype('Float')
        df = pd.concat([df_initial['m/z'],df_initial['absolute_intensity'],df_initial['err_ppm'],df_initial['molecular_formula'],df_initial[het_for_formula.columns]],axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df = df.reset_index(drop=True)
        heteroatoms = het_for_formula.reset_index(drop=True)
        df_type = 'Attributed'
        return cls(df,df_type,heteroatoms)
    
    @classmethod
    def from_csv_petroOrg(cls, df_initial):
        """
        Initialize the Peak_list class for a attributed csv file from petroOrg.

        Args:
            df (pandas.DataFrame): A pandas DataFrame containing the xls file
                information.

        Returns an object of the class RawData.
        """
        mol_form = ""
        names_dict = {3:'m/z',5:'absolute_intensity', 4: 'err_ppm'}
        
        if df_initial.iloc[:,len(df_initial.columns)-1].isnull().values.any():
            df_initial.drop(df_initial.columns[len(df_initial.columns)-1],axis=1,inplace=True)
        if "13C" in df_initial.iloc[0].to_list():
            u = df_initial.iloc[0].to_list().index("13C")
            df_initial.drop(columns=df_initial.columns[[u,u+1]],inplace = True)
        mol_form = df_initial.loc[:,10:len(df_initial.columns)+1]
        df_initial.drop(mol_form.columns,axis = 1, inplace = True)
        last_col = len(mol_form.columns)-1
        mol_form.iloc[:,last_col] = mol_form.iloc[:,last_col].fillna(0).astype(int) #convert last column to int
        mol_form.iloc[:,last_col-1] = mol_form.iloc[:,last_col-1].fillna("") #Erase NaN
        mol_form.iloc[:,-2] = mol_form.iloc[:,-2].replace({'56Fe':"Fe","24Mg":"Mg"})
        mol_form = mol_form.apply(lambda row: ''.join(map(str, row)), axis=1)
        heteroatoms = pd.DataFrame(list([chemparse.parse_formula(formula) for formula in mol_form]))
        if heteroatoms.iloc[:,len(heteroatoms.columns)-1].isnull().values.any():
            heteroatoms.drop(heteroatoms.columns[len(heteroatoms.columns)-1],axis=1,inplace=True)
        heteroatoms.fillna(0,inplace=True)
        df_initial['molecular_formula'] = mol_form
        df_initial = df_initial.rename(columns=names_dict)
        df = pd.DataFrame().astype('Float')
        df = pd.concat([df_initial['m/z'],df_initial['absolute_intensity'],df_initial['err_ppm'],df_initial['molecular_formula'],heteroatoms],axis=1)
        df['normalized_intensity'] = df["absolute_intensity"].values/ \
            df["absolute_intensity"].values.max()*100
        df.fillna(0,inplace=True)
        df_type = 'Attributed'
        return cls(df,df_type,heteroatoms)
