# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain
import time
import gc

import numpy as np
from matplotlib import pyplot as plt
from IPython.core.pylabtools import figsize
import pylab

import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme




# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'demoMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main():
    print("\n----------------------------------------------------------------------------------------------\n")
    print("Projet IA et Jeux 2021 - Groupe 3 - LOI Alessia, MOULOUEL Myriem")
    print("\n----------------------------------------------------------------------------------------------\n")



    #-------------------------------
    # Initialisation
    #-------------------------------

    iterations = 100 # default
    if len(sys.argv) == 2: # nombre iterations defini en parametre
        iterations = int(sys.argv[1])
    print ("Iterations: ",iterations)


    # Choix du tableau de jeu
    #init('demoMap')
    #init('exAdvCoopMap')
    #init('map1_2equipes_2joueurs')
    #init('map1_2equipes_5joueurs')
    #init('map2_2equipes_1joueur')
    init('map2_2equipes_2joueurs')
    #init('map2_2equipes_3joueurs')
    #init('map2_2equipes_5joueurs')
    #init('map2_2equipes_10joueurs')
    #init('map2_croisement')

#-------------------------------

    print ("Description de l'environnement de jeu :")

    nbLignes = game.spriteBuilder.rowsize
    print("Lignes :", nbLignes)
    nbCols = game.spriteBuilder.colsize
    print("Colonnes :", nbCols)

    #-------------------------------

    players = [o for o in game.layers['joueur']] #liste des joueurs [i for i range(0,4)]=>[0,1,2,3]
    nbPlayers = len(players)

                
    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    # on localise tous les objets ramassables
    # sur le layer ramassable
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    # sur le layer obstacle
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    print ("Wall states:", wallStates)
    
    def legal_position(row,col):
        # une position legale est dans la carte et pas sur un mur
        return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols

    print("\n----------------------------------------------------------------------------------------------\n")



    #-------------------------------
    # Positions initiales des joueurs
    #-------------------------------

    initStates_equipeB = []
    initStates_equipeR = []

    nbPlayersEquipe = int(nbPlayers / 2)

    for i in range (nbPlayersEquipe):
        initStates_equipeB.append(initStates[i])

    for j in range (i+1, nbPlayersEquipe*2):   
        initStates_equipeR.append(initStates[j])



    #-------------------------------
    # Attribution aleatoire des fioles 
    #-------------------------------
    
    objectifs_equipeB = []
    objectifs_equipeR = []

    #random.seed(42)
    objectifs = goalStates
    #random.shuffle(objectifs)

    # Objectifs de l'equipe Rouge
    print("Objectifs de l'équipe Rouge")
    for i in range(nbPlayersEquipe):
        objectifs_equipeR.append(objectifs[i])
        print("\tJoueur jR" + str(i), objectifs_equipeR[i])
    random.shuffle(objectifs_equipeR)

    # Objectifs de l'equipe Bleue
    print("\nObjectifs de l'équipe Bleue")
    for i in range(nbPlayersEquipe):
        objectifs_equipeB.append(objectifs[nbPlayersEquipe+i])
        print("\tJoueur jB" + str(i), objectifs_equipeB[i])
    random.shuffle(objectifs_equipeR)



    #-------------------------------
    # Creation d'une gille des positions des elements dans le plan de jeu
    #-------------------------------
    
    g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True  
    for w in wallStates:            # putting False for walls
        g[w]=False



    #-------------------------------
    # Attribution joueurs au sein de chaque équipe
    #-------------------------------

    # Attribution joueurs équipe Bleue
    equipeB = []
    for i in range(nbPlayersEquipe):
        p = ProblemeGrid2D(initStates_equipeB[i],objectifs_equipeB[i],g,'manhattan')
        equipeB.append(p)

    # Attributions joueurs équipe Rouge
    equipeR = []
    for i in range(nbPlayersEquipe):
        p = ProblemeGrid2D(initStates_equipeR[i],objectifs_equipeR[i],g,'manhattan')
        equipeR.append(p)


        
    #-------------------------------
    # 2 équipes de <nbPlayersEquipe> agents chacune
    # Strategies applicables : 
    #       1) Local Repair A* : A* indépendants au sein d'une équipe, recalcul du chemin en cas de collision
    #       2)
    #       3)
    # 
    #-------------------------------

    # strategies
    LOCAL_REPAIR = 1
    COLLAB_PATH_FINDING = 2
    MINMAX = 3

    # Choix de la strategie à employer pour chaque équipe
    strategieB = LOCAL_REPAIR
    strategieR = LOCAL_REPAIR

    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------

    # Listes des positions courantes de chaque joueur, initialisées avec leurs positions initiales       
    posPlayersB = initStates_equipeB 
    posPlayersR = initStates_equipeR

    # Listes des scores associés à chaque joueur
    scoreB = [0]*nbPlayersEquipe 
    scoreR = [0]*nbPlayersEquipe


    #listes des joueurs en attente
    B_en_attente = []
    
    R_en_attente = []


    pathB = [[coup] for coup in posPlayersB]
    pathR = [[coup] for coup in posPlayersR]



    for tour_jeu in range(iterations):

        print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   Iteration de jeu n." + str(tour_jeu) + "   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        for i in range(len(equipeB)):
            B_en_attente.append(i)

        for i in range(len(equipeR)):
            R_en_attente.append(i)

        # on fait bouger chaque équipe séquentiellement :
        
        # Equipe Bleue 
        print("\nEQUIPE BLEUE")   

        if strategieB == LOCAL_REPAIR:
            posPlayersB = probleme.localRepair_astar(equipeB,posPlayersB,posPlayersR,scoreB)
            print(posPlayersB)
        if strategieB == COLLAB_PATH_FINDING:
            posPlayersB = probleme.collaborativePathfinding(equipeB,posPlayersB,posPlayersR,objectifs_equipeB,initStates_equipeB,scoreB)
            print(posPlayersB)
        if strategieB == MINMAX:
            posPlayersB = probleme.MinMax(g, equipeB, equipeR, posPlayersB, posPlayersR, 1)
            print(posPlayersB)

        # Deplacement sur les cases choisies   
        print("\nDeplacements définis pour l'équipe BLEUE :")        
        for i in range(nbPlayersEquipe):
            row,col = posPlayersB[i]
            players[i].set_rowcol(row,col)
            print("Le joueur jB" + str(i), "se deplace en", (row,col))

        # Comptabilisation des nouveaux scores obtenus pendant cette iteration (tour de jeu)
        for i in range(nbPlayersEquipe):
            if scoreB[i]==0 and posPlayersB[i]==objectifs_equipeB[i]:
                scoreB[i] += 1
                B_en_attente.remove(i)
                print("Le joueur jB" + str(i) + " a atteint son but!")

        # Les bleus ont gagné?
        if sum(scoreB) == nbPlayersEquipe:
            break


        print("\n----------------------------------------------------------------------------------------------") 

        # Equipe Rouge 
        print("\nEQUIPE ROUGE")   

        if strategieR == LOCAL_REPAIR:
            posPlayersR = probleme.localRepair_astar(equipeR,posPlayersR,posPlayersB,scoreR)
        if strategieR == COLLAB_PATH_FINDING:
            posPlayersR = probleme.collaborativePathfinding(equipeR,posPlayersR,posPlayersB,objectifs_equipeR,initStates_equipeR,scoreR)
        if strategieR == MINMAX:
            posPlayersR = probleme.MinMax(g, equipeR, equipeB, posPlayersR, posPlayersB, 2)
        
        # Deplacement sur les cases choisies   
        print("\nDeplacements définis pour l'équipe ROUGE :")           
        for i in range(nbPlayersEquipe):
            row,col = posPlayersR[i]
            players[nbPlayersEquipe+i].set_rowcol(row,col)
            print("Le joueur jR" + str(i), "se deplace en", (row,col))

        # Comptabilisation des nouveaux scores obtenus pendant cette iteration (tour de jeu)
        for i in range(nbPlayersEquipe):
            if scoreR[i]==0 and posPlayersR[i]==objectifs_equipeR[i]:
                scoreR[i] += 1
                R_en_attente.remove(i)
                print("Le joueur jR" + str(i) + " a atteint son but!")

        # Les rouges ont gagné?
        if sum(scoreR) == nbPlayersEquipe:
            break

        for i in range(len(equipeB)):
            if posPlayersB[i] not in pathB[i]:
                pathB[i].append(posPlayersB[i])
        for i in range(len(equipeR)):
            if posPlayersR[i] not in pathR[i]:
                pathR[i].append(posPlayersR[i])



        
        # On passe a l'iteration suivante du jeu
        game.mainiteration()


    #-------------------------------
    # Critères de victoire
    #-------------------------------                

    print("\n----------------------------------------------------------------------------------------------\n")       
    print ("Scores de l'équipe Bleue :", scoreB)
    print ("Scores de l'équipe Rouge :", scoreR)

    resultat = sum(scoreB) - sum(scoreR)
    if resultat > 0:
        print("\nL'équipe Bleu a gagné!")
    elif resultat < 0:
        print("\nL'équipe Rouge a gagné!")
    else: # si scoreB.sum() = scoreR.sum()
        taille_chemin1 = 0
        taille_chemin2 = 0
        for i in range(len(equipeB)):
            taille_chemin1+=(len(pathB[i]))
        for i in range(len(equipeR)):
            taille_chemin2+=(len(pathR[i]))

        if taille_chemin1 > taille_chemin2:
            print("equipe B et R ont le meme score, mais R a fait moins de trajet => R gagne")
        elif taille_chemin2 > taille_chemin1:
            print("equipe B et R ont le meme score, mais B a fait moins de trajet => B gagne")
        else:
            print("\nLes équipes Bleue et Rouge ont eu le même score et ont parcouru la meme distance!") 


    # Attente de 5 secondes avant de fermer la fenetre graphique
    time.sleep(5) 
    pygame.quit()
    
    del(pathB)
    del(pathR)
    #gc.collect()
    #-------------------------------
    print("resultat: ",resultat)
    return (sum(scoreB),sum(scoreR))
    
if __name__ == '__main__':
    filename = "nom_du_fichier" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(2):
            scoreB,scoreR = main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
    
    
    
    
        