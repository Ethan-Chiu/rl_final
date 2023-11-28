from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

game = "dots_and_boxes"
num_matches = 1
num_games = 10
directory = "./open_spiel/results/dab/"
mcts = [2, 5, 10, 30]
az = [i for i in range(0, 1001, 50)]
log = "battle2.log"

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
for m in range(num_matches):
    for a in az:
        for m in mcts:
            FLAGS.az_path = directory + "/checkpoint-" + str(a)
            FLAGS.az_path2 = directory + "/checkpoint-" + str(a)
            FLAGS.max_simulations = m
            FLAGS.max_simulations2 = m
            FLAGS.player1 = "az"
            FLAGS.player2 = "mcts"
            try:
                app.run(evaluation.main)
            except:
                pass
            FLAGS.player1 = "mcts"
            FLAGS.player2 = "az"
            try:
                app.run(evaluation.main)
            except:
                pass