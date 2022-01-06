from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
from Input import input
import pandas as pd
from Panneau import Panneau
from MotPompeDC import MotPompeDC
import matplotlib.pyplot as plt
import sys 
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
demandegam = "Quelle est l'azimuth solaire ?"
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
    paramet = input(Title1,None)
    beta, Albedo, Lat, Long, gam = paramet.mespot(demandebeta,demandealb,demandeLat,demandeLong,demandegam)
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
        potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta.get(),Albedo.get(),gam.get())
        constante = input("Quelles sont les valeurs des constantes solaires ?","Regardez les constantes de Hottel pour compléter")
        ro,r1,rk,Alt = constante.mesconst("r0 :","r1 :","rk :", "Altitude par rapport au niveau de la mer de la localisation (en m) :")
        y_valuesIt = potentiel_test.Potentiel_solaire_theo(ro.get(),r1.get(),rk.get(),Alt.get())
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
        #Calcul de l'énergie récupérable avec le panneau solaire 
        #Courbe d'énergie récupérée par le panneau :
        parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?') 
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
        panneau_pot = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        Preel = panneau_pot.energ_recup(y_pot)
        #Courbe I-V puis P-V du panneau : 
        Ipan, Vpan, npan = panneau_pot.courbeIV()
        #Courbe I_V moteur-pompe DC :
        dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
        pu = dem_pump.meschemin()
        #\PS150_BOOST_60.txt
        chem_pump = 'Calcul_dimensionnement_solaire\Package\pump_files'+pu.get()
        Motpompe = MotPompeDC(chem_pump)
        tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
        tdh = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ")
        xpomp, ypomp = Motpompe.functIforVH_Arab()
        Vrange_load = np.arange(*ypomp['V'](tdh))
        ivgraphpomp = Basegraph(Vrange_load,xpomp(Vrange_load, tdh, error_raising=False),"Courant I en Ampère", "Tension V en Volt", "Courbe I-V de l'ensemble moteur pompe")
        ivgraphpomp.show()
        npan = max(len(Vpan),len(Vrange_load))
        courbe_pf = Basegraph(None, None,'Courant en Ampère','Tension en Volt','Courbes IV : panneau en bleu, moteur-pompe en vert')
        courbe_pf.operating_point(Ipan,Vpan,xpomp(Vrange_load, tdh, error_raising=False),Vrange_load,Ms.get(),Mp.get())
        #Débit du point de fonctionnement :
        Qpomp, PHpomp = Motpompe.functQforPH_Arab()
        pf = input("Quel est le point de fonctionnement identifié ?",None)
        IPF, VPF = pf.mespf('If (en A) :','Vf (en V) :')
        Power = float((IPF.get())*(VPF.get()))
        Qreel, Qtotal = Motpompe.debannee(Preel,Power,tdh,Qpomp)
        print("Le systeme a pompe :",Qtotal,"L sur une annee soit :", Qtotal/365,"L par jours")
#Calcul expérimentalement du potentiel solaire maximum de la Potentiel_Localisation :
    else : 
        demchem = "\Continent\ nomdufichierfichier.tm2"
        demche = "Entrez le fichier comme suit : "+ demchem.replace(" ","")
        chemin = input("Quel est le fichier que vous souhaitez utiliser ?",demche)
        chem_met = chemin.meschemin() 
        #\Europe\FR-Bordeaux-75100.tm2
        nom_met = "Calcul_dimensionnement_solaire\Package\datamet"  + chem_met.get()
        potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta.get(),Albedo.get(),gam.get())
        y_valuesIt = potentiel_test.Potentiel_solaire_met(nom_met)
        x_values = np.arange(0,8761)
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
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
        panneau_pot = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        Preel = panneau_pot.energ_recup(y_pot)
        #Courbe I-V puis P-V du panneau : 
        Ipan, Vpan, npan = panneau_pot.courbeIV()
        #Courbe I_V moteur-pompe DC :
        dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
        pu = dem_pump.meschemin()
        #\PS150_BOOST_60.txt
        chem_pump = 'Calcul_dimensionnement_solaire\Package\pump_files'+pu.get()
        Motpompe = MotPompeDC(chem_pump)
        tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
        tdh,NPSHreq = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ", "Quel est le NPSH requis de la pompe ?")
        xpomp, ypomp = Motpompe.functIforVH_Arab()
        Vrange_load = np.arange(*ypomp['V'](tdh))
        ivgraphpomp = Basegraph(Vrange_load,xpomp(Vrange_load, tdh, error_raising=False),"Courant I en Ampère", "Tension V en Volt", "Courbe I-V de l'ensemble moteur pompe")
        ivgraphpomp.show()
        npan = max(len(Vpan),len(Vrange_load))
        courbe_pf = Basegraph(None, None,'Courant en Ampère','Tension en Volt','Courbes IV : panneau en bleu, moteur-pompe en vert')
        courbe_pf.operating_point(Ipan,Vpan,xpomp(Vrange_load, tdh, error_raising=False),Vrange_load,Ms.get(),Mp.get())
        #Débit du point de fonctionnement :
        Qpomp, PHpomp = Motpompe.functQforPH_Arab()
        pf = input("Quel est le point de fonctionnement identifié ?",None)
        IPF, VPF = pf.mespf('If (en A) :','Vf (en V) :')
        Power = float((IPF.get())*(VPF.get()))
        Qreel, Qtotal = Motpompe.debannee(Preel,Power,tdh,Qpomp)
        print("Le systeme a pompe :",Qtotal,"L sur une annee soit :", Qtotal/365,"L par jours")
        
else :
    parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
    effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
    panneau_test = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(), Aire.get())
    # 4.5,21.4,3.95,16.5,-0.085,0.00026,36,0.633
    #Courbe I-V puis P-V du panneau : 
    Ipan, Vpan, npan = panneau_test.courbeIV()
    #Courbe I_V moteur-pompe DC :
    dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
    pu = dem_pump.meschemin()
    #\PS150_BOOST_60.txt
    chem_pump = 'Calcul_dimensionnement_solaire\Package\pump_files'+pu.get()
    Motpompe = MotPompeDC(chem_pump)
    tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
    tdh = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ")
    xpomp, ypomp = Motpompe.functIforVH_Arab()
    Vrange_load = np.arange(*ypomp['V'](tdh))
    ivgraphpomp = Basegraph(Vrange_load,xpomp(Vrange_load, tdh, error_raising=False),"Courant I en Ampère", "Tension V en Volt", "Courbe I-V de l'ensemble moteur pompe")
    ivgraphpomp.show()
    #Point de fonctionnement : (à chercher sur graphe)
    npan = max(len(Vpan),len(Vrange_load))
    courbe_pf = Basegraph(None, None,'Courant en Ampère','Tension en Volt','Courbes IV : panneau en bleu, moteur-pompe en vert (cherchez graphiquement le point de fonctionnement et le retenir)')
    courbe_pf.operating_point(Ipan,Vpan,xpomp(Vrange_load, tdh, error_raising=False),Vrange_load,Ms.get(),Mp.get())
    #Débit du point de fonctionnement :
    Qpomp, PHpomp = Motpompe.functQforPH_Arab()
    pf = input("Quel est le point de fonctionnement identifié ?",None)
    IPF, VPF = pf.mespf('If (en A) :','Vf (en V) :')
    Power = float((IPF.get())*(VPF.get()))
    print("La puissance requise minimale de fonctionnement est de :",Power," en W")
    Qp = Qpomp(Power, tdh)
    print("Pour ce point de fonctionnement le debit est de :",Qp['Q']," en L/min")
    print("La puissance non utilisee est de :",Qp['P_unused']," en W")

    


