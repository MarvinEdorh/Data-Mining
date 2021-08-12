#################################### ETL - BigQuery - Python - Data Studio #########################################

#Analyses des données e-commerce Google Analytics importées dans BigQuery avec Python afin d'effectuer segmentation
#des acheteurs

import os; os.chdir('C:/Users/marvi/Desktop/MsMDA/AutoFormation/SQL BigQuery')

################################################### SQL BigQuery #################################################

import numpy as np ; import pandas as pd ; from google.cloud import bigquery

#https://cloud.google.com/docs/authentication/production

client = bigquery.Client.from_service_account_json(
json_credentials_path='mrvtestproject45-bbc9aec8eae9.json', 
project='mrvtestproject45')

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

ID_Transaction = [] ; deviceCategory = [] ; operatingSystem = [] ; campaign = [] ; 
medium = [] ; country = [] ; Product = [] ; Product_Category = [] ; Totals_Product_Visits = [] ;
Totals_Product_Category_Visits = [] ; CA = [] ;

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
                  "CA":CA,} 

BigQuery_table = pd.DataFrame(BigQuery_table)

#BigQuery_table.to_csv('clustering.csv')

################################################### Clustering #################################################

#On applique le modele K-Means sur des variables numeriqes, 
#on recode les varibles categorielles par un label encoding 

col = list(BigQuery_table.columns); del col[0]
clustering  = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:11]], columns = col ) 
clustering["deviceCategory"] = clustering["deviceCategory"].astype('category')
clustering["deviceCategory"] = clustering["deviceCategory"].cat.codes
clustering["operatingSystem"] = clustering["operatingSystem"].astype('category')
clustering["operatingSystem"] = clustering["operatingSystem"].cat.codes
clustering["campaign"] = clustering["campaign"].astype('category')
clustering["campaign"] = clustering["campaign"].cat.codes
clustering["medium"] = clustering["medium"].astype('category')
clustering["medium"] = clustering["medium"].cat.codes
clustering["country"] = clustering["country"].astype('category')
clustering["country"] = clustering["country"].cat.codes
clustering["Product"] = clustering["Product"].astype('category')
clustering["Product"] = clustering["Product"].cat.codes
clustering["Product_Category"] = clustering["Product_Category"].astype('category')
clustering["Product_Category"] = clustering["Product_Category"].cat.codes

#On ne sait pas a priori quel est le nombre optimal de clusters pour que le population soit separer 
#de maniere à ce que les groupes constituées soient à la fois le plus homogenes possible et differents les un des autres.
#on utlise pour cela la courbe d'elbow en testant une decomposition de 1 à 10 groupes

from sklearn.cluster import KMeans ; import matplotlib.pyplot as plt

distortions = [] ; K = range(1,10)

for k in K :
    kmeanModel = KMeans(n_clusters=k)
    kmeanModel.fit(clustering)
    distortions.append(kmeanModel.inertia_)

plt.figure(figsize=(16,8)) ; plt.plot(K, distortions, 'bx-') ; plt.xlabel('k') ; plt.ylabel('Distortion')
plt.title('The Elbow Method showing the optimal k') ; plt.show()

#la courbe d'elbow montre qu'il est optimal de constituer 4 groupes, le point de cassure de la courbe

kmeanModel = KMeans(n_clusters= 3) ; kmeanModel.fit(clustering)

#On assigne chaque pays à son cluster
BigQuery_table['cluster'] = kmeanModel.predict(clustering)

#Caracterisation des clusters

BigQuery_table.groupby('cluster').count()[['ID_Transaction']]

clusters_means = pd.DataFrame(BigQuery_table.groupby('cluster').mean()) ; clusters_means

#Après analyses, export des résultats vers Google Cloud Platform BigQuery Storage 
#afin de mieux les visualiser sur des outils BI de Data Visualisation comme Tableau ou Data Studio
from pandas.io import gbq
BigQuery_table.to_gbq(destination_table='test.clustering', project_id='data_pipeline', if_exists='replace')
#copier coller le code d'autorisation dans la console

#Dataviz : https://datastudio.google.com/reporting/fb6b9a87-7aff-41b6-89ce-b12a260b9658/page/p_2t5s4p71lc
