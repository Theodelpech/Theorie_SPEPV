#coding: latin-1
#   fonctions utiles systemes solaires
#       alp_alpn(the)
#       angle_diffus(beta)
#       angle_reflechi(beta)
#       angle_horaire(sol_t)
#       angle_sunset(phi,delta)
#       azimuth_solaire(thes,delta,phi,ome)
#       Calcul_Ka(It,Itb,Itd,Itr,theb,bo,beta)
#       Calcul_pertes(T1c,data)
#       normale_solaire(delt,phi,ome,beta,gam)
Gsc = 1367.0
from numpy import *
from scipy.integrate import quad,nquad
from scipy.special import erf,erfc
from collections import *
from time import *
from properties_mod import *
from scipy.optimize import root,newton,fsolve,brentq,fmin_l_bfgs_b

hrm = array([744,672,744,720,744,720,744,744,720,744,720,744])  # nombre d'heures dans chaque mois
hrr = array([744,1416,2160,2880,3624,4344,5088,5832,6552,7296,8016,8760]) # nombre d'heures ?coul?es apr?s chaque mois
jjm = array([17,47,75,105,135,162,198,228,258,288,318,344])
jnm = array([31,28,31,30,31,30,31,31,30,31,30,31])
jjr = array([0,31,59,90,120,151,181,212,243,273,304,334])
nom = ['jan','fev','mars','avr','mai','juin','juil','aout','sept','oct','nov','dec']

def sind(the):
    y = sin(the*pi/180.0)
    return y
def cosd(the):
    y = cos(the*pi/180.0)
    return y
def tand(the):
    y = tan(the*pi/180.0)
    return y
def arccosd(ct):
    y = arccos(ct)
    return y*180/pi
def arcsind(ct):
    y = arcsin(ct)
    return y*180/pi
def arctand(ct):
    y = arctan(ct)
    return y*180/pi
def alp_alpn(the):
    # RELATION 4.11.1 db 3RD
    y = 1 - 1.5879e-3*the+2.7314e-4*the**2-2.3026e-5*the**3+9.0244e-7*the**4-1.8e-8*the**5+1.7734e-10*the**6 - 6.9937e-13*the**7
    y = max(y,0)
    return y
def angle_diffus(beta):
    # relation  5.4.2 DB 3RD edition
    y = 59.7 - 0.1388*beta+0.001497*beta**2
    return y
def angle_reflechi(beta):
    # relation  5.4.1 DB 3RD edition
    y = 90.0 - 0.5788*beta + 0.002693*beta**2
    return y
def angle_horaire(sol_t):
    # sol_t temps solaire en heures minutes de 0 � 24 hr
    # terre tourne 15 deg par heure
    # ome = 0 � midi solaire (>0 PM, <0 AM)
    x = sol_t.hr + sol_t.min/60.0
    ome = 15.0*(x-12.0)
    return ome
def angle_sunset(phi,delta):
    com = -tand(phi)*tand(delta)
    omes = arccos(com)*180.0/pi
    return omes


def azimuth_solaire(thes,delta,phi,ome):
    #     (Eq 1.6.6 de DB 3rd edition)
    #   angle d'azimuth du soleil en degres
    #        thes : zenith solaire
    #        del : declinaison en degre
    #        ome : angle horaire en degre
    #       phi : latitude en degr�es

    cosz = (cosd(thes)*sind(phi)-sind(delta))/(sind(thes)*cosd(phi))
    cosz = min(1,cosz);
    gams = sign(ome)*arccos(cosz)*180/pi
    return gams

def Calcul_Ka(It,Itb,Itd,Itr,theb,bo,beta,b1 = 0):

    def  kta(the):
        if the > 60:
            kta = 1 - bo - b1
            kta = kta*(1 - (the - 60.0)/30.0)
        else:
            kta = 1 - bo*(1/cosd(the)-1) - b1*(1/cosd(the)-1)**2
        return kta
    Kb = kta(theb)
    thed = angle_diffus(beta)
    Kd = kta(thed)
    ther = angle_reflechi(beta)
    Kr = kta(ther)
    Ka = (Kb*Itb+Kd*Itd+Kr*Itr)/It
    return Ka

def decl_solaire(n,cas =1):
    # declinaison solaire en degr�s (Eq 1.6.1a de DB 3rd edition)
    # Pour utiliser 1.6.1b, cas =2
    dec = 23.45*sind(360.0*(284.0+n)/365.0);
    if cas == 2:
        B = (n-1)*360/365.25
        dec = 180/pi*(0.006918-0.399912*cosd(B)+0.070257*sind(B) - \
            0.006758*cosd(2*B) + 0.000907*sind(2*B) \
            -0.002679*cosd(3*B) + 0.00148*sind(3*B))
    return dec


def normale_solaire(delt,phi,ome,beta,gam):
    #     (Eq 1.6.2 de DB 3rd edition)
    #
    #        beta : angle du capteur pr plan horizontal
    #        gam : azimuth capteur
    #        delt : declinaison en degre
    #        ome : angle horaire en degre
    #        phi : latitude en degr�es

    cosz = sind(delt)*sind(phi)*cosd(beta)-sind(delt)*cosd(phi)*sind(beta)*cosd(gam) \
           + cosd(delt)*cosd(phi)*cosd(beta)*cosd(ome) + cosd(delt)*sind(phi)*sind(beta)*cosd(ome)*cosd(gam) \
           + cosd(delt)*sind(gam)*sind(beta)*sind(ome)
    cosz = min(1,cosz)
    cosz = max(-1,cosz)
    the = arccos(cosz)*180.0/pi
    return the
def normale_solaire2(thez,gams,beta,gam):
    #     (Eq 1.6.2 de DB 3rd edition)
    #
    #        beta : angle du capteur pr plan horizontal
    #        gam : azimuth capteur
    #        delt : declinaison en degre
    #        ome : angle horaire en degre
    #        phi : latitude en degr�es

    cosz = cosd(thez)*cosd(beta)+sind(thez)*sind(beta)*cosd(gams-gam)
    cosz = min(1,cosz)
    cosz = max(-1,cosz)
    the = arccos(cosz)*180.0/pi
    return the
def  zenith_solaire(phi,delt,ome):
    # (1.6.5) de D.B 3rd �dition
    # angle de zenith du soleil en degres
    #       phi : latitude en degre nord positif, sud negatif
    #        del : declinaison en degre
    #        ome : angle horaire en degre
    cosz = cosd(phi)*cosd(delt)*cosd(ome) + sind(phi)*sind(delt)
    cosz = min(1,cosz)
    cosz = max(-1,cosz)
    thez = arccos(cosz)*180.0/pi
    return thez
def heure_angle(ome):
    sol_tn  = namedtuple('temps',['hr','min','jour'])
    if ome == 0:
        sol_tn.hr = 12.0
        sol_tn.min = 0.0
    else:
        heur = ome/15.0
        dh = sign(ome)*(floor(abs(ome/15.0))+0.5)-0.5
        dmin = (heur - dh)*60.0
        sol_tn.hr = 12.0+dh
        sol_tn.min = dmin
        if(sol_tn.min >= 60):
            sol_tn.min = sol_tn.min - 60
            sol_tn.hr = sol_tn.hr+1
    return sol_tn

def equation_temps(n):
    B = (n-1)*360.0/365.0
    E = 229.2*(0.000075+0.001868*cosd(B)- \
        0.032077*sind(B)-0.014615*cosd(2*B) - 0.04089*sind(2*B))
    return E

def heure_solaire(lon,Lst,del_h=0,st=0):
    # st : temps legal
    #   st_jour : jour de l'ann�e
    #   st_hr : heure , st_min : minute
    #   lon : longitude (lon.deg, lon.min )
    #   Lst : longitude du m�ridien de l'heure (-180 � 180, ex: -75 eastern time)
    #   del_h : difference entre l'heure legale et l'heure strandard
    #               Amerique    0 hiver , 1 ete
    #               Europe       1 hiver , 2 ete
    sol_t  = namedtuple('temps',['hr','min','jour'])
    if st == 0:  # calul du temps actuel
        st  = namedtuple('temps',['hr','min','jour'])
        t = localtime()
        st.hr = t.tm_hour
        st.min = t.tm_min
        jour = t.tm_mday
        n = t.tm_yday
        del_h = t.tm_isdst
    else:
        n = st.jour
    B = (n-1)*360.0/365.0
    E = 229.2*(0.000075+0.001868*cosd(B)- \
        0.032077*sind(B)-0.014615*cosd(2*B) - 0.04089*sind(2*B))
    dt = 4.0*(lon-Lst)+E
    dh = sign(dt)*floor(abs(dt/60.0))
    dmin = dt - dh*60.0
    sol_t.hr =   st.hr - del_h + dh
    sol_t.min =   st.min + dmin
    if(sol_t.min >= 60.0):
        sol_t.min = sol_t.min - 60
        sol_t.hr = sol_t.hr+1
    if(sol_t.min < 0.0):
        sol_t.min = sol_t.min + 60
        sol_t.hr = sol_t.hr-1
    if(sol_t.hr < 0.0):
        sol_t.hr = sol_t.hr + 24
        n = n -1
    if(sol_t.hr >= 24.0):
        sol_t.hr = sol_t.hr - 24
        n = n  + 1
    sol_t.jour = n
    return sol_t
def heure_legale(lon,Lst,del_h=0,sol_t=0):
    # sol_t : temps solaire
    #   solt_jour : jour de l'ann�e
    #   solt_hr : heure , st_min : minute
    #   lon : longitude (lon.deg, lon.min )
    #   Lst : longitude du m�ridien de l'heure (-180 � 180, ex: -75 eastern time)
    #   del_h : difference entre l'heure legale et l'heure strandard
    #               Amerique    0 hiver , 1 ete
    #               Europe       1 hiver , 2 ete
    st  = namedtuple('temps',['hr','min','jour'])
    if sol_t == 0:  # calul du temps actuel
        t = localtime()
        st.hr = t.tm_hour
        st.min = t.tm_min
        jour = t.tm_mday
        n = t.tm_yday
        st.jour = n
        del_h = t.tm_isdst
    else:
        n = sol_t.jour
        B = (n-1)*360.0/365.0
        E = 229.2*(0.000075+0.001868*cosd(B)- \
            0.032077*sind(B)-0.014615*cosd(2*B) - 0.04089*sind(2*B))
        dt = 4.0*(lon-Lst)+E
        dh = sign(dt)*floor(abs(dt/60.0))
        dmin = dt - dh*60.0
        st.hr =   sol_t.hr + del_h - dh
        st.min =   sol_t.min - dmin
        if(st.min >= 60.0):
            st.min = st.min - 60
            st.hr = st.hr + 1
        if(st.min < 0.0):
            st.min = st.min + 60
            st.hr = st.hr-1
        if(st.hr < 0.0):
            st.hr = st.hr + 24
            n = n -1
        if(st.hr >= 24.0):
            st.hr = st.hr - 24
            n = n  + 1
        st.jour = n
    return st


def fchart(X,Y):
    f = 1.029*Y-0.065*X-0.245*Y**2+0.0018*X**2+0.0215*Y**3
    f = min(f,1)
    f = max(f,0)
    return f

def fchart_air(X,Y):
    f = 1.04*Y-0.065*X-0.159*Y**2+0.00187*X**2 - 0.0095*Y**3
    f = min(f,1)
    f = max(f,0)
    return f

def duree_jour(n,phi):
    jour  = namedtuple('temps',['hr','min','jour'])
    delt  = decl_solaire(n)
    com = -tand(phi)*tand(delt)
    om = arccos(com)*180.0/pi
    lever = heure_angle(-om)
    lever.jour = n
    coucher = heure_angle(om)
    coucher.jour = n
    hr = abs(om/15.0)
    dh = floor(hr)
    dh = floor(2*hr)
    dmin = (2*hr - dh)*60
    jour.hr  = dh
    jour.min = dmin
    jour.jour = n
    return lever,coucher,jour
def duree_jour_mod(n,phi):
    jour  = namedtuple('temps',['hr','min','jour'])
    lever  = namedtuple('temps',['hr','min','jour'])
    coucher  = namedtuple('temps',['hr','min','jour'])
    aa = cosd(90+5.0/6.0)
    delt  = decl_solaire(n)
    com = (aa-sind(phi)*sind(delt))/(cosd(phi)*cosd(delt))
    om = arccos(com)*180.0/pi
    hr = abs(om/15.0)
    lever = heure_angle(-om)
    lever.jour = n
    coucher = heure_angle(om)
    coucher.jour = n
    dh = floor(2*hr)
    dmin = (2*hr - dh)*60
    jour.hr  = dh
    jour.min = dmin
    jour.jour = n
    return lever,coucher,jour

def irradiation_extraterrestre_normale(n):
    G = Gsc*(1+0.033*cosd(360.0*n/365.0))
    return G
def irradiation_extraterrestre(n,thez):
    Gn = Gsc*(1+0.033*cosd(360.0*n/365.0))
    G = Gn*cosd(thez)
    return G
def irradiation_extraterrestre_jour(n,phi):
    #
    #
    G2 = irradiation_extraterrestre_normale(n)
    delt  = decl_solaire(n)
    omes =  angle_sunset(phi,delt)
    Ho = 24.0*3600.0*G2/pi*(cosd(phi)*cosd(delt)*sind(omes)+pi*omes/180.0*sind(phi)*sind(delt))
    Ho = max(Ho,0)
    return Ho

def irradiation_extraterrestre_horaire(n,phi,ome1,ome2,cas = 1):
    # eq 1.10.4 de DB 3rd edition
    G2 = irradiation_extraterrestre_normale(n)
    delt  = decl_solaire(n,cas)
    thez1 = zenith_solaire(phi,delt,ome1)
    thez2 = zenith_solaire(phi,delt,ome2)
    ct1 = cosd(thez1)
    ct2 = cosd(thez2)
    if (ct1<0) and (ct2 < 0):
        Io = 0
    elif (cosd(thez1) < 0):
        # ome1 est avant le coucher du soleil
        # % on remplace ome1 par omes
        com = -tand(phi)*tand(delt)
        ome1 = -arccos(com)*180.0/pi
    elif cosd(thez2) < 0:
        # ome2 est apr�s le coucher du soleil
        # on remplace ome2 par omes
        com = -tand(phi)*tand(delt)
        ome2 = arccos(com)*180.0/pi
    Ion = 3600*G2
    Io = Ion*12.0/pi*(cosd(phi)*cosd(delt)*(sind(ome2)-sind(ome1))+pi*(ome2-ome1)/180.0*sind(phi)*sind(delt))
    Io = max(Io,0)
    return Io
def irradiation_extraterrestre_jour_moyen(nmois,phi):
    # nmois jan = 1, dec = 12
    nj1 = jjr[nmois-1]+1
    nj2 = jnm[nmois-1]
    ss = 0
    for j in range(0,nj2):
        jm = nj1+j
        ss = ss + irradiation_extraterrestre_jour(jm,phi)
    Hob = ss/(1.0*nj2)
    return Hob

def jour_mois_jour_annee(jour,mois):
    #
    # fonction qui transforme une date en jour et mois
    # en jour de 1 � 365
    # Les mois doivent s'�crire
    # 'jan';'fev';'mars';'avr';'mai';'juin';'juil';'aout';'sept';'oct
    # ';'nov';'dec'

    ind = -999;
    for i in range(0,12):
        if nom[i]==mois:
            ind = i
    if(ind == -999):
        print('on doit entrer un de ces noms de mois')
        print(nom)
        n = None
    else:
        n = jjr[ind] + jour
    return n

def jour_annee_jour_mois(n):
    #
    # fonction qui transforme un jour  de 1 � 365
    # � une date en jour du mois
    i = cherche_index(n,jjr)
    mois = nom[i]
    jour = n-jjr[i]
    return jour,mois

def Erbs_horaire(kt):
    #
    # Erbs correlation horaire (Eq 2.10.1 de DB 3rd edition)
    if kt <= 0.22:
        Idt = 1.0-0.09*kt
    elif kt<= 0.8:
        Idt = 0.9511-0.1604*kt+4.388*kt**2-16.638*kt**3+12.336*kt**4
    else:
        Idt = 0.165
    return Idt
def Erbs_jour(kt,ws):
    if ws <= 81.4:  # ws est en degres
        if kt <= 0.715:
            Hdt = 1-0.2727*kt+2.4495*kt**2-11.9514*kt**3+9.3879*kt**4
        else:
            Hdt = 0.143
    else:
        if kt <= 0.722:
            Hdt = 1+0.2832*kt-2.5557*kt**2+0.8448*kt**3
        else:
            Hdt = 0.175
    return Hdt

def Erbs_mois(kt,ws):
    if ws <= 81.4:  # ws est en degres
        if (kt <= 0.8) & (kt > 0.3):
            Hdt = 1.391-3.56*kt+4.189*kt**2-2.137*kt**3
        else:
            print('Hors limite')
            Hdt = -999
    else:
        if (kt <= 0.8) & (kt > 0.3):
            Hdt =  1.311 - 3.022*kt+3.427*kt**2-1.821*kt**3
        else:
            print('Hors limite')
            Hdt = -999
    return Hdt

def  Collares_total(ome,omes):
    #
    # eq 2.13.2 DB 3rd edition
    #
    num = cosd(ome)-cosd(omes)
    den = sind(omes)-pi*omes/180.0*cosd(omes)
    a = 0.409+0.5016*sind(omes-60.0)
    b = 0.6609-0.4767*sind(omes-60.0)
    r = pi/24.0*(a+b*cosd(ome))*num/den
    return r

def Collares_diffus(ome,omes):
    #
    # eq 2.13.4 DB 3rd edition
    #
    num = cosd(ome)-cosd(omes)
    den = sind(omes)-pi*omes/180.0*cosd(omes)
    r = pi/24.0*num/den
    return r

def  Calcul_pertes(T1c,beta,H,Y,uinf,Tinfc,Tskyc,Lair,e1,e2,Lv = 0,kv = 1,e3=-1):
    def fct2(T2c,T3c=-999):
    	# syst�me d'�quation non-lin�raire pour trouver
    	# la du vitrage
    	# � partir des bilans thermique
        if T3c == -999:
            T3c = T2c
        Dt = T1c-T2c
        T2k = T2c + 273
        T3k = T3c + 273
        Tairk = (T1k+T2k)/2
        # Calcul du coef de convection interne
        betas = 1/Tairk
        nui = air_prop('nu',Tairk)
        ali = air_prop('al',Tairk)
        ki = air_prop('k',Tairk)
        Ra = g*betas*abs(Dt)*Lair**3/(nui*ali)
        Ra_c = 1708.0/cosd(beta)
        ct = cosd(beta)
        f1 = max(0,1.0-1708.0/(Ra*ct))
        f2 = 1.0-1708*(sind(1.8*beta))**1.6/(Ra*ct)
        f3 = max(0,(Ra*ct/5830)**(1.0/3.0)-1.0)
        Nui = 1.0 + 1.44*f1*f2+f3
        hconvi = Nui*ki/Lair
        # Calcul du coefficient de radiation interne
        hradi = sig*(T1k+T2k)*(T1k**2+T2k**2)/(1.0/e1+1.0/e2-1.0)
        R1pp = 1.0/(hconvi+hradi)    # r�sistance �quivalente interne
        Ripp = R1pp + Lv/kv
        # Calcul du coef de convection externe
        Recr = 500000.0
        Textk = (T3k+Tinfk)/2.0
        nue = air_prop('nu',Textk)
        ale = air_prop('al',Textk)
        ke = air_prop('k',Textk)
        Pr = air_prop('Pr',Textk)
        Lc = 4*Ac/P
        #
        Re = uinf*Lc/nue
        if Re< Recr :
            Nu = 0.86*sqrt(Re)*Pr**(1.0/3.0)     # laminaire
        else:
            Nu = (0.037*Re**(4.0/5.0)-871)*Pr**(1.0/3.0)     # turbulent
        hconve = Nu*ke/Lc
        # Calcul du coefficient de radiation externe
        hrade = e3*sig*(T3k**2+Tskyk**2)*(T3k+Tskyk)
        Rcpp = 1/hconve
        Rrpp = 1/hrade
        #
        # fin du calcul des r�sistances thermiques
        # v�rification des bilans thermiques avec hypothese
        qppi = (T1c - T2c)/Ripp
        qconvi = hconvi*(T1c-T2c)
        qradi = hradi*(T1c-T2c)
        qppi2 = qconvi+qradi
        #
        # Bilan radiatif � la surface externe de la vitre
        #
        C1 = 1/Ripp +  1/Rcpp + 1/Rrpp
        T3n = (T1c/Ripp + Tinfc/Rcpp+Tskyc/Rrpp)/C1
        qconve = hconve*(T3n-Tinfc)
        qrade = hrade*(T3n-Tskyc)
        qppe = qconve+qrade
        T2n = T1c - qppe*R1pp
        Uh = qppe/(T1c-Tinfc)
        if Lv == 0:
            return T2n,Uh
        else:
            return T2n,T3n,Uh


    #     fonction calculant les pertes du haut d'un capteur � un vitrage
    #     caract�rictiques du capteur
    Tskyk = Tskyc+273
    T1k = T1c+273
    Tinfk = Tinfc + 273
    g = 9.8
    sig = 5.67e-8
    if e3 <0:
        e3 = e2
    Ac = H*Y
    P = 2.0*(H+Y)
    Lc = 4.0*Ac/P
    # valeurs initiales pour le calcul it�ratif
    T2i = T1c-2.0
    ok = False
    compt = 1
    delta = 1e-4
    itermax = 200
    err = 0
    T3i = T2i  - 1.0
    while (ok != True):
        if Lv == 0:
            T2n,Uh = fct2(T2i)
            if(abs(T2i-T2n)<delta):
                ok = True
            else:
                compt = compt+1
                T2i = T2n
                if compt > itermax:
                    err = 1
                    ok = True
            T2c = T2n
        else:
            T2n,T3n,Uh = fct2(T2i,T3i)
            if(abs(T2i-T2n)<delta) and (abs(T3i-T3n)<delta):
                ok = True
            else:
                compt = compt+1
                T2i = T2n
                T3i = T3n
                if compt > itermax:
                    err = 1
                    ok = True
            T2c = T2n
            T3c = T3n
    if Lv == 0:
        return T2c,Uh
    else:
        return T2c,T3c,Uh

def  Eval_pertes(T1c,T2c,beta,H,Y,uinf,Tinfc,Tskyc,Lair,e1,e2,Lv = 0,kv = 1,e3=-1,T3c = -999):

    Tskyk = Tskyc+273
    T1k = T1c+273
    Tinfk = Tinfc + 273
    g = 9.8
    sig = 5.67e-8
    if e3 <0:
        e3 = e2
    Ac = H*Y
    P = 2.0*(H+Y)
    Lc = 4.0*Ac/P
    if T3c == -999:
        T3c = T2c
    Dt = T1c-T2c
    T2k = T2c + 273
    T3k = T3c + 273
    Tairk = (T1k+T2k)/2
    # Calcul du coef de convection interne
    betas = 1/Tairk
    nui = air_prop('nu',Tairk)
    ali = air_prop('al',Tairk)
    ki = air_prop('k',Tairk)
    Ra = g*betas*abs(Dt)*Lair**3/(nui*ali)
    Ra_c = 1708.0/cosd(beta)
    ct = cosd(beta)
    f1 = max(0,1.0-1708.0/(Ra*ct))
    f2 = 1.0-1708*(sind(1.8*beta))**1.6/(Ra*ct)
    f3 = max(0,(Ra*ct/5830)**(1.0/3.0)-1.0)
    Nui = 1.0 + 1.44*f1*f2+f3
    hconvi = Nui*ki/Lair
    # Calcul du coefficient de radiation interne
    hradi = sig*(T1k+T2k)*(T1k**2+T2k**2)/(1.0/e1+1.0/e2-1.0)
    R1pp = 1.0/(hconvi+hradi)    # r�sistance �quivalente interne
    Ripp = R1pp + Lv/kv
    # Calcul du coef de convection externe
    Recr = 500000.0
    Textk = (T3k+Tinfk)/2.0
    nue = air_prop('nu',Textk)
    ale = air_prop('al',Textk)
    ke = air_prop('k',Textk)
    Pr = air_prop('Pr',Textk)
    Lc = 4*Ac/P
    #
    Re = uinf*Lc/nue
    if Re< Recr:
        Nu = 0.86*sqrt(Re)*Pr**(1.0/3.0)     # laminaire
    else:
        Nu = (0.037*Re**(4.0/5.0)-871)*Pr**(1.0/3.0)     # turbulent
    hconve = Nu*ke/Lc
    # Calcul du coefficient de radiation externe
    hrade = e3*sig*(T3k**2+Tskyk**2)*(T3k+Tskyk)
    Rcpp = 1/hconve
    Rrpp = 1/hrade
    #
    # fin du calcul des r�sistances thermiques
    # v�rification des bilans thermiques avec hypothese
    qppi = (T1c - T2c)/Ripp
    qconvi = hconvi*(T1c-T2c)
    qradi = hradi*(T1c-T2c)
    qppi2 = qconvi+qradi
    #
    # Bilan radiatif � la surface externe de la vitre
    #
    qconve = hconve*(T3c-Tinfc)
    qrade = hrade*(T3c-Tskyc)
    qppe = qconve+qrade
    return hconvi,hconve,hradi,hrade,qppi,qppe




def U_Klein(T_pc,T_ac,Slope,h,Emitt,emig,n):
    # Equation 6.4.9 pour les pertes du haut
    # T_pc : Temperatue de la plaque en Celsius
    # T_ac : Temperatue ambiante  en Celsius
    # Slope : angle beta
    # h : coefficient de convection ext�rieur
    # Emitt : emissivit� de la plaque
    # emig: emissivit�e du verre
    # n : nombre de vitre
    #
    T_p = T_pc + 273
    T_a = T_ac + 273
    f=(1.0+0.089*h-0.1166*h*Emitt)*(1.0+0.07866*n)
    e=0.430*(1.0-100.0/T_p)
    if(Slope<70.0):
        b = Slope
    else:
        b = 70.0
    c=520.0*(1-0.000051*b**2)
    x=(((T_p-T_a)/(n+f))**e)*c/T_p
    y=5.67e-8*(T_p+T_a)*(T_p**2+T_a**2.0)
    z=(Emitt+0.00591*n*h)**(-1.0)+(2*n+f-1+0.133*Emitt)/emig-n
    Ut=(n/x+1/h)**(-1.0)+y/z
    return Ut

def  Calcul_rendement(Tfi,Itw,Sw,N,ka,deltaa,D,Rpjoint,mp1,Ucote,Ubas,beta,H,Y,uinf,Tinfc,Tskyc,Lair,e1,e2,Lv = 0,kv = 1,e3=-1,flag_turb = 0):
    def fct2(Tpc,Tfo):
    	# syst�me d'�quation non-lin�raire pour trouver
    	# la temperature de la plaque
    	# � partir des bilans thermique
        if Lv == 0:
            T2,Uhaut =  Calcul_pertes(Tpc,beta,H,Y,uinf,Tinfc,Tskyc,Lair,e1,e2,e3= e3)

        else:
            T2,T3,Uhaut =  Calcul_pertes(Tpc,beta,H,Y,uinf,Tinfc,Tskyc,Lair,e1,e2,Lv,kv,e3)
        qhaut = Uhaut*(Tpc-Tinfc)
        # Calcul du Utotal
        UL = Uhaut+Ubas+Ucote
        # Calcul des coefficeint F
        m = sqrt(UL/(ka*deltaa))
        x = m*(W-D)/2
        # Calcul du rendement d'ailette F
        F = tanh(x)/x
        # Propri�t�es de l'eau
        Tf = (Tfi+Tfo)/2.0
        Tfk = Tf+273.0
        mu = eau_prop('muf',Tfk)
        Pr = eau_prop('Prf',Tfk)
        kf = eau_prop('kf',Tfk)
        Cp = eau_prop('Cpf',Tfk)
        Re = 4.0*mp1/(pi*D*mu)
        if Re<2300 and flag_turb ==0 :      # laminaire
            Nud = 3.66
        else:
            f = (0.790*log(Re)-1.64)**(-2)
            Nud = (f/8.0)*(Re-1000.0)*Pr/(1.0+12.7*sqrt(f/8.0)*(Pr**(2.0/3.0)-1.0))
            Nud = max(5,Nud)
        hf = Nud*kf/D
        Rpconv = 1.0/(hf*pi*D)
        den = W*(1.0/(UL*(D+(W-D)*F))+Rpjoint+Rpconv)
        # Calcul du rendement d'absorbeur F'
        Fp = 1.0/(UL*den)
        zz = UL*Ac*Fp/(mpt*Cp)
        # Calcul du facteur de r�cup�ration FR
        Fpp = 1/zz*(1-exp(-zz))
        Fr = Fp*Fpp
        UDT = UL*(Tfi-Tinfc)            # pertes en W/m2
        qupp = Fr*(Sw-UDT)
        qupp2 =(Sw-UL*(Tpc-Tinfc))
        qu = qupp*Ac
        rend = qupp/Itw
        # Calcul des nouvelles temp�ratures
        Tfo = Tfi + qu/(mpt*Cp)
        Tf = Tfi+qupp/(Fr*UL)*(1-Fpp)
        Tf2 = (Tfi+Tfo)/2
        Tpn = Tfi+qupp/(Fr*UL)*(1-Fr)
        return Tpn,Tfo,qupp,rend

    #     fonction calculant le rendement d'un capteur � partir de son modele theorique et la temperature d'entree
    W = H/real(N)
    Ac = H*Y
    mpt = mp1*N
    if ((Itw < 1e-3) | (mp1 < 1e-6)): # Si on n'a pas assez de soleil ou si le debit est nul, on arrete les calculs
        rend = 0
        qu = 0
        Tfo = Tinfc
        Tpn = Tfo
    else:
        ok = False
        compt = 1
        delta = 1e-4
        itermax = 200
        err = 0
        Tfo = Tfi + 2.0          # valeur initiale pour le processus iteratif
        Tpc = Tfi + 10.0        # valeur initiale pour le processus iteratif
        while (ok != True):
            Tpn,Tfo,qupp,rend = fct2(Tpc,Tfo)
            if(abs(Tpn-Tpc)<delta):
                ok = True
            else:
                compt = compt+1
                Tpc = Tpn
                if compt > itermax:
                    err = 1
                    ok = True
    return rend,qupp,Tpn,Tfo

def calcul_Rb(phi,n,ome,beta,gam,cas = 1):
#% On calcule Rb avec 1.8.1 (DB 3rd edition)
# l'heure comprend le lever ou le coucher du soleil, on prend la moyenne
# sur l'heure (2.14.6) (DB 3rd edition
# sol_t: heure solaire
    hr1  = namedtuple('temps',['hr','min','jour'])
    hr2  = namedtuple('temps',['hr','min','jour'])
    delt  = decl_solaire(n,cas)    # calcul de la declinaison solaire
    lever,coucher,jour = duree_jour(n,phi)
    the = normale_solaire(delt,phi,ome,beta,gam)
    thez = zenith_solaire(phi,delt,ome)
    Rb = cosd(the)/cosd(thez)
    sol_t = heure_angle(ome)
    if (sol_t.hr == lever.hr):
        # cas ou l'heure demand�e comprend le lever du soleil
        ome1 = angle_horaire(lever)
        hr2.hr = sol_t.hr+1
        hr2.min = 0
        ome2 = angle_horaire(hr2)
        a = (sind(delt)*sind(phi)*cosd(beta)-sind(delt)*cosd(phi)*sind(beta)*cosd(gam))*(ome2-ome1)*pi/180.0 \
           + (cosd(delt)*cosd(phi)*cosd(beta) + cosd(delt)*sind(phi)*sind(beta)*cosd(gam)) \
           *(sind(ome2)-sind(ome1))-cosd(delt)*sind(gam)*sind(beta)*(cosd(ome2)-cosd(ome1))
        b =  cosd(phi)*cosd(delt)*(sind(ome2)-sind(ome1)) + sind(phi)*sind(delt)*pi*(ome2-ome1)/180.0
        if b == 0:
            gg = 0
        Rb = a/b
    if (sol_t.hr == coucher.hr):
    # cas ou l'heure demand�e comprend le coucher du soleil
        ome2 = angle_horaire(coucher)
        hr1.hr = sol_t.hr
        hr1.min = 0;
        ome1 = angle_horaire(hr1)
        if(abs(ome2-ome1)<5):
            Rb = 0
        else:
            a = (sind(delt)*sind(phi)*cosd(beta)-sind(delt)*cosd(phi)*sind(beta)*cosd(gam))*(ome2-ome1)*pi/180 \
               + (cosd(delt)*cosd(phi)*cosd(beta) + cosd(delt)*sind(phi)*sind(beta)*cosd(gam)) \
               *(sind(ome2)-sind(ome1))-cosd(delt)*sind(gam)*sind(beta)*(cosd(ome2)-cosd(ome1))
            b =  cosd(phi)*cosd(delt)*(sind(ome2)-sind(ome1)) + sind(phi)*sind(delt)*pi*(ome2-ome1)/180.0
            Rb = a/b
    Rb = max(Rb,0)
    return Rb


def  calcul_Rb_mois(phi,n,beta,gam):

    # On calcule Rbb avec 2.19.3a (DB 3rd edition)
    delt  = decl_solaire(n)
    ome = angle_sunset(phi,delt)
    ome1 = arccosd(-tand(phi)*tand(delt))
    s = sign(cosd(gam))
    ome2 = arccosd(-tand(phi-s*beta)*tand(delt))
    omes = min(ome1,ome2)
#    omes = ome1
    num = sind(omes)*cosd(delt)*(cosd(phi)*cosd(beta)+sind(phi)*sind(beta)*cosd(gam))+ \
        sind(delt)*(sind(phi)*cosd(beta)-cosd(phi)*sind(beta)*cosd(gam))*pi/180*omes
    den = cosd(phi)*cosd(delt)*sind(ome)+pi/180*ome*sind(phi)*sind(delt)
    Rbm = num/den
    return Rbm


def modele_isotropique(I,Ib,Id,beta,Rb,rhog):
#
    Ibt = Ib*Rb
    Idt = Id*(1+cosd(beta))/2.0
    Irt = I*rhog*(1-cosd(beta))/2.0
    It =  Ibt+Idt+Irt
    return It,Ibt,Idt,Irt
def modele_hay_davis(I,Ib,Id,beta,Rb,rhog,Io):
    if Io > 0:
        Ai = Ib/Io
        Ai = min(Ai,1)
        Ibt = (Ib+Id*Ai)*Rb
        Idt = Id*(1-Ai)*(1+cosd(beta))/2.0
        Irt = I*rhog*(1-cosd(beta))/2.0
        It =  Ibt+Idt+Irt
    else:
        Ibt = 0
        Idt = 0
        Irt = 0
        It = 0
    return It,Ibt,Idt,Irt
def modele_hdkr(I,Ib,Id,beta,Rb,rhog,Io):
    if ((Io >0) & (I > 0)):
        Ai = Ib/Io
        Ai = min(Ai,1)
        f = sqrt(Ib/I)
        Ibt = (Ib+Id*Ai)*Rb;
        Idt = Id*(1-Ai)*(1+cosd(beta))/2.0*(1+f*sind(beta/2.0)**3)
        Irt = I*rhog*(1-cosd(beta))/2.0
        It =  Ibt+Idt+Irt
    else:
        Ibt = 0
        Idt = 0
        Irt = 0
        It = 0
    return It,Ibt,Idt,Irt


def modele_perez(I,Ib,Id,beta,Rb,rhog,Io,Ion,thez,the):
    #
    # I irradiation sur plan horizontal
    #% Io irradiation sur plan horizontal extraterrestre
    #beta angle du capteur
    # Rb : rapprt plan incline aur plan horizontal
    # rhos : albedo
    # thez : zennith sozire
    # the : angle entre normale capteur et radiation directe
    #
    # eq 2.16.14 DB 3rd edition
    if ((Io >0) & (I > 0)):
        a = max(0,cosd(the))
        b = max(cosd(85),cosd(thez))
        epv = array([1.065,1.230,1.500,1.950,2.800,4.500,6.200])
        P11 =array([-0.008,0.13,0.33,0.568,0.873,1.132,1.060,0.678])
        P12 =array([0.588,0.683,0.487,0.187,-0.392,-1.237,-1.6,-0.327])
        P13 =array([-0.062,-0.151,-0.221,-0.295,-0.362,-0.412,-0.359,-0.250])
        P21 =array([-0.06,-0.019,0.055,0.109,0.226,0.288,0.264,0.156])
        P22 =array([0.072,0.066,-0.064,-0.152,-0.462,-0.823,-1.127,-1.377])
        P23 =array([-0.022,-0.029,-0.026,0.014,0.001,0.056,0.131,0.251])
        m = 1.0/b
        Ibn = m*Ib
        f = sqrt(Ib/I)
        Ai = Ib/Io
        c1 = 5.535e-6
        if Id > 0:
            ep =  ((Id+Ibn)/Id+c1*thez**3)/(1+c1*thez**3)
            i = cherche_index(ep,epv)
        else:
            i = length(P11)-1
        f11 = P11[i+1]
        f12 = P12[i+1]
        f13 = P13[i+1]
        f21 = P21[i+1]
        f22 = P22[i+1]
        f23 = P23[i+1]
        delta = Id/Io
        delta = m*Id/Ion
        F1 = max(0,f11+f12*delta+pi*thez/180.0*f13)
        F2 = f21+f22*delta+pi*thez/180.0*f23
        Ibt = Ib*Rb
        Idt = Id*((1-F1)*(1+cosd(beta))/2+F1*a/b)+ \
        Id*F2*sind(beta)
        Idt = max(Idt,0)
        Irt = I*rhog*(1-cosd(beta))/2.0
        It = Ibt + Idt + Irt
    else:
        Ibt = 0
        Idt = 0
        Irt = 0
        It = 0
    return It,Ibt,Idt,Irt


def  snell(th1,nv,na=1):
    # calcul de l'angle de r�flexion donn�e par la loi de snell
    # Si on ne donne que 2  arguments, on suppose que  la radiaton incidente est
    # dans l'air ou le vie n = 1
    sth2 = na*sind(th1)/nv
    th2 = arcsind(sth2)
    return th2

def r_coef(th1,th2,n2=1.526,n1=1):
    #
    # fnction calcule dles coefficients de Fresnel
    # ecrit par Louis Lamarche 11-3-10
    if th1 == 0:
        r = ((n1-n2)/(n1+n2))**2
        rpe = r
        rpa = r
    else:
        th12 = th1+th2
        th2m1 = th2-th1
        rpe = sind(th2m1)**2/sind(th12)**2
        rpa = tand(th2m1)**2/tand(th12)**2
        r = (rpe+rpa)/2
    return rpe,rpa,r

def Calcul_coef_vitre(rpe,rpa,tau_al,N=1):
    #
    # fonction calcule les coefficients de absrortion pour N plaques identiques
    # ecrit par Louis Lamarche 11-3-10
    # voir DB 5.3.1 SH 18.7
    tau_pe1 = tau_al*(1-rpe)/(1+rpe)*((1-rpe**2)/(1-(rpe*tau_al)**2))
    tau_pa1 = tau_al*(1-rpa)/(1+rpa)*((1-rpa**2)/(1-(rpa*tau_al)**2))
    rho_pe1 = rpe*(1+tau_al*tau_pe1)
    rho_pa1 = rpa*(1+tau_al*tau_pa1)
    al_pe1 = (1-tau_al)*(1-rpe)/(1-rpe*tau_al)
    al_pa1 = (1-tau_al)*(1-rpa)/(1-rpa*tau_al)
    al_pa = al_pa1
    al_pe = al_pe1
    tau_pa = tau_pa1
    tau_pe = tau_pe1
    rho_pa = rho_pa1
    rho_pe = rho_pe1
    if N > 1:
        for i in range(2,N+1):
            tau_pe = tau_pe1*tau_pe/(1-rho_pe1*rho_pe)
            tau_pa = tau_pa1*tau_pa/(1-rho_pa1*rho_pa)
            rho_pe = rho_pe1 + rho_pe*tau_pe1**2/(1-rho_pe1*rho_pe)
            rho_pa = rho_pa1 + rho_pa*tau_pa1**2/(1-rho_pa1*rho_pa)
            al_pe = 1 - (rho_pe+tau_pe)
            al_pa = 1 - (rho_pa+tau_pa)
    alp = 0.5*(al_pa+al_pe)
    tau = 0.5*(tau_pa+tau_pe)
    rho = 0.5*(rho_pa+rho_pe)
    return tau,rho,alp


def  Calcul_tau_al(the1,alpn,KL,n2=1.526,n1=1,N=1):
    # calcul de (tau_alpha)
    # the1 angle incidente
    # alpn, coeficient d,absorbeur faible longueur d'onde
    # n2 : indice de r�fraction de la vitre ( d�faut 1.53)
    # n1 : indice de r�fraction de l'air ( d�faut 1)
    the2 = snell(the1,n2,n1)
    rpe,rpa,r = r_coef(the1,the2,n2,n1)
    tau_pe = (1-rpe)/(1+rpe)
    tau_pa = (1-rpa)/(1+rpa)
    tau_r = 0.5*(tau_pa+tau_pe)
    tau_a = exp(-KL/cosd(the2))
    tau,rho,alpv = Calcul_coef_vitre(rpe,rpa,tau_a,N)
    alpc = alpn*alp_alpn(the1);
    tau_al = tau*alpc/(1-(1-alpc)*rho);
    return tau_al

def  angle_diffus(beta):
    # relation  5.4.2 DB 3RD edition
    y = 59.7 - 0.1388*beta+0.001497*beta**2
    return y

def angle_reflechi(beta):
    # relation  5.4.1 DB 3RD edition
    y = 90.0 - 0.5788*beta + 0.002693*beta**2

    return y

def pv_fct(x,param):

    k = 1.381e-23
    Tref = 25.0 + 273.15
    Isc = param[0]
    Voc = param[1]
    Im = param[2]
    Vm = param[3]
    muV = param[4]
    muI = param[5]
    y = [0,0,0,0,0]
    IL = x[0]
    Io = x[1]
    a = x[2]
    Rsh = x[3]
    Rs = x[4]
    Idsc = Io*(exp(Isc*Rs/a) - 1.0)
    Idoc =Io*(exp(Voc/a) - 1.0)
    exm = exp((Vm+Im*Rs)/a)
    Idm =Io*(exm - 1.0)
    # short-circuit
    y[0] = Isc - IL + Idsc + Isc*Rs/Rsh
    # open-circuit ref
    y[1] =  -IL + Idoc + Voc/Rsh
    # max Im
    y[2] = Im - IL + Idm + (Vm+Im*Rs)/Rsh
    # max Im der
    y[3] = Im - Vm*(Io*exm/a + 1.0/Rsh)/(1.0+Io*exm*Rs/a+Rs/Rsh)
    T2 = Tref + 2
    Voc2 = (T2-Tref)*muV + Voc
    a2 = a*T2/Tref
    IL2 = IL + muI*(T2-Tref)
    C = 0.0002677
    Eg =  1.796e-19
    Eg2 = Eg*(1-C*(T2-Tref))
    Io2 = Io*(T2/Tref)**3*exp(Eg2/(k*Tref) - Eg2/(k*T2))
    # open-circuit T2
    Idoc2 =Io2*(exp(Voc2/a2) - 1.0)
    y[4] =  -IL2 + Idoc2 + Voc2/Rsh
    return y




def pv_module(xi,*param):
    sol = root(pv_fct,xi,args = param,method='lm')
    xf = sol.x
    xf = append(xf,param[0][5])
    return xf



def I_pvV(x,V,G = 1000.0,T = 25.0 + 273.15):

    IL = x[0]
    Io = x[1]
    a = x[2]
    Rsh = x[3]
    Rs = x[4]
    muI = x[5]
    k = 1.381e-23
    Tref = 25.0 + 273.15
    a = a*T/Tref
    C = 0.0002677
    Eg =  1.794e-19
    Eg2 = Eg*(1-C*(T-Tref))
    Rsh = Rsh*1000/G
    Io = Io*(T/Tref)**3*exp(Eg/(k*Tref) - Eg2/(k*T))
    IL = G/1000.0*(IL + muI*(T-Tref))

    def I_pv_fct(I):
        Id = Io*(exp((V+I*Rs)/a) - 1)
        In = IL - Id - (V+I*Rs)/Rsh
        y = In - I
        return y
    try:
        Im = newton(I_pv_fct,1)
    except RuntimeError:
        Im = 0
    g = I_pv_fct(Im)
    Im = max(Im,0)
    return Im

def G_pvI(x,I,V = 8.0,T = 25.0 + 273.15):

    ILn = x[0]
    Io = x[1]
    a = x[2]
    Rshn = x[3]
    Rs = x[4]
    muI = x[5]
    k = 1.381e-23
    Tref = 25.0 + 273.15
    a = a*T/Tref
    C = 0.0002677
    Eg =  1.794e-19
    Eg2 = Eg*(1-C*(T-Tref))
    Io = Io*(T/Tref)**3*exp(Eg/(k*Tref) - Eg2/(k*T))


    def I_pv_fctG(G):
        Rsh = Rshn*1000/G
        Id = Io*(exp((V+I*Rs)/a) - 1)
        IL = I + Id + (V+I*Rs)/Rsh
        Gn = IL*1000.0/(ILn + muI*(T-Tref))
        y = Gn - G
        return y
    try:
        Gm = newton(I_pv_fctG,800)
    except RuntimeError:
        Gm = 0

    return Gm

def Vocr(x,Voci,G = 1000.0,T = 25.0 + 273.15):

    IL = x[0]
    Io = x[1]
    a = x[2]
    Rsh = x[3]
    Rs = x[4]
    muI = x[5]
    k = 1.381e-23
    Tref = 25.0 + 273.15
    a = a*T/Tref
    C = 0.0002677
    Eg =  1.794e-19
    Eg2 = Eg*(1-C*(T-Tref))
    Rsh = Rsh*1000/G
    Io = Io*(T/Tref)**3*exp(Eg/(k*Tref) - Eg2/(k*T))
    IL = G/1000.0*(IL + muI*(T-Tref))

    def Voc_fct(V):
        Id = Io*(exp(V/a) - 1)
        y = IL - Id - V/Rsh
        return y
    try:
        Vv = newton(Voc_fct,Voci)
    except RuntimeError:
        Vv = 0
    Vm = max(Vv,0)
    return Vm

def I_pvR(x,R,G = 1000.0,T = 25.0 + 273.15):

    IL = x[0]
    Io = x[1]
    a = x[2]
    Rsh = x[3]
    Rs = x[4]
    muI = x[5]
    k = 1.381e-23
    Tref = 25.0 + 273.15
    Rsh = Rsh*1000/G
    a = a*T/Tref
    C = 0.0002677
    Eg =  1.794e-19
    Eg2 = Eg*(1-C*(T-Tref))
    Io = Io*(T/Tref)**3*exp(Eg/(k*Tref) - Eg2/(k*T))
    IL = G/1000.0*(IL + muI*(T-Tref))

    def I_pv_fct(I):
        V = R*I
        Id = Io*(exp((V+I*Rs)/a) - 1)
        In = IL - Id - (V+I*Rs)/Rsh
        y = In - I
        return y

#    Im = newton(I_pv_fct,6)
    Im = brentq(I_pv_fct,0,IL)
    Im = max(Im,0)
    return Im


def IV_pv_peak(x,G= 1000.0,T = 25.0 + 273.15,Vi = 35):

    IL = x[0]
    Io = x[1]
    a = x[2]
    Rsh = x[3]
    Rs = x[4]
    muI = x[5]
    k = 1.381e-23
    Tref = 25.0 + 273.15
    a = a*T/Tref
    C = 0.0002677
    Eg =  1.794e-19
    Eg2 = Eg*(1-C*(T-Tref))
    Rsh = Rsh*1000/G
    Io = Io*(T/Tref)**3*exp(Eg/(k*Tref) - Eg2/(k*T))
    IL = G/1000.0*(IL + muI*(T-Tref))

    def Peak_pv_fct(xin):
        y = zeros(2)
        I = xin[0]
        V = xin[1]
        Id = Io*(exp((V+I*Rs)/a) - 1)
        In = IL - Id - (V+I*Rs)/Rsh
        y[0] = In - I
        exm = exp((V+I*Rs)/a)
        y[1] = I*(1+Io*exm*Rs/a+Rs/Rsh) - V*(Io*exm/a + 1/Rsh)
        return y

    y = fsolve(Peak_pv_fct,[IL,Vi])
    return y

def  cherche_index(xi,x):
    """ cherche l'index o� x(i) <= xi < x(i+1)"""
    err = 0
    ok = 1
    i = 0
    if  (xi <= x[0] ):
        i = 0
    elif (xi > x[len(x)-1]):
        i = len(x)-1
    else:
        while ok:
            if (xi>=x[i]) & (xi<=x[i+1]):
                ok = 0
            else:
                i=i+1
                if i >= len(x):
                    ok =0
                    err =-1
                    i = nan
    return i

def f12_integrand(y,z,m,alp):
    So = sqrt(y**2 + z**2 - 2*y*z*cosd(alp))
    f = y*z*arctan(m/So)/So**3
    return f

def F12(m,p,n,alp):
    F =  nquad(f12_integrand,[[0, p],[0, n]], args=(m,alp))
    F12 = sind(alp)*sind(alp)*F[0]/(p*pi)
    return F12

def Calcul_kta_nouv(beta,b0,b1):
    Slope_Collector = beta
    thT = arange(0.0,100.0,10.0)
    thL = arange(0.0,100.0,10.0)
    nx = len(thT)
    ny = len(thL)
    IncidentRadiation_Total=0.
    IAM_Total=0.
    for i in range(0,360):
        for j in range(0,90):
            Zenith_Angle = j+0.5
            SolarAzimuth_Angle = i + 0.5
            Incidence_Angle=arccosd(cosd(Zenith_Angle)*cosd(Slope_Collector)+sind(Zenith_Angle)*sind(Slope_Collector)*cosd(SolarAzimuth_Angle))
            #Calculate surface area of piece of sky dome for this incident radiation
            SurfArea_SkySection=(2.*pi*(1.-cosd(j+1.0))-2.*pi*(1.-cosd(j*1.0)))/360.
            Intensity=1.
            IncidentRadiation=Intensity*SurfArea_SkySection*cosd(Incidence_Angle)
            if ((Incidence_Angle>0.) and (Incidence_Angle<90.)) :
                if Incidence_Angle < 60:
                    s_beam = 1.0/cosd(Incidence_Angle) - 1
                    IAM_Diffuse_Sky = 1.0 - b0*s_beam - b1*s_beam**2
                else:
                    s_beam = 1.0
                    IAM_Diffuse_Sky = 1.0 - b0*s_beam - b1*s_beam**2
                    IAM_Diffuse_Sky=IAM_Diffuse_Sky-IAM_Diffuse_Sky*(Incidence_Angle-60.)/30.
                IncidentRadiation_Total=IncidentRadiation_Total+IncidentRadiation
                IAM_Total=IAM_Total+IncidentRadiation*IAM_Diffuse_Sky
    IAM_Diffuse_Sky=IAM_Total/IncidentRadiation_Total
    if (Slope_Collector==0.) :
        IAM_Diffuse_Ground=0.0
    else:
        IncidentRadiation_Total=0.
        IAM_Total=0
        J_Count=int(Slope_Collector-0.5)+1
        for i in range(0,360):
            for j in range(0,J_Count):
                Angle_FromHorizon=-(j+0.5)*Slope_Collector/(1.0*J_Count)
                Angle_FromSouth=i + 0.5
                Incidence_Angle=arccosd(sind(Angle_FromHorizon)*cosd(Slope_Collector)+cosd(Angle_FromHorizon)*sind(Slope_Collector)*cosd(Angle_FromSouth))
                SurfArea_GroundProjectedonDome=(2.*pi*(1.-sind(j*1.0*(Slope_Collector/(1.0*J_Count))))-2.*pi*(1.-sind((j+1.0)*Slope_Collector/(1.0*J_Count))))/360.0
                Intensity=1.
                IncidentRadiation=Intensity*SurfArea_GroundProjectedonDome*cosd(Incidence_Angle)
                if ((Incidence_Angle>0.) and (Incidence_Angle<90.)):
                    if Incidence_Angle < 60:
                        s_beam = 1.0/cosd(Incidence_Angle) - 1
                        IAM_Diffuse_Ground = 1.0 - b0*s_beam - b1*s_beam**2
                    else:
                        s_beam = 1.0
                        IAM_Diffuse_Ground = 1.0 - b0*s_beam - b1*s_beam**2
                        IAM_Diffuse_Ground=IAM_Diffuse_Ground-IAM_Diffuse_Ground*(Incidence_Angle-60.)/30.
                    IncidentRadiation_Total=IncidentRadiation_Total+IncidentRadiation
                    IAM_Total=IAM_Total+IncidentRadiation*IAM_Diffuse_Ground
        IAM_Diffuse_Ground=IAM_Total/IncidentRadiation_Total
    return IAM_Diffuse_Sky,IAM_Diffuse_Ground