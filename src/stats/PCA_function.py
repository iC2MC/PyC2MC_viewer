import pandas
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d

def plot_pca(pca_data_raw,axes,n_comp,pca_on,para_dict):
    """
    Plots PCA results

    Parameters
    ----------
    pca_data_raw : pandas.DataFrame
        Raw data to be analysed.
    axes : int
        Allows to choose wich axis will be represented on the final plot.
    n_comp : int
        Number of component to take into account (min 3).
    pca_on : str
        Allows to choose between performing the analysis on  the whole dataset or only on common individuals.
    para_dict : dict
        Contains several parameters (font size, dot size).

    Returns
    -------
    loadings_df : pandas.DataFrame
        Original dataframe with the calculated PCA coefficients.
    first_comps : float
        Explained variance of the 3 first components.

    """
    
    if pca_on == 'all' : 
        pass
    elif pca_on == 'common' : 
        max_count = max(pca_data_raw['count'])
        pca_data_raw = pca_data_raw[pca_data_raw['count'] == max_count] 
    mz = pca_data_raw['m/z']
    pca_data = pca_data_raw.filter(like = 'Rel')
    pca_data = pca_data.transpose()
    pca_out=PCA(n_components=n_comp)

    pca_scores=pca_out.fit_transform(pca_data)

        
    loadings = pca_out.components_
    n_comp = pca_out.n_components_
    first_comps= np.sum(pca_out.explained_variance_ratio_[0:3])*100
    loadings_df = pandas.DataFrame(
        {f"PC{i + 1}": loadings[i, :] for i in range(n_comp)}
    )
    loadings_df.index.name = "variable"
    
    scores = pca_out.explained_variance_ratio_ / pca_out.explained_variance_ratio_.sum() * 100
    if axes ==0: 
        x =0
        y =1
        z =2
    elif axes ==1:
        x =1
        y =2
        z = 0
    elif axes==2:
        x =0
        y =2
        z = 1
    elif axes ==3:
        x =0
        y =1
        z = 2
    #Loading
    if axes <=2:
        fig, ax = plt.subplots(figsize=(9, 7))
        p = ax.scatter(pca_scores[:,x], pca_scores[:,y],c=pca_scores[:,z], marker="o", s=para_dict['ds'])
        ax.set_xlabel(f"PC{x + 1} ({scores[x]:.2f} %)",fontsize=para_dict['fs']+2)
        ax.set_ylabel(f"PC{y + 1} ({scores[y]:.2f} %)",fontsize=para_dict['fs']+2)
        cbar= plt.colorbar(p)
        cbar.set_label(f"PC{z + 1} ({scores[z]:.2f} %)", rotation=90,fontsize=para_dict['fs'])
        cbar.ax.tick_params(labelsize=para_dict['fs']-2)
        plt.xticks(fontsize=para_dict['fs']-2)
        plt.yticks(fontsize=para_dict['fs']-2)
        for i, label in enumerate(pca_data.index):
            label = label.replace('Rel_intens_','')
            label = label.replace('.csv','')
            ax.annotate(label, (pca_scores[i, x], pca_scores[i, y]),fontsize=para_dict['fs']-4, alpha = 0.8)    
        plt.title('Principal Component Analysis', fontsize=para_dict['fs']+4)
        loadings_df.set_index(mz,inplace=True)
        fig.show()
    else:
        fig = plt.figure(figsize=(9,7))
        ax = fig.add_subplot(111, projection='3d')
        
        fig.patch.set_facecolor('white')
        
         
        ax.scatter(pca_scores[:,x], pca_scores[:,y], pca_scores[:,z], s=para_dict['ds'], c = 'red')
        for i, label in enumerate(pca_data.index):
            label = label.replace('Rel_intens_','')
            label = label.replace('.csv','')
            ax.text(pca_scores[i, x], pca_scores[i, y],pca_scores[i, z],label,size=para_dict['fs']-4, alpha = 0.8)  
        # for loop ends
        ax.set_xlabel(f"PC{x + 1} ({scores[x]:.2f} %)",fontsize=para_dict['fs']+2)
        ax.set_ylabel(f"PC{y + 1} ({scores[y]:.2f} %)",fontsize=para_dict['fs']+2)
        ax.set_zlabel(f"PC{z + 1} ({scores[z]:.2f} %)",fontsize=para_dict['fs']+2)
        loadings_df.set_index(mz,inplace=True)
        ax.legend()
        plt.show()

    return loadings_df,first_comps