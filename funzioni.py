import copy
import random
import time
from itertools import product
from mip import *


def load_model(n,m,F,p):
    M = 1e6

    model = Model(name="DPFSP")

    x = [[[model.add_var(var_type=BINARY) for f in range(F)] for j in range(n)] for k in range(n)]
    y = [[model.add_var(var_type=BINARY) for f in range(0, F)] for j in range(0, n)]
    C = [[model.add_var(var_type=CONTINUOUS, lb=0) for i in range(m)] for j in range(n)]

    Cmax = model.add_var(var_type=CONTINUOUS)
    model.objective = minimize(Cmax)

    for j in range(1, n):  # ogni job deve avere un predecessore ed è lavorato in una sola factory
        model += xsum(x[k][j][f] for f in range(F) for k in range(n) if k != j) == 1

    for j in range(1, n):  # ogni job è lavorato in una sola factory
        model += xsum(y[j][f] for f in range(F)) == 1

    for (j, f) in product(range(1, n), range(F)):
        model += xsum(x[k][j][f] + x[j][k][f] for k in range(n) if k != j) <= 2 * y[j][f]

    for k in range(1, n):
        model += xsum(x[k][j][f] for f in range(F) for j in range(1, n) if j != k) <= 1

    for f in range(F):  # ogni job è lavorato in una sola factory
        model += xsum(x[0][j][f] for j in range(1, n)) == 1

    for k in range(1, n - 1):
        for j in range(k + 1, n):
            model += xsum(x[k][j][f] + x[j][k][f] for f in range(F)) <= 1

    for (j, i) in product(range(n), range(m)):
        if i > 0:
            model += C[j][i] >= C[j][i - 1] + p[j][i]

    for (j, k, i) in product(range(n), range(n), range(m)):
        if j != k:
            model += C[j][i] >= C[k][i] + p[j][i] + ((xsum(x[k][j][f] for f in range(F))) - 1) * M

    for j in range(n):
        model += Cmax >= C[j][m - 1]

    return model,x, Cmax


def generate_jobs(n_max, m_max,seed):
    p = []
    random.seed(seed)
    for j in range(n_max):
        pj = []
        if j == 0:  # il dummy ha pt 0 in tutte le macchine
            for i in range(m_max):
                pj.append(0)
        else:
            pj = []  # array per i process time di un job sulle varie macchine
            for i in range(m_max):
                pj.append(random.randint(1, 100))
        p.append(pj)  # aggiungo i pt di un job al vettore totale contenente tutti i pt
    return p

def assign_factory(n,m,F,p,tic,time_limit):
    job_in_factory = {}
    if time.time() - tic > time_limit:
        return job_in_factory
    else:
        for f in range(F):
            job_in_factory[f] = [0]   #ogni factory comincia con il dummy job

        assigned = set()
        assigned.add(0)     #ogni factory comincia con il dummy job

        jobs_by_weight = sorted(range(1, n), key=lambda j: sum(p[j][i] for i in range(m)), reverse=True)

        for f in range(F): #prima assegnazione: assegno gli f job più pesanti a factory separate
            if jobs_by_weight != []:
                heaviest = jobs_by_weight[0]
                job_in_factory[f].append(heaviest)
                assigned.add(heaviest)
                jobs_by_weight.pop(0)

        for job in range(n):    #seconda assegnazione: assegno i job rimanenti man mano alle factory meno pesanti
            if job not in assigned:
                min_makespan = 1e6      #lo inizializzo a un numero molto grande
                for f in range(F):
                    current_sequence = job_in_factory[f] + [job]   #assegno il job alla factory meno carica CONTROLLO GROSSOLANO
                    current_makespan = compute_factory_makespan(current_sequence, m, p)
                    if current_makespan < min_makespan:
                        min_makespan = current_makespan
                        best_factory = f
                job_in_factory[best_factory].append(job)
                assigned.add(job)
        return job_in_factory

def improve_factory_allocation(job_in_factory, factory_makespan, m, p, F, tic, time_limit):
    if time.time() - tic > time_limit:
        return  job_in_factory, factory_makespan

    new_job_in_factory = {}
    best_factory= 0
    worst_factory = 0
    makespan_best = 10e5
    makespan_worse = 0.0

    for f in range(F):      #trovo la factory con makespan più alto e più basso
        if factory_makespan[f]< makespan_best:
            best_factory = f
            makespan_best = compute_factory_makespan(job_in_factory[best_factory], m, p)
        elif factory_makespan[f]>makespan_worse:
            worst_factory = f
            makespan_worse = compute_factory_makespan(job_in_factory[worst_factory], m, p)

    improved = False

    for job in job_in_factory[worst_factory][1:]:  #TENTATIVO:rimuovo il job dalla peggiore e lo metto alla migliore
        print(f"\nPROVO A SPOSTARE job {job} da {worst_factory + 1} a {best_factory + 1}")
        new_worst_sequence = job_in_factory[worst_factory].copy()
        new_worst_sequence.remove(job)
        new_best_sequence = job_in_factory[best_factory] + [job]

        new_job_in_factory = copy.deepcopy(job_in_factory)  #copio il vicchio dict e cambio in maniera mirata cio che mi interessa
        new_job_in_factory[worst_factory] = new_worst_sequence
        new_job_in_factory[best_factory] = new_best_sequence

        new_factory_makespan = copy.deepcopy(factory_makespan)
        new_factory_makespan[best_factory] = compute_factory_makespan(new_job_in_factory[best_factory], m, p)
        new_factory_makespan[worst_factory] = compute_factory_makespan(new_job_in_factory[worst_factory], m, p)

        # vedo qual è la permutazione migliore di questa nuova sequenza -- IN MANIERA MIRATA (?)
        best_permutation, best_makespan = swap_neighbours(new_job_in_factory[best_factory][1:], m, p, tic, time_limit)  # elimino il dummy gia passandole
        new_job_in_factory[best_factory], new_factory_makespan[best_factory] = best_permutation, best_makespan
       # print(f"best permutation {best_permutation}")
        best_permutation, best_makespan = swap_neighbours(new_job_in_factory[worst_factory][1:], m, p, tic, time_limit)
        new_job_in_factory[worst_factory], new_factory_makespan[worst_factory] = best_permutation, best_makespan

        old_Cmax = max(factory_makespan.values())
        new_Cmax = max(new_factory_makespan.values())

       # print(f"old_Cmax {old_Cmax}     new_Cmax {new_Cmax}")
        if new_Cmax < old_Cmax:
            #IL TENTATIVO MIGLIORA IL MIO MAKESPAN -> applico spostamento e riparto con questo nuovo punto di partenza
            job_in_factory[worst_factory].remove(job)
            job_in_factory[best_factory].append(job)
            print(f"    Spostato job {job} da {worst_factory+1} a {best_factory+1} (Cmax migliorato da {old_Cmax:.2f} → {new_Cmax:.2f})")
            improved = True

        if improved:    #finchè le perturbazioni hanno successo, continuo a esplorare
            return improve_factory_allocation(new_job_in_factory, new_factory_makespan, m, p, F, tic, time_limit)  # non ci sono miglioramenti, fine

        return job_in_factory, factory_makespan


def compute_factory_makespan(job_sequence, m, p):
    if job_sequence == []:
        print("Non sono ancora stati assegnati job.")
        return 0.0

    completion_time = [[0.0 for i in range(m)] for j in range(len(job_sequence))]

    for (j, job) in enumerate(job_sequence):  # per ogni job della sequenza
        for i in range(m):  # il job passa per tutte le macchine
            if j == 0 and i == 0:  # primo job sulla prima macchina
                completion_time[j][i] += p[job][i]
            elif j == 0:  # primo job sulle altre macchine
                completion_time[j][i] += completion_time[j][i - 1] + p[job][i]
            elif i == 0:  # prima macchina per job successivi
                completion_time[j][i] += completion_time[j - 1][i] + p[job][i]
            else:  # altre macchine per i job successivi
                completion_time[j][i] += max(completion_time[j - 1][i],
                                             completion_time[j][i - 1]) + p[job][i]
    #factory_makespan[f] = completion_time[len(job_sequence) - 1][m - 1]
    return completion_time[len(job_sequence) - 1][m - 1]


def swap_neighbours(sequence,m,p,tic, time_limit):
    if len(sequence) == 1 or (time.time() - tic) > time_limit:
        return [0] + sequence,  compute_factory_makespan(sequence,m,p)

    while(time.time() - tic < 60):
       # print(f"RIPARTO CON: {sequence}")
        improved = False
        best_sequence = sequence
        best_makespan = compute_factory_makespan(sequence,m,p)

        for i in range(len(sequence) - 1):  # scambio ognuno con il vicino
            swapped = sequence.copy()
            swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
            current_makespan = compute_factory_makespan(swapped,m,p)
          #  print(f"    permutation {swapped} -> {current_makespan}")

            if current_makespan < best_makespan:    #best tra tutte le permutazioni di sequence
                best_makespan = current_makespan
                best_sequence = swapped
                improved = True

            #della permutazione best, vedo se posso permutare ancora meglio
        if improved:
            return swap_neighbours(best_sequence, m, p, tic, time_limit)#se il makespan delle 'sottopermutazioni' è peggiore, sono gia all'ottimo
        return [0] + best_sequence, best_makespan


  #  return [0] + sequence, compute_factory_makespan(sequence,m,p)
