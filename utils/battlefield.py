import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

game = "dots_and_boxes"

num_matches = 10
num_games = 10

directories = ["/results/3x3_None-2",
              "/results/3x3_None-2",]
mcts = [10000]
az = [100, 1000]
log = "/results/3x3.log"


FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
FLAGS.num_actors = num_matches

for directory, a in zip(directories, az):
    for m in mcts:
        FLAGS.az_path = directory + "/checkpoint-" + str(a)
        FLAGS.az_path2 = directory + "/checkpoint-" + str(a)
        FLAGS.max_simulations = m
        FLAGS.max_simulations2 = m
        FLAGS.player1 = "az"
        FLAGS.player2 = "mcts"
        try:
            app.run(evaluation.parallel)
        except:
            pass
        FLAGS.player1 = "mcts"
        FLAGS.player2 = "az"
        try:
            app.run(evaluation.parallel)
        except:
            pass
