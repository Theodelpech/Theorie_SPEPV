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
Titlepot = "Souhaitez vous calculer le potentiel solaire d'une localisation sans et avec un panneau PV ?"
demandeLong = "Quelle est la longitude ? (degré)"
demandeLat = "Quelle est la latitude ? (degré)"
demandebool = "Saisir 1 pour la méthode théorique ou 0 pour l'expérimental"
demandebeta = "Quel est l'angle d'inclinaison du panneau ? (degré)"
demandealb = "Quel est l'albédo du lieu d'implantation ?"
demandepot =  "Saisir 1 pour calculer ce potentiel ou 0 pour passer directement à la suite des calculs"
#Variables :
pot = input(Titlepot,demandepot)
choixpot = pot.message()
if choixpot.get() == 1 :
    methode = input(Title2, demandebool)
    choixmet = methode.message()
    if choixmet.get() == 1:
        Theo_ou_meteo = True
    else :
        Theo_ou_meteo = False
    paramet = input(Title1,'Coucou')
    beta, Albedo, Lat, Long = paramet.mespot(demandebeta,demandealb,demandeLat,demandeLong)

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
        x_values = np.arange(0,8761)
        x_valuespd = pd.DataFrame(x_values)
        y_pd = pd.DataFrame(y_valuesIt)
        y_g = y_pd.replace(np.nan,0)
        x= np.array(x_valuespd)
        y_pottheo=np.array(y_g)
        GRAPH_pottheo = Basegraph(x,y_pottheo)
        GRAPH_pottheo.show()
        #Calcul de l'énergie récupérable avec le panneau solaire 
        #Courbe d'énergie récupérée par le panneau : 
        parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire = parampan.messagemult('Efficacite du panneau (en décimal après le 0) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =')
        panneau_pottheo = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        panneau_pottheo.energ_recup(y_pottheo)
        #Courbe I-V puis P-V du panneau : 
        panneau_pottheo.courbeIV()
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
        parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire = parampan.messagemult('Efficacite du panneau (en décimal après le 0) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =')
        panneau_potmet = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        panneau_potmet.energ_recup(y_potmet)
        #Courbe I-V puis P-V du panneau : 
        panneau_potmet.courbeIV()
else :
    parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
    effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire = parampan.messagemult('Efficacite du panneau (en décimal après le 0) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =')
    panneau_test = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(), Aire.get())
    # 4.5,21.4,3.95,16.5,-0.085,0.00026,36,0.633
    #Courbe I-V puis P-V du panneau : 
    panneau_test.courbeIV()

 

