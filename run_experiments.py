import FlowShop
import time

output_file = "results6.txt"
n = 0
delta = 0
tot_tempo_optimize = 0
tot_tempo_mio = 0
with open(output_file, "w") as f:
    f.write("Experiment,Makespan\n")
    f.write("{makespan_optimize} {tempo_optimize} {makespan_mio} {tempo_mio} {lower_bound}\n")

    for i in range(1, 21):

        print(f"\n--- NUMERO TENTTIVO {i} ---")
        makespan_optimize, makespan_mio, tempo_optimize, tempo_mio, lower_bound = FlowShop.main(i)
        f.write(f"{makespan_optimize} {tempo_optimize} {makespan_mio} {tempo_mio} {lower_bound}\n")



