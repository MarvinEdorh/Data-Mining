############################################# A/B Testing  ##########################################################

import os; os.chdir('C:/Users/marvin/Python')
import pandas as pd

################################################ Khi-2 ############################################################### 

ab_test = pd.read_csv('ab_test.csv', sep=",")

#tri croisé
cont = pd.crosstab(ab_test['Views'],ab_test['Conversions'])
cont

from scipy.stats import chi2_contingency

khi_2 = chi2_contingency(cont)

pd.DataFrame({'Stats':['test statistic','p-value','df'], 'Value' : khi_2[:][0:3]})

# le test n'est pas significatif car la p-valeur est superieure à 0,05
# On ne peut donc pas dire que le fait d'effectuer une conversion est lié au type de pages vues

#################################### Régression Logistique Binomial #################################################
#On modélise le fait d'effectuer une conversion en fonction du type de page vue 
#par rapport au profil de réference (ici le profil de reference est d'avoir vu la page orginal), 
#mais généralement on prend comme profil de reference des vars exlicatives les modalités qui on le plus fort effectif
#Python prend comme profil de reference la premiere modalité dans l'ordre alphabétique
#en regression logistique l'evenement à modeliser est codé 1 et le non evenement 0

# Méthode 1
import numpy as np
ab_test['Conversions'] = np.where(ab_test['Conversions'] == "oui", 1, ab_test['Conversions'] )
ab_test['Conversions'] = np.where(ab_test['Conversions'] == "non", 0, ab_test['Conversions'] )

# Méthode 2 cat.codes transforme var cat en num Mod1 = 0, Mod2 = 1 ...dans l'odre alphb des Mod
ab_test["Conversions"] = ab_test["Conversions"].astype('category')
ab_test["Conversions"] = ab_test["Conversions"].cat.codes

import statsmodels.api as sm ; import statsmodels.formula.api as smf

model = smf.glm(formula = 'Conversions ~ Views', data=ab_test, family=sm.families.Binomial())

result = model.fit()

result.summary()

#ni le fait d'avoir vu la page A ni le fait d'avoir vu la page B a une incidence significative 
#sur le fait d'effectuer une coversion car leurs p-valeur sont superieures à 0,005 
#et 0 appartient à l'interval de confiance

#odds ratio
conf = result.conf_int()
conf['Odds Ratio'] = result.params
conf.columns = ['5%', '95%', 'Odds Ratio']
np.exp(conf)

#le fait de voir la page A multiplie par 0,9 par 
#rapport au fait d'avoir vu la page original les chance de conversions (quasi constant)

#le fait de voir la page A multiplie par 0,9 les chance de conversions (quasi constant)

################################################ GLM ##################################################

transactions = pd.read_csv('transactions.csv', sep=",")

device = pd.DataFrame(transactions.groupby('deviceCategory').count()[['ID_Transaction']]) 
device

continent = pd.DataFrame(transactions.groupby('continent').count()[['ID_Transaction']]) 
continent

#le profil de référence est Americas & Desktop

transactions['continent'] = transactions.continent.replace({"Americas":"1.Americas","Asia":"2.Asia",
                                                            "Europe":"3.Europe","Oceania":"4.Oceania",
                                                            "Africa":"5.Africa","(not set)":"6.(not set)"})

import numpy as np ; import statsmodels.formula.api as smf

model_glm = smf.poisson('CA ~ deviceCategory + continent', data = transactions)

result = model_glm.fit()

result.summary()

#odds ratio
conf = result.conf_int()
conf['Odds Ratio'] = result.params
conf.columns = ['5%', '95%', 'Odds Ratio']
np.exp(conf)

#chaque modalité a une incidence significative sur le CA par rapport au profil de reference

