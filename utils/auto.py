import os

path = ['test_dots_and_boxes_3*3_apt_maxsim100']
pcr_p = [0.5, 0.25]
pcr_f = [0.5, 0.5]

for i in range(len(path)):
    command = f"python runner.py --path=/home/howard/RL/final_project/results/{path[i]} --apt=True --apt_w=0.15 "
    os.popen(command).read()
