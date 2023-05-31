# Imports
import numpy as np
from random import randrange
# Specs
width = 15
lenght = 15
grille=50
range_scan=50

# Fonctions utiles
def scal(a,b):
    """ Produit scalaire des vecteurs a et b"""
    return (a[0]*b[0]+a[1]*b[1])
def distance (a,b):
    """Renvoie la distance entre deux points"""
    return np.sqrt((b[0]-a[0])**2+(b[1]-a[1])**2)
def find_min(a,L):
    if len(L)==0:
        return None
    elif len(L)==1:
        return distance(L[0],a)
    else:
        mini=distance(L[0],a)
        indice=0
        for k in range(1, len(L)):
            if distance(a,k)<mini:
                mini=distance(a,k)
                indice=k
        return L[indice]
# ef order(L):
#    """Ordonne la liste des points pour placer les points par proximité (algo glouton)"""
#    res=[]
#    for i in range(len(L)):
#        for j in range(len(L)-1):

testmap= [[1+0.1*k,1] for k in range (100)]

def visible_2_points(case_depart,case_arrivee,dens,seuil):
    res = np.zeros((100, 100))   
    if case_depart[0] != case_arrivee[0]:
        pente = (case_arrivee[1] - case_depart[1]) / (case_arrivee[0] - case_depart[0])
        ordonnee_origine = case_depart[1] - pente * case_depart[0]  
        for ligne in range(case_depart[0], case_arrivee[0] + 1):
            colonne = int(pente * ligne + ordonnee_origine)
            res[ligne, colonne] = 1
    else:
        ligne = case_depart[0]
        res[ligne, case_depart[1]:case_arrivee[1] + 1] = 1
    # Affichage de la grille résultante
    print(res)


def density(map, grille,range_scan):
    step= range_scan/grille
    res=np.array([[0]*grille for i in range(grille)])
    for point in map:
        print(point[0]//step)
        res[int(point[0]//step),int(point[1]//step)]+=1
    return res

def visible(map, point,grille, range_scan,seuil,nombre_points):
    sources=[[randrange(int(range_scan)),randrange(int(range_scan))] for i in range(nombre_points)]
    dsty= density(map,grille,range_scan)

    