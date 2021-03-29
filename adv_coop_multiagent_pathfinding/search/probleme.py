# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import functools
import time
import gc





def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 



    
###############################################################################

class Probleme(object):
    """ On definit un probleme comme étant: 
        - un état initial
        - un état but
        - une heuristique
        """
        
    def __init__(self,init,but,heuristique):
        self.init=init
        self.but=but
        self.heuristique=heuristique
        
    @abstractmethod
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        pass
        
    @abstractmethod    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            """
        pass
        
    @abstractmethod
    def successeurs(self,etat):
        """ retourne une liste avec les successeurs possibles
            """
        pass
        
    @abstractmethod
    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        pass
    
    



###############################################################################

@functools.total_ordering # to provide comparison of nodes
class Noeud:
    def __init__(self, etat, g, pere=None):
        self.etat = etat
        self.g = g
        self.pere = pere
        
    def __str__(self):
        #return np.array_str(self.etat) + "valeur=" + str(self.g)
        return str(self.etat) + " valeur=" + str(self.g)
        
    def __eq__(self, other):
        return str(self) == str(other)
        
    def __lt__(self, other):
        return str(self) < str(other)
        
    def expand(self,p):
        """ étend un noeud avec ces fils
            pour un probleme de taquin p donné
            """
        nouveaux_fils = [Noeud(s,self.g+p.cost(self.etat,s),self) for s in p.successeurs(self.etat)]
        return nouveaux_fils
        
    def expandNext(self,p,k):
        """ étend un noeud unique, le k-ième fils du noeud n
            ou liste vide si plus de noeud à étendre
            """
        nouveaux_fils = self.expand(p)
        if len(nouveaux_fils)<k: 
            return []
        else: 
            return self.expand(p)[k-1]
            
    def trace(self,p):
        """ affiche tous les ancetres du noeud
            """
        n = self
        c=0    
        while n!=None :
            print (n)
            n = n.pere
            c+=1
        print ("Nombre d'étapes de la solution:", c-1)
        return            
        
        
###############################################################################
# A*
###############################################################################

def astar(p,verbose=False,stepwise=False):
    """
    application de l'algorithme a-star
    sur un probleme donné
        """
        
    startTime = time.time()

    nodeInit = Noeud(p.init,0,None)
    frontiere = [(nodeInit.g+p.h_value(nodeInit.etat,p.but),nodeInit)] 

    reserve = {} # nodes already visited        
    bestNoeud = nodeInit
    
    while frontiere != [] and not p.estBut(bestNoeud.etat):              
        (min_f,bestNoeud) = heapq.heappop(frontiere)
           
    # VERSION 1 --- On suppose qu'un noeud en réserve n'est jamais ré-étendu
    # Hypothèse de consistence de l'heuristique
        
        if p.immatriculation(bestNoeud.etat) not in reserve:            
            reserve[p.immatriculation(bestNoeud.etat)] = bestNoeud.g #maj de reserve
            nouveauxNoeuds = bestNoeud.expand(p)
            for n in nouveauxNoeuds:
                f = n.g+p.h_value(n.etat,p.but)
                heapq.heappush(frontiere, (f,n))

    # TODO: VERSION 2 --- Un noeud en réserve peut revenir dans la frontière        
        
        stop_stepwise=""
        if stepwise==True:
            stop_stepwise = input("Press Enter to continue (s to stop)...")
            print ("best", min_f, "\n", bestNoeud)
            print ("Frontière: \n", frontiere)
            print ("Réserve:", reserve)
            if stop_stepwise=="s":
                stepwise=False
    
            
    # Mode verbose            
    # Affichage des statistiques (approximatives) de recherche   
    # et les differents etats jusqu'au but
    if verbose:
        bestNoeud.trace(p)          
        print ("=------------------------------=")
        print ("Nombre de noeuds explorés", len(reserve))
        c=0
        for (f,n) in frontiere:
            if p.immatriculation(n.etat) not in reserve:
                c+=1
        print ("Nombre de noeuds de la frontière", c)
        print ("Nombre de noeuds en mémoire:", c + len(reserve))
        print ("temps de calcul:", time.time() - startTime)
        print ("=------------------------------=")
     
    n=bestNoeud
    path = []
    while n!=None :
        path.append(n.etat)
        n = n.pere
    return path[::-1] # extended slice notation to reverse list


###############################################################################
# Local Repair A*
###############################################################################

import random

def localRepair_astar(equipe,posPlayersEquipe,posPlayersAdv,scoreEquipe,verbose=False,stepwise=False):
    """
    A* indépendants au sein d'une équipe,
    avec recalcul du chemin en cas de collision

    equipe : problemeGrid2D
    """

    # Définition de l'ordre de jeu des joueurs de l'équipeB ayant un score = 0
    joueursEnAttente = []
    joueursEnAttente = [i for i in range(len(scoreEquipe)) if scoreEquipe[i]==0]     
    random.shuffle(joueursEnAttente)

    # Durée tour de l'équipeB : tant que tous les joueurs aient fait leur deplacement 
    while len(joueursEnAttente) > 0:
        joueurBloqueParAmi = False
        joueurBloqueParEnnemi = False

        joueur = joueursEnAttente.pop(0) # on traite le premier joueur de la liste 
        if verbose:
            print("\nC'est le tour de j" + str(joueur), "---> joueursEnAttente =", joueursEnAttente) # test

        # Chemin pre-calculé à suivre associé au joueur
        pathJoueur = equipe[joueur].path

        # Si il n'existe pas un chemin déjà calculé en precedence pour ce joueur (ex: debut du jeu),
        # alors on calcule un nouveau chemin
        if len(pathJoueur) == 0 :
            pathJoueur = astar(equipe[joueur])                    
            pathJoueur.pop(0) # elimination de la case position initiale de la liste des pas à faire
            #print("Le joueur j" + str(joueur), "n'a pas encore de chemin: il génère son path =", pathJoueur) # test

        #print("Le joueur j" + str(joueur), "a un path à suivre =", pathJoueur) # test
        row,col = pathJoueur.pop(0) # case choisie
        #print("Le joueur j" + str(joueur), "voudrait se deplacer en", (row,col)) # test

        # Gestion des collisions 1 : la case (row,col) choisie est occupée par un joueur de notre équipe
        # 2 cas possibles:
        #       - le joueur qui occupe ma case a déjà joué --> le joueur courant fait une pause = il ne se deplace pas dans ce tour de jeu
        #       - le joueur qui occupe ma case doit encore jouer --> on place le joueur courant en fin de liste joueursEnAttente,
        #         pour voir si la case se libère autretemps
        if (row,col) in posPlayersEquipe:
            if posPlayersEquipe.index((row,col)) in joueursEnAttente:
                joueursEnAttente.append(joueur)
            else:
                joueurBloqueParAmi = True

        # Gestion des collisions 2 : la case (row,col) choisie est occupée par un joueur de l'équipe adversaire
        # 2 cas possibles:
        #       - tant qu'il y a d'autres cases accessibles (facteur de branchement) ---> le joueur cherche un nouveau path
        #       - si il n'y a plus de cases accessibles ---> le joueur courant fait une pause = il ne se deplace pas dans ce tour de jeu
        if (row,col) in posPlayersAdv:
            facteurBr = equipe[joueur].successeurs(posPlayersEquipe[joueur]) # cette liste n'est jamais vide au départ = il y a toujours min 1 case accessible
            #print("\tfacteurBr ---> Cases voisines de la position courante", posPlayersEquipe[joueur], ":", facteurBr)
            while (row,col) in posPlayersAdv:
                equipe[joueur].grid[row][col] = False
                pathJoueur = astar(equipe[joueur])
                equipe[joueur].grid[row][col] = True
                pathJoueur.pop(0) # elimination de la case position initiale de la liste paths des pas à faire
                row,col = pathJoueur.pop(0) # case choisie
                #print("Case choisie :", (row,col))
                if (row,col) in facteurBr:
                    facteurBr.remove((row,col))
                #print("\tfacteurBr ---> Mise à jour des cases voisines :", facteurBr) #
                if len(facteurBr) == 0:
                    joueurBloqueParEnnemi = True
                    break 

        # Si la case choisie n'est pas occupée par un autre agent (ami ou adversaire),
        # alors la case est libre et on s'y place            
        if joueurBloqueParAmi == False and joueurBloqueParEnnemi == False:
            posPlayersEquipe[joueur]=(row,col)
            equipe[joueur].init=(row,col)

        # Mise à jour du chemin pour ce joueur
        equipe[joueur].path = pathJoueur 
        
    if stepwise:
        stop_stepwise = input("Press Enter to continue (s to stop)...")
        if stop_stepwise=="s":
            stepwise=False

    return posPlayersEquipe





###############################################################################
# Collaborative Pathfinding with A*
###############################################################################

def collaborativePathfinding(equipe,posPlayersEquipe,posPlayersAdv,objectifsEquipe,initStatesEquipe,scoreEquipe,verbose=False,stepwise=False):
    """
    Collaborative Pathfinding with A* :
    les agents d'une meme équipe evitent de croiser leurs chemins

    equipe : ensemble de joueurs = N problemeGrid2D
    posPlayersEquipe : positions des dernieres cases occupées par notre équipe
    posPlayersAdv : positions des dernieres cases occupées par l'adversaire
    scoreEquipe : score de chaque joueur au sein de l'equipe
    """

    # Initialisation de la reservationTable, une par équipe
    reservationTable = equipe[0].reservationTable

    # Définition de l'ordre de jeu des joueurs de l'équipe ayant un score = 0
    joueursEnAttente = []
    joueursEnAttente = [i for i in range(len(scoreEquipe)) if scoreEquipe[i]==0]     
    random.shuffle(joueursEnAttente)

    # Durée tour de l'équipeB : tant que tous les joueurs aient fait leur deplacement 
    while len(joueursEnAttente) > 0:
        joueurBloqueParEnnemi = False

        joueur = joueursEnAttente.pop(0) # on traite le premier joueur de la liste 
        if verbose:
            print("\nC'est le tour de j" + str(joueur), "---> joueursEnAttente =", joueursEnAttente) # test

        posPlayersEquipe_saufMoi = list(posPlayersEquipe)
        del posPlayersEquipe_saufMoi[joueur]

        # Chemin pre-calculé à suivre associé au joueur
        pathJoueur = equipe[joueur].path

        # Si il n'existe pas un chemin déjà calculé en precedence pour ce joueur (ex: debut du jeu),
        # alors on calcule un nouveau chemin
        if len(pathJoueur) == 0 :
            pathJoueur, reservationTable = collaborativePath(equipe[joueur],reservationTable)                  
            pathJoueur.pop(0) # elimination de la case "position initiale" de la liste des pas à faire
            #print("Le joueur j" + str(joueur), "n'a pas encore de chemin: il génère son path =", pathJoueur) # test

        #print("Le joueur j" + str(joueur), "a un path à suivre =", pathJoueur) # test
        row,col = pathJoueur.pop(0) # case choisie
        #print("Le joueur j" + str(joueur), "voudrait se deplacer en", (row,col)) # test

        # test gestion des collisions 1 : normalement cette situation (case occupée par un joueur de notre équipe) ne doit pas se produire,
        # sauf si la case occupée est une case objectif et l'autre agent l'a rejoint avant notre passage.
        # Dans ce cas, on recalcule le chemin
        if (row,col) in posPlayersEquipe_saufMoi:
            if (row,col) in objectifsEquipe:
                if verbose:
                    print("La case choisie", (row,col), "est occupée par un joueur de notre équipe...")
                equipe[joueur].grid[row][col] = False
                freeExCollaborativePath(equipe[joueur],reservationTable) # on rend à nouveau accessible le chemin qu'on avait reservé
                pathJoueur, reservationTable = collaborativePath(equipe[joueur],reservationTable) # recalcul chemin
                pathJoueur.pop(0) # elimination de la case "position initiale" de la liste paths des pas à faire
                equipe[joueur].grid[row][col] = True
                #print("\tGeneration d'un nouveau path =", pathJoueur)
                row,col = pathJoueur.pop(0) # case choisie
                #print("\tLe joueur j" + str(joueur), "voudrait se deplacer en", (row,col)) # test

        # Gestion des collisions 2 : la case (row,col) choisie est occupée par un joueur de l'équipe adversaire
        # 2 cas possibles:
        #       - tant qu'il y a d'autres cases accessibles (facteur de branchement) ---> le joueur cherche un nouveau path
        #       - si il n'y a plus de cases accessibles ---> le joueur courant fait une pause = il ne se deplace pas dans ce tour de jeu
        if (row,col) in posPlayersAdv:
            if verbose:
                print("La case choisie", (row,col), "est déjà occupée par un adversaire...")
            facteurBr_aVisiter = equipe[joueur].successeurs(posPlayersEquipe[joueur])
            facteurBr_dejaVisitees = []
            #print("\tCases voisines de la position courante", posPlayersEquipe[joueur], ":", facteurBr_aVisiter)
            while (row,col) in posPlayersAdv:
                equipe[joueur].grid[row][col] = False
                freeExCollaborativePath(equipe[joueur],reservationTable) # on rend à nouveau accessible le chemin qu'on avait reservé
                pathJoueur, reservationTable = collaborativePath(equipe[joueur],reservationTable) # recalcul chemin
                pathJoueur.pop(0) # elimination de la case "position initiale" de la liste paths des pas à faire
                #print("\tGeneration d'un nouveau path =", pathJoueur)
                row,col = pathJoueur.pop(0) # case choisie
                facteurBr_aVisiter.remove((row,col))
                facteurBr_dejaVisitees.append((row,col))
                #print("\tMise à jour de la liste des cases voisines :", facteurBr_aVisiter)
                #print("\tLe joueur j" + str(joueur), "voudrait se deplacer en", (row,col)) # test
                if len(facteurBr_aVisiter) == 0:
                    joueurBloqueParEnnemi = True
                    if verbose:
                        print("\tJe suis bloqué par l'adversaire! Je ne pourrai pas bouger pas pour ce tour de jeu")
                    break 

            for r,c in facteurBr_dejaVisitees:
                equipe[joueur].grid[r][c] = True

        # Si la case choisie n'est pas occupée par un autre agent (adversaire),
        # alors la case est libre et on s'y place            
        if joueurBloqueParEnnemi == False:
            posPlayersEquipe[joueur]=(row,col)
            equipe[joueur].init=(row,col)
            equipe[joueur].t_ecoule += 1

        # Mise à jour du chemin pour ce joueur
        equipe[joueur].path = pathJoueur

    # Mise à jour de la reservationTable pour l'équipe    
    equipe[0].reservationTable = reservationTable
    if stepwise:
        stop_stepwise = input("Press Enter to continue (s to stop)...")
        if stop_stepwise=="s":
            stepwise=False

    return posPlayersEquipe





def collaborativePath(p,reservationTable,verbose=False,stepwise=False):
    """Retourne un chemin qui ne collide pas
    avec les chemins des autres joueurs au sein de la même équipe

    p : un joueur = 1 problemeGrid2D
    reservationTable (dictionnaire): structure en 3 dimensions (x,y,t) permettant de savoir
    si un chemin est déjà pris par un joueur de notre équipe ou pas
    """
    path = []
    path_astar = []
    path_astar = astar(p)
    t = p.t_ecoule

    # Pour tout pas à suivre dans le chemin astar :
    #       - si la case (x,y) du prochain coup n'est pas encore réservée (i.e clé inexistante dans reservationTable)
    #         ou elle a été liberée par un équipier (i.e reservationTable[x,y,t] vaut False) alors on réserve (x,y) à l'instant t
    #       - sinon, la case (x,y) est occupée à l'instance t et il faut attendre le 'temps necessaire' pour qu'elle se libère
    #         L'attente est representée par un chemin qui repète la dernière case, avant de poursuivre avec le chemin A* calculé
    #         Temps necessaire : nombre de cases occupées consecutives sur le chemin du joueur courant

    for iCase in range(len(path_astar)):
        row,col = path_astar[iCase]
        if (row,col,t) not in reservationTable.keys() or reservationTable[row,col,t] == False:
            reservationTable[row,col,t] = True
            path.append((row,col))    
        else: # reservationTable[row,col,t] == True ---> case occupée par un chemin en cours
            cptAttente = 0
            iCase_tmp = iCase
            row_tmp = row
            col_tmp = col
            t_tmp = t
            while (row_tmp,col_tmp,t_tmp) in reservationTable.keys() and reservationTable[row_tmp,col_tmp,t_tmp] == True:
                    cptAttente +=1
                    path.append(path[-1]) # path[-1] : derniere case chargée dans path
                    iCase_tmp += 1
                    t_tmp +=1
                    row_tmp, col_tmp = path_astar[iCase_tmp]

            t += cptAttente
            reservationTable[row,col,t] = True
            path.append((row,col))
            #print("Risque collision maitrisé en", (row,col))

        t += 1

    # Sauvegarde du path crée, au cas où il faudra effacer les réservations
    # avec la fonction freeExCollaborativePath
    p.path_history = list(path)
    if verbose:
        print("reservationTable =", reservationTable)

    return path, reservationTable



def freeExCollaborativePath(p,reservationTable,verbose=False,stepwise=False):
    """Retourne la reservationTable après avoir effacé
    l'ancienne réservation de chemin precedemment effectuée par le joueur p.
    Ainsi l'ancien path de p est eventuellement disponible
    pour les autres joueurs de l'équipe, en cas de besoin

    p : un joueur = 1 problemeGrid2D
    reservationTable (dictionnaire): structure en 3 dimensions (x,y,t) permettant de savoir
    si un chemin est déjà pris par un joueur de notre équipe ou pas
    """

    exPath = p.path_history
    for iCase in range(len(exPath)):
        row,col = exPath[iCase]
        reservationTable[row,col,iCase] = False

    #print("reservationTable =", reservationTable)
    p.path_history.clear()




###############################################################################
# minmax
###############################################################################
def compteur():
    compteur.c = compteur.c + 1
    print("Appel numéro : ", compteur.c)

def MinMax(g, equipe1, equipe2, position1, position2, depth, verbose=False, stepwise=False):
    compteur.c = 0
    N = Noeud([position1,position2], 0, None)
    coup_valide_par_joueur = coups_valides(g, equipe1, equipe2, position1, position2)
    #print(coup_valide_par_joueur)
    l_coups_valides = ensemble_coup(coup_valide_par_joueur)
    if verbose:
        print(position1)
        print(len(l_coups_valides))
    #stop_stepwise = input("Press Enter to continue (s to stop)...")
    #print(l_coups_valides)
    evalu = -100000
    coup_choisi = l_coups_valides[0]
    iter = 0
    for coups in l_coups_valides:
        iter+=1
        noeud_impair = Noeud([coups,position2], 0, N)
        val = minValue(noeud_impair, [coups,position2], g, equipe1, equipe2, depth)
        if verbose:
            print("coups : ",coups)
            print("val minValue :", val)
            print("iteration = ",iter)
        noeud_impair.g = val
        if evalu < noeud_impair.g:
            evalu = noeud_impair.g
            coup_choisi = noeud_impair.etat
    for j in range(len(equipe1)):
        equipe1[j].init = coup_choisi[0][j]
    position1 = coup_choisi[0]
    if verbose:
        print(position1)
    if stepwise:
        stop_stepwise = input("Press Enter to continue (s to stop)...")
        if stop_stepwise=="s":
            stepwise=False
    gc.collect()
    return position1

def maxValue(noeud, coup, g, equipe1, equipe2, depth):
    if depth == 1:
        return Evaluation(noeud.etat, equipe1, equipe2)
    else:
        #print("coups : ",coup)
        coup_valide_par_joueur = coups_valides(g, equipe1, equipe2, coup[0], coup[1])
        l_coups_valides = ensemble_coup(coup_valide_par_joueur)
        evalu = -100000
        for coups in l_coups_valides:
            #print("coups:",coups)
            #print("coup[1]",coup[1])
            noeud_impair = Noeud([coups,coup[1]], 0, noeud)
            #print(noeud_impair)
            val = minValue(noeud_impair, [coups,coup[1]], g, equipe1, equipe2, depth-1)
            #print("val :",val)
            noeud_impair.g = val
            if evalu < noeud_impair.g:
                evalu = noeud_impair.g
        gc.collect()
        return evalu

def minValue(noeud, coup, g, equipe1, equipe2, depth):
    evalu = 100000
    if depth == 1:
        #print("noeud etat ",noeud.etat)
        evalu = Evaluation(noeud.etat, equipe1, equipe2)
        #print("depth=1, evalu ", evalu)
    else:
        #print("coups : ",coup)
        coup_valide_par_joueur = coups_valides(g, equipe2, equipe1, coup[1], coup[0])
        l_coups_valides = ensemble_coup(coup_valide_par_joueur)
        for coups in l_coups_valides:
            #print("coup[0]:",coup[0])
            #print("coups",coups)
            noeud_pair = Noeud([coup[0],coups], 0, noeud)
            val = maxValue(noeud_pair, [coup[0],coups], g, equipe1, equipe2, depth-1)
            #print("val :",val)
            noeud_pair.g = val
            if evalu > noeud_pair.g:
                evalu = noeud_pair.g
    gc.collect()
    return evalu

def coups_valides(g, equipe1, equipe2, position1, position2):
    #retourne une matrice des coups valide de chaque joueur
    imax = len(g)
    jmax = len(g[0])
    liste = [[] for i in range(len(equipe1))]
    #print(len(equipe1))
    for joueur in range(len(equipe1)):
        if equipe1[joueur].but == position1[joueur] and position1[joueur] not in liste[joueur]:
            liste[joueur].append(position1[joueur])
        else:
            #obstacles pour chaque joueur
            obstacles = []
            for i in range(imax):
                for j in range(jmax):
                    if not g[i][j]:
                        obstacles.append((i,j))
            for player in range(len(equipe1)):
                if player != joueur and position1[player] not in obstacles:
                    obstacles.append(position1[player])

            for player in range(len(equipe2)):
                if position2[player] not in obstacles:
                    obstacles.append(position2[player])
            #print("obstacles ", obstacles)
            # successeurs valides pour chaque joueur
            coup_valide = []
            i = position1[joueur][0]
            j = position1[joueur][1]
            if i>0 and (i-1,j) not in obstacles:
                coup_valide.append((i-1,j))
            if i<imax-1 and (i+1,j) not in obstacles:
                coup_valide.append((i+1,j))
            if j>0 and (i,j-1) not in obstacles:
                coup_valide.append((i,j-1))
            if j<jmax-1 and (i,j+1) not in obstacles:
                coup_valide.append((i,j+1))
            #print(coup_valide)

            liste[joueur] = liste[joueur] + coup_valide
            #print(joueur)
    gc.collect()
    return liste

# epartir les coups au sein d'une meme equipe
def ensemble_coup(matrice):
    liste = []
    i = len(matrice)
    j = len(matrice[0])
    if i == 1:
        for elem in matrice[0]:
            liste.append([elem])
    else:
        liste = ensemble_coup(matrice[1:])
        liste_tmp = []
        for index in range(j):
            for indexL in range(len(liste)):
                tmp = [matrice[0][index]] + copy.deepcopy(liste[indexL])
                liste_tmp.append(tmp)
        liste = liste_tmp
    gc.collect()
    return liste

def Evaluation(coups, equipe1, equipe2):
    #compteur()
    evalu = 0
    #chemin1 = 0
    #chemin2 = 0
    for i in range(len(equipe1)):
        tmp = equipe1[i].init
        #print(tmp)
        equipe1[i].init = coups[0][i]
        #print(equipe1[i].init)
        path = astar(equipe1[i])
        #print(len(path))
        equipe1[i].init = tmp
        if len(path)==0:
            evalu+=1
        else:
            evalu+=(1/len(path))
        #print("joueur : ",i)
        #chemin1 = distManhattan(coups[0][i], equipe1[i].but)
        #evalu-=chemin1
    
    #for i in range(len(equipe2)):
        #chemin2 = distManhattan(coups[1][i], coups[1][i])
        #evalu+=chemin2
    #print("evalu = ", evalu)
    gc.collect()
    return evalu

###############################################################################
# AlphaBeta
###############################################################################

def alpha_beta(p, position):
    """ 
        p: grid2D [init, but, grid, heurestique]
        position: position courante
        retourne la case optimal selon l'algorithme alpha-beta
    """
    compteur.c = 0
    N = Noeud([position1,position2], 0, None)
    coup_valide_par_joueur = coups_valides(g, equipe1, equipe2, position1, position2)
    #print(coup_valide_par_joueur)
    l_coups_valides = ensemble_coup(coup_valide_par_joueur)
    print(position1)
    print(len(l_coups_valides))
    #stop_stepwise = input("Press Enter to continue (s to stop)...")
    #print(l_coups_valides)
    evalu = -100000
    coup_choisi = l_coups_valides[0]
    iter = 0
    for coups in l_coups_valides:
        iter+=1
        noeud_impair = Noeud([coups,position2], 0, N)
        val = minValue(noeud_impair, [coups,position2], g, equipe1, equipe2, depth)
        print("coups : ",coups)
        print("val minValue :", val)
        print("iteration = ",iter)
        noeud_impair.g = val
        if evalu < noeud_impair.g:
            evalu = noeud_impair.g
            coup_choisi = noeud_impair.etat
    for j in range(len(equipe1)):
        equipe1[j].init = coup_choisi[0][j]
    position1 = coup_choisi[0]
    print(position1)
    #stop_stepwise = input("Press Enter to continue (s to stop)...")
    gc.collect()
    return position1
