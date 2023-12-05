import matplotlib.pyplot as plt
# files = ["dab/tree-2/log-learner.txt", "dab/tree-0/log-learner.txt", "dab/tree-1/log-learner.txt"]
files = ["/home/howard/RL/final_project/results/test_dots_and_boxes_3*3_all_1_maxsim100/log-learner.txt",]
splits=["total","policy","value","l2","opp"]
split="total"
for i,split in enumerate(splits):
    plt.figure()
    for f in files:
        log = []
        lines = open(f).readlines()
        for line in lines:
            if len(line.split('Losses')) > 1:
                log.append(float(line.split(f'{split}: ')[-1][:5]))
        plt.plot(range(len(log)), log, label=f.split("/")[-2])
    plt.legend()
    plt.xlabel("steps")
    plt.ylabel("loss")
    plt.title(f"{split} loss")
plt.show()
