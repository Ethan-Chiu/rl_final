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

"""Simple AlphaZero tic tac toe example.

Take a look at the log-learner.txt in the output directory.

If you want more control, check out `alpha_zero.py`.
"""

import os
import random
from absl import app
from absl import flags
import numpy as np
import tensorflow as tf

from open_spiel.python.algorithms.alpha_zero import alpha_zero
from open_spiel.python.utils import spawn

flags.DEFINE_string("path", "../../../results/3x3_test1", "Where to save checkpoints.")
FLAGS = flags.FLAGS
seed = 0

def main(unused_argv):
  config = alpha_zero.Config(
      game="dots_and_boxes",
      path=FLAGS.path,
      learning_rate=0.01,
      weight_decay=1e-4,
      train_batch_size=64,
      replay_buffer_size=2**14,
      replay_buffer_reuse=10,
      max_steps=100,
      checkpoint_freq=10,

      actors=4,
      evaluators=0,
      uct_c=1,
      max_simulations=100,
      policy_alpha=0.25,
      policy_epsilon=0.25,
      temperature=1,
      temperature_drop=24,
      evaluation_window=100,
      eval_levels=18,

      nn_model="resnet",
      nn_width=128,
      nn_depth=2,
      observation_shape=None,
      output_size=None,

      quiet=True,

      use_playout_cap_randomization = False,
      playout_cap_randomization_p = 0.25,
      playout_cap_randomization_fraction = 0.25,

      use_forced_playouts_and_policy_target_pruning = False,
      forced_playouts_and_policy_target_pruning_k = 2,
      forced_playouts_and_policy_target_pruning_exponent = 0.5,

      growing = 0,
      fill = 0,

      # APT
      use_auxiliary_policy_target=False,
      auxiliary_policy_target_weight= 0.25,

      # Game branch
      use_game_branch=False,
      game_branch_number=1,
      game_branch_max_prob=0.5,
      game_branch_prob_power=4,
  )

  set_seed(seed)
  alpha_zero.alpha_zero(config)

def set_seed(seed):
  # os.environ['PYTHONHASHSEED'] = str(seed)
  random.seed(seed)
  np.random.seed(seed)
  # tf.compat.v1.set_random_seed(seed)
  # tf.compat.v1.random.set_random_seed(seed)
  # tf.random.set_seed(seed)
  # tf.experimental.numpy.random.seed(seed)
  # tf.config.experimental.enable_op_determinism()
  # os.environ['TF_DETERMINISTIC_OPS'] = '1'
  # os.environ['TF_CUDNN_DETERMINISTIC'] = '1'


if __name__ == "__main__":
  with spawn.main_handler():
    app.run(main)
