from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
from Input import input
import pandas as pd
from Panneau import Panneau
from MotPompeDC import MotPompeDC
import matplotlib.pyplot as plt
import sys as sys
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
        y_pot=np.array(y_g)
        GRAPH_pottheo = Basegraph(x,y_pot,'Potentiel Solaire (W/m2)', "Heures de l'année","Potentiel solaire sur une année de la localisation")
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
        y_pot=np.array(y_g)
        GRAPH_potmet = Basegraph(x,y_pot,'Potentiel Solaire (W/m2)', "Heures de l'année","Potentiel solaire sur une année de la localisation" )
        GRAPH_potmet.show()
    #Calcul de l'énergie récupérable avec le panneau solaire 
    #Courbe d'énergie récupérée par le panneau : 
    parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
    effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire = parampan.messagemult('Efficacite du panneau (en décimal après le 0) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =')
    panneau_pot = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
    panneau_pot.energ_recup(y_pot)
    #Courbe I-V puis P-V du panneau : 
    panneau_pot.courbeIV()
    Motpompe = MotPompeDC('Calcul_dimensionnement_solaire\Package\pump_files\PS150_BOOST_60.txt')
    tdh=40
    xpomp, ypomp = Motpompe.functIforVH_Arab()
    Vrange_load = np.arange(*ypomp['V'](tdh))
    ivgraphpomp = Basegraph(Vrange_load,xpomp(Vrange_load, tdh, error_raising=False),"Courant I en Ampère", "Tension V en Volt", "Courbe I-V de l'ensemble moteur pompe")
    ivgraphpomp.show()
else :
    parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
    effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =')
    panneau_test = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(), Aire.get())
    # 4.5,21.4,3.95,16.5,-0.085,0.00026,36,0.633
    #Courbe I-V puis P-V du panneau : 
    Ipan, Vpan, npan = panneau_test.courbeIV()
    #Courbe I_V moteur-pompe DC :
    Motpompe = MotPompeDC('Calcul_dimensionnement_solaire\Package\pump_files\PS150_BOOST_60.txt')
    tdh=40
    xpomp, ypomp = Motpompe.functIforVH_Arab()
    Vrange_load = np.arange(*ypomp['V'](tdh))
    ivgraphpomp = Basegraph(Vrange_load,xpomp(Vrange_load, tdh, error_raising=False),"Courant I en Ampère", "Tension V en Volt", "Courbe I-V de l'ensemble moteur pompe")
    ivgraphpomp.show()
    #Point de fonctionnement :
    npan = max(len(Vpan),len(Vrange_load))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x1=Vpan
    y1=Ipan
    x2=Vrange_load
    y2=xpomp(Vrange_load, tdh, error_raising=False)
    ax.plot(x1, y1, color='lightblue',linewidth=3, marker='s')
    ax.plot(x2, y2, color='darkgreen', marker='^')
    y_lists = y1[:]
    y_lists.extend(y2)
    y_dist = max(y_lists)/200.0
    x_lists = x1[:]
    x_lists.extend(x2)  
    x_dist = max(x_lists)/900.0
    division = 1000
    x_begin = min(x1[0], x2[0])     # 3
    x_end = max(x1[-1], x2[-1])     # 8
    points1 = [t for t in zip(x1, y1) if x_begin<=t[0]<=x_end]  # [(3, 50), (4, 120), (5, 55), (6, 240), (7, 50), (8, 25)]
    points2 = [t for t in zip(x2, y2) if x_begin<=t[0]<=x_end]  # [(3, 25), (4, 35), (5, 14), (6, 67), (7, 88), (8, 44)]
    # print points1
    # print points2
    x_axis = np.linspace(x_begin, x_end, division)
    idx = 0
    id_px1 = 0
    id_px2 = 0
    x1_line = []
    y1_line = []
    x2_line = []
    y2_line = []
    xpoints = len(x_axis)
    intersection = []
    while idx < xpoints:
        # Iterate over two line segments
        x = x_axis[idx]
        if id_px1>-1:
            if x >= points1[id_px1][0] and id_px1<len(points1)-1:
                y1_line = np.linspace(points1[id_px1][1], points1[id_px1+1][1], 1000) # 1.4 1.401 1.402 etc. bis 2.1
                x1_line = np.linspace(points1[id_px1][0], points1[id_px1+1][0], 1000)
                id_px1 = id_px1 + 1
        if id_px1 == len(points1):
            x1_line = []
            y1_line = []
            id_px1 = -1
        if id_px2>-1:
            if x >= points2[id_px2][0] and id_px2<len(points2)-1:
                y2_line = np.linspace(points2[id_px2][1], points2[id_px2+1][1], 1000)
                x2_line = np.linspace(points2[id_px2][0], points2[id_px2+1][0], 1000)
                id_px2 = id_px2 + 1
        if id_px2 == len(points2):
            x2_line = []
            y2_line = []
            id_px2 = -1
        if x1_line!=[] and y1_line!=[] and x2_line!=[] and y2_line!=[]:
            i = 0
            while abs(x-x1_line[i])>x_dist and i < len(x1_line)-1:
                i = i + 1
                y1_current = y1_line[i]
                j = 0
                while abs(x-x2_line[j])>x_dist and j < len(x2_line)-1:
                    j = j + 1
                    y2_current = y2_line[j]
        if abs(y2_current-y1_current)<y_dist and i != len(x1_line) and j != len(x2_line):
            ymax = max(y1_current, y2_current)
            ymin = min(y1_current, y2_current)
            xmax = max(x1_line[i], x2_line[j])
            xmin = min(x1_line[i], x2_line[j])
            intersection.append((x, ymin+(ymax-ymin)/2))
            ax.plot(x, y1_current, 'ro') # Plot the cross point
        idx += 1    
    print ('intersection points', intersection)
    plt.show()