import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from collections import OrderedDict
import evaluation
from evaluation import FLAGS
from absl import app
import random

# game = "dots_and_boxes"
game = "othello"

# 'dab33_pcr_p05_f025', 'dab33_pcr_p025_f05', 'dab33_pcr_p075_f075', 'dab33_pcr_p075_f025', 'dab33_pcr_p025_f075'
# 'dab33_fpptp_k1_5_e05', 'dab33_fpptp_k1_5_e025', 'dab33_fpptp_k2_e025'
# 'dab33_fpptp_k3_e05', 'dab33_fpptp_k3_e075', 'dab33_fpptp_k2_5_e05'
# directory = "../open_spiel/results/dab33_fpptp_k3_e05"
# directorys = ["../open_spiel/results/dab33_gb_mp099_n8_3", "../open_spiel/results/dab33_gb_mp099_n8_4"]
# log = "dab33_gb_mp099_n8.log"
# directories = [
#     "../open_spiel/results/dab33_none_final",
# ] * 3
# directories = [
#     "../open_spiel/results/dab33_growing_fill_gb_p11_n16_final",
# ] * 3
# directories = ["../open_spiel/results/dab33_pcr_p075_f02_growing_fill_gb_p099_n16"]
# directories = ["../open_spiel/results/othello66_growing_fill_gb_p099_n16"]
# othello66_growing_fill_gb_p23_n4
# directories = ["../open_spiel/results/othello66_none"] * 3
directories = ["../open_spiel/results/othello66_growing_fill_gb_p23_n4"] * 3
log = "final.log"

# "/home/howard/RL/final_project/models/base"
# directory = "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_all_maxsim100"
# log = "/home/howard/RL/final_project/logs/test_dots_and_boxes_3*3_all_maxsim100.log"

# directory = "./dab/0505"
# log = "battle.log"

num_matches = 10
num_games = 20

mcts = [10, 100, 500]
# az = list(range(20, 101, 20))
# az = [9, 21, 35] # , 52, 68, 85, 101, 117, 133, 150
# az = [25, 55, 80, 105, 135]
# az = [10, 30, 50]
az = [15, 40, 65]
# az = [0]

FLAGS.game = game
FLAGS.num_games = num_games
FLAGS.log = log
FLAGS.num_actors = num_matches


# FLAGS.az_path = "../open_spiel/results/dab33_growing_fill_gb_p11_n16_final" + "/checkpoint-" + str(150)
# FLAGS.az_path2 = "../open_spiel/results/dab33_none_final" + "/checkpoint-" + str(60)
# FLAGS.max_simulations = 1000
# FLAGS.max_simulations2 = 1000
# FLAGS.player1 = "az"
# FLAGS.player2 = "az"
# try:
#     app.run(evaluation.parallel)
# except:
#     pass
# FLAGS.az_path = "../open_spiel/results/dab33_none_final" + "/checkpoint-" + str(60)
# FLAGS.az_path2 = "../open_spiel/results/dab33_growing_fill_gb_p11_n16_final" + "/checkpoint-" + str(150)
# FLAGS.player1 = "az"
# FLAGS.player2 = "az"
# try:
#     app.run(evaluation.parallel)
# except:
#     pass


for directory, a in zip(directories, az):
    for m in mcts:
        # if m == 10000:
        #     FLAGS.num_games = 20
        # else:
        #     FLAGS.num_games = 40
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
print("")
# othello 66
# none
# 10
# [492.   7.   1.]   [486.  10.   4.] 
# [179. 297.  24.]   [180. 296.  24.] 

# 100
# [457.  32.  11.]   [437.  54.   9.] 
# [302. 170.  28.]   [395.  89.  16.] 

# 1000
# [347. 136.  17.]   [322. 155.  23.]
# [444.  45.  11.]   [480.  17.   3.] 

# 10 
# [496.   2.   2.] 
# [ 67. 423.  10.] 

# 100
# [470.  20.  10.]
# [242. 245.  13.]

# 1000
# [378. 107.  15.]
# [417.  68.  15.]
        


# othello 88
# none
# 10
# 138 [138. 351.  11.]
# 202 [279. 202.  19.]

# 100
# 15 [ 15. 484.   1.] 
# 27 [470.  27.   3.]

# 1000
# 2 [  2. 498.   0.] 
# 2 [498.   2.   0.]

# 10 
# 178 [178. 301.  21.]
# 210 [274. 210.  16.]

# 100
# 30 [ 30. 460.  10.]
# 40 [455.  40.  5.] 

# 1000
# 
# 




# 156, 126
# 66, 25
# 25, 5

# 188, 121
# 165, 35
# 140, 11

