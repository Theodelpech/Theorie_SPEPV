from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Graph_potentiel import Graph_potentiel
Longitude = 47.22
Latitude = -1.55
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Localisation(Longitude,Latitude,Theo_ou_meteo,beta,Albedo)
GRAPH_test = Graph_potentiel()
GRAPH_test.show()
