from sklearn import preprocessing

def Normalize(intens):
    error = 0
    intens=intens.values.reshape(-1,1)
    if intens.shape[0]>1:
        min_max_scaler = preprocessing.MinMaxScaler()
        intens = min_max_scaler.fit_transform(intens)
    elif intens.shape[0]==1:
        intens = 1
    else:
        error = 1
    return intens,error