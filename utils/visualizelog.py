import matplotlib.pyplot as plt
files = ["dab/tree-2/log-learner.txt", "dab/tree-0/log-learner.txt", "dab/tree-1/log-learner.txt"]

for f in files:
    log = []
    lines = open(f).readlines()
    for line in lines:
        if len(line.split('Losses')) > 1:
            log.append(float(line.split('total: ')[-1][:5]))
    plt.plot(range(len(log)), log)
plt.show()
