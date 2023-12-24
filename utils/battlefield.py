import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import evaluation
from evaluation import FLAGS
from absl import app

game = "dots_and_boxes" # othello
directories = ["../open_spiel/results/othello66_growing_fill_gb_p23_n4"] * 3
log = "final.log"

num_matches = 10
num_games = 20

mcts = [10, 100, 1000, 10000]
az = [10, 20, 30, 40, 50, 60]

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


# BATTLE between 2 AlphaZero Agent
# agent1_checkpoint = "../open_spiel/results/agent1" + "/checkpoint-" + str(10)
# agent2_checkpoint = "../open_spiel/results/agent2" + "/checkpoint-" + str(60)

# FLAGS.az_path = agent1_checkpoint
# FLAGS.az_path2 = agent2_checkpoint
# FLAGS.max_simulations = 1000
# FLAGS.max_simulations2 = 1000
# FLAGS.player1 = "az"
# FLAGS.player2 = "az"
# try:
#     app.run(evaluation.parallel)
# except:
#     pass
# FLAGS.az_path = agent2_checkpoint
# FLAGS.az_path2 = agent1_checkpoint
# FLAGS.player1 = "az"
# FLAGS.player2 = "az"
# try:
#     app.run(evaluation.parallel)
# except:
#     pass
