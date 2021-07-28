from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
Longitude = 47.22
Latitude = -1.55
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Localisation(Longitude,Latitude,Theo_ou_meteo,beta,Albedo)
Val_TestIt, Val_TestRb, Val_TestIo, Val_TestIth, Val_TestThe = potentiel_test.Potentiel_solaire_theo()
print(max(Val_TestIt))
y_valuesIt, y_valuesRb, y_valuesIo, y_valuesIth, y_valuesThe = potentiel_test.Potentiel_solaire_theo()
x_values = range(0,8760)
x= np.array(x_values)
y=np.array(y_valuesIt)
GRAPH_test = Basegraph(x,y) #problème 6945 et 6951
GRAPH_test.show()
print(y_valuesIt[36])
