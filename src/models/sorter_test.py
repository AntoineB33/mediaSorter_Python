from networkx import DiGraph, topological_sort, NetworkXUnfeasible, simple_cycles
import os
from ortools.sat.python import cp_model
import re

class SolutionCollector(cp_model.CpSolverSolutionCallback):
    def __init__(self, pos_vars, n, max_solutions):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.pos_vars = pos_vars
        self.n = n
        self.max_solutions = max_solutions
        self.solutions = []
        self.count = 0

    def OnSolutionCallback(self):
        if self.count >= self.max_solutions:
            return
        current_pos = [self.Value(var) for var in self.pos_vars]
        permutation = sorted(range(self.n), key=lambda x: current_pos[x])
        self.solutions.append(permutation)
        self.count += 1
        if self.count >= self.max_solutions:
            self.StopSearch()

    def get_solutions(self):
        return self.solutions

def find_valid_sortings(table, roles):
    n = len(table)

    graph = DiGraph()
    graph.add_nodes_from(range(n))
    dependencies = [[] for _ in range(n)]
    upper_bounds = []
    optimization_terms = []

    for i in range(n):
        row = table[i]
        for col_index, entry in enumerate(row):
            role = roles[col_index]
            if role == 'dependencies':
                m1 = re.match(r'after\s+([1-9][0-9]*)', entry)
                m2 = re.match(r'within\s+(\d+)\s+after\s+([1-9][0-9]*)', entry)
                m3 = re.match(r'as far as possible from (\d+)', entry)

                if m1:
                    j = int(m1.group(1)) - 1
                    if j < 0 or j >= n:
                        return f"Invalid dependency: {entry} in row {i+1}"
                    dependencies[i].append(j)
                    graph.add_edge(j, i)
                elif m2:
                    dist_str = m2.group(1)
                    j_str = m2.group(2)
                    try:
                        dist_val = int(dist_str)
                        j = int(j_str) - 1
                    except ValueError:
                        return f"Invalid numbers in entry: {entry} in row {i+1}"
                    if j < 0 or j >= n:
                        return f"Invalid index in entry: {entry} in row {i+1}"
                    if dist_val < 1:
                        return f"Distance must be at least 1 in entry: {entry} in row {i+1}"
                    dependencies[i].append(j)
                    graph.add_edge(j, i)
                    upper_bounds.append((i, j, dist_val))
                elif m3:
                    X = int(m3.group(1)) - 1
                    if X < 0 or X >= n:
                        return f"Invalid optimization term: {entry} in row {i+1}"
                    optimization_terms.append((i, X))
                else:
                    return f"Invalid entry: {entry} in row {i+1}"

    try:
        topological_order = list(topological_sort(graph))
    except NetworkXUnfeasible:
        try:
            cycle = next(simple_cycles(graph))
            cycle_str = ' -> '.join([str(node + 1) for node in cycle]) + f' -> {cycle[0] + 1}'
            return f"The dependency graph contains a cycle: {cycle_str}"
        except StopIteration:
            return "The dependency graph is not a DAG (unexpected error)."

    if not optimization_terms and not upper_bounds:
        return [list(topological_order)]

    model = cp_model.CpModel()
    pos = [model.NewIntVar(0, n-1, f'pos_{i}') for i in range(n)]
    model.AddAllDifferent(pos)

    for i in range(n):
        for j in dependencies[i]:
            model.Add(pos[j] < pos[i])

    for (i, j, d) in upper_bounds:
        model.Add(pos[i] <= pos[j] + d)

    if optimization_terms:
        diff_vars = []
        for i, X in optimization_terms:
            diff = model.NewIntVar(0, n-1, f'diff_{i}_{X}')
            model.AddAbsEquality(diff, pos[i] - pos[X])
            diff_vars.append(diff)
        model.Maximize(sum(diff_vars))

    workers = 1
    cpu_available = os.cpu_count()
    if n > 100:
        workers = min(cpu_available, 4)
    if n > 300:
        workers = min(cpu_available, 5)
    if n > 500:
        workers = min(cpu_available, 6)
    if n > 700:
        workers = min(cpu_available, 7)
    if n > 900:
        workers = min(cpu_available, 8)
    if n > 1000:
        workers = min(cpu_available, 16)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        solution = [solver.Value(pos[i]) for i in range(n)]
        permutation = sorted(range(n), key=lambda x: solution[x])
        return [permutation]
    else:
        return []
    


if __name__ == "__main__":

    table = [[] for i in range(50)]
    table[0] = ["within 3 after 2", "as far as possible from 2"]

    print(find_valid_sortings(table, ['dependencies', 'dependencies']))