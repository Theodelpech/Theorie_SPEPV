import solar_mod as sm
import numpy as np
import time as tm
"""
Module defining class and functions for modeling Solar potential 

@author: Delpech Théo

"""

Gsc = 1367.0 #W/m2 irradiation extraterrestre qui frappe la Terre
Jour = 1 #Premier jour d'une année de 365 jours, le 1er Janvier
MAX_LONGITUDE = -180
MAX_LATITUDE = 180
MN_LATITUDE = -90
MIN_LONGITUDE = 90
class Potentiel_Localisation(object):
    def __init__(self,Longitude,Latitude,Theo_ou_meteo,beta,Albedo,gam):
        self.Longitude = Longitude #à demander
        self.Latitude = Latitude #à demander
        self.Theo_ou_meteo = Theo_ou_meteo #à demander
        self.beta = beta #à demander
        self.Albedo = Albedo #0.2 albedo moyen entre une forêt de conifère et un sol sombre (à demander)
        self.gam = gam

        
    # Start of user code -> properties/constructors for Potentiel_Localisation class

    # End of user code
    def Potentiel_solaire_met(self,nom):
        donnees = np.loadtxt(nom,skiprows = 1, usecols=(6,12))
        Ih =  donnees[:,0]   # valeurs de I total donné par fichier météo en Wh/m2
        Ibh = donnees[:,1]   # valeurs de I direct donné par fichier météo en Wh/m2
        Idh  = Ih - Ibh   # valeurs de I diffus donné par fichier météo en Wh/m2
        i_hr = 0
        It=np.zeros(8761)
        Itb = np.zeros(8761)
        Itd = np.zeros(8761)
        Itr = np.zeros(8761)  
        for jour in range(1,366):        # ij : jour du mois
            for j in range(0,24):
                ome1 = -180.0 + 15.0*j
                ome2 = ome1 + 15.0
                omem = (ome1+ome2)/2.0
                Rb = sm.calcul_Rb(self.Latitude,jour,omem,self.beta,self.gam)
                # modele isotrope
                It [i_hr],Itb[i_hr],Itd[i_hr],Itr[i_hr] = sm.modele_isotropique(Ih[i_hr],Ibh[i_hr],Idh[i_hr],self.beta,Rb,self.Albedo)
                i_hr = i_hr+1
        # Start of user code protected zone for Potentiel_solaire_met function body
        return It
        # End of user code	
    def Potentiel_solaire_theo(self,ro,run,rk,Alth):
        Alt = Alth/1000
        ao = ro*(0.4237-0.00821*(6-Alt)**2)
        aun = run*(0.5055+0.00595*(6.5-Alt)**2)
        k = rk*(0.2711-0.01858*(2.5-Alt)**2)
        It_global = np.zeros(8761)
        kh = 1
        Jour = 1
        Rbh = np.zeros(8761)
        Ioh = np.zeros(8761)
        Ithh = np.zeros(8761)
        for Jour in range(1,366):
            for Temps_solaire in range (0,24):
                omega_1 = (Temps_solaire-12)*15
                omega_2 = (omega_1)+15
                ome_moy = (omega_1+omega_2)/2
                delta = sm.decl_solaire(Jour)
                thetaz_moy = sm.zenith_solaire(self.Latitude,delta,omega_1)
                m_air = np.exp(-0.0001184*Alth)/(sm.cosd(thetaz_moy)+0.50572*(96.07995-thetaz_moy)**(-1.6364))
                Io = sm.irradiation_extraterrestre_horaire(Jour, self.Latitude,omega_1,omega_2)
                Ioh[kh] = Io
                tau_b = ao + aun*np.exp(-k*m_air)
                Ibh = max(0,Io*tau_b*sm.cosd(thetaz_moy))
                tau_d = 0.271 - 0.294*tau_b
                Idh = Io*tau_d
                Ith = Idh + Ibh
                Ithh[kh] = Ith
                Rb = sm.calcul_Rb(self.Latitude, Jour,ome_moy,self.beta, self.gam)
                Rbh[kh] = Rb
                It,Itb,Itd,Itr = sm.modele_isotropique(Ith,Ibh,Idh,self.beta,Rb,self.Albedo) #en W/m2
                It_global[kh] = It
                kh = kh+1 
                Temps_solaire = Temps_solaire +1
        return It_global

