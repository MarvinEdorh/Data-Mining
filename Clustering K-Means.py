#################################### ETL - BigQuery - Python - Data Studio #########################################

#ETL des données e-commerce Google Analytics stockées dans BigQuery vers Python afin d'effectuer une segmentation
#des achats en utilsant un modèle de clustering k-means afin de mieux comprendre les differnts profils. Les données
#des segments constitués seront ensuite envoyer vers Google Cloud Platform pour une visualisation sur Data Studio. 

import os; os.chdir('C:/Users/marvin/Desktop/Python')

################################################### SQL BigQuery #################################################

import numpy as np ; import pandas as pd ; from google.cloud import bigquery

#Création d'un compte de service GCP : https://cloud.google.com/docs/authentication/production
#Authentification du compte dans Python en ajouant lien du fichier JSON téléchargé en local après la creation de la clé

client = bigquery.Client.from_service_account_json(
json_credentials_path='data_pipeline-bbc9aec8eae9.json', 
project='data_pipeline')

#Requête SQL : Pour chaque achat on selectionne le device, l'os, la source de traffic et de campagne, le pays, 
#les produits et catégorie produits achetés, le nombre de visites que l'acheteur a effectué sur les produits 
#et catégorie produits achetés, et le CA.

query = """
WITH 
transactions AS (
SELECT DISTINCT hits.transaction.transactionId AS ID_Transaction, device.deviceCategory, device.operatingSystem,
trafficSource.campaign, trafficSource.medium, geoNetwork.country, fullvisitorid , hp.v2ProductName AS Product, 
hp.v2ProductCategory AS Product_Category, IFNULL(hits.transaction.transactionRevenue/1000000,0) AS CA, 
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
UNNEST(ga.hits) AS hits, UNNEST(hits.product) AS hp 
WHERE hits.transaction.transactionId IS NOT NULL
ORDER BY CA DESC,ID_Transaction),
visits_products AS (
SELECT fullvisitorid, hp.v2ProductName AS Product, SUM(totals.visits) AS Totals_Product_Visits
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
UNNEST(ga.hits) AS hits, UNNEST(hits.product) AS hp 
GROUP BY fullvisitorid, Product ),
visits_products_category AS (
SELECT fullvisitorid, hp.v2ProductCategory AS Product_Category, SUM(totals.visits) AS Totals_Product_Category_Visits
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga,
UNNEST(ga.hits) AS hits, UNNEST(hits.product) AS hp 
GROUP BY fullvisitorid, Product_Category )
SELECT ID_Transaction, deviceCategory, operatingSystem, campaign, medium, country,transactions.Product, 
transactions.Product_Category, Totals_Product_Visits, Totals_Product_Category_Visits, CA, 
FROM transactions LEFT JOIN visits_products 
ON transactions.fullvisitorid = visits_products.fullvisitorid 
AND transactions.Product = visits_products.Product
LEFT JOIN visits_products_category
ON transactions.fullvisitorid = visits_products_category.fullvisitorid 
AND transactions.Product_Category = visits_products_category.Product_Category
ORDER BY CA DESC """

query_results = client.query(query) ; query_results = query_results.result()

#Table des résultats

ID_Transaction = [] ; deviceCategory = [] ; operatingSystem = [] ; campaign = [] 
medium = [] ; country = [] ; Product = [] ; Product_Category = [] ; Totals_Product_Visits = []
Totals_Product_Category_Visits = [] ; CA = [] 

for row in query_results: 
    ID_Transaction.append(row[0]) 
    deviceCategory.append(row[1])
    operatingSystem.append(row[2])
    campaign.append(row[3])
    medium.append(row[4])
    country.append(row[5])
    Product.append(row[6])
    Product_Category.append(row[7])
    Totals_Product_Visits.append(row[8])
    Totals_Product_Category_Visits.append(row[9])
    CA.append(row[10])
    
BigQuery_table = {"ID_Transaction":ID_Transaction,
                  "deviceCategory":deviceCategory,
                  "operatingSystem":operatingSystem,
                  "campaign":campaign,
                  "medium":medium,
                  "country":country,
                  "Product":Product,
                  "Product_Category":Product_Category,
                  "Totals_Product_Visits":Totals_Product_Visits,
                  "Totals_Product_Category_Visits":Totals_Product_Category_Visits,
                  "CA":CA} 

BigQuery_table = pd.DataFrame(BigQuery_table) #BigQuery_table.to_csv('clustering.csv')

#On applique le modele K-Means sur des variables numeriqes, on transforme les variables categorielles en effectant une ACM
####################################################### ACM #######################################################

col = list(BigQuery_table.columns); del col[0]; del col[7]; del col[7]; del col[7]
data_acm = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:8]], columns = col )    
                       
import prince ; acm = prince.MCA(n_components=100) ; acm.fit(data_acm) #on crée le modèle

ev = pd.DataFrame(acm.eigenvalues_) ##on selectionne les axe dont la valeure propre est superieure à 1/Nb variables

#Coordonnées des individes
coord_acm = acm.transform(data_acm) ; coord_acm_ind = pd.DataFrame(coord_acm)

####################################################### ACP ########################################################
#si les varibles numérique sont corrélés on peut egalement les transformées en effectuant une ACP
col = list(BigQuery_table.columns)
del col[0] ; del col[0] ; del col[0] ; del col[0] ; del col[0] ; del col[0] ; del col[0] ; del col[0]
data_acp = pd.DataFrame(np.c_[BigQuery_table.iloc[:,8:11]], columns = col) 

data_acp.corr(method='pearson') #corrélations

n = data_acp.shape[0] ; p = data_acp.shape[1] #nombre d'observations ; nombre de variables

from sklearn.preprocessing import StandardScaler #transformation – centrage-réduction

data_acp_cr = StandardScaler().fit_transform(data_acp) ; data_acp_cr = pd.DataFrame(data_acp_cr)

#on crée le modèle
from sklearn.decomposition import PCA ; acp = PCA(svd_solver='full') 
coord_acp = acp.fit_transform(data_acp_cr)

#Valeur propres
eigval = (n-1)/n*acp.explained_variance_  ; prct_explained = acp.explained_variance_ratio_*100
eigval = pd.DataFrame({'eigval':eigval.tolist(),'prct_explained':prct_explained.tolist()}) ; eigval
#on selectionne les axe dont la valeure propre est superieure à 1

#coordonnées des individus
coord_acp_ind = pd.DataFrame(coord_acp)

#################################################### Clustering #######################################################

clustering = pd.DataFrame(np.c_[coord_acm_ind.iloc[:,0:96],BigQuery_table.iloc[:,8:11]])

#On ne sait pas a priori quel est le nombre optimal de clusters pour que le population soit separer de maniere 
#à ce que les segments constituées soient à la fois le plus homogenes possible et differents les un des autres.
#On utlise pour cela la courbe d'elbow en testant une décomposition de 1 à 10 groupes.

from sklearn.cluster import KMeans ; import matplotlib.pyplot as plt

distortions = [] ; K = range(1,10)

for k in K :
    kmeanModel = KMeans(init="random", n_clusters=k, max_iter=1500)
    kmeanModel.fit(clustering)
    distortions.append(kmeanModel.inertia_)

plt.figure(figsize=(14,8)) ; plt.plot(K, distortions, 'bx-') ; plt.xlabel('number of clusters')
plt.ylabel('Distortion') ; plt.title('The Elbow Method showing the optimal number of clusters') 

#la courbe d'elbow montre qu'il est optimal de constituer 3 ou 4 clusters, les points de cassure de la courbe

#On crée un modele à 3 cluster
kmeanModel = KMeans(init="random", n_clusters=3, max_iter=1500) ; kmeanModel.fit(clustering)
#On assigne chaque transaction à son cluster
BigQuery_table['cluster_3'] = kmeanModel.predict(clustering)

#On crée un modele à 4 cluster
kmeanModel = KMeans(init="random", n_clusters=4, max_iter=1500) ; kmeanModel.fit(clustering)
#On assigne chaque pays à son cluster
BigQuery_table['cluster_4'] = kmeanModel.predict(clustering)

#Caracterisation des clusters
BigQuery_table.groupby('cluster_3').count()[['ID_Transaction']] #effectif des clusters
BigQuery_table.groupby('cluster_4').count()[['ID_Transaction']]
clusters_means = pd.DataFrame(BigQuery_table.groupby('cluster_3').mean()) ; clusters_means #moyennes varibles numériques
clusters_means = pd.DataFrame(BigQuery_table.groupby('cluster_6').mean()) ; clusters_means

#Export des résultats vers Google Cloud Platform BigQuery Storage 
#afin de mieux les visualiser sur des outils BI de Data Visualisation comme Tableau ou Data Studio
from pandas.io import gbq
BigQuery_table.to_gbq(destination_table='test.clustering', project_id='mrvtestproject45', if_exists='replace')
#copier coller le code d'autorisation dans la console 

#dataviz : https://datastudio.google.com/reporting/70144ced-e19d-4010-9d93-721df23ea257/page/NJrXC

#En faisant tourner régulierement ce process on peut voir l'évolution des comportement e-commerce 
#pour une meilleure prise de décision
