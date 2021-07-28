########################################### Machine Learning  ##########################################################

import os; os.chdir('C:/Users/marvin/Desktop/Python')

########################################### Clustering K-Means  #######################################################

import pandas as pd ; import numpy as np ; pays = pd.read_csv('pays.csv', sep=",")

col = list(pays.columns); del col[0]

pays_clusters = pd.DataFrame(np.c_[pays.iloc[:,1:4]], columns = col, index = pays['country']) 

# Attention On appliquer le modele K-Means sur des variables numeriqes, 
#si varibles categorielles, les tranformer avec une analyse factorielle ou un label encoding en utlisant cat.codes 


#On ne sait pas a priori quel est le nombre optimal de clusters pour que le population soit separer de maniere
#à ce que les groupes constituées soit à la fois le plus homogenes possible et differents les un des autres
#on utlise pour cela la courbe d'elbow en testant une decomposition de 1 à 10 groupes
from sklearn.cluster import KMeans ; import matplotlib.pyplot as plt

distortions = [] ; K = range(1,10)

for k in K:
    kmeanModel = KMeans(n_clusters=k)
    kmeanModel.fit(pays_clusters)
    distortions.append(kmeanModel.inertia_)

plt.figure(figsize=(16,8)) ; plt.plot(K, distortions, 'bx-') ; plt.xlabel('k') ; plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k') ; plt.show()

#la courbe d'elbow montre qu'il est optimal de constituer 3 groupes, le point après la cassure de la courbe

kmeanModel = KMeans(n_clusters=3) ; kmeanModel.fit(pays_clusters)

#On assigne chaque pays à son cluster
pays['cluster'] = kmeanModel.predict(pays_clusters)

#Caracterisation des clusters

pays.groupby('cluster').count()[['country']]

pays_clusters_means = pd.DataFrame(pays.groupby('cluster').mean())

#Cluster 0 : 219 pays : peu de visiteur, peu de produits achetés, faible CA
#Cluster 1 : 1 pays, beaucoup de visiteurs, beaucoup de produits, tres fort CA
#Cluster 2 : 2 pays, moyennement de visiteurs, moyennement de produits, moyen CA

pays.to_csv('C:/Users/marvin/Desktop/Python/pays_clusters.csv')
