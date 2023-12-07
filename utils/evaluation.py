import collections
import random
import sys

from absl import app
from absl import flags
import numpy as np

from open_spiel.python.algorithms import mcts
from open_spiel.python.algorithms.alpha_zero import azbot
from open_spiel.python.algorithms.alpha_zero import evaluator as az_evaluator
from open_spiel.python.algorithms.alpha_zero import model_og as az_model
from open_spiel.python.bots import gtp
from open_spiel.python.bots import human
from open_spiel.python.bots import uniform_random
from open_spiel.python.utils import spawn
import pyspiel

_KNOWN_PLAYERS = [
    "mcts",
    "random",
    "human",
    "gtp",
    "az"
]

flags.DEFINE_string("game", "tic_tac_toe", "Name of the game.")
flags.DEFINE_enum("player1", "az", _KNOWN_PLAYERS, "Who controls player 1.")
flags.DEFINE_enum("player2", "az", _KNOWN_PLAYERS, "Who controls player 2.")
flags.DEFINE_string("gtp_path", None, "Where to find a binary for gtp.")
flags.DEFINE_multi_string("gtp_cmd", [], "GTP commands to run at init.")
flags.DEFINE_string("az_path", "./tictactoe/checkpoint-50",
                    "Path to an alpha_zero checkpoint. Needed by an az player.")
flags.DEFINE_string("az_path2", "./tictactoe/checkpoint-50",
                    "Path to an alpha_zero checkpoint. Needed by an az player.")
flags.DEFINE_integer("uct_c", 2, "UCT's exploration constant.")
flags.DEFINE_integer("rollout_count", 1, "How many rollouts to do.")
flags.DEFINE_integer("max_simulations", 30, "How many simulations to run.")
flags.DEFINE_integer("max_simulations2", 30, "How many simulations to run.")
flags.DEFINE_string("name", "", "Name of the model.")
flags.DEFINE_string("name2", "", "Name of the model.")
flags.DEFINE_integer("num_games", 30, "How many games to play.")
flags.DEFINE_integer("seed", None, "Seed for the random number generator.")
flags.DEFINE_bool("random_first", False, "Play the first move randomly.")
flags.DEFINE_bool("solve", True, "Whether to use MCTS-Solver.")
flags.DEFINE_bool("quiet", True, "Don't show the moves as they're played.")
flags.DEFINE_bool("verbose", False, "Show the MCTS stats of possible moves.")
flags.DEFINE_string("log", "arena.log", "Where to save log.")
flags.DEFINE_integer("num_actors", 1, "How many actors to play.")

flags.DEFINE_bool("pcr", True, "")
flags.DEFINE_float("pcr_p", 0.25, "")
flags.DEFINE_float("pcr_f", 0.25, "")

flags.DEFINE_bool("fpptp", True, "")
flags.DEFINE_float("fpptp_k", 2., "")
flags.DEFINE_float("fpptp_e", 0.5, "")

FLAGS = flags.FLAGS


def _opt_print(*args, **kwargs):
  if not FLAGS.quiet:
    print(*args, **kwargs)


def _init_bot(bot_type, game, player_id):
  """Initializes a bot by type."""
  rng = np.random.RandomState(FLAGS.seed)
  if bot_type == "mcts":
    evaluator = mcts.RandomRolloutEvaluator(FLAGS.rollout_count, rng)
    maxsim = FLAGS.max_simulations if player_id == 0 else FLAGS.max_simulations2
    return mcts.MCTSBot(
        game,
        FLAGS.uct_c,
        maxsim,
        evaluator,
        random_state=rng,
        solve=FLAGS.solve,
        verbose=FLAGS.verbose)
  if bot_type == "az":
    path = FLAGS.az_path if player_id == 0 else FLAGS.az_path2
    model = az_model.Model.from_checkpoint(path)
    evaluator = az_evaluator.AlphaZeroEvaluator(game, model)
    return mcts.MCTSBot(
        game,
        FLAGS.uct_c,
        10,
        evaluator,
        random_state=rng,
        child_selection_fn=mcts.SearchNode.puct_value,
        solve=FLAGS.solve,
        verbose=FLAGS.verbose,
        use_playout_cap_randomization = False,
        use_forced_playouts_and_policy_target_pruning = False,
        playout_cap_randomization_p = 0.25,
        playout_cap_randomization_fraction = 0.25,
        forced_playouts_and_policy_target_pruning_k = 2,
        forced_playouts_and_policy_target_pruning_exponent = 0.5)
    # return azbot.AZBot(
        # game,
        # evaluator,)
  if bot_type == "random":
    return uniform_random.UniformRandomBot(player_id, rng)
  if bot_type == "human":
    return human.HumanBot()
  if bot_type == "gtp":
    bot = gtp.GTPBot(game, FLAGS.gtp_path)
    for cmd in FLAGS.gtp_cmd:
      bot.gtp_cmd(cmd)
    return bot
  raise ValueError("Invalid bot type: %s" % bot_type)


def _get_action(state, action_str):
  for action in state.legal_actions():
    if action_str == state.action_to_string(state.current_player(), action):
      return action
  return None


def _play_game(game, bots, initial_actions):
  """Plays one game."""
  state = game.new_initial_state()
  _opt_print("Initial state:\n{}".format(state))

  history = []

  if FLAGS.random_first:
    assert not initial_actions
    initial_actions = [state.action_to_string(
        state.current_player(), random.choice(state.legal_actions()))]

  for action_str in initial_actions:
    action = _get_action(state, action_str)
    if action is None:
      sys.exit("Invalid action: {}".format(action_str))

    history.append(action_str)
    for bot in bots:
      bot.inform_action(state, state.current_player(), action)
    state.apply_action(action)
    _opt_print("Forced action", action_str)
    _opt_print("Next state:\n{}".format(state))

  while not state.is_terminal():
    current_player = state.current_player()
    # The state can be three different types: chance node,
    # simultaneous node, or decision node
    if state.is_chance_node():
      # Chance node: sample an outcome
      outcomes = state.chance_outcomes()
      num_actions = len(outcomes)
      _opt_print("Chance node, got " + str(num_actions) + " outcomes")
      action_list, prob_list = zip(*outcomes)
      action = np.random.choice(action_list, p=prob_list)
      action_str = state.action_to_string(current_player, action)
      _opt_print("Sampled action: ", action_str)
    elif state.is_simultaneous_node():
      raise ValueError("Game cannot have simultaneous nodes.")
    else:
      # Decision node: sample action for the single current player
      bot = bots[current_player]
      action = bot.step(state)
      action_str = state.action_to_string(current_player, action)
      _opt_print("Player {} sampled action: {}".format(current_player,
                                                       action_str))

    for i, bot in enumerate(bots):
      if i != current_player:
        bot.inform_action(state, current_player, action)
    history.append(action_str)
    state.apply_action(action)

    _opt_print("Next state:\n{}".format(state))

  returns = state.returns()
  # print("Returns:", " ".join(map(str, returns)), ", Game actions:", " ".join(history))

  for bot in bots:
    bot.restart()

  return returns, history

def actor(*, game, queue):
    bots = [
        _init_bot(FLAGS.player1, game, 0),
        _init_bot(FLAGS.player2, game, 1),
    ]
    l = []
    overall_wins = np.zeros((3))
    for game_num in range(FLAGS.num_games):
        returns, history = _play_game(game, bots, [])
        if returns[0] > 0:
            overall_wins[0] += 1
        elif returns[0] < 0:
            overall_wins[1] += 1
        elif returns[0] == 0:
            overall_wins[2] += 1
        l.append(returns[0])
    queue.put(overall_wins)

def parallel(argv):
    game = pyspiel.load_game(FLAGS.game)
    actors = [spawn.Process(actor, kwargs={"game":game}) for i in range(FLAGS.num_actors)]
    overall = np.zeros((3))
    for proc in actors:
      p = proc.queue.get()
      overall += p
      proc.join(0.1)
    if FLAGS.player1 == "mcts":
        player1 = "mcts" + str(FLAGS.max_simulations)
    if FLAGS.player2 == "mcts":
        player2 = "mcts" + str(FLAGS.max_simulations2)
    if FLAGS.player1 == "az":
        player1 = "az" + str(FLAGS.az_path.split('checkpoint-')[1]) + FLAGS.name
    if FLAGS.player2 == "az":
        player2 = "az" + str(FLAGS.az_path2.split('checkpoint-')[1]) + FLAGS.name2
    print(player1, "v.s.", player2, "results", overall)

def main(argv):
    game = pyspiel.load_game(FLAGS.game)
    bots = [
        _init_bot(FLAGS.player1, game, 0),
        _init_bot(FLAGS.player2, game, 1),
    ]
    histories = collections.defaultdict(int)
    average_return = 0
    overall_wins = [0, 0, 0]
    game_num = 0
    l = []
    if FLAGS.player1 == "mcts":
        FLAGS.player1 = "mcts" + str(FLAGS.max_simulations)
    if FLAGS.player2 == "mcts":
        FLAGS.player2 = "mcts" + str(FLAGS.max_simulations2)
    if FLAGS.player1 == "az":
        FLAGS.player1 = "az" + str(FLAGS.az_path.split('checkpoint-')[1]) + FLAGS.name
    if FLAGS.player2 == "az":
        FLAGS.player2 = "az" + str(FLAGS.az_path2.split('checkpoint-')[1]) + FLAGS.name2
    for game_num in range(FLAGS.num_games):
        returns, history = _play_game(game, bots, argv[1:])
        histories[" ".join(history)] += 1
        average_return += returns[0]
        if returns[0] > 0:
            overall_wins[0] += 1
        elif returns[0] < 0:
            overall_wins[1] += 1
        elif returns[0] == 0:
            overall_wins[2] += 1
        l.append(returns[0])
    print(FLAGS.player1, "v.s.", FLAGS.player2, "results", overall_wins)
    f = open(FLAGS.log, 'a')
    f.write(FLAGS.player1 + "/" + FLAGS.player2 + "/" + str(l) + '\n')
    f.close()
    # tf.keras.backend.clear_session()
    # print("Average return", average_return/FLAGS.num_games)

if __name__ == "__main__":
    app.run(main)
