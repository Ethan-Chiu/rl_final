import os

path = ['dab33_result']

for i in range(len(path)):
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --pcr=True --pcr_p={str(pcr_p[i])} --pcr_f={str(pcr_f[i])}"
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --fpptp=True --fpptp_k={str(fpptp_k[i])} --fpptp_e={str(fpptp_e[i])}"
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --gb=True --gb_n={str(gbn[i])} --gb_mp={str(gbmp)}"
    command = f"python runner.py --path=../open_spiel/results/{path[i]}"
    os.popen(command).read()
