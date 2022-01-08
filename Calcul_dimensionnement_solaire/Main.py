from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
from Input import input
import pandas as pd
from Panneau import Panneau
import matplotlib.pyplot as plt
import sys 
from pump import Pump
from reservoir import Reservoir
"""
Module defining a main algorithm for sizing a PV punping system

@author: Delpech Théo 

"""
#Demandes de saisie, départ de l'algorithme :
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

#Variables de départ, modélisation de l'environnement :
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
    
    #Calcul théoriquement du potentiel solaire maximum de la localisation
    if Theo_ou_meteo == True : 
        
        #Calcul du potentiel théorique :
        potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta.get(),Albedo.get(),gam.get())
        constante = input("Quelles sont les valeurs des constantes solaires ?","Regardez les constantes de Hottel pour compléter")
        ro,r1,rk,Alt = constante.mesconst("r0 :","r1 :","rk :", "Altitude par rapport au niveau de la mer de la localisation (en m) :")
        
        #Courbe de potentiel sur un plan incliné de beta chaque heures de l'année :
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
        
        #Modélisation du panneau PV :
        parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?') 
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
        panneau_pot = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        
        #Courbe d'énergie récupérée par le panneau à chaque heures de l'année en W :
        Preel = panneau_pot.energ_recup(y_pot)
        
        #Courbe I-V puis P-V du panneau : 
        Ipan, Vpan, npan = panneau_pot.courbeIV()
        
        #Modélisation canalisation et HMT :
        tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
        tdh = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ")
        
        #Demande type de couplage :
        couple_dem = input('Type de couplage','1 pour un couplage MPPT et 0 pour un couplage direct')
        couple = couple_dem.message()
        
        #Modélisation couplage direct
        if couple.get() == 0:
            
            #Modélisation pompe :
            dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
            pu = dem_pump.meschemin()
            chem_pump = 'Package\pump_files'+pu.get()
            Motpompe = Pump(chem_pump,None, None, np.nan, None, None, 'arab')
            
            #Courbe I-V pompe :
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
            IPF, VPF, dsp = pf.mespf('If (en A) :','Vf (en V) :','Si aucun point de fonctionnement identifié, mettre 0 :')
            if dsp.get() == 0 :
                print("Recherche d'autres composants nécessaire ou réaliser un couplage MPPT")
                breakpoint
            Power = float((IPF.get())*(VPF.get()))
            Qp = Qpomp(Power, tdh)
            Qreel, Qtotal = Motpompe.debanneeIV(Preel,Power,tdh,Qpomp)
            print("Le systeme a pompe :",Qtotal/1000,"m3 sur une annee soit :", Qtotal/(365*1000),"m3 par jours")
    
    #Modélisation couplage MPPT :
        else :
            dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
            pu = dem_pump.meschemin()
            chem_pump = 'Package\pump_files'+pu.get()
            Motpompe = Pump(chem_pump,None,None ,np.nan ,None ,None,  'hamidat')
            Qpomp, PHpomp = Motpompe.functQforPH_Hamidat()
            mppt_dem = input('MPPT paramètre', 'Efficacité (en décimal):')
            mppt = mppt_dem.message()
            Power = Preel*mppt.get()
            Qreel, Qtotal = Motpompe.debannee(Power,tdh,Qpomp)
            print("Le systeme a pompe :",Qtotal/1000,"m3 sur une annee soit :", Qtotal/(365*1000),"m3 par jours")
    
#Calcul expérimentalement du potentiel solaire maximum de la Potentiel_Localisation :
    else : 
        
        #Chemin du fichier météo à utiliser :
        demchem = "\Continent\ nomdufichierfichier.tm2"
        demche = "Entrez le fichier comme suit : "+ demchem.replace(" ","")
        chemin = input("Quel est le fichier que vous souhaitez utiliser ?",demche)
        chem_met = chemin.meschemin() 
        nom_met = "Package\datamet"  + chem_met.get()
        
        #Calcul du potentiel solaire sur une surface inclinée de beta en W/m2 :
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
        
        #Modélisation du panneau PV :
        parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?') 
        effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
        panneau_pot = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(),Aire.get())
        
        #Calcul de l'énergie récupérée par le panneau PV à chaque heures de l'année :
        Preel = panneau_pot.energ_recup(y_pot)
        
        #Courbe I-V puis P-V du panneau : 
        Ipan, Vpan, npan = panneau_pot.courbeIV()
        
        #Modélisation canalisation et HMT :
        tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
        tdh = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ")
        
        #Demande type de couplage :
        couple_dem = input('Type de couplage','1 pour un couplage MPPT et 0 pour un couplage direct')
        couple = couple_dem.message()
        
        #Modélisation couplage direct
        if couple.get() == 0:
            
            #Modélisation pompe :
            dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
            pu = dem_pump.meschemin()
            chem_pump = 'Package\pump_files'+pu.get()
            Motpompe = Pump(chem_pump,None, None, np.nan, None, None, 'arab')
            
            #Courbe I-V pompe :
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
            IPF, VPF,dsp = pf.mespf('If (en A) :','Vf (en V) :','Si aucun point de fonctionnement identifié, mettre 0 :')
            if dsp.get() == 0 :
                print("Recherche d'autres composants nécessaire ou réaliser un couplage MPPT")
                breakpoint
            Power = float((IPF.get())*(VPF.get()))
            Qp = Qpomp(Power, tdh)
            Qreel, Qtotal = Motpompe.debanneeIV(Preel,Power,tdh,Qpomp)
            print("Le systeme a pompe :",Qtotal/1000,"m3 sur une annee soit :", Qtotal/(365*1000),"m3 par jours")
    
    #Modélisation couplage MPPT :
        else :
            #Modélisation de la pompe :
            dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
            pu = dem_pump.meschemin()
            chem_pump = 'Package\pump_files'+pu.get()
            Motpompe = Pump(chem_pump,None,None ,np.nan ,None ,None,  'hamidat')
            Qpomp, PHpomp = Motpompe.functQforPH_Hamidat()
            #Modélisation MPPT :
            mppt_dem = input('MPPT paramètre', 'Efficacité (en décimal):')
            mppt = mppt_dem.message()
            #Modélisation réservoir :
            res_dem = input('Réservoir paramètre','Volume du réservoir (m3) :')
            volres = res_dem.message()
            res = Reservoir(volres.get())
            #Modélisation demande eau :
            eaubes_dem = input('Demande en eau, paramètrage','Besoin en eau (m3) :')
            eaubes = eaubes_dem.message()
            Power = Preel*mppt.get()
            Qreel, Qtotal = Motpompe.debannee(Power,tdh,Qpomp)
            print("Le systeme a pompe :",Qtotal/1000,"m3 sur une annee soit :", Qtotal/(365*1000),"m3 par jours")
        
else :
    
    #Modélisation Panneau PV
    parampan = input('Paramètres du panneau à entrer','Quels sont les paramètres du panneau ?')
    effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire, Mp, Ms = parampan.messagemult('Efficacite du panneau (en %) =', 'Isc (en A) = ','Voc (en V) =','Imp (en A) =','Vmp (en V) =', 'Uvoc =','UIl =','Nombre de cellules =','Aire (en m2) =','Nombre de panneaux en parallèle :','Nombre de panneaux en série :')
    panneau_test = Panneau(effi.get(), Isc.get(), Voc.get(),Imp.get(),Vmp.get(),Uvoc.get(),UIl.get(),Cel.get(), Aire.get())
    
    #Courbe I-V puis P-V du panneau : 
    Ipan, Vpan, npan = panneau_test.courbeIV()
    
    #Modélisation moteur-pompe DC :
    tdhpara = input('Paramètres du système de pompage pour le calcul de la HMT',None)
    tdh = tdhpara.mestdh("Hauteur entre le niveau d'eau et l'apiration de la pompe (en m):", "Hauteur entre le refoulement et le point d'utilisation (en m):","Longueur des tuyaux (en m):", "Pression résiduelle à la sortie du robinet (en bars): ")
    
    #Demande type de couplage :
    couple_dem = input('Type de couplage','1 pour un couplage MPPT et 0 pour un couplage direct')
    couple = couple_dem.message()
    
    #Modélisation couplage direct
    if couple.get() == 0:
       
        #Modélisation de la pompe :
        dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
        pu = dem_pump.meschemin()
        chem_pump = 'Package\pump_files'+pu.get()
        
        #Courbe I-V de la pompe :
        Motpompe = Pump(chem_pump,None, None, np.nan, None, None, 'arab')
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
        IPF, VPF, dsp = pf.mespf('If (en A) :','Vf (en V) :','Si aucun point de fonctionnement identifié, mettre 0 :')
        if dsp.get() == 0 :
            print("Recherche d'autres composants nécessaire ou réaliser un couplage MPPT")
            breakpoint
        Power = float((IPF.get())*(VPF.get()))
        Qp = Qpomp(Power, tdh)
        print("Pour ce point de fonctionnement le debit est de :",Qp['Q']*(60/1000),"m3/h")
        print("La puissance non utilisee est de :",Qp['P_unused'],"W")
    
    #Modélisation couplage MPPT :
    else :
        
        #Modélisation de la pompe :
        dem_pump = input("Quelle pompe souhaitez vous utiliser ?", "Entrez la pompe comme suit : \pompe.txt")
        pu = dem_pump.meschemin()
        chem_pump = 'Package\pump_files'+pu.get()
        Motpompe = Pump(chem_pump,None,None ,np.nan ,None ,None,  'hamidat')
        Qpomp, PHpomp = Motpompe.functQforPH_Hamidat()
        mppt_dem = input('MPPT paramètre', 'Efficacité (en décimal):')
        mppt = mppt_dem.message()
        Power_dem = input('Puissance de test du système à entrer', 'Puissance (en W) :')
        Power = Power_dem.message()
        Qp = Qpomp(Power.get()*mppt.get(), tdh)
        print("Pour cette puissance essayée le debit est de :",Qp['Q']*(60/1000),"m3/h")
        print("La puissance non utilisée est de :",Qp['P_unused'],"W")
        
        

    


