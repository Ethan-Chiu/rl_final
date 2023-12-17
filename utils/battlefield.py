import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

game = "dots_and_boxes"
num_matches = 10
num_games = 100
seed=0
# "/home/howard/RL/final_project/models/base"
base = "/home/howard/RL/final_project/results/"
# directories=["test_dots_and_boxes_3*3_allFalse",]
directories =["test_dots_and_boxes_3*3_new_pcr_0.75_0.02",
        "test_dots_and_boxes_3*3_new_pcr_0.75_0.05",]
directories = [base + d for d in directories]
az = [120,110]
# az = [100]
# directory = "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_apt_0.35"
mcts = [1000] # [2, 5, 10, 30, 100]
# az = [i for i in range(100,101,100)]
log = "/home/howard/RL/final_project/logs/test_dots_and_boxes_3*3_apt_0.25.log"

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
FLAGS.num_actors = num_matches
FLAGS.seed = seed

for directory, a in zip(directories,az):
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
