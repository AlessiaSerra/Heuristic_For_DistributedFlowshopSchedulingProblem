import funzioni as fz
import time

output_file = "results.txt"


# j,k indice per job, n tot job
# i.l indice per macchina, m tot macchine
# f indice per factory, F max factory
# Cji completation time del job sulle macchine [1,2,3,4]
# IL FLOW E' UGUALE -> IL PT NON CAMBIA DI FABBRICA IN FABBRICA, MA IL PT
# DEI VARI JOB CAMBIA TRA LORO!!!!!!!!!

def main(seed):
    n = 50  # num di job che voglio generare
    m = 20  # num macchine da cui i job dvono passare
    F = 4
    M = 1e6
    time_limit = 120

    factory_makespan = {}
    factory_sequenza = {}
    for f in range(F):  # inizializzo i dict
        factory_sequenza[f] = []
        factory_makespan[f] = 0.0

    p = []

    p = fz.generate_jobs(n, m, seed)
    print(p)

    # print("---------------PRINT ISTANZE----------------")
    # print(p)

    (model, x, Cmax) = fz.load_model(n, m, F, p)
    tic = time.time()
    model.optimize(max_seconds=time_limit)
    toc = time.time()

    tempo_optimize = toc - tic
    print("------------------------------------------------------")
    print(f"\n\n***TEMPO DI PROCESSAMENTO MODEL.OPTIMIZE: {toc - tic}")

    # CREO VETTORE SEQUENZA
    # for f in range(F):  # CREO VETTORE SEQUENZA
    #     sequenza = []
    #     corrente = 0  # da dopo il dummy job 0
    #     visitati = set()
    #
    #     while True:
    #         trovato = False
    #         for j in range(n):
    #             if x[corrente][j][f].x == 1 and j not in visitati:
    #                 sequenza.append(j)
    #                 visitati.add(j)
    #                 corrente = j
    #                 trovato = True
    #                 break
    #         if not trovato:
    #             break
    #     factory_sequenza[f] = sequenza
    # print(f"Factory {f + 1}: {sequenza}")

    for f in range(F):
        Cmax_temp = fz.compute_factory_makespan(factory_sequenza[f], m, p)
        print(f"Makespan per factory {f + 1} con funzione {Cmax_temp}")
        factory_makespan[f] = Cmax_temp

    print("\n\n--------------------SOLUZIONI DI model.optimize()---------------------------\n")
    makespan_optimize = Cmax.x
    print(f"Makespan (Cmax): {Cmax.x}")
    lower_bound = model.objective_bound
    # print("Sequenza dei job:")
    # for f in range(F):
    #     print(f"Assegnati alla factory {f+1}")
    #     for k in range(n):
    #         for j in range(n):
    #             if x[k][j][f].x == 1:  # se il job j precede il job k
    #                 print(f"Job {k} precede il Job {j}")

    # makespan_tot = max(makespan_parziale for makespan_parziale in factory_makespan.values())
    #  print(f"\n\nIl makespan totale è {makespan_tot}")
    print("\n-------------------------------------------------------\n")

    print("\n\n------------------------ASSEGNAZ JOB->FACTORY-----------------------------")
    tic = time.time()
    job_in_factory = fz.assign_factory(n, m, F, p, tic, time_limit)
    print(job_in_factory)
    for f in range(F):
        # print(f"Factory {f+1}: sequenza {job_in_factory[f]}, makespan iniziale: {fz.compute_factory_makespan(job_in_factory[f],m,p)}")
        best_permutation, best_makespan = fz.swap_neighbours(job_in_factory[f][1:], m, p, tic,
                                                             time_limit)  # elimino il dummy gia passandole
        # print(f"best permutation {best_permutation}")
        job_in_factory[f], factory_makespan[
            f] = best_permutation, best_makespan  # assegno al vettore la migliore permutazione

    print("\n\n** CAMBIO IL VICINATO!!***")
    new_neighbourhood, new_factory_makespan = fz.improve_factory_allocation(job_in_factory, factory_makespan, m, p, F,
                                                                            tic, time_limit)
    for f in range(F):
        best_permutation, best_makespan = fz.swap_neighbours(new_neighbourhood[f][1:], m, p, tic,
                                                             time_limit)  # elimino il dummy gia passandole
        # print(f"best permutation {best_permutation}")
        new_neighbourhood[f], new_factory_makespan[f] = best_permutation, best_makespan

    # for f in factory_makespan.keys():
    #     print(f"factory {f}: makespan finale: {new_factory_makespan[f]}")

    makespan_mio = max(makespan_parziale for makespan_parziale in new_factory_makespan.values())
    print(f"\nIl makespan totale è {makespan_mio}")
    print("-----------------------------------------------------------------------")
    tempo_mio = time.time() - tic
    print(f"***TEMPO DI PROCESSAMENTO MIO: {time.time() - tic}")

    return makespan_optimize, makespan_mio, tempo_optimize, tempo_mio, lower_bound
