from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

# game = "tic_tac_toe"
game = "dots_and_boxes"
num_matches = 20
num_games = 5
# "/home/howard/RL/final_project/models/base"
directory = "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_all_maxsim100"
mcts = [10000] # [2, 5, 10, 30, 100]
az = [i for i in range(1000,1001,10)]
log = "/home/howard/RL/final_project/logs/test_dots_and_boxes_3*3_all_maxsim100.log"

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
                print("1")
            except Exception as e:
                print("ERROR")
                print(e)
                pass
            print("2")
            FLAGS.player1 = "mcts"
            FLAGS.player2 = "az"
            try:
                app.run(evaluation.main)
            except Exception as e:
                print("ERROR")
                print(e)
                pass
