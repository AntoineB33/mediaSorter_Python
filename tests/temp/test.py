from ortools.sat.python import cp_model
from collections import defaultdict

def parse_constraints(table):
    """
    Extract hard constraints and optimization goals from a table of strings.
    Returns: (hard_constraints, optimization_goals)
    """
    hard_constraints = []
    optimization_goals = []
    tag_to_objects = defaultdict(list)
    name_to_tag = {}
    name_to_object = {}

    # First pass: collect tags and names
    for row in table:
        if 'Role.NAME' in row and 'Role.TAG' in row:
            name = row['Role.NAME'].strip()
            tag = row['Role.TAG'].strip()
            if name and tag:
                tag_to_objects[tag].append(name)
                name_to_tag[name] = tag
                name_to_object[name] = name

    # Second pass: parse conditions
    for row in table:
        condition = row.get('Role.CONDITION', '').strip()
        if not condition:
            continue

        # Handle hard constraints
        if 'before' in condition.lower():
            parts = condition.lower().split('before')
            source = parts[0].strip()
            target = parts[1].strip()
            
            if source in tag_to_objects and target in tag_to_objects:
                # Tag-based constraint (e.g., "A before B")
                hard_constraints.append(('tag_before', source, target))
            elif target in name_to_object:
                # Object-based constraint (e.g., "chair before apple")
                hard_constraints.append(('object_before', source, target))

        elif 'place before' in condition.lower():
            parts = condition.lower().split('place before')
            offset = int(parts[0].strip().split()[0])
            target = parts[1].strip()
            source = row['Role.NAME'].strip()
            hard_constraints.append(('offset_before', source, target, offset))

        # Handle optimization goals
        if 'as far as possible' in condition.lower():
            tag = row['Role.TAG'].strip()
            if tag in tag_to_objects:
                optimization_goals.append(('max_distance', tag))

    return hard_constraints, optimization_goals, tag_to_objects, name_to_object

def solve_sorting_problem(table):
    # Parse constraints and goals
    hard_constraints, optimizations, tag_to_objects, name_to_object = parse_constraints(table)
    
    # Create model
    model = cp_model.CpModel()
    objects = list(name_to_object.keys())
    N = len(objects)
    positions = {obj: model.NewIntVar(0, N-1, f'pos_{obj}') for obj in objects}
    
    # Add all-different constraint
    model.AddAllDifferent(positions.values())

    # Apply hard constraints
    for constraint in hard_constraints:
        const_type = constraint[0]
        
        if const_type == 'tag_before':
            source_tag, target_tag = constraint[1], constraint[2]
            for source in tag_to_objects.get(source_tag, []):
                for target in tag_to_objects.get(target_tag, []):
                    model.Add(positions[source] < positions[target])
                    
        elif const_type == 'object_before':
            source, target = constraint[1], constraint[2]
            model.Add(positions[source] < positions[target])
            
        elif const_type == 'offset_before':
            source, target, offset = constraint[1], constraint[2], constraint[3]
            model.Add(positions[source] == positions[target] - offset)

    # Add optimization goals
    objective_terms = []
    for goal in optimizations:
        goal_type, tag = goal
        if goal_type == 'max_distance':
            group = tag_to_objects.get(tag, [])
            if len(group) >= 2:
                distances = []
                for i in range(len(group)):
                    for j in range(i+1, len(group)):
                        diff = model.NewIntVar(-N, N, '')
                        model.Add(diff == positions[group[i]] - positions[group[j]])
                        abs_diff = model.NewIntVar(0, N, '')
                        model.AddAbsEquality(abs_diff, diff)
                        distances.append(abs_diff)
                if distances:
                    min_distance = model.NewIntVar(0, N, 'min_distance')
                    model.AddMinEquality(min_distance, distances)
                    objective_terms.append(min_distance)

    # Maximize the minimum distance
    if objective_terms:
        model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        sorted_items = sorted(objects, key=lambda x: solver.Value(positions[x]))
        return sorted_items
    return None

# Example usage
if __name__ == "__main__":
    # Example table input (list of dictionaries)
    example_table = [
        {'Role.NAME': 'A', 'Role.CONDITION': 'before B', 'Role.TAG': ''},
        {'Role.NAME': 'A1', 'Role.CONDITION': '', 'Role.TAG': 'A'},
        {'Role.NAME': 'A2', 'Role.CONDITION': '', 'Role.TAG': 'A'},
        {'Role.NAME': 'B1', 'Role.CONDITION': '', 'Role.TAG': 'B'},
        {'Role.NAME': 'B2', 'Role.CONDITION': '', 'Role.TAG': 'B'},
        {'Role.NAME': 'chair', 'Role.CONDITION': 'two place before apple', 'Role.TAG': 'furniture'},
        {'Role.NAME': 'apple', 'Role.CONDITION': '', 'Role.TAG': 'food'},
        {'Role.NAME': 'banana', 'Role.CONDITION': '', 'Role.TAG': 'food'},
        {'Role.CONDITION': 'as far as possible from each other', 'Role.TAG': 'food'}
    ]

    solution = solve_sorting_problem(example_table)
    if solution:
        print("Optimal ordering:", solution)
    else:
        print("No solution found")