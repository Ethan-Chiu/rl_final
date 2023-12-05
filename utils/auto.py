import os

path = ['test3', 'test4']
pcr_p = [0.5, 0.25]
pcr_f = [0.5, 0.5]

for i in range(2):
    command = f"python runner.py --path=dab/{path[i]} --pcr=True --pcr_p={str(pcr_p[i])} --pcr_f={str(pcr_f[i])}"
    os.popen(command).read()
