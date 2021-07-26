from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
Longitude = 47.22
Latitude = -1.55
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Localisation(Longitude,Latitude,Theo_ou_meteo,beta,Albedo)
Val_TestIt, Val_TestRb, Val_TestIo = potentiel_test.Potentiel_solaire_theo()
print(max(Val_TestIo))
y_valuesIt, y_valuesRb, y_valuesIo = potentiel_test.Potentiel_solaire_theo()
x_values = range(0,8760,1)
GRAPH_test = Basegraph(x_values,y_valuesIo)
GRAPH_test.show()
