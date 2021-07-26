from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
Longitude = 47.22
Latitude = -1.55
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Localisation(Longitude,Latitude,Theo_ou_meteo,beta,Albedo)
TEST = potentiel_test.Potentiel_solaire_theo()
print(TEST[12])