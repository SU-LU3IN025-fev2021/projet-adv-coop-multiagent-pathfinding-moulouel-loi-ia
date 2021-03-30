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

import main

test = 8

if test == 1:
    filename = "1joueur_localrepair_collabpath.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==2:
    filename = "1joueur_localrepair_minmax3.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==3:
    filename = "1joueur_collabpath_localrepair.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==4:
    filename = "3joueur_collabpath_minmax2.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==5:
    filename = "2joueur_minmax2_localrepair.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==6:
    filename = "5joueur_collapath_localrepair.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==7:
    filename = "3joueur_minmax2_localrepair.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
elif test ==8:
    filename = "3joueur_minmax2_collabpath.txt" 
    with open(filename, 'w') as f: 
        f.write("iteration\tscoreB\tscoreR\n")
        for i in range(100):
            scoreB,scoreR = main.main()
            
            f.write(str(i)+"\t"+str(scoreB)+"\t"+str(scoreR)+"\n")
            gc.collect()
