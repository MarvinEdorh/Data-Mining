# Correlation & Anova
A/B Testing process on numeric variables

l'hypothèse nulle qui envisage une egalité entre les groupes, c'est à dire qu'il y aurait ici en propotion autant de conversions effectuées parmis les personnes qui on vu la page originale que parmis ceux qui on vu la page A et que ceux qui on vu la page B. Si cette hypothèse est vraie Le test calcule la probabilité sous l'hypothèse nulle 

# Chi-2 & Logistic Regression 

A/B Test : https://github.com/MarvinEdorh/Data-Mining/blob/main/Chi-2%20%26%20Logistic%20Regression.py

Afin de savoir si la mis à jour d'une page a un effet significatif sur les conversions, on peut utilser le test statistique du chi-2 ainsi qu'une regression logistique dans un process d'A/B testing. Le test du chi-2 est un test statique qui permert de savoir si 2 variables catégorielles sont liées entre elles, ici la premiere variable sera le type de page vue (orginale, A ou B) et la seconde, le fait d'effectuer une conversion (oui ou non). Comme tout test statistique le test du chi-2 pose H0 evisageant une egalité entre les groupes, c'est à dire qu'il y aurait ici en propotion autant de conversions effectuées parmis les personnes qui on vu la page originale que parmis ceux qui on vu la page A et ceux qui on vu la page B, et l'hypothèse alternative H1 evisageant une difference entre les groupes. Si la p-valeure associée au test est inférieure à 5% alors on rejette H0 et on se tourne vers H1 pour en conclure qu'il y a bien un lien significatif entre le type de page vue et le fait d'effectuer une conversion. 

Si à la suite du test du chi-2 on conclut à un lien significatif entre les 2 varibles et que les variables dependantes est dicotomique alors il est pertinent d'effectuer un modèle de regression logistique binomiale afin de mesurer l'impact des variables explicatives sur celle-ci, ici on modélise le fait d'effectuer une conversion (variable dependante) en fonction du type de page vue (variable explicative). Le modèle de regression logistique calcule la probabilité qu' un individu à de prendre la premiere modailité pour la variable dependante sachant ses modalités pour les variables explicatives par rapport au profil de réference. Généralement on prend comme profil de reference les modalités des variables exlicatives qui on le plus fort effectif mais ici dans le cadre d'A/B testing le profil de reference sera le fait d'avoir vu la page orginale.


# K-Means Clustering
Clusters dataviz : https://datastudio.google.com/s/hRcohz4T4DI

![Courbe d'elbow](https://user-images.githubusercontent.com/83826055/129334001-457b71dd-c30f-43de-897e-d2dab6f01a60.png)

# Kaplan Meier Survival

![KMF](https://user-images.githubusercontent.com/83826055/129444429-fcef0f33-b30f-4c5c-9b22-af75347ed59e.png)

![KMF_Device](https://user-images.githubusercontent.com/83826055/129444431-0271e2aa-c5cc-4988-9497-2b6b61337bb1.png)

![KMF_2](https://user-images.githubusercontent.com/83826055/129450587-cf45114a-ea53-49d4-b7ee-a1bb04a8b7f3.png)

![KMF_Device_2](https://user-images.githubusercontent.com/83826055/129450589-e52c90a2-8391-4d86-9827-43318689c2ae.png)
