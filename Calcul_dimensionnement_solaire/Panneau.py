import solar_mod as sm
import numpy as np
from Basegraph import Basegraph
import pandas as pd
import matplotlib as ml
ml.use('TkAgg')
import matplotlib.pyplot as plt
class Panneau (object):
    def __init__(self, effi, Isc, Voc, Imp, Vmp, Uvoc, UIl, Cel, Aire):
        self.effi = effi
        self.Isc = Isc
        self.Voc = Voc
        self.Imp = Imp
        self.Vmp = Vmp
        self.Uvoc = Uvoc
        self.UIl = UIl
        self.Cel = Cel
        self.Aire = Aire
    def energ_recup (self, It):
        Itreel = It*(self.effi/100)
        x_values = np.arange(0,8761)
        x_valuespd = pd.DataFrame(x_values)
        y_pd = pd.DataFrame(Itreel)
        y_g = y_pd.replace(np.nan,0)
        x= np.array(x_valuespd)
        y_energrecup=np.array(y_g)
        GRAPH_pottheo = Basegraph(x,y_energrecup,"Energie en W/m2","Heures de l'année","Energie récupérée par le panneau à chaque heures de l'année")
        GRAPH_pottheo.show()
    def courbeIV (self):
        k = 1.381e-23
        q = 1.602e-19
        Tref = 25.0 + 273.15
        N = self.Cel
        A = self.Aire
        Isc = self.Isc
        Voc = self.Voc
        Im = self.Imp
        Vm = self.Vmp
        muI = self.UIl 
        muV = self.Uvoc
        #Initialisation
        Rsh1 = 100
        a1 = 1.5*k*Tref*N/q
        IL1 = Isc
        Io1 = (IL1)/(np.exp(Voc/a1))
        Rs1 = (a1*np.log((IL1-Im)/Io1+1) - Vm)/Im
        if Rs1 < 0:
            Rs1 =0.1
        xi = np.zeros(5)
        xi[0] = IL1
        xi[1] = Io1
        xi[2] = a1
        xi[3] = Rsh1
        xi[4] = Rs1
        param = np.array([Isc,Voc,Im,Vm,muV,muI])
        #Résolution
        xf = sm.pv_module(xi,param)
        """
        IL = xf[0]
        Io = xf[1]
        a = xf[2]
        Rsh = xf[3]
        Rs = xf[4]
        """
        #génération courbe I-V du panneau :
        dV = 0.25
        Vv = np.arange(0.0,Voc+dV,dV)
        nV = len(Vv)
        Iv = np.zeros(nV)
        for i  in range(0,nV):
            Iv[i] = sm.I_pvV(xf,Vv[i])
        # Courbe IV pour une température différente T = 40°C
        T2 = 40 + 273.15
        Voc2 = (T2-Tref)*muV + Voc
        Vocc = sm.Vocr(xf,Voc2,T = T2)
        Vv2 = np.arange(0.0,Vocc+dV,dV)
        nV2 = len(Vv2)
        Iv2 = np.zeros(nV2)
        for i  in range(0,nV2):
            Iv2[i] = sm.I_pvV(xf,Vv2[i],T = T2)
        # calcul de I lorsque l'irradiation est différente de 1000 W/m2 : 600 W/m2
        Vocc = sm.Vocr(xf,Voc2,G = 600)
        Vv3 = np.arange(0.0,Vocc+dV,dV)
        nV3 = len(Vv3)
        Iv3 = np.zeros(nV3)
        for i  in range(0,nV3):
            Iv3[i] = sm.I_pvV(xf,Vv3[i],G = 600)
        plt.figure(1)
        plt.plot(Vv,Iv,Vv2,Iv2,Vv3,Iv3)
        plt.legend(('Valeurs standards','T = 40 C','G = 600 W/m2'))
        plt.title('Courbe I-V du panneau selon différentes conditions')
        plt.xlabel('Tension en Volt')
        plt.ylabel('Courant en Ampère')
        Pv = Iv*Vv
        Pv2 = Iv2*Vv2
        Pv3 = Iv3*Vv3
        plt.figure(2)
        plt.plot(Vv,Pv,Vv2,Pv2,Vv3,Pv3)
        plt.legend(('Valeurs standards','T = 40 C','G = 600 W/m2'))
        plt.title('Courbe V-P du panneau selon différentes conditions')
        plt.xlabel('Tension en Volt')
        plt.ylabel('Puissance en Watt')
        Basegraph.plotyy(Vv,Iv,Vv,Pv)
        plt.show()
        return Iv, Vv, nV