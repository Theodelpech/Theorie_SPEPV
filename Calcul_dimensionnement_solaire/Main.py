from Potentiel_Localisation import Potentiel_Loc
import solar_mod as sm
Longitude = 47.22
Latitude = -1.55
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Loc(Longitude,Latitude,Theo_ou_meteo,beta,Albedo)
print(potentiel_test.Potentiel_solaire_theo())