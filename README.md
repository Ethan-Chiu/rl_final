# Techniques for Accelerating Self-play in Board Games

This code base is extended from the OpenSpiel by Deepmind.

# How to install

1. Install open_spiel

    ```bash
    cd open_spiel
    ./install.sh
    ```

2. Setup python enviroment

    Install your dependencies in Python 3 using `virtualenv`:

    ```bash
    virtualenv -p python3 venv
    source venv/bin/activate
    ```

    `pip` should be installed once and upgraded:

    ```bash
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    pip3 install --upgrade pip
    pip3 install --upgrade setuptools testresources
    ```

    ```bash
    pip install tensorflow # make sure you install the correct version that fits your device
    ```

3. Build games

    ```bash
    # in open_spiel directory
    python3 -m pip install -r requirements.txt
    ./open_spiel/scripts/build_and_run_tests.sh
    ``````

4. Python environment variable
    
    ```bash
    # For the python modules in open_spiel.
    export PYTHONPATH=$PYTHONPATH:/<path_to_open_spiel>
    # For the Python bindings of Pyspiel
    export PYTHONPATH=$PYTHONPATH:/<path_to_open_spiel>/build/python
    ``````

# How to execute

1. Finish the installation steps.

2. Run experiment

    Activate the virtualenv first.

    ```bash
    cd utils
    python runner.py --path=../open_spiel/results/<experiment name>
    ``````

# A list of available commmand line arguments

This Python script `runner.py` accepts the following command line arguments:

**Path**
- `--path`: Specifies the path to save checkpoints. Default value is "dab/test".

**Maximum Steps**
- `--max_steps`: Sets the number of simulations to run. Default value is 100.

**Maximum Simulations**
- `--max_simulations`: Sets the maximum number of simulations to run. Default value is 100.

**Playout Cap Randomization**
- `--pcr`: Enables playout_cap_randomization.
- `--pcr_p`: Sets the playout_cap_randomization_p. Default value is 1.0.
- `--pcr_f`: Sets the playout_cap_randomization_fraction. Default value is 1.0.

**Forced Playouts and Policy Target Pruning**
- `--fpptp`: Enables forced_playouts_and_policy_target_pruning.
- `--fpptp_k`: Sets the forced_playouts_and_policy_target_pruning_k. Default value is 1.0.
- `--fpptp_e`: Sets the forced_playouts_and_policy_target_pruning_exponent. Default value is 1.0.

**Growing**
- `--grow`: Sets the growing parameter. Default value is 0.

**Fill**
- `--fill`: Sets the fill parameter. Default value is 0.

**Auxiliary Policy Target**
- `--apt`: Enables auxiliary_policy_target.
- `--apt_w`: Sets the auxiliary_policy_target_weight. Default value is 1.0.

**Game Branch**
- `--gb`: Enables game_branch.
- `--gb_n`: Sets the game_branch_number. Default value is 1.
- `--gb_mp`: Sets the game_branch_max_prob. Default value is 0.5.
- `--gb_pp`: Sets the game_branch_prob_power. Default value is 4.


# Reference

```bibtex
@article{LanctotEtAl2019OpenSpiel,
  title     = {{OpenSpiel}: A Framework for Reinforcement Learning in Games},
  author    = {Marc Lanctot and Edward Lockhart and Jean-Baptiste Lespiau and
               Vinicius Zambaldi and Satyaki Upadhyay and Julien P\'{e}rolat and
               Sriram Srinivasan and Finbarr Timbers and Karl Tuyls and
               Shayegan Omidshafiei and Daniel Hennes and Dustin Morrill and
               Paul Muller and Timo Ewalds and Ryan Faulkner and J\'{a}nos Kram\'{a}r
               and Bart De Vylder and Brennan Saeta and James Bradbury and David Ding
               and Sebastian Borgeaud and Matthew Lai and Julian Schrittwieser and
               Thomas Anthony and Edward Hughes and Ivo Danihelka and Jonah Ryan-Davis},
  year      = {2019},
  eprint    = {1908.09453},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  journal   = {CoRR},
  volume    = {abs/1908.09453},
  url       = {http://arxiv.org/abs/1908.09453},
}
```