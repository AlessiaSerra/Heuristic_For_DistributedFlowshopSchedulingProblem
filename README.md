# Solving the Distributed Permutation Flowshop Scheduling Problem (DPFSP)

This repository contains the implementation of a Mixed Integer Linear Programming (MILP) model and a custom Heuristic-based approach to solve the **Distributed Permutation Flowshop Scheduling Problem (DPFSP)**. 

This project was developed as part of a Bachelor's Thesis in Management Engineering (Ingegneria Gestionale) at **Politecnico di Torino** by Alessia Serra.

## Problem Description

The Distributed Permutation Flowshop Scheduling Problem is a variant of the classical sequential Flowshop problem. It involves:
- **$F$** identical factories (plants).
- **$m$** machines in series within each factory.
- **$n$** jobs that need to be assigned and processed.

The goal is to assign the $n$ jobs to the $F$ factories and determine the processing sequence within each factory to **minimize the total makespan** (the maximum completion time among all factories). Since multi-site manufacturing is becoming increasingly important in today's globalized market, efficiently distributing the workload across multiple facilities is crucial.

As DPFSP is NP-Hard, exact solvers struggle with larger instances due to combinatorial explosion. This project introduces a fast heuristic approach that provides near-optimal solutions in a fraction of the time required by exact solvers.

## Repository Structure

- `FlowShop.py`: The main execution script. It generates a random instance, runs the MILP model (via Python `mip`), runs the heuristic approach, and compares the makespan and computational time.
- `funzioni.py`: Contains the core logic and functions used in the project:
  - `load_model`: Formulates the MILP model with variables and constraints.
  - `generate_jobs`: Generates randomized processing times for the jobs.
  - `assign_factory`: Initial heuristic allocation of jobs to factories based on workload balancing.
  - `improve_factory_allocation`: A perturbation method to escape local minima by shifting jobs between the most and least loaded factories.
  - `swap_neighbours`: A local search function that optimizes the job sequence within a single factory.
  - `compute_factory_makespan`: Calculates the completion time of a given sequence of jobs.
- `run_experiments.py`: A script to automate the execution of multiple experimental runs and log the results into a text file.
- `tuttoinsieme.py` / `non_funzionante.py`: Scratchpad and legacy files showing the iterative development of the algorithms.
- `results*.txt`: Output logs from the experiments comparing the exact MILP solver and the heuristic approach.
- `Tesi.pdf`: The full thesis document detailing the mathematical formulation, the heuristic design, and the experimental results.

## Requirements

To run this project, you need Python 3 installed along with the `mip` (Mixed-Integer Linear Programming) package.

```bash
pip install mip
```

*Note: The `mip` package uses the CBC solver by default but can be configured to use Gurobi or CPLEX if you have the respective licenses.*

## Usage

To run a single instance of the problem and see the comparison between the MILP solver and the heuristic:

```bash
python FlowShop.py
```

To run a batch of experiments and save the output to a results file (e.g., `results6.txt`):

```bash
python run_experiments.py
```

## Results Highlights

The experimental results (as seen in `results.txt`, `results6.txt`, and `results7.txt`) demonstrate the effectiveness of the heuristic method:
- **Time limits & Complexity:** For larger instances (e.g., $n=50$, $m=20$, $F=4$), the exact MILP solver often reaches the 120-second time limit without finding an optimal solution (or sometimes failing to find a feasible solution, returning `None`).
- **Heuristic Speed:** The heuristic algorithm consistently finds good quality solutions in extremely short computational times (often $< 0.1$ seconds).
- **Makespan Quality:** The heuristic's makespan is highly competitive and scales gracefully with problem size, bypassing the exponential time complexity barrier faced by the MILP solver.

## Author
**Alessia Serra**  
Politecnico di Torino  
Corso di Laurea in Ingegneria Gestionale (2024/2025)
