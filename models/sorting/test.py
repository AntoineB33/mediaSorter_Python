from ortools.sat.python import cp_model

# Define the list of objects to sort
objects = ["A1", "A2", "B1", "B2", "C1", "D1", "D2", "D3"]
N = len(objects)  # Total number of objects

# Define subsets of objects
A_objects = ["A1", "A2"]  # Objects labeled "A"
B_objects = ["B1", "B2"]  # Objects labeled "B"
D_objects = ["D1", "D2", "D3"]  # Objects labeled "D"

# Create the CP-SAT model
model = cp_model.CpModel()

# Variables: position[i] = index of object i in the sorted list
positions = {obj: model.NewIntVar(0, N - 1, f'pos_{obj}') for obj in objects}

# Hard constraint: All "A" objects must appear before all "B" objects
for a in A_objects:
    for b in B_objects:
        model.Add(positions[a] < positions[b])

# Soft constraint: Maximize the minimum distance between "D" objects
D_pairs = [(d1, d2) for d1 in D_objects for d2 in D_objects if d1 < d2]
distances = [model.NewIntVar(0, N, f'dist_{d1}_{d2}') for d1, d2 in D_pairs]

# Use AddAbsEquality to handle absolute differences
for (d1, d2), dist_var in zip(D_pairs, distances):
    diff = model.NewIntVar(-N, N, f'diff_{d1}_{d2}')  # Difference can be negative
    model.Add(diff == positions[d1] - positions[d2])  # Compute the difference
    model.AddAbsEquality(dist_var, diff)  # Absolute value of the difference

# Maximize the minimum distance between "D" objects
min_distance = model.NewIntVar(0, N, 'min_distance')
model.AddMinEquality(min_distance, distances)  # Compute the minimum distance
model.Maximize(min_distance)  # Maximize the minimum distance

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Check if a solution was found
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution found!")
    # Sort objects by their assigned positions
    sorted_list = sorted(objects, key=lambda x: solver.Value(positions[x]))
    print("Sorted list:", sorted_list)
    # Print positions of "D" objects
    for d in D_objects:
        print(f"Position of {d}: {solver.Value(positions[d])}")
else:
    print("No solution found.")