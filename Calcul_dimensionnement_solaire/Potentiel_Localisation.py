import solar_mod as sm
import numpy as np
import time as tm
import sys
sys.path.append(' c:/Users/theod/OneDrive/Bureau/Recherche/Python/Theorie_SPEPV/Calcul_dimensionnement_solaire/Package/datamet/Europe/ ')

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
    def Potentiel_solaire_met(self,nom):
        j_type = np.array([17,47,75,105,135,162,198,228,258,288,318,344])      # jour type de chaque mois
        nm = np.array([31,28,31,30,31,30,31,31,30,31,30,31])                # nombre de jours par mois
        hrm = np.array([744,672,744,720,744,720,744,744,720,744,720,744])  # nombre d'heures dans chaque mois
        hrr = np.array([744,1416,2160,2880,3624,4344,5088,5832,6552,7296,8016,8760]) # nombre d'heures écoulées après chaque mois
        donnees = np.loadtxt(nom,skiprows = 1)
        hr = donnees[:,0]   # heures
        Ih =  donnees[:,6]   # valeurs de I total donné par fichier météo en Wh/m2
        Ibh = donnees[:,12]   # valeurs de I direct donné par fichier météo en Wh/m2
        Idh  = Ih - Ibh   # valeurs de I diffus donné par fichier météo en Wh/m2
        i_hr = 0
        i_jour = 0
        gam = 0
        It=np.zeros(8760)
        Itb = np.zeros(8760)
        Itd = np.zeros(8760)
        Itr = np.zeros(8760)
        for im in range(0,12):  
            for ij in range(0,nm[im]):        # ij : jour du mois
                for j in range(0,24):
                    ome1 = -180.0 + 15.0*j
                    ome2 = ome1 + 15.0
                    omem = (ome1+ome2)/2.0
                    Rb = sm.calcul_Rb(self.Latitude,i_jour+1,omem,self.beta,gam)
                    delt  = sm.decl_solaire(i_jour+1)
                    theb = sm.normale_solaire(delt,self.Latitude,omem,self.beta,gam)
                    thez = sm.zenith_solaire(delt,self.Latitude,omem)
                    # modele isotrope
                    Itb [i_hr] = Ibh[i_hr]*Rb
                    Itd[i_hr] = Idh[i_hr]*(1+sm.cosd(self.beta))/2.0
                    Itr[i_hr] = Ih[i_hr]*self.Albedo*(1-sm.cosd(self.beta))/2.0
                    It [i_hr]= Itb[i_hr] + Itd[i_hr] + Itr[i_hr]
                    i_hr = i_hr+1
            i_jour = i_jour+1
        # Start of user code protected zone for Potentiel_solaire_met function body
        return It
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
                It_global[kh] = It
                kh = kh+1 
                Temps_solaire = Temps_solaire +1
        return It_global, Rbh, Ioh, Ithh, thetaz_moyh
        # End of user code	
    # Start of user code -> methods for Potentiel_Localisation class
        
    # End of user code

