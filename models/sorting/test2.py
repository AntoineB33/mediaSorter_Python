from ortools.sat.python import cp_model

total_length = 10
_data = [
    ["A", ["appears before B", "appears before C"]],
    ["B", ["appears after C"]],
    ["C", []]
]

model = cp_model.CpModel()

# Create variables for each element's position
variables = {}
for entry in _data:
    name = entry[0]
    variables[name] = model.NewIntVar(0, total_length - 1, name)

# Ensure all positions are distinct
model.AddAllDifferent(variables.values())

# Add constraints based on the conditions provided
for entry in _data:
    name = entry[0]
    condition = entry[1]
    if condition:
        parts = condition.split()
        relation = parts[1]
        other_element = parts[2]
        if relation == 'before':
            model.Add(variables[name] < variables[other_element])
        elif relation == 'after':
            model.Add(variables[name] > variables[other_element])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the sorted elements based on their positions
if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    sorted_elements = sorted(variables.keys(), key=lambda x: solver.Value(variables[x]))
    print("Sorted order:", ' '.join(sorted_elements))
else:
    print("No solution found.")