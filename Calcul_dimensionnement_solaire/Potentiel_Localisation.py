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
        ao = ro*(0.4237-0.00821*(6-Alt)**2)
        aun = run*(0.5055+0.00595*(6.5-Alt)**2)
        k = rk*(0.2711-0.01858*(2.5-Alt)**2)
        gam = 0
        It_global = np.zeros(8760)
        kh = 1
        Jour = 1
        Rbh = np.zeros(8760)
        Ioh = np.zeros(8760)
        Ithh = np.zeros(8760)
        thetaz_moyh = np.zeros(8760)
        for Jour in range(1,365):
            for Temps_solaire in range (0,24):
                omega_1 = (Temps_solaire-12)*15
                omega_2 = (omega_1)+15
                ome_moy = (omega_1+omega_2)/2
                delta = sm.decl_solaire(Jour)
                #Gon = self.Gsc*(1+0.033((360*self.Jour)/365)) 
                thetaz_moy = sm.zenith_solaire(self.Latitude,delta,omega_1)
                thetaz_moyh[kh] = thetaz_moy
                alphas_moy = 90 - thetaz_moy
                m_air = 1/(sm.cosd(thetaz_moy)+0.50572*(96.07995-thetaz_moy)**(-1.6364))
                #m_air = 2
                Io = sm.irradiation_extraterrestre_horaire(Jour, self.Latitude,omega_1,omega_2)
                Ioh[kh] = Io
                tau_b = ao + aun*np.exp(-k*m_air)
                Ibh = Io*tau_b
                tau_d = 0.271 - 0.294*tau_b
                Idh = Io*tau_d
                Ith = Idh + Ibh
                Ithh[kh] = Ith
                Rb = sm.calcul_Rb(self.Latitude, Jour,ome_moy,self.beta, gam)
                Rbh[kh] = Rb
                It,Itb,Itd,Itr = sm.modele_isotropique(Ith,Ibh,Idh,self.beta,Rb,self.Albedo) #en W/m2
                if It == 'nan':
                    It = 0
                It_global[kh] = It
                kh = kh+1 
                Temps_solaire = Temps_solaire +1
        return It_global, Rbh, Ioh, Ithh, thetaz_moyh
        # End of user code	
    # Start of user code -> methods for Potentiel_Localisation class
        
    # End of user code

