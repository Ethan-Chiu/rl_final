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

from absl import app
from absl import flags

from open_spiel.python.algorithms.alpha_zero import alpha_zero
from open_spiel.python.utils import spawn

flags.DEFINE_string("path", "/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_allFalse_1_maxsim100", "Where to save checkpoints.")
FLAGS = flags.FLAGS

def main(unused_argv):
  config = alpha_zero.Config(
      game="dots_and_boxes",
      path=FLAGS.path,
      learning_rate=0.001,
      weight_decay=1e-4,
      train_batch_size=128,
      replay_buffer_size=2**14,
      replay_buffer_reuse=10,
      max_steps=1000,
      checkpoint_freq=10,

      actors=4,
      evaluators=0,
      uct_c=1,
      max_simulations=100,
      policy_alpha=1,
      policy_epsilon=0.25,
      temperature=1,
      temperature_drop=12,
      evaluation_window=20,
      eval_levels=18,

      nn_model="resnet",
      nn_width=256,
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
      fill = 1,

      # APT
      use_auxiliary_policy_target=False,
      auxiliary_policy_target_weight= 0.15,
  )
  alpha_zero.alpha_zero(config)
  # config = alpha_zero.Config(
  #     game="dots_and_boxes",
  #     path=FLAGS.path,
  #     learning_rate=0.01,
  #     weight_decay=1e-4,
  #     train_batch_size=64,
  #     replay_buffer_size=2**14,
  #     replay_buffer_reuse=10,
  #     max_steps=1000,
  #     checkpoint_freq=10,

  #     actors=4,
  #     evaluators=0,
  #     uct_c=1,
  #     max_simulations=100,
  #     policy_alpha=1,
  #     policy_epsilon=0.25,
  #     temperature=1,
  #     temperature_drop=4,
  #     evaluation_window=20,
  #     eval_levels=18,

  #     nn_model="resnet",
  #     nn_width=256,
  #     nn_depth=2,
  #     observation_shape=None,
  #     output_size=None,

  #     quiet=True,

  #     use_playout_cap_randomization = False,
  #     playout_cap_randomization_p = 0.25,
  #     playout_cap_randomization_fraction = 0.25,

  #     use_forced_playouts_and_policy_target_pruning = False,
  #     forced_playouts_and_policy_target_pruning_k = 2,
  #     forced_playouts_and_policy_target_pruning_exponent = 0.5,

  #     growing = 0,
  #     fill = 1,

  #     # APT
  #     use_auxiliary_policy_target=False,
  #     auxiliary_policy_target_weight= 0.15,
  # )
  # alpha_zero.alpha_zero(config)


if __name__ == "__main__":
  with spawn.main_handler():
    app.run(main)
