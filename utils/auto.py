import os

# path = ['dab33_pcr_p05_f025', 'dab33_pcr_p025_f05', 'dab33_pcr_p075_f075', 'dab33_pcr_p075_f025', 'dab33_pcr_p025_f075']
# pcr_p = [0.5, 0.25, 0.75, 0.75, 0.25]
# pcr_f = [0.25, 0.5, 0.75, 0.25, 0.75]
# path = ['dab33_fpptp_k1_5_e05', 'dab33_fpptp_k1_5_e025', 'dab33_fpptp_k2_e025']
# fpptp_k = [1.5, 1.5, 2]
# fpptp_e = [0.5, 0.25, 0.25]
# path = ['dab33_fpptp_k3_e05', 'dab33_fpptp_k3_e075', 'dab33_fpptp_k2_5_e05']
# fpptp_k = [3, 3, 2.5]
# fpptp_e = [0.5, 0.75, 0.5]
# path = ['dab33_none']

path = ['dab33_gb_mp099_n1_3', 'dab33_gb_mp099_n2_3', 'dab33_gb_mp099_n4_3', 'dab33_gb_mp099_n8_3', 'dab33_gb_mp099_n1_4', 'dab33_gb_mp099_n2_4', 'dab33_gb_mp099_n4_4', 'dab33_gb_mp099_n8_4']
gbmp = 0.999
gbn = [1, 2, 4, 8, 1, 2, 4, 8]

for i in range(len(path)):
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --pcr=True --pcr_p={str(pcr_p[i])} --pcr_f={str(pcr_f[i])}"
    # command = f"python runner.py --path=../open_spiel/results/{path[i]} --fpptp=True --fpptp_k={str(fpptp_k[i])} --fpptp_e={str(fpptp_e[i])}"
    # command = f"python runner.py --path=../open_spiel/results/{path[i]}"
    command = f"python runner.py --path=../open_spiel/results/{path[i]} --gb=True --gb_n={str(gbn[i])} --gb_mp={str(gbmp)}"
    os.popen(command).read()
