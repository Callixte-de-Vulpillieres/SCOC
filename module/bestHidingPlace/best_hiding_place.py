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

def density(map,grille,range_scan,seuil=1):
    step= range_scan/grille
    res=np.zeros(grille)
    for point in map:
        print(point[0]//step)
        res[int(point[0]//step),int(point[1]//step)]+=1
    return (2*res//seuil).astype(bool)

def visible(dsty, point,grille, range_scan,seuil,nombre_points):
    """map: carte des points (coordonnées)
    point: coordonnées du point dont on veut savoir la visibilité
    grille: nombre de points sur un axe de la grille
    range_scan : distance de la grille
    seuil: seuil de densité suffisant pour considérer que c'est un mur
    nombre_points: nombre tiré au hasard d'observateurs"""
    sources=[[randrange(int(range_scan)),randrange(int(range_scan))] for i in range(nombre_points)]
    step= range_scan/grille
    score=0
    for elt in sources:
        print("step:", step)
        if not visible_2_points([int(point[0])//step,int(point[1]//step)],elt,dsty,seuil):
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

def decidemove(map, time, origin, tau ,position, nombre_points, densite, grille, scanning_range, score, taille, factor=1, seuil=1):
    """
    map: liste des positions des points
    time: temps actuel (sera fourni par time.time)
    origin: ordonnée à l'origine de la loi de proba
    tau: temps de décroissance
    position: [x,y] position du robot
    nombre_points: nombre tiré au hasard d'observateurs pour le lancer de rayons
    densité: matrice des densités (espace discrétisé)
    grille: taille de la grille (carrée)
    scanning_range: distance à laquelle on scanne avec le robot (scan carré)
    score: liste des score ([[score, x, y]])
    taille: taille du robot (circulaire)
    factor: facteur de diminution dans le scan (ex: on test une cachette tous les 3 points dans la grille)
    seuil: Densité de points seuil à partir de laquelle on considère qu'il y a un mur, inutile dans l'implémentation True False retenue
    """
    try:
        best_score=score[-1][0]
    except:
        best_score=0
    if best_score > min_score(time, origin, tau):
        # Chemin vers best_score
        print("Moving to best found place :" + score[0])
    else:
        for point in simplify(densite, factor, position, scanning_range):
            dejavu=False
            for elt in score:
                if elt[1:] == point:
                    elt[0]=score_cachette(map, point, grille, range_scan, seuil, nombre_points,taille)
                    dejavu=True
                    break
            if not dejavu:
                score.append([score_cachette(map, point, grille, range_scan, seuil, nombre_points,taille)]+point)
        score.sort()
        # Renvoyer chemin vers le score[-1][1:]
if __name__== '__main__':
    testmap= [[1+0.1*k,1] for k in range (100)]
    #print(decidemove(testmap,0,1,100,np.array([35,10]),10,densite=density(testmap,grille=grille,range_scan=range_scan, seuil=1,),grille=grille,scanning_range=10,score=[],taille=2,factor=1,seuil=1))
    print(visible(map=density(testmap,[grille,grille],grille), point=[2,2],grille=grille,range_scan=10,seuil=1,nombre_points=10))