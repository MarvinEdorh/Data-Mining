import os; os.chdir('C:/Users/marvin/python')

################################################### SQL BigQuery #################################################

import numpy as np ; import pandas as pd ; from google.cloud import bigquery

#https://cloud.google.com/docs/authentication/production

client = bigquery.Client.from_service_account_json(
json_credentials_path='data_pipeline-bbc9aec8eae9.json', 
project='data_pipeline')

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

fullvisitorid = [] ; time = [] ; device	= [] ; transaction = [] 

for row in query_results: 
    fullvisitorid.append(row[0]) 
    time.append(row[1])
    transaction.append(row[2])
    device.append(row[3])
    
BigQuery_table = {"fullvisitorid":fullvisitorid,
                  "time":time,
                  "transaction":transaction,
                  "device":device} 

BigQuery_table = pd.DataFrame(BigQuery_table)

############################################### Analyse de survie #################################################

col = list(BigQuery_table.columns); del col[0] 
survival_data = pd.DataFrame(np.c_[BigQuery_table.iloc[:,1:4]], columns = col,
                             index = BigQuery_table['fullvisitorid']) 

from lifelines import KaplanMeierFitter ; import matplotlib.pyplot as plt

kmf = KaplanMeierFitter()
kmf.fit(survival_data['time'],survival_data['transaction'])

event_table = kmf.event_table
kmf.predict(11)
survival_probability = kmf.survival_function_

kmf.plot()
plt.xlabel("time in days")
plt.ylabel("survival probability")
plt.title("KMF")

plt.figure(figsize=(15,10)) ; kmf.plot()
plt.xlabel('time in days') ; plt.ylabel('survival probability') ; plt.title("Survival Function")
plt.ylim([0.45,1]) 

########################################### test du log-rank ##########################################

# Dividing data into groups :
desktop = survival_data.query("device == 'desktop'")
mobile = survival_data.query("device == 'mobile'")
tablet = survival_data.query("device == 'tablet'")

# kmf_m for male data.
kmf_desktop = KaplanMeierFitter() 
kmf_mobile = KaplanMeierFitter() 
kmf_tablet = KaplanMeierFitter() 

kmf_desktop.fit(desktop['time'],desktop['transaction'])
kmf_mobile.fit(mobile['time'],mobile['transaction'])
kmf_tablet.fit(tablet['time'],tablet['transaction'])

# Plot the survival_function data :
plt.figure(figsize=(15,10)) ; kmf_desktop.plot(label='desktop')
kmf_mobile.plot(label='mobile') ; kmf_tablet.plot(label='tablet')
plt.xlabel("time in days") ; plt.ylabel("survival probability") 
plt.title("Survival Functions") ; plt.ylim([0.45,1])  

from lifelines.statistics import multivariate_logrank_test

log_rank_test = multivariate_logrank_test(survival_data['time'], survival_data['device'],
                                          survival_data['transaction'])

log_rank_test.summary

################################## Modele de Cox ###############################################

# Cox regression :
survival_data["device"] = survival_data["device"].astype('category')
survival_data["device"] = survival_data["device"].cat.codes

from lifelines import CoxPHFitter

cph = CoxPHFitter()
cph.fit(survival_data,"time","transaction")
cph.summary # -0.946602,  8.758189e-221 

# Plot the survival function :
d_data = survival_data.iloc[0:5,:]
cph.predict_survival_function(d_data).plot()
