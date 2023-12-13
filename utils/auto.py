import os

path = ["test_dots_and_boxes_3*3_pcr_0.5_0.25","test_dots_and_boxes_3*3_pcr_0.5_0.5","test_dots_and_boxes_3*3_pcr_0.5_0.75"]
# path = ['test_dots_and_boxes_3*3_apt_0.25',]
f =[0.25,0.5,0.75]
for i in range(len(path)):
    command = f"python runner.py --path=/home/howard/RL/final_project/results/{path[i]} --pcr=True --pcr_p=0.5 --pcr_f={f[i]}"
    os.popen(command).read()
   
