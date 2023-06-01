# Imports
import numpy as np
from random import randrange
# Specs
width = 12
lenght = 12
grille=50
range_scan=50
step=grille/range_scan

# Fonctions utiles

def visible_2_points(case_depart,case_arrivee,dens,seuil=1):
    case_depart=np.array(case_depart).astype(int)
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
    step= range_scan/grille[0]
    res=np.zeros(grille)
    for point in map:
        res[int(point[0]//step),int(point[1]//step)]+=1
    return (2*res//seuil).astype(bool)

def visible(dsty, point,step,seuil,nombre_points):
    """map: carte des points (coordonnées)
    point: coordonnées du point dont on veut savoir la visibilité
    grille: liste du nombre de point par côté de la grille
    range_scan : distance de la grille
    seuil: seuil de densité suffisant pour considérer que c'est un mur
    nombre_points: nombre tiré au hasard d'observateurs"""
    sources=[[randrange(int(range_scan)),randrange(int(range_scan))] for i in range(nombre_points)]
    score=0
    for elt in sources:
        if not visible_2_points([int(point[0])//step,int(point[1]//step)],elt,dsty,seuil):
            score+=1
    return score/nombre_points

def score_cachette(density, point,step,seuil,nombre_points,taille):
    # if acccessible :
    a,b=density.shape
    crop = density[max(0,point[0]-taille):min(a,point[0]+taille),max(0,point[1]-taille):min(b,point[1]+taille)]
    c,d=crop.shape
    if crop.all() == np.zeros([c,d]).all():
        return visible(density,point,step,seuil,nombre_points)
    else:
        return 0

def min_score(t,origine,tau):
    return origine*np.exp(-t/tau)

def simplify(grid,factor,centre, radius):
    a,b=grid.shape
    res=[]
    for i in range(max(0,centre[0]-radius),min(b,centre[0]+radius),factor):
        for j in range(max(0,centre[1]-radius),min(b,centre[1]+radius),factor):
            res.append((i,j))
    return res

def decidemove(time, origin, tau ,position, nombre_points, densite, step, scanning_range, score, taille, factor=1, seuil=1):
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
                    elt[0]=score_cachette(densite, point, step, seuil, nombre_points,taille)
                    dejavu=True
                    break
            if not dejavu:
                score.append([score_cachette(densite, point, step , seuil, nombre_points,taille)]+list(point))
        score.sort()
        return score[-1][1:]
        # Renvoyer chemin vers le score[-1][1:]
if __name__== '__main__':
    testmap= [[1+0.1*k,1] for k in range (100)]
    #print(decidemove(testmap,0,1,100,np.array([35,10]),10,densite=density(testmap,grille=grille,range_scan=range_scan, seuil=1,),grille=grille,scanning_range=10,score=[],taille=2,factor=1,seuil=1))
    print(visible(dsty=density(testmap,[grille,grille],grille), point=[2,2],step=step,seuil=1,nombre_points=10))
    print(score_cachette(density=density(testmap,[grille,grille],grille),point=[2,2],step=step,seuil=1,nombre_points=1000,taille=2))
    print(decidemove(time=0,origin=1,tau=100, position=[20,20], nombre_points=100, densite=density(testmap,[grille,grille],grille),step=step,scanning_range=20,score=[],taille=2))