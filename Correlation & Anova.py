############################################# A/B Testing Num Variable #############################################

import os; os.chdir('C:/Users/marvin/Desktop/Python')
import pandas as pd

############################################### Correlation ########################################################## 
pays = pd.read_csv('pays.csv', sep=",")

#DataFrame de la matrice de correlation de toute les variables numeriques
correl  = pays.corr(method='pearson') 
# (ici il y a une forte de correlation entre le nb de visiteurs et le CA 
# car le coeff de correlation est proche de 1 en valeur absolue )

# affichage de la matrice de correlation
import seaborn as sn ; sn.heatmap(correl, annot=True) 

################################################ Anova ############################################################### 
transactions = pd.read_csv('transactions.csv', sep=",")

device_avg = pd.DataFrame(transactions.groupby('deviceCategory').mean()) 
device_avg

#boxplot du Products par device
import seaborn as sn
bx_plt_device= sn.boxplot(x='deviceCategory', y='Products', data=transactions, color='#99c2a2')

#significativité
import statsmodels.api as sm ; from statsmodels.formula.api import ols

Device_Anova = ols('Products ~ C(deviceCategory)', data=transactions).fit()
anova_table = sm.stats.anova_lm(Device_Anova, typ=2)
anova_table

# les moyennes de produits achetés en fonction des device sont significatives car la  p-value < 0,05

#boxplot du CA par device
import seaborn as sn
bx_plt_device= sn.boxplot(x='deviceCategory', y='CA', data=transactions, color='#99c2a2')

#significativité
import statsmodels.api as sm ; from statsmodels.formula.api import ols

Device_Anova = ols('CA ~ C(deviceCategory)', data=transactions).fit()
anova_table = sm.stats.anova_lm(Device_Anova, typ=2)
anova_table

# les moyennes de CA en fonction des device ne sont pas significatives car la  p-value > 0,05

