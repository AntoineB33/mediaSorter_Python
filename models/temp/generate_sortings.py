from ortools.sat.python import cp_model

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

def find_valid_sortings(table, k):
    n = len(table)
    dependencies = []
    for i in range(n):
        deps = []
        for s in table[i]:
            parts = s.strip().split()
            if len(parts) >= 2 and parts[0].lower() == 'after':
                try:
                    j = int(parts[1])
                    if 0 <= j < n:
                        deps.append(j)
                except ValueError:
                    pass
        dependencies.append(deps)

    model = cp_model.CpModel()
    pos = [model.NewIntVar(0, n - 1, f'pos_{i}') for i in range(n)]
    model.AddAllDifferent(pos)

    for i in range(n):
        for j in dependencies[i]:
            model.Add(pos[i] < pos[j])

    solver = cp_model.CpSolver()
    solution_collector = SolutionCollector(pos, n, k)
    solver.parameters.enumerate_all_solutions = True
    solver.Solve(model, solution_collector)

    return solution_collector.get_solutions()