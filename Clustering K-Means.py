import os; os.chdir('C:/Users/marvi/Desktop/MsMDA/AutoFormation/Python')

import pandas as pd ; import numpy as np ; acheteurs = pd.read_csv('acheteurs.csv', sep=",")

#On appliquer le modele K-Means sur des variables numeriqes, 
#On recode les varibles categorielles avec un label encoding 

acheteurs_clusters = pd.DataFrame(np.c_[acheteurs.iloc[:,1:10]]) 

import pandas as pd ; import numpy as np ; acheteurs = pd.read_csv('acheteurs.csv', sep=",")

col = list(acheteurs.columns); del col[0]
acheteurs_clusters = pd.DataFrame(np.c_[acheteurs.iloc[:,1:10]], columns = col ) 
acheteurs_clusters["deviceCategory"] = acheteurs_clusters["deviceCategory"].astype('category')
acheteurs_clusters["deviceCategory"] = acheteurs_clusters["deviceCategory"].cat.codes
acheteurs_clusters["campaign"] = acheteurs_clusters["campaign"].astype('category')
acheteurs_clusters["campaign"] = acheteurs_clusters["campaign"].cat.codes
acheteurs_clusters["medium"] = acheteurs_clusters["medium"].astype('category')
acheteurs_clusters["medium"] = acheteurs_clusters["medium"].cat.codes
acheteurs_clusters["continent"] = acheteurs_clusters["continent"].astype('category')
acheteurs_clusters["continent"] = acheteurs_clusters["continent"].cat.codes
acheteurs_clusters["Product_Category"] = acheteurs_clusters["Product_Category"].astype('category')
acheteurs_clusters["Product_Category"] = acheteurs_clusters["Product_Category"].cat.codes


acheteurs_clusters = pd.DataFrame(np.c_[acheteurs_clusters.iloc[:,0:9]], columns = col)

#On ne sait pas a priori quel est le nombre optimal de clusters pour que le population soit separer de maniere
#à ce que les groupes constituées soit à la fois le plus homogenes possible et differents les un des autres
#on utlise pour cela la courbe d'elbow en testant une decomposition de 1 à 10 groupes

from sklearn.cluster import KMeans ; import matplotlib.pyplot as plt

distortions = [] ; K = range(1,10)

for k in K :
    kmeanModel = KMeans(n_clusters=k)
    kmeanModel.fit(acheteurs_clusters)
    distortions.append(kmeanModel.inertia_)

plt.figure(figsize=(16,8)) ; plt.plot(K, distortions, 'bx-') ; plt.xlabel('k') ; plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k') ; plt.show()

#la courbe d'elbow montre qu'il est optimal de constituer 4 groupes, le point après la cassure de la courbe

kmeanModel = KMeans(n_clusters= 4) ; kmeanModel.fit(acheteurs_clusters)

#On assigne chaque pays à son cluster
acheteurs['cluster'] = kmeanModel.predict(acheteurs_clusters)

#Caracterisation des clusters

acheteurs.groupby('cluster').count()[['ID_Visitor']]

pays_clusters_means = pd.DataFrame(acheteurs.groupby('cluster').mean()) ; pays_clusters_means

acheteurs.to_csv('acheteurs_clusters.csv', index = False)

#https://datastudio.google.com/reporting/fb6b9a87-7aff-41b6-89ce-b12a260b9658/page/p_2t5s4p71lc
