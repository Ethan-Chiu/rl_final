# Copyright 2019 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A basic AlphaZero implementation.

This implements the AlphaZero training algorithm. It spawns N actors which feed
trajectories into a replay buffer which are consumed by a learner. The learner
generates new weights, saves a checkpoint, and tells the actors to update. There
are also M evaluators running games continuously against a standard MCTS+Solver,
though each at a different difficulty (ie number of simulations for MCTS).

Due to the multi-process nature of this algorithm the logs are written to files,
one per process. The learner logs are also output to stdout. The checkpoints are
also written to the same directory.

Links to relevant articles/papers:
  https://deepmind.com/blog/article/alphago-zero-starting-scratch has an open
    access link to the AlphaGo Zero nature paper.
  https://deepmind.com/blog/article/alphazero-shedding-new-light-grand-games-chess-shogi-and-go
    has an open access link to the AlphaZero science paper.
"""

import collections
import datetime
import functools
import itertools
import json
import os
import random
import sys
import tempfile
import time
import traceback

import numpy as np

from open_spiel.python.algorithms import mcts
from open_spiel.python.algorithms.alpha_zero import evaluator as evaluator_lib
from open_spiel.python.algorithms.alpha_zero import model as model_lib
import pyspiel
from open_spiel.python.utils import data_logger
from open_spiel.python.utils import file_logger
from open_spiel.python.utils import spawn
from open_spiel.python.utils import stats

# Time to wait for processes to join.
JOIN_WAIT_DELAY = 0.001


class TrajectoryState(object):
  """A particular point along a trajectory."""

  def __init__(self, observation, current_player, legals_mask, action, policy,
               value, opp_policy, opp_legals_mask):
    self.observation = observation
    self.current_player = current_player
    self.legals_mask = legals_mask
    self.action = action
    self.policy = policy
    self.value = value
    # NOTE: ADD opp_policy
    self.opp_policy = opp_policy
    self.opp_legals_mask = opp_legals_mask


class Trajectory(object):
  """A sequence of observations, actions and policies, and the outcomes."""

  def __init__(self):
    self.states = []
    self.returns = None

  def add(self, information_state, action, policy):
    self.states.append((information_state, action, policy))


class Buffer(object):
  """A fixed size buffer that keeps the newest values."""

  def __init__(self, max_size):
    self.max_size = max_size
    self.data = []
    self.total_seen = 0  # The number of items that have passed through.

  def __len__(self):
    return len(self.data)

  def __bool__(self):
    return bool(self.data)

  def append(self, val):
    return self.extend([val])

  def extend(self, batch):
    batch = list(batch)
    self.total_seen += len(batch)
    self.data.extend(batch)
    self.data[:-self.max_size] = []

  def sample(self, count):
    return random.sample(self.data, count)


class Config(collections.namedtuple(
    "Config", [
        "game",
        "path",
        "learning_rate",
        "weight_decay",
        "train_batch_size",
        "replay_buffer_size",
        "replay_buffer_reuse",
        "max_steps",
        "checkpoint_freq",
        "actors",
        "evaluators",
        "evaluation_window",
        "eval_levels",

        "uct_c",
        "max_simulations",
        "policy_alpha",
        "policy_epsilon",
        "temperature",
        "temperature_drop",

        "nn_model",
        "nn_width",
        "nn_depth",
        "observation_shape",
        "output_size",

        "quiet",

        "use_playout_cap_randomization",
        "playout_cap_randomization_p",
        "playout_cap_randomization_fraction",

        "use_forced_playouts_and_policy_target_pruning",
        "forced_playouts_and_policy_target_pruning_k",
        "forced_playouts_and_policy_target_pruning_exponent",

        "growing", # 0: ordinary, 1: reusing simulations for both player(expected fastest), 2: each player has a tree
        "fill", # 0: constant simulations per action, 1: fill to the max_simulation

        "use_auxiliary_policy_target",
        "auxiliary_policy_target_weight", # weight for auxiliary policy targets (opponent's policy) loss

        "use_game_branch",
        "game_branch_number",
        "game_branch_max_prob",
        "game_branch_prob_power",
    ])):
  """A config for the model/experiment."""
  pass


def _init_model_from_config(config):
  return model_lib.Model.build_model(
      config.nn_model,
      config.observation_shape,
      config.output_size,
      config.nn_width,
      config.nn_depth,
      config.weight_decay,
      config.learning_rate,
      config.path,
      # NOTE: for auxiliary policy target
      config.use_auxiliary_policy_target,
      config.auxiliary_policy_target_weight,
      )


def watcher(fn):
  """A decorator to fn/processes that gives a logger and logs exceptions."""
  @functools.wraps(fn)
  def _watcher(*, config, num=None, **kwargs):
    """Wrap the decorated function."""
    name = fn.__name__
    if num is not None:
      name += "-" + str(num)
    with file_logger.FileLogger(config.path, name, config.quiet) as logger:
      print("{} started".format(name))
      logger.print("{} started".format(name))
      try:
        return fn(config=config, logger=logger, **kwargs)
      except Exception as e:
        logger.print("\n".join([
            "",
            " Exception caught ".center(60, "="),
            traceback.format_exc(),
            "=" * 60,
        ]))
        print("Exception caught in {}: {}".format(name, e))
        raise
      finally:
        logger.print("{} exiting".format(name))
        print("{} exiting".format(name))
  return _watcher


def _init_bot(config, game, evaluator_, evaluation):
  """Initializes a bot."""
  noise = None if evaluation else (config.policy_epsilon, config.policy_alpha)
  return mcts.MCTSBot(
      game,
      config.uct_c,
      config.max_simulations,
      evaluator_,
      config.use_playout_cap_randomization,
      config.playout_cap_randomization_p,
      config.playout_cap_randomization_fraction,
      config.use_forced_playouts_and_policy_target_pruning,
      config.forced_playouts_and_policy_target_pruning_k,
      config.forced_playouts_and_policy_target_pruning_exponent,
      random_state=np.random.RandomState(),
      solve=False,
      dirichlet_noise=noise,
      child_selection_fn=mcts.SearchNode.puct_value,
      verbose=False,
      dont_return_chance_node=True)

def _play_game(config,logger, game_num, game, bots, temperature, temperature_drop, 
               growing, fill, 
               use_apt, 
               use_game_branch, game_len_stat, branch_num, game_branch_max_prob, game_branch_prob_power):
  # Start a new game
  init_state = game.new_initial_state()
  trajectory, branch_states = _play_game_from_state(config,init_state, logger, game_num, game, bots, temperature, temperature_drop, 
                                                    growing, fill,
                                                    use_apt, 
                                                    use_game_branch, game_len_stat, game_branch_max_prob, game_branch_prob_power)
  trajectory_list: list[Trajectory] = []
  trajectory_list.append(trajectory)

  # If use game branch, sample some middle states and play on
  if use_game_branch:
    branch_states_count = len(branch_states)
    logger.print("Branch game, Total branch count: {};".format(branch_states_count))

    # indices = random.choices(range(branch_states_count), k = branch_num)
    # for idx_s in indices:
    #   s = branch_states[idx_s]
    #   bs = s[0].clone()
    #   alt_action = s[2]
    #   logger.print("Taken action {} instead of best action {}".format(bs.action_to_string(bs.current_player(), alt_action), bs.action_to_string(bs.current_player(), s[1])))
    #   bs.apply_action(alt_action)
    #   t, _ = _play_game_from_state(config, bs, logger, game_num, game, bots, temperature, temperature_drop, 
    #                                growing, fill, 
    #                                use_apt, 
    #                                False, None, 0, 0)
    #   trajectory_list.append(t)

    sample_count = branch_num if branch_num <= branch_states_count else branch_states_count
    sampled_branch_states = random.sample(branch_states, sample_count)
      
    for s in sampled_branch_states:
      bs = s[0]
      alt_action = s[2]
      logger.print("Taken action {} instead of best action {}".format(bs.action_to_string(bs.current_player(), alt_action), bs.action_to_string(bs.current_player(), s[1])))
      bs.apply_action(alt_action)
      t, _ = _play_game_from_state(config, bs, logger, game_num, game, bots, temperature, temperature_drop, 
                                   growing, fill, 
                                   use_apt, 
                                   False, None, 0, 0)
      trajectory_list.append(t)

  return trajectory_list
  

def _play_game_from_state(config,init_state, logger, game_num, game, bots, temperature, temperature_drop, 
                          growing, fill, 
                          use_apt, 
                          use_game_branch, mean_game_len, game_branch_max_prob, game_branch_prob_power):
  """Play one game, return the trajectory."""
  trajectory = Trajectory()
  actions = []
  state = init_state
  random_state = np.random.RandomState()
  logger.opt_print(" Starting game {} ".format(game_num).center(60, "-"))
  logger.opt_print("Initial state:\n{}".format(state))
  tree = [None] * 2
  # NOTE: For use game branch
  branch_states = []
  current_len = 0
  while not state.is_terminal():
    if state.is_chance_node():
      # For chance nodes, rollout according to chance node's probability
      # distribution
      outcomes = state.chance_outcomes()
      action_list, prob_list = zip(*outcomes)
      action = random_state.choice(action_list, p=prob_list)
      state.apply_action(action)
    else:
      player = state.current_player()
      if growing == 2:
          root = bots[player].mcts_search(state, tree[player], fill)
      elif growing == 1:
          root = bots[player].mcts_search(state, tree[0], fill)
      else:
          root = bots[player].mcts_search(state, None, fill)
      policy = np.zeros(game.num_distinct_actions())
      best_action = root.best_child().action
      for c in root.children:
        policy[c.action] = c.pruned_explore_count(root.explore_count, best_action == c.action)
      policy = policy**(1 / temperature)
      # print("normal", policy.sum())
      policy /= policy.sum()
      if len(actions) >= temperature_drop:
        action = best_action
      else:
        action = np.random.choice(len(policy), p=policy)

      # NOTE: Calculate target opp policy
      opp_policy = np.zeros(game.num_distinct_actions())
      if use_apt:
        best_child = root.best_child()
        if len(best_child.children) != 0:
          best_child_action = best_child.best_child().action
          for cc in best_child.children:
            opp_policy[cc.action] = cc.pruned_explore_count(best_child.explore_count, best_child_action == cc.action)
          opp_policy = opp_policy**(1 / temperature)
          opp_policy /= opp_policy.sum()
        else:
          opp_policy[:] = 1/len(opp_policy)
      
      observation = state.observation_tensor()
      current_player = state.current_player()
      legal_actions_mask = state.legal_actions_mask()

      # NOTE: growing technique
      if growing == 2:
          for c in root.children:
              if c.action == action:
                  tree[player] = c
                  break
          else:
              tree[player] = None
          notroot = tree[1-player]
          if notroot:
              for c in notroot.children:
                  if c.action == action:
                      tree[1-player] = c
                      break
              else:
                  tree[1-player] = None
      elif growing == 1:
          for c in root.children:
              if c.action == action:
                  tree[0] = c
                  break
    
      action_str = state.action_to_string(state.current_player(), action)

      # NOTE: Use game branch 
      if use_game_branch:
        go_branch = False
        if game_branch_max_prob <= 1:
          p = game_branch_max_prob * (2 * (0.5 - abs((current_len / mean_game_len) - 0.5)))**game_branch_prob_power
          p = 0 if p < 0 else p
          p = p if p < game_branch_max_prob else game_branch_max_prob
          if random.random() < p:
            clone_state = state.clone()
            policy_without_best = policy.copy()
            policy_without_best[action] = 0.0
            sum = policy_without_best.sum()
            # print("debug", sum)
            if not sum == 0:
              policy_without_best /= sum
              alt_action = np.random.choice(len(policy_without_best), p=policy_without_best)
            else:
              alt_action = best_action
            branch_states.append((clone_state, action, alt_action))
        elif current_len == game_branch_max_prob:
            policy_without_best = policy.copy()
            policy_without_best[action] = 0.0
            for z in range(config.game_branch_number):
                clone_state = state.clone()
                sum = policy_without_best.sum()
                if not sum == 0:
                  alt_action = np.random.choice(len(policy_without_best), p=policy_without_best/sum)
                else:
                  alt_action = best_action
                policy_without_best[alt_action] = 0.0
                branch_states.append((clone_state, action, alt_action))
            

      # NOTE: Add opp_legal_actions_mask
      state.apply_action(action)
      opp_legal_actions_mask = state.legal_actions_mask()

      trajectory.states.append(
          TrajectoryState(observation, current_player,
                          legal_actions_mask, action, policy,
                          root.total_reward / root.explore_count,
                          opp_policy, opp_legal_actions_mask))
      
      actions.append(action_str)
      logger.opt_print("Player {} sampled action: {}".format(
          current_player, action_str))
    current_len += 1
      
  logger.opt_print("Next state:\n{}".format(state))

  trajectory.returns = state.returns()
  logger.print("Game {}: Returns: {}; Actions: {}".format(
      game_num, " ".join(map(str, trajectory.returns)), " ".join(actions)))
  return trajectory, branch_states


def update_checkpoint(logger, queue, model, az_evaluator):
  """Read the queue for a checkpoint to load, or an exit signal."""
  path = None
  while True:  # Get the last message, ignore intermediate ones.
    try:
      path = queue.get_nowait()
    except spawn.Empty:
      break
  if path:
    logger.print("Inference cache:", az_evaluator.cache_info())
    logger.print("Loading checkpoint", path)
    model.load_checkpoint(path)
    az_evaluator.clear_cache()
  elif path is not None:  # Empty string means stop this process.
    return False
  return True


@watcher
def actor(*, config, game, logger, queue):
  """An actor process runner that generates games and returns trajectories."""
  logger.print("Initializing model")
  model = _init_model_from_config(config)
  logger.print("Initializing bots")
  az_evaluator = evaluator_lib.AlphaZeroEvaluator(game, model)
  bots = [
      _init_bot(config, game, az_evaluator, False),
      _init_bot(config, game, az_evaluator, False),
  ]
  length_stat = []
  mean_length = 1
  for game_num in itertools.count():
    if not update_checkpoint(logger, queue, model, az_evaluator):
      return
    trajectories = _play_game(config,logger, game_num, game, bots, temperature=config.temperature,
                         temperature_drop=config.temperature_drop, growing=config.growing, fill=config.fill,
                         use_apt=config.use_auxiliary_policy_target, 
                         use_game_branch=config.use_game_branch, game_len_stat=mean_length, branch_num=config.game_branch_number, game_branch_max_prob=config.game_branch_max_prob, game_branch_prob_power=config.game_branch_prob_power)
    
    for t in trajectories:
      if len(t.states) > 0:
        queue.put(t)

    # NOTE: stat for game length. only take the first trajectory, since the first trajectory is complete
    length_stat.append(len(trajectories[0].states))
    mean_length = sum(length_stat) / len(length_stat)


@watcher
def evaluator(*, game, config, logger, queue):
  """A process that plays the latest checkpoint vs standard MCTS."""
  results = Buffer(config.evaluation_window)
  logger.print("Initializing model")
  model = _init_model_from_config(config)
  logger.print("Initializing bots")
  az_evaluator = evaluator_lib.AlphaZeroEvaluator(game, model)
  random_evaluator = mcts.RandomRolloutEvaluator(random_state=np.random.RandomState())

  for game_num in itertools.count():
    if not update_checkpoint(logger, queue, model, az_evaluator):
      return

    az_player = game_num % 2
    difficulty = (game_num // 2) % config.eval_levels
    max_simulations = int(config.max_simulations * (10 ** (difficulty / 2)))
    bots = [
        _init_bot(config, game, az_evaluator, True),
        mcts.MCTSBot(
            game,
            config.uct_c,
            max_simulations,
            random_evaluator,
            random_state=np.random.RandomState(),
            use_playout_cap_randomization=config.use_playout_cap_randomization,
            playout_cap_randomization_p=config.playout_cap_randomization_p,
            playout_cap_randomization_fraction=config.playout_cap_randomization_fraction,
            use_forced_playouts_and_policy_target_pruning=config.use_forced_playouts_and_policy_target_pruning,
            forced_playouts_and_policy_target_pruning_k=config.forced_playouts_and_policy_target_pruning_k,
            forced_playouts_and_policy_target_pruning_exponent=config.forced_playouts_and_policy_target_pruning_exponent,
            solve=True,
            verbose=False,
            dont_return_chance_node=True)
    ]
    if az_player == 1:
      bots = list(reversed(bots))

    trajectory = _play_game(config,logger, game_num, game, bots, temperature=1,
                            temperature_drop=0, growing=0, fill=0,
                            use_apt=config.use_auxiliary_policy_target, 
                            use_game_branch=False, game_len_stat=None, branch_num=None, game_branch_max_prob=None, game_branch_prob_power=None)[0]
    results.append(trajectory.returns[az_player])
    queue.put((difficulty, trajectory.returns[az_player]))

    logger.print("AZ: {}, MCTS: {}, AZ avg/{}: {:.3f}".format(
        trajectory.returns[az_player],
        trajectory.returns[1 - az_player],
        len(results), np.mean(results.data)))


@watcher
def learner(*, game, config, actors, evaluators, broadcast_fn, logger):
  """A learner that consumes the replay buffer and trains the network."""
  logger.also_to_stdout = True
  replay_buffer = Buffer(config.replay_buffer_size)
  learn_rate = config.replay_buffer_size // config.replay_buffer_reuse
  logger.print("Initializing model")
  model = _init_model_from_config(config)
  logger.print("Model type: %s(%s, %s)" % (config.nn_model, config.nn_width,
                                           config.nn_depth))
  logger.print("Model size:", model.num_trainable_variables, "variables")
  save_path = model.save_checkpoint(0)
  logger.print("Initial checkpoint:", save_path)
  broadcast_fn(save_path)

  data_log = data_logger.DataLoggerJsonLines(config.path, "learner", True)

  stage_count = 7
  value_accuracies = [stats.BasicStats() for _ in range(stage_count)]
  value_predictions = [stats.BasicStats() for _ in range(stage_count)]
  game_lengths = stats.BasicStats()
  game_lengths_hist = stats.HistogramNumbered(game.max_game_length() + 1)
  outcomes = stats.HistogramNamed(["Player1", "Player2", "Draw"])
  evals = [Buffer(config.evaluation_window) for _ in range(config.eval_levels)]
  total_trajectories = 0

  def trajectory_generator():
    """Merge all the actor queues into a single generator."""
    while True:
      found = 0
      for actor_process in actors:
        try:
          yield actor_process.queue.get_nowait()
        except spawn.Empty:
          pass
        else:
          found += 1
      if found == 0:
        time.sleep(0.01)  # 10ms

  def collect_trajectories():
    """Collects the trajectories from actors into the replay buffer."""
    num_trajectories = 0
    num_states = 0
    for trajectory in trajectory_generator():
      num_trajectories += 1
      num_states += len(trajectory.states)
      game_lengths.add(len(trajectory.states))
      game_lengths_hist.add(len(trajectory.states))

      p1_outcome = trajectory.returns[0]
      if p1_outcome > 0:
        outcomes.add(0)
      elif p1_outcome < 0:
        outcomes.add(1)
      else:
        outcomes.add(2)

      replay_buffer.extend(
          model_lib.TrainInput(
              s.observation, s.legals_mask, s.policy, p1_outcome, s.opp_policy, s.opp_legals_mask)
          for s in trajectory.states)

      for stage in range(stage_count):
        # Scale for the length of the game
        index = (len(trajectory.states) - 1) * stage // (stage_count - 1)
        n = trajectory.states[index]
        accurate = (n.value >= 0) == (trajectory.returns[n.current_player] >= 0)
        value_accuracies[stage].add(1 if accurate else 0)
        value_predictions[stage].add(abs(n.value))

      if num_states >= learn_rate:
        break
    return num_trajectories, num_states

  def learn(step):
    """Sample from the replay buffer, update weights and save a checkpoint."""
    losses = []
    for _ in range(len(replay_buffer) // config.train_batch_size):
      data = replay_buffer.sample(config.train_batch_size)
      losses.append(model.update(data))

    # Always save a checkpoint, either for keeping or for loading the weights to
    # the actors. It only allows numbers, so use -1 as "latest".
    save_path = model.save_checkpoint(
        step if step % config.checkpoint_freq == 0 else -1)
    losses = sum(losses, model_lib.Losses(0, 0, 0, 0)) / len(losses)
    logger.print(losses)
    logger.print("Checkpoint saved:", save_path)
    return save_path, losses

  last_time = time.time() - 60
  for step in itertools.count(1):
    for value_accuracy in value_accuracies:
      value_accuracy.reset()
    for value_prediction in value_predictions:
      value_prediction.reset()
    game_lengths.reset()
    game_lengths_hist.reset()
    outcomes.reset()

    num_trajectories, num_states = collect_trajectories()
    total_trajectories += num_trajectories
    now = time.time()
    seconds = now - last_time
    last_time = now

    logger.print("Step:", step)
    logger.print(
        ("Collected {:5} states from {:3} games, {:.1f} states/s. "
         "{:.1f} states/(s*actor), game length: {:.1f}").format(
             num_states, num_trajectories, num_states / seconds,
             num_states / (config.actors * seconds),
             num_states / num_trajectories))
    logger.print("Buffer size: {}. States seen: {}".format(
        len(replay_buffer), replay_buffer.total_seen))

    save_path, losses = learn(step)

    for eval_process in evaluators:
      while True:
        try:
          difficulty, outcome = eval_process.queue.get_nowait()
          evals[difficulty].append(outcome)
        except spawn.Empty:
          break

    batch_size_stats = stats.BasicStats()  # Only makes sense in C++.
    batch_size_stats.add(1)
    data_log.write({
        "step": step,
        "total_states": replay_buffer.total_seen,
        "states_per_s": num_states / seconds,
        "states_per_s_actor": num_states / (config.actors * seconds),
        "total_trajectories": total_trajectories,
        "trajectories_per_s": num_trajectories / seconds,
        "queue_size": 0,  # Only available in C++.
        "game_length": game_lengths.as_dict,
        "game_length_hist": game_lengths_hist.data,
        "outcomes": outcomes.data,
        "value_accuracy": [v.as_dict for v in value_accuracies],
        "value_prediction": [v.as_dict for v in value_predictions],
        "eval": {
            "count": evals[0].total_seen,
            "results": [sum(e.data) / len(e) if e else 0 for e in evals],
        },
        "batch_size": batch_size_stats.as_dict,
        "batch_size_hist": [0, 1],
        "loss": {
            "policy": losses.policy,
            "value": losses.value,
            "l2reg": losses.l2,
            "opp_policy": losses.opp,
            "sum": losses.total,
        },
        "cache": {  # Null stats because it's hard to report between processes.
            "size": 0,
            "max_size": 0,
            "usage": 0,
            "requests": 0,
            "requests_per_s": 0,
            "hits": 0,
            "misses": 0,
            "misses_per_s": 0,
            "hit_rate": 0,
        },
    })
    logger.print()

    if config.max_steps > 0 and step >= config.max_steps:
      break

    broadcast_fn(save_path)


def alpha_zero(config: Config):
  """Start all the worker processes for a full alphazero setup."""
  game = pyspiel.load_game(config.game)
  config = config._replace(
      observation_shape=game.observation_tensor_shape(),
      output_size=game.num_distinct_actions())

  print("Starting game", config.game)
  if game.num_players() != 2:
    sys.exit("AlphaZero can only handle 2-player games.")
  game_type = game.get_type()
  if game_type.reward_model != pyspiel.GameType.RewardModel.TERMINAL:
    raise ValueError("Game must have terminal rewards.")
  if game_type.dynamics != pyspiel.GameType.Dynamics.SEQUENTIAL:
    raise ValueError("Game must have sequential turns.")
  if game_type.chance_mode != pyspiel.GameType.ChanceMode.DETERMINISTIC:
    raise ValueError("Game must be deterministic.")

  path = config.path
  if not path:
    path = tempfile.mkdtemp(prefix="az-{}-{}-".format(
        datetime.datetime.now().strftime("%Y-%m-%d-%H-%M"), config.game))
    config = config._replace(path=path)

  if not os.path.exists(path):
    os.makedirs(path)
  if not os.path.isdir(path):
    sys.exit("{} isn't a directory".format(path))
  print("Writing logs and checkpoints to:", path)
  print("Model type: %s(%s, %s)" % (config.nn_model, config.nn_width,
                                    config.nn_depth))

  with open(os.path.join(config.path, "config.json"), "w") as fp:
    fp.write(json.dumps(config._asdict(), indent=2, sort_keys=True) + "\n")

  actors = [spawn.Process(actor, kwargs={"game": game, "config": config,
                                         "num": i})
            for i in range(config.actors)]
  evaluators = [spawn.Process(evaluator, kwargs={"game": game, "config": config,
                                                 "num": i})
                for i in range(config.evaluators)]

  def broadcast(msg):
    for proc in actors + evaluators:
      proc.queue.put(msg)

  try:
    learner(game=game, config=config, actors=actors,  # pylint: disable=missing-kwoa
            evaluators=evaluators, broadcast_fn=broadcast)
  except (KeyboardInterrupt, EOFError):
    print("Caught a KeyboardInterrupt, stopping early.")
  finally:
    broadcast("")
    # for actor processes to join we have to make sure that their q_in is empty,
    # including backed up items
    for proc in actors:
      while proc.exitcode is None:
        while not proc.queue.empty():
          proc.queue.get_nowait()
        proc.join(JOIN_WAIT_DELAY)
    for proc in evaluators:
      proc.join()
