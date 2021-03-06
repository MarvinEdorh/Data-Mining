import os; os.chdir('C:/Users/marvin/Desktop/SQL BigQuery')

################################################### SQL BigQuery ########################################################

import numpy as np ; import pandas as pd ; from google.cloud import bigquery

client = bigquery.Client.from_service_account_json(
json_credentials_path='data_pipeline-bbc9aec8eae9.json', 
project='data_pipeline')

#Pour chaque visiteur on calcule la durée entre sa premiere visite et son premier achat 
#s'il en a effectué et la durée entre sa premiere et sa derniere visite sinon
#On indique également le device sur lequel il a effectué la transaction ou sa dernière visite sinon. 
#On code 1 s'il a effectué une transaction 0 sinon. 

query = """
WITH 

visit AS (
SELECT fullvisitorid, MIN(date) AS date_first_visit, MAX(date) AS date_last_visit 
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` GROUP BY fullvisitorid),

device_visit AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`),

transactions AS (
SELECT fullvisitorid, MIN(date) AS date_transactions, 1 AS transaction
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
UNNEST(ga.hits) AS hits WHERE  hits.transaction.transactionId IS NOT NULL GROUP BY fullvisitorid),

device_transactions AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, 
UNNEST(ga.hits) AS hits WHERE hits.transaction.transactionId IS NOT NULL),

visits_transactions AS (
SELECT visit.fullvisitorid, date_first_visit, date_transactions, date_last_visit , 
       device_visit.deviceCategory AS device_last_visit, 
       device_transactions.deviceCategory AS device_transaction, 
       IFNULL(transactions.transaction,0) AS transaction
FROM visit LEFT JOIN transactions ON visit.fullvisitorid = transactions.fullvisitorid
LEFT JOIN device_visit ON visit.fullvisitorid = device_visit.fullvisitorid 
AND visit.date_last_visit = device_visit.date

LEFT JOIN device_transactions ON visit.fullvisitorid = device_transactions.fullvisitorid 
AND transactions.date_transactions = device_transactions.date ),

mortality_table AS (
SELECT fullvisitorid, date_first_visit, 
       CASE WHEN date_transactions IS NULL THEN date_last_visit ELSE date_transactions  END AS date_event, 
       CASE WHEN device_transaction IS NULL THEN device_last_visit ELSE device_transaction END AS device, transaction
FROM visits_transactions )

SELECT CONCAT("ID",fullvisitorid) AS fullvisitorid, 
       DATE_DIFF(PARSE_DATE('%Y%m%d',date_event),PARSE_DATE('%Y%m%d', date_first_visit),DAY) AS time, 
       transaction, device FROM mortality_table"""

query_results = client.query(query) ; query_results = query_results.result()

#Résutats de la reqête
fullvisitorid = [] ; time = [] ; device	= [] ; transaction = [] 

for row in query_results: 
    fullvisitorid.append(row[0]) 
    time.append(row[1])
    transaction.append(row[2])
    device.append(row[3])
    
BigQuery_table = {"fullvisitorid":fullvisitorid, "time":time, "transaction":transaction, "device":device} 
BigQuery_table = pd.DataFrame(BigQuery_table)

########################################### Analyse de survie de Kaplan Meier ###########################################

#On importe le jeu de donnée de la table BigQuery
col = list(BigQuery_table.columns); del col[0] 
survival_data = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:4]], columns = col, index = BigQuery_table['fullvisitorid']) 

#On crée le modèle
from lifelines import KaplanMeierFitter ; import matplotlib.pyplot as plt
kmf = KaplanMeierFitter() ; kmf.fit(survival_data['time'],survival_data['transaction'])

#Résultats
event_table = kmf.event_table #table des évenements
kmf.predict(11) #prediction d'etre en vie à 11 jours
survival_probability = kmf.survival_function_ #table des probabilités de survie

#Courbe de la fonction de survie de Kaplan Meier
kmf.plot(); plt.xlabel("time in days"); plt.ylabel("survival probability"); plt.title("Kaplan Meier Survival Function")

#Courbe plus lisible
plt.figure(figsize=(15,10)) ; kmf.plot() ; plt.xlabel('time in days') ; plt.ylabel('survival probability') 
plt.title("Kaplan Meier Survival Function") ; plt.ylim([0.45,1]) 

########################################## segmentaion & test du log-rank ################################################

#On divise le jeu de données en fonction des segment
desktop = survival_data.query("device == 'desktop'")
mobile = survival_data.query("device == 'mobile'")
tablet = survival_data.query("device == 'tablet'")

#On crée les modèle
kmf_desktop = KaplanMeierFitter()  ; kmf_mobile = KaplanMeierFitter()  ; kmf_tablet = KaplanMeierFitter() 
kmf_desktop.fit(desktop['time'],desktop['transaction'])
kmf_mobile.fit(mobile['time'],mobile['transaction'])
kmf_tablet.fit(tablet['time'],tablet['transaction'])

#Courbes de survie en fonction des segments
plt.figure(figsize=(15,10)) ; plt.ylim([0.45,1])
kmf_desktop.plot(label='desktop') ; kmf_mobile.plot(label='mobile') ; kmf_tablet.plot(label='tablet')
plt.xlabel("time in days") ; plt.ylabel("survival probability") ; plt.title("Kaplan Meier Survival Functions") 


#test du log-rank
from lifelines.statistics import multivariate_logrank_test
log_rank_test = multivariate_logrank_test(survival_data['time'], survival_data['device'], survival_data['transaction'])

log_rank_test.summary
#les différence de survie sont significative car la p-valeur est inferieure à 5%

##################################################### Modele de Cox ######################################################
#On calucule l'impact des différentes modalités sur le risque absolu de décès (effectuer une transaction)
from lifelines import CoxPHFitter

#On recode en 2 la modalité que l'on souhaite analyser et 1 les autres
survival_data = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:4]], columns = col, index = BigQuery_table['fullvisitorid']) 
survival_data["device"] = survival_data.device.replace({"desktop":2,"mobile":1, "tablet":1})
cph = CoxPHFitter() ; cph.fit(survival_data,"time","transaction") ; cox_reg = cph.summary ; cox_reg
#le rélultat est significatif car la p-valeure est inferieure à 5%
#La valeure exp(coef) mesure l'impact de la modalité sur le risque absolue de décès
#Si exp(coef) = 1 il n'y a pas d'effet sur le risque absolue de decéder
#Si exp(coef) < 1 avoir cette modalité réduit le risque de décéder
#exp(coef) > 1 augmente le risque de le risque de décéder
#Ici être sur la version sur desktop multiplie le risque de décéder par 3.128524 6 soit une augmentation de 213%

survival_data = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:4]], columns = col, index = BigQuery_table['fullvisitorid']) 
survival_data["device"] = survival_data.device.replace({"desktop":1,"mobile":2, "tablet":1})
cph = CoxPHFitter() ; cph.fit(survival_data,"time","transaction") ; cox_reg = cph.summary ; cox_reg
#le rélultat est significatif car la p-valeure est inferieure à 5%
#Ici être sur la version sur mobile multiplie le risque de décéder par 0.316285 6 soit une réduction de 68%   

survival_data = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:4]], columns = col, index = BigQuery_table['fullvisitorid']) 
survival_data["device"] = survival_data.device.replace({"desktop":1,"mobile":1, "tablet":2})
cph = CoxPHFitter() ; cph.fit(survival_data,"time","transaction") ; cox_reg = cph.summary ; cox_reg
#le rélultat est significatif car la p-valeure est inferieure à 5%
##Ici être sur la version sur tablet multiplie le risque de décéder par 0.469092 6 soit une réduction de 53%   

#Prédiction de la survie d'un individus
d_data = survival_data.iloc[0:5,:]
cph.predict_survival_function(d_data).plot()

###################################################### Retention #########################################################

#On calcule maintenant la durée entre sa premiere visite et son dernier achat

query = """
WITH 

visit AS (
SELECT fullvisitorid, MIN(date) AS date_first_visit, MAX(date) AS date_last_visit 
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` GROUP BY fullvisitorid),

device_visit AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`),

transactions AS (
SELECT fullvisitorid, MAX(date) AS date_transactions, 1 AS transaction
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, UNNEST(ga.hits) AS hits
WHERE  hits.transaction.transactionId IS NOT NULL GROUP BY fullvisitorid),

device_transactions AS (
SELECT DISTINCT fullvisitorid, date, device.deviceCategory
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS ga, UNNEST(ga.hits) AS hits
WHERE hits.transaction.transactionId IS NOT NULL),

visits_transactions AS (
SELECT visit.fullvisitorid, date_first_visit, date_transactions, date_last_visit , 
       device_visit.deviceCategory AS device_last_visit, device_transactions.deviceCategory AS device_transaction, 
       IFNULL(transactions.transaction,0) AS transaction
FROM visit LEFT JOIN transactions ON visit.fullvisitorid = transactions.fullvisitorid
LEFT JOIN device_visit ON visit.fullvisitorid = device_visit.fullvisitorid 
AND visit.date_last_visit = device_visit.date

LEFT JOIN device_transactions ON visit.fullvisitorid = device_transactions.fullvisitorid 
AND transactions.date_transactions = device_transactions.date ),

mortality_table AS (
SELECT fullvisitorid, date_first_visit, 
       CASE WHEN date_transactions IS NULL THEN date_last_visit ELSE date_transactions  END AS date_event, 
       CASE WHEN device_transaction IS NULL THEN device_last_visit ELSE device_transaction END AS device, transaction
FROM visits_transactions )

SELECT fullvisitorid, DATE_DIFF(PARSE_DATE('%Y%m%d',date_event), PARSE_DATE('%Y%m%d', date_first_visit),DAY) AS time, 
       transaction, device FROM mortality_table"""

query_results = client.query(query) ; query_results = query_results.result()

#Résutats de la reqête
fullvisitorid = [] ; time = [] ; device	= [] ; transaction = [] 
for row in query_results: 
    fullvisitorid.append(row[0]) 
    time.append(row[1])
    transaction.append(row[2])
    device.append(row[3])
    
BigQuery_table_2 = {"fullvisitorid":fullvisitorid, "time":time, "transaction":transaction, "device":device} 

BigQuery_table_2 = pd.DataFrame(BigQuery_table_2)

survival_data_2 = pd.DataFrame(np.c_[BigQuery_table_2.iloc[:,1:4]], 
                               columns = col, index = BigQuery_table_2['fullvisitorid']) 

#On crée le modèle
kmf_2 = KaplanMeierFitter() ; kmf_2.fit(survival_data_2['time'],survival_data_2['transaction'])

#Courbe de survie
plt.figure(figsize=(15,10)) ; plt.ylim([0,35,1]) ; kmf.plot(label='conversion') ; kmf_2.plot(label='retention') 
plt.xlabel('time in days') ; plt.ylabel('survival probability') ; plt.title("Kaplan Meier Survival Functionsn") 

#On divise le jeu de données en fonction des segment
desktop_2 = survival_data_2.query("device == 'desktop'")
mobile_2 = survival_data_2.query("device == 'mobile'")
tablet_2 = survival_data_2.query("device == 'tablet'")

#On crée le modèle
kmf_desktop_2 = KaplanMeierFitter() ; kmf_mobile_2 = KaplanMeierFitter() ; kmf_tablet_2 = KaplanMeierFitter() 
kmf_desktop_2.fit(desktop_2['time'],desktop_2['transaction'])
kmf_mobile_2.fit(mobile_2['time'],mobile_2['transaction'])
kmf_tablet_2.fit(tablet_2['time'],tablet_2['transaction'])

#Courbes de survie en fonction des segments
plt.figure(figsize=(15,10)) ; kmf_desktop_2.plot(label='desktop') ; kmf_mobile_2.plot(label='mobile') 
kmf_tablet_2.plot(label='tablet') ; plt.xlabel("time in days") ; plt.ylabel("survival probability") 
plt.title("Kaplan Meier Survival Functions") ; plt.ylim([0.35,1])  
