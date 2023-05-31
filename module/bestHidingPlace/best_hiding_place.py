# Imports
import numpy as np
from random import randrange
# Specs
width = 12
lenght = 12
grille=50
range_scan=50

# Fonctions utiles
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

testmap= [[1+0.1*k,1] for k in range (100)]
def affichaget(L):
    res=''
    for i in range(len(L)):
        for j in range(len(L[0])):
            res=res+str(L[i,j])+' ; '
        res+='\n'
    print(res)

def visible_2_points(case_depart,case_arrivee,dens,seuil=1):
    if case_depart[0] != case_arrivee[0]:
        pente = (case_arrivee[1] - case_depart[1]) / (case_arrivee[0] - case_depart[0])
        ordonnee_origine = case_depart[1] - pente * case_depart[0]  
        for ligne in range(case_depart[0], case_arrivee[0] + 1):
            colonne = int(pente * ligne + ordonnee_origine)
            if dens[ligne,colonne]>=seuil:
                return False
    else:
        ligne = int(case_depart[0])
        for cl in range(int(case_depart[1]), int(case_arrivee[1]) + 1):
            if dens[ligne, cl] >= seuil:
                return False
    return True
# affichaget(visible_2_points([0,1],[5,7], [[0 for i in range(10)] for j in range(10)]))
def density(map, grille,range_scan,seuil=1):
    step= range_scan/grille
    res=np.array([[0]*grille for i in range(grille)])
    for point in map:
        print(point[0]//step)
        res[int(point[0]//step),int(point[1]//step)]+=1
    return (2*res//seuil).astype(bool)

def visible(map, point,grille, range_scan,seuil,nombre_points):
    """map: carte des points (coordonnées)
    point: coordonnées du point dont on veut savoir la visibilité
    grille: nombre de points sur un axe de la grille
    range_scan : distance de la grille
    seuil: seuil de densité suffisant pour considérer que c'est un mur
    nombre_points: nombre tiré au hasard d'observateurs"""
    sources=[[randrange(int(range_scan)),randrange(int(range_scan))] for i in range(nombre_points)]
    step= range_scan/grille
    dsty= density(map,grille,range_scan)
    score=0
    for elt in sources:
        if not visible_2_points(point//step,elt,dsty,seuil):
            score+=1
    return score/nombre_points
def score_cachette(map, point,grille, range_scan,seuil,nombre_points,taille):
    # if acccessible : 
    for pt in map:
        if (pt[0]-point[0])**2+(pt[1]-point[1])**2<taille:
            return 0
    else:
        return visible(map, point,grille, range_scan,seuil,nombre_points)
def min_score(t,origine,tau):
    return origine*np.exp(-t/tau)
def simplify(grid,factor,centre, radius):
    a,b=grid.shape
    res=[]
    for i in range(max(0,centre[0]-radius),min(b,centre[0]+radius),factor):
        for j in range(max(0,centre[1]-radius),min(b,centre[1]+radius),factor):
            res.append((i,j))
    return res
print(simplify(np.zeros([10,10]),2,(4,2),6))

def decidemove(map, time, origin, tau ,position, nombre_points, seuil, densite, grille, scanning_range, score, factor=1, best_score=0):
    if best_score > min_score(time, origin, tau):
        # Chemin vers best_score
        print("Moving to best found place :" + score[0])
    else:
        for point in simplify(densite, factor, position, scanning_range):
            dejavu=False
            for elt in score:
                if elt[1:] == point:
                    elt[0]=score_cachette(map, point, grille, range_scan, seuil, nombre_points)
                    dejavu=True
                    break
            if not dejavu:
                score.append([score_cachette(map, point, grille, range_scan, seuil, nombre_points)]+point)
        score.sort()
        # Renvoyer chemin vers le score[-1][1:]
