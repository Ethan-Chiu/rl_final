import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

game = "dots_and_boxes"

# 'dab33_pcr_p05_f025', 'dab33_pcr_p025_f05', 'dab33_pcr_p075_f075', 'dab33_pcr_p075_f025', 'dab33_pcr_p025_f075'
# 'dab33_fpptp_k1_5_e05', 'dab33_fpptp_k1_5_e025', 'dab33_fpptp_k2_e025'
# 'dab33_fpptp_k3_e05', 'dab33_fpptp_k3_e075', 'dab33_fpptp_k2_5_e05'
# directory = "../open_spiel/results/dab33_fpptp_k3_e05"
# directorys = ["../open_spiel/results/dab33_gb_mp099_n8_3", "../open_spiel/results/dab33_gb_mp099_n8_4"]
# log = "dab33_gb_mp099_n8.log"
directorys = ["../open_spiel/results/jimmybasic"]
log = "jimmybasic.log"

# "/home/howard/RL/final_project/models/base"
# directory = "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_all_maxsim100"
# log = "/home/howard/RL/final_project/logs/test_dots_and_boxes_3*3_all_maxsim100.log"

# directory = "./dab/0505"
# log = "battle.log"

num_matches = 10
num_games = 100
mcts = [1000]
az = [100]

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
FLAGS.num_actors = num_matches
for directory in directorys:
    for a in az:
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
