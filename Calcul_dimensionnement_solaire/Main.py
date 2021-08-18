from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
from Input import input
import pandas as pd
from Panneau import Panneau



#Demande de saisie :
Title1 = "Saisie des informations"
Title2 = "Vous souhaitez calculer le potentiel théoriquement ou expérimentalement par un fichier météo ?"
Titlepan = "Paramètres du panneau"
demandeLong = "Quelle est la longitude ?"
demandeLat = "Quelle est la latitude ?"
demandebool = "Saisir 1 pour la méthode théorique ou 0 pour l'expérimental"
demandebeta = "Quel est l'angle d'inclinaison du panneau ?"
demandealb = "Quel est l'albédo du lieu d'implantation ?"
demandeeffi = "Quelle est l'efficacité du panneau ?"
#Variables :
Longitude = input(Title1, demandeLong)
Latitude = input(Title1, demandeLat)
methode = input(Title2, demandebool)
choixmet = methode.message()
if choixmet.get() == 1:
    Theo_ou_meteo = True
else :
    Theo_ou_meteo = False
beta_dem = input(Title1,demandebeta)
Albedo_dem = input(Title1,demandealb)
beta = beta_dem.message()
Albedo = Albedo_dem.message()
Lat = Latitude.message()
Long = Longitude.message()
#Main du programme :
"""
print(Long.get())
print(Lat.get())
print(Albedo.get())
print(beta.get())
print(choixmet.get())
"""
#Calcul théoriquement du potentiel solaire maximum de la localisation
if Theo_ou_meteo == True : 
    potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta.get(),Albedo.get())
    y_valuesIt = potentiel_test.Potentiel_solaire_theo()
    x_values = np.arange(1,8761)
    x_valuespd = pd.DataFrame(x_values)
    y_pd = pd.DataFrame(y_valuesIt)
    y_g = y_pd.replace(np.nan,0)
    x= np.array(x_valuespd)
    y_pottheo=np.array(y_g)
    GRAPH_pottheo = Basegraph(x,y_pottheo)
    GRAPH_pottheo.show()
    """
    #Sauvegarde des données dans des fichiers externes
    np.savetxt('Test_x.csv', (x), delimiter=' ')
    np.savetxt('Test_y.csv', (y), delimiter=' ')
    """
#Calcul expérimentalement du potentiel solaire maximum de la Potentiel_Localisation
else :  
    nom_met = 'Calcul_dimensionnement_solaire\Package\datamet\Europe\FR-Bordeaux-75100.tm2'
    potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta.get(),Albedo.get())
    y_valuesIt = potentiel_test.Potentiel_solaire_met(nom_met)
    x_values = np.arange(1,8761)
    x_valuespd = pd.DataFrame(x_values)
    y_pd = pd.DataFrame(y_valuesIt)
    y_g = y_pd.replace(np.nan,0)
    x= np.array(x_valuespd)
    y_potmet=np.array(y_g)
    GRAPH_potmet = Basegraph(x,y_potmet)
    GRAPH_potmet.show()
    #Calcul de l'énergie récupérable avec le panneau solaire 
    #Courbe d'énergie récupérée par le panneau : 
    effi_dem = input(Titlepan, demandeeffi)
    effi = effi_dem.message()
    panneau_potmet = Panneau(effi,0,0,0,0,0,0)
    panneau_potmet.energ_recup(y_potmet)

 
#Courbe I-V puis P-V du panneau : 
