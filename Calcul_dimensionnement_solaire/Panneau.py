import solar_mod as sm
import numpy as np
from Basegraph import Basegraph
import pandas as pd
class Panneau (object):
    def __init__(self, effi, Isc, Voc, Imp, Vmp, Uvoc, UIl):
        self.effi = effi
        self.Isc = Isc
        self.Voc = Voc
        self.Imp = Imp
        self.Vmp = Vmp
        self.Uvoc = Uvoc
        self.UIl = UIl
    def energ_recup (self, It):
        Itreel = It*(self.effi/100)
        x_values = np.arange(1,8761)
        x_valuespd = pd.DataFrame(x_values)
        y_pd = pd.DataFrame(Itreel)
        y_g = y_pd.replace(np.nan,0)
        x= np.array(x_valuespd)
        y_energrecup=np.array(y_g)
        GRAPH_pottheo = Basegraph(x,y_energrecup)
        GRAPH_pottheo.show()
