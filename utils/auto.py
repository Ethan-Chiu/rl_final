import os

path = [
        # "test_dots_and_boxes_3*3_new_pcr_0.25_0.2",
        # "test_dots_and_boxes_3*3_new_pcr_0.25_0.3",
        # "test_dots_and_boxes_3*3_new_pcr_0.5_0.2",
        # "test_dots_and_boxes_3*3_new_pcr_0.5_0.3",
        "test_dots_and_boxes_3*3_new_pcr_0.75_0.02",
        "test_dots_and_boxes_3*3_new_pcr_0.75_0.05",
        # "test_dots_and_boxes_3*3_new_pcr_0.25_0.1",
        # "test_dots_and_boxes_3*3_new_pcr_0.25_0.1",
        ]
# path = ['test_dots_and_boxes_3*3_apt_0.25',]
p=[0.75,0.75]
f =[0.02,0.05]
max_steps=[150,150]
for i in range(len(path)):
    command = f"python runner.py --path=/home/howard/RL/final_project/results/{path[i]} --pcr=True --pcr_p={p[i]} --pcr_f={f[i]} --max_steps={max_steps[i]}"
    os.popen(command).read()
   
