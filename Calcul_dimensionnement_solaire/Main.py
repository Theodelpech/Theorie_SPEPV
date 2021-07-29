from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
import csv
from Input import input
Title = "Saisie des coordonnées de la localisation"
demande = "Quelle est la longitude ?"
Longitude = input(Title, demande)
Latitude = 47.22
Theo_ou_meteo = True
beta = 10
Albedo = 0.2
potentiel_test = Potentiel_Localisation(Longitude.message(),Latitude,Theo_ou_meteo,beta,Albedo)
Val_TestIt, Val_TestRb, Val_TestIo, Val_TestIth, Val_TestThe = potentiel_test.Potentiel_solaire_theo()
print(max(Val_TestIt))
y_valuesIt, y_valuesRb, y_valuesIo, y_valuesIth, y_valuesThe = potentiel_test.Potentiel_solaire_theo()
x_values = np.arange(1,8761)
x= np.array(x_values)
y=np.array(y_valuesIt)
GRAPH_test = Basegraph(x,y)
GRAPH_test.show()
np.savetxt('Test_x.csv', (x), delimiter=' ')
np.savetxt('Test_y.csv', (y), delimiter=' ')