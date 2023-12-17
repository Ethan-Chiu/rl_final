import os

<<<<<<< HEAD
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
=======
# path = ['dab33_pcr_p05_f025', 'dab33_pcr_p025_f05', 'dab33_pcr_p075_f075', 'dab33_pcr_p075_f025', 'dab33_pcr_p025_f075']
# pcr_p = [0.5, 0.25, 0.75, 0.75, 0.25]
# pcr_f = [0.25, 0.5, 0.75, 0.25, 0.75]
path = ['dab33_fpptp_k1_5_e05', 'dab33_fpptp_k1_5_e025', 'dab33_fpptp_k2_e025']
fpptp_k = [1.5, 1.5, 2]
fpptp_e = [0.5, 0.25, 0.25]

for i in range(len(path)):
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --pcr=True --pcr_p={str(pcr_p[i])} --pcr_f={str(pcr_f[i])}"
    command = f"python runner.py --path=../open_spiel/results/{path[i]} --fpptp=True --fpptp_k={str(fpptp_k[i])} --fpptp_e={str(fpptp_e[i])}"
>>>>>>> 70a6728d94ffbdc50295f131fd48045f7561d25d
    os.popen(command).read()
   
