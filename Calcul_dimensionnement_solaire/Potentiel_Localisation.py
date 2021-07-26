import solar_mod as sm
import numpy as np

Gsc = 1367.0 #W/m2 irradiation extraterrestre qui frappe la Terre
Jour = 1 #Premier jour d'une année de 365 jours, le 1er Janvier
MAX_LONGITUDE = -180
MAX_LATITUDE = 180
MN_LATITUDE = -90
MIN_LONGITUDE = 90
class Potentiel_Localisation(object):
    def __init__(self,Longitude,Latitude,Theo_ou_meteo,beta,Albedo):
        self.Longitude = Longitude #à demander
        self.Latitude = Latitude #à demander
        self.Theo_ou_meteo = Theo_ou_meteo #à demander
        self.beta = beta #à demander
        self.Albedo = Albedo #0.2 albedo moyen entre une forêt de conifère et un sol sombre (à demander)

        
    # Start of user code -> properties/constructors for Potentiel_Localisation class

    # End of user code
    def Potentiel_solaire_met(self):
        # Start of user code protected zone for Potentiel_solaire_met function body
        return 0.
        # End of user code	
    def Potentiel_solaire_theo(self):
        ro = 0.97 #à demander
        run = 0.99 #à demander
        rk = 1.02 #à demander
        Alt = 0.052 #en km à demander à l'utilisateur
        gam = 0
        It_global = np.zeros(8760)
        kh = 0
        Temps_solaire = 0
        Jour = 1
        Rbh = np.zeros(8760)
        Ioh = np.zeros(8760)
        m_air = np.zeros(8760)
        tau_b = np.zeros(8760)
        Ibh = np.zeros(8760)
        tau_d = np.zeros(8760)
        Idh = np.zeros(8760)
        Ith = np.zeros(8760)
        for nj in range(0,365,1):
            for hj in range (0,24,1):
                omega_1 = (Temps_solaire-12)*15.000000
                omega_2 = (omega_1)+15
                ome_moy = (omega_1+omega_2)/2
                delta = sm.decl_solaire(Jour)
                #Gon = self.Gsc*(1+0.033((360*self.Jour)/365)) 
                thetaz_moy = sm.zenith_solaire(self.Latitude,delta,omega_1)
                #alphas_moy = 90 - thetaz_moy
                m_air[kh] = 1/np.cos(thetaz_moy)
                Ioh[kh] = sm.irradiation_extraterrestre_horaire(Jour, self.Latitude,omega_1,omega_2)
                ao = ro*(0.4237-0.00821*np.square((6-Alt)))
                aun = run*(0.5055+0.00595*np.square((6.5-Alt)))
                k = rk*(0.2711-0.01858*np.square((2.5-Alt)))
                tau_b[kh]= ao + aun*np.exp(-k*m_air[kh])
                Ibh[kh] = Ioh[kh]*tau_b[kh]
                tau_d[kh] = 0.271 - 0.294*tau_b[kh]
                Idh[kh] = Ioh[kh]*tau_d[kh]
                Ith[kh] = Ibh[kh] + Idh[kh]
                Rb = sm.calcul_Rb(self.Latitude, Jour,ome_moy,self.beta, gam)
                Rbh[kh] = Rb
                It,Itb,Itd,Itr = sm.modele_isotropique(Ith[kh],Ibh[kh],Idh[kh],self.beta,Rb[kh],self.Albedo) #en W/m2
                It_global[kh] = It
                kh = kh+1 
                Temps_solaire = Temps_solaire +1
            Jour = Jour + 1
            Temps_solaire = 0

        return It_global, Rbh, Ioh
        # End of user code	
    # Start of user code -> methods for Potentiel_Localisation class
        
    # End of user code

