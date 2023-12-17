from absl import app
from absl import flags

from open_spiel.python.algorithms.alpha_zero import alpha_zero
from open_spiel.python.utils import spawn

flags.DEFINE_string("path", "dab/test", "Where to save checkpoints.")
flags.DEFINE_integer("max_steps", 100, "How many simulations to run.")
flags.DEFINE_integer("max_simulations", 100, "How many simulations to run.")
flags.DEFINE_bool("pcr", False, "use playout_cap_randomization")
flags.DEFINE_float("pcr_p", 1., "playout_cap_randomization_p")
flags.DEFINE_float("pcr_f", 1., "playout_cap_randomization_fraction")
flags.DEFINE_bool("fpptp", False, "use forced_playouts_and_policy_target_pruning")
flags.DEFINE_float("fpptp_k", 1., "forced_playouts_and_policy_target_pruning_k")
flags.DEFINE_float("fpptp_e", 1., "forced_playouts_and_policy_target_pruning_exponent")
flags.DEFINE_integer("grow", 0, "growing")
flags.DEFINE_integer("fill", 0, "fill")
flags.DEFINE_bool("apt", False, "use auxiliary_policy_target")
flags.DEFINE_float("apt_w", 1., "auxiliary_policy_target_weight")
flags.DEFINE_bool("gb", False, "use game_branch")
flags.DEFINE_integer("gb_n", 1, "game_branch_number")
flags.DEFINE_float("gb_mp", 0.5, "game_branch_max_prob")
flags.DEFINE_integer("gb_pp", 4, "game_branch_prob_power")
FLAGS = flags.FLAGS

def main(unused_argv):
  config = alpha_zero.Config(
      seed=0,
      game="dots_and_boxes",
      path=FLAGS.path,
      learning_rate=0.01,
      weight_decay=1e-4,
      train_batch_size=64,
      replay_buffer_size=2**14,
      replay_buffer_reuse=10,
      max_steps=FLAGS.max_steps,
      checkpoint_freq=10,

      actors=4,
      evaluators=0,
      uct_c=1,
      max_simulations=FLAGS.max_simulations,
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

      use_playout_cap_randomization = FLAGS.pcr,
      playout_cap_randomization_p = FLAGS.pcr_p,
      playout_cap_randomization_fraction = FLAGS.pcr_f,

      use_forced_playouts_and_policy_target_pruning = FLAGS.fpptp,
      forced_playouts_and_policy_target_pruning_k = FLAGS.fpptp_k,
      forced_playouts_and_policy_target_pruning_exponent = FLAGS.fpptp_e,

      growing = FLAGS.grow,
      fill = FLAGS.fill,

      # APT
      use_auxiliary_policy_target = FLAGS.apt,
      auxiliary_policy_target_weight = FLAGS.apt_w,

      # Game branch
      use_game_branch = FLAGS.gb,
      game_branch_number = FLAGS.gb_n,
      game_branch_max_prob = FLAGS.gb_mp,
      game_branch_prob_power = FLAGS.gb_pp,
  )
  alpha_zero.alpha_zero(config)


if __name__ == "__main__":
  with spawn.main_handler():
    app.run(main)
