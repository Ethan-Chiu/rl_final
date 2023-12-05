from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

# game = "tic_tac_toe"
game = "dots_and_boxes"
num_matches = 1
num_games = 25
# "/home/howard/RL/final_project/models/base"
directory = "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_allFalse_1_maxsim100"
mcts = [10,20,25,33,50,100,200,250,330,500,1000] # [2, 5, 10, 30, 100]
mcts2 = [10,20,25,33,50,100,200,250,330,500,1000]
az = [i for i in range(0,1001,100)]
log = "/home/howard/RL/final_project/logs/mcts.log"

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
# for m in range(num_matches):
#     for a in az:
#         for m in mcts:
#             FLAGS.az_path = directory + "/checkpoint-" + str(a)
#             FLAGS.az_path2 = directory + "/checkpoint-" + str(a)
#             FLAGS.max_simulations = m
#             FLAGS.max_simulations2 = m
#             FLAGS.player1 = "az"
#             FLAGS.player2 = "mcts"
#             try:
#                 app.run(evaluation.main)
#             except Exception as error:
#                 print("An error occurred:", error) 
#             FLAGS.player1 = "mcts"
#             FLAGS.player2 = "az"
#             try:
#                 app.run(evaluation.main)
#             except Exception as error:
#                 print("An error occurred:", error) 
for m in range(num_matches):
    for m1 in mcts:
        for m2 in mcts2:
            # FLAGS.az_path = directory + "/checkpoint-" + str(a)
            # FLAGS.az_path2 = directory + "/checkpoint-" + str(a)
            FLAGS.max_simulations = m1
            FLAGS.max_simulations2 = m2
            FLAGS.player1 = "mcts"
            FLAGS.player2 = "mcts"
            try:
                app.run(evaluation.main)
            except :
                pass
            FLAGS.player1 = "mcts"
            FLAGS.player2 = "mcts"
            FLAGS.max_simulations = m2
            FLAGS.max_simulations2 = m1
            try:
                app.run(evaluation.main)
            except :
                pass
               
