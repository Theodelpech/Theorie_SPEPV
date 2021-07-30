from Potentiel_Localisation import Potentiel_Localisation
import solar_mod as sm
from Basegraph import Basegraph
import numpy as np
from Input import input
from Input_bool import input_bool
#Demande de saisie :
Title1 = "Saisie des coordonnées de la localisation"
Title2 = "Vous souhaitez calculer le potentiel théoriquement ou expérimentalement par un fichier météo ?"
demandeLong = "Quelle est la longitude ?"
demandeLat = "Quelle est la latitude ?"
demandebool = "Saisir théorique ou expériemental"
#Variables :
Longitude = input(Title1, demandeLong)
Latitude = input(Title1, demandeLat)
bool = input_bool(Title2, demandebool)
if bool.message_bool() == "théorique":
    Theo_ou_meteo = True
else :
    Theo_ou_meteo = False
beta = 10
Albedo = 0.2
Lat = Latitude.message()
Long = Longitude.message()
#Main du programme :
potentiel_test = Potentiel_Localisation(Long.get(),Lat.get(),Theo_ou_meteo,beta,Albedo)
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