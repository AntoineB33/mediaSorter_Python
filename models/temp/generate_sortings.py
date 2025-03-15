from ortools.sat.python import cp_model
from networkx import DiGraph, topological_sort, NetworkXUnfeasible
import os


def reduce_redundancy(table):
    """
    Reduces redundancy in the dependency table by removing implied constraints.
    For example, if 3 must come after 1 and 1 must come after 2, the constraint
    "3 must come after 2" is redundant and removed.
    """
    n = len(table)
    # Build the dependency graph: graph[i] contains direct dependencies of i
    graph = {i: set() for i in range(n)}
    for i in range(n):
        for entry in table[i]:
            if entry.startswith("after "):
                j = int(entry.split()[1])
                graph[i].add(j)  # Edge: j -> i (i must come after j)

    # Compute ancestors for each node (all nodes that must come before it)
    ancestors = {i: set() for i in range(n)}
    for i in range(n):
        visited = set()
        stack = [i]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                # Traverse dependencies (edges j -> node)
                for dependency in graph[node]:
                    if dependency not in visited:
                        stack.append(dependency)
        ancestors[i] = visited

    # Remove redundant dependencies
    reduced_table = [[] for _ in range(n)]
    for X in range(n):
        dependencies = list(graph[X])
        non_redundant = []
        for Z in dependencies:
            # Check if Z is implied by other dependencies
            redundant = False
            # Check all other dependencies Y != Z
            for Y in dependencies:
                if Y == Z:
                    continue
                if Z in ancestors[Y]:
                    redundant = True
                    break
            if not redundant:
                non_redundant.append(f"after {Z}")
        reduced_table[X] = non_redundant

    return reduced_table

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

def find_valid_sortings(table):
    n = len(table)
    
    # Check if the graph is a DAG and use topological sort if possible
    graph = DiGraph()
    graph.add_nodes_from(range(n))
    for i in range(n):
        for entry in table[i]:
            if entry.startswith("after "):
                j = int(entry.split()[1])
                graph.add_edge(j, i)
    solutions = []
    try:
        solutions = list(topological_sort(graph))
    except NetworkXUnfeasible:
        print("The dependency graph is not a DAG.")
        return []


    
    table = reduce_redundancy(table)
    return solutions