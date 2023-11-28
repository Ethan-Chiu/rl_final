import evaluation
from evaluation import FLAGS
from absl import app
import random

game = "dots_and_boxes"
num_matches = 3
num_games = 10
names = ["tree2", "tree1", "tree0"]
directories = ["./dab/tree-2", "./dab/tree-1", "./dab/tree-0"]
az = [[i for i in range(0, 220, 20)], [i for i in range(0, 220, 20)], [i for i in range(0, 220, 20)]]
log = "battle.log"

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
FLAGS.max_simulations = 100
FLAGS.max_simulations2 = 100

def battle(g1, g2, n1, n2):
    FLAGS.az_path = directories[g1] + "/checkpoint-" + str(n1)
    FLAGS.az_path2 = directories[g2] + "/checkpoint-" + str(n2)
    FLAGS.name = names[g1]
    FLAGS.name2 = names[g2]
    FLAGS.player1 = "az"
    FLAGS.player2 = "az"
    try:
        app.run(evaluation.main)
    except:
        pass

for m in range(num_matches):
    for g1 in range(len(names)):
        for a in az[g1]:
            for b in az[g1]:
                if a != b:
                    battle(g1, g1, a, b)
            for g2 in range(len(names)):
                if g2 != g1:
                    for b in az[g2]:
                        battle(g1, g2, a, b)
