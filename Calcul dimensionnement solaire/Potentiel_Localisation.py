import solar_mod as sm
import numpy as np
class Potentiel_Localisation(object):
    def __init__(self):
        self.Longitude = 0. #à demander
        self.Latitude = 0. #à demander
        self.Theo_ou_meteo = True #à demander
        self.beta = 0 #à demander
        self.Albedo = 0.2 #albedo moyen entre une forêt de conifère et un sol sombre (à demander)
        self.Gsc = 1367.0 #W/m2 irradiation extraterrestre qui frappe la Terre
        self.Temps_solaire = 0 #Première heure solaire d'une journée de 24 heures solaire
        self.Jour = 1 #Premier jour d'une année de 365 jours, le 1er Janvier
        self.MAX_LONGITUDE = -180
        self.MAX_LATITUDE = 180
        self.MN_LATITUDE = -90
        self.MIN_LONGITUDE = 90
        
    # Start of user code -> properties/constructors for Potentiel_Localisation class

    # End of user code
    def Potentiel_solaire_met(self):
        # Start of user code protected zone for Potentiel_solaire_met function body
        return 0.
        # End of user code	
    def Potentiel_solaire_theo(self):
        r0 = 1 #à demander
        r1 = 1 #à demander
        rk = 1 #à demander
        Alt = 1 #en km à demander à l'utilisateur
        for self.Jour in range(1,365,1):
            for self.Temps_solaire in range (0,24,1):
                omega_1 = (self.Temps_solaire-12)*15.000000
                omega_2 = omega_1+15
                ome_moy = (omega_1+omega_2)/2
                delta = sm.decl_solaire(self.Jour)
                Gon = self.Gsc*(1+0.033((360*self.Jour)/365)) 
                thetaz_moy = sm.zenith_solaire(self.Latitude,delta,omega_1)
                alphas_moy = 90 - thetaz_moy
                m_air = 1/np.cos(thetaz_moy)
                I0 = sm.irradiation_extraterrestre_horaire(self.Jour, self.Latitude,omega_1,omega_2)
                a0 = r0*(0.4237-0.00821*(6-Alt)^2)
                a1 = r1*(0.5055+0.00595(6.5-Alt)^2)
                k = rk*(0.2711-0.01858*(2.5-Alt)^2)
                tau_b = a0 + a1*np.exp(-k*m_air)
                Ibh = I0*tau_b
                tau_d = 0.271 - 0.294*tau_b
                Idh = I0*tau_d
                Ith = Idh + Ibh
                the_moy = sm.arccosd(sm.cosd(delta)*sm.sind(self.Latitude-self.beta)+sm.cosd(delta)*cosd(ome_moy)*sm.cosd(self.Latitude-self.beta))
                Rb = np.cos(the_moy)/np.cos(thetaz_moy)
                It = sm.modele_isotropique(Ith,Ibh,Idh,self.beta,Rb,self.Albedo) #en W/m2
                
                


                return
            return
        # End of user code	
    # Start of user code -> methods for Potentiel_Localisation class
        return 0.
    # End of user code

