# Correlation & Anova
Demo : https://github.com/MarvinEdorh/Data-Mining/blob/main/Correlation%20%26%20Anova.py

Lorsque l'on effectue une analyse ux analytics et que l'on souhaite savoir si des variables ont lien l'une les une avec les autres, plusieurs tests statistique peuveut permettre d'analyser cette question. Le test de correlation est un test statistique qui permert de savoir de quel est le degré relation linéaire entre 2 variables numériques. Il calcule un coefficient de correlation pouvant aller de -1 à 1. Plus ce coefficient est proche de 1 en valeure absolue plus il a une forte relation de proportionnalité (positif ou négatif) entre ces 2 variables et donc que ces variables sont liées entre elles. Plus ce coefficient est proche de 0 moins ces variables sont liées entre elles.

Également dans le cadre d'un A/B testing on peut être amener à comparer le nombre moyens de conversions sur plusieurs effectifs mais il ne serait pas pertinent de comparer des moyennes entre un effectif de 10 individus et un autre de 10 000. Le test statisque anova nous permet justement savoir si les effectifs sont suffisament importants pour conclure de la significativité des résultats. En statistique on pose l'hypothèse nulle (H0) estimant d'une egalité entre les groupes. Si cette hypothèse est vraie alors la différence de moyenne est du à un echantillon trop faible puisque chaque effectif vienne de la même distribution. En augmentant la taille de l'echantillon les moyenne devrait tendre vers une même valeure. En revanche si l'hypothese nulle est fausse alors même en augmentant la taille de l´echantillon on ne pourrait pas faire disparaitre les diffences entre les moyennes puisque les effectifs viendraient de 2 distributions distinctes. Le test calcule la probabilité (p-valeure) d'observer ces resultats sous l'hypothèse nulle. si la p-valeure est tres petite (souvent inférieure au seuil de 0,05) alors on rejette H0. On se tourne alors vers l'hypothèse alternative (H1), que nos effectifs proviennent de 2 distributions significativement différentes et on conclut alors à une différence significative entre les moyennes. En revanche si la p-valeure est supérieure à 5% alors on ne peut pas rejeter H0.

# Chi-2 & Logistic Regression 
Demo : https://github.com/MarvinEdorh/Data-Mining/blob/main/Chi-2%20%26%20Logistic%20Regression.py

En ux analytics, lorsqu'on souhaite par exemple savoir si la mis à jour d'une page a un effet significatif sur les conversions, on peut utilser le test statistique du chi-2 dans un process d'A/B testing afin d'analyser la significativité des résultats. Le test du chi-2 est un test statique qui comme le test de correlation permert de savoir si des variables sont liées entre elles mais cette fois 2 variables catégorielles. Ici la premiere variable sera le type de page vue (orginale, A ou B) et la seconde, le fait d'effectuer une conversion (oui ou non). Comme tout test statistique, le test du chi-2 pose H0 estimant d'une egalité entre les groupes, c'est à dire ici qu'il y aurait en propotion autant de conversions effectuées parmis les personnes qui ont vu la page originale que parmis celles qui ont vu la page A et celles qui ont vu la page B, et l'hypothèse alternative H1 estimant d'une difference entre les groupes. Si la p-valeure calculé par le test est inférieure à 5% alors on rejette H0 et on se tourne vers H1 pour en conclure qu'il y a bien un lien significatif entre le type de page vue et le fait d'effectuer une conversion. 

Si à la suite du test du chi-2 on conclut à un lien significatif entre les 2 varibles et que les variables dépendantes est   dichotomique (2 modalités) alors il est pertinent d'effectuer un modèle de regression logistique binomiale afin de mesurer l'impact de la variable explicative sur celle-ci. Ici on modélise le fait d'effectuer une conversion (variable dépendante) en fonction du type de page vue (variable explicative). Le modèle de regression logistique calcule la probabilité qu'un individu à de prendre la premiere modailité pour la variable dépendante sachant ses modalités pour les variables explicatives par rapport au profil de réference. Généralement on prend comme profil de réference les modalités des variables exlicatives qui ont le plus fort effectif mais ici dans le cadre d'un A/B testing le profil de réference sera le fait d'avoir vu la page orginale. On poura ainsi mesurer de combien fait évoluer les chances d'effectuer une transaction le fait d'avoir vu la page A ou B par rapport au fait d'avoir vu la page originale.

Également si on veut maintenant modéliser une variable numérique en fonction de variables catégorielles on peut utiliser le modele lineaire généralisé qui comme la regression logistique calcule l'impact des autres modalités des variables explicatives sur la variable dépendante par rapport au profil de reférence. On peut par exemple pour un site e-commerce analyser le montant des transactions en fonction des versions du site et voir de combien fait evoluer ce motant le fait d'avoir vu la page A ou B par raport au fait d'avoir vu la page originale.


# K-Means Clustering
En markerketing digital il très important de bien connaitre ses consomateurs et de bien les segmenter afin de pouvoir diriger des actions ciblées. Le modele de machine learning de clustering k-means permert justement de segment une population de manière ce que les groupes constitués soient à la fois en intra le plus homogènes possible et et en extra differents les un des autres selon un algorithme ittératif.

#On ne sait pas a priori quel est le nombre optimal de clusters pour que le population soit separer de maniere 
#à ce que les segments constituées soient à la fois le plus homogenes possible et differents les un des autres.
#On utlise pour cela la courbe d'elbow en testant une décomposition de 1 à 10 groupes.

Clusters dataviz : https://datastudio.google.com/s/hRcohz4T4DI

![Courbe d'elbow](https://user-images.githubusercontent.com/83826055/129334001-457b71dd-c30f-43de-897e-d2dab6f01a60.png)

# Kaplan Meier Survival

![KMF](https://user-images.githubusercontent.com/83826055/129444429-fcef0f33-b30f-4c5c-9b22-af75347ed59e.png)

![KMF_Device](https://user-images.githubusercontent.com/83826055/129444431-0271e2aa-c5cc-4988-9497-2b6b61337bb1.png)

![KMF_2](https://user-images.githubusercontent.com/83826055/129450587-cf45114a-ea53-49d4-b7ee-a1bb04a8b7f3.png)

![KMF_Device_2](https://user-images.githubusercontent.com/83826055/129450589-e52c90a2-8391-4d86-9827-43318689c2ae.png)
