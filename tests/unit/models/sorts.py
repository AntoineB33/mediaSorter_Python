import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict

class ConstraintSorter:
    def __init__(self, elements: List[str]):
        self.elements = elements
        self.n = len(elements)
        self.forbidden_constraints = []      # (x, y, intervals) where x cannot be in intervals around y
        # New constraint type: (x, y_list, intervals)
        # x's position relative to *at least one* y in y_list must NOT be in the forbidden intervals.
        self.required_disjunctive_constraints = []
        self.maximize_distance = []          # (x, y) where distance between x and y should be maximized

    def add_forbidden_constraint(self, x: str, y: str, intervals: List[Tuple[int, int]]):
        """
        Add a constraint that element x cannot be placed in specified intervals around element y.
        Intervals are relative positions: [-10,-6] means x cannot be 10 to 6 positions before y.
        Use float('inf') for 'end of list' in intervals.
        """
        self.forbidden_constraints.append((x, y, intervals))

    def add_forbidden_constraint_any_y(self, x: str, y_list: List[str], intervals: List[Tuple[int, int]]):
        """
        Adds a constraint that x's relative position to AT LEAST ONE element in y_list
        must fall OUTSIDE the specified forbidden intervals.

        For example:
        add_forbidden_constraint_any_y('E', ['F', 'G', 'H'], [(-float('inf'), 0), (2, float('inf'))])
        This defines the forbidden relative positions as (<= 0) or (>= 2).
        Therefore, the only allowed relative position is 1.
        The constraint means that (pos(E) - pos(y)) must be 1 for at least one y in ['F', 'G', 'H'].
        In other words, E must immediately follow F, or G, or H.
        """
        self.required_disjunctive_constraints.append((x, y_list, intervals))

    def add_maximize_distance_constraint(self, x: str, y: str):
        """
        Add a constraint that elements x and y should be as far apart as possible.
        """
        self.maximize_distance.append((x, y))
    
    def add_group_maximize(self, index_set: Set[int]):
        """
        For every unordered pair of indices in index_set, add a
        maximize_distance constraint between the corresponding elements.
        """
        # Map indices to element names
        names = [self.elements[i] for i in index_set]
        # For each pair (a, b) add both directions to maximize distance
        for u, v in itertools.combinations(names, 2):
            self.add_maximize_distance_constraint(u, v)


    def is_valid_placement(self, arrangement: List[str]) -> bool:
        """Check if an arrangement satisfies all constraints."""
        pos = {elem: i for i, elem in enumerate(arrangement) if elem is not None}

        # 1. Check standard forbidden constraints
        for x, y, intervals in self.forbidden_constraints:
            if x not in pos or y not in pos:
                continue

            x_pos, y_pos = pos[x], pos[y]
            relative_pos = x_pos - y_pos

            for start, end in intervals:
                _start, _end = start, end
                if _end == float('inf'):
                    _end = self.n  # A safe upper bound
                if _start == -float('inf'):
                    _start = -self.n # A safe lower bound

                if _start <= relative_pos <= _end:
                    return False  # Violation

        # 2. Check the "required disjunctive" constraints
        for x, y_list, intervals in self.required_disjunctive_constraints:
            if x not in pos:
                continue

            is_satisfied_for_x = False
            # Check if any y in the list satisfies the condition for x
            for y in y_list:
                if y not in pos:
                    continue

                x_pos, y_pos = pos[x], pos[y]
                relative_pos = x_pos - y_pos

                is_in_forbidden_zone = False
                for start, end in intervals:
                    _start, _end = start, end
                    if _end == float('inf'):
                        _end = self.n
                    if _start == -float('inf'):
                        _start = -self.n

                    if _start <= relative_pos <= _end:
                        is_in_forbidden_zone = True
                        break  # It's in a forbidden interval, this y is not valid

                if not is_in_forbidden_zone:
                    # Found a 'y' for which 'x' is in an allowed position.
                    is_satisfied_for_x = True
                    break  # This disjunctive constraint is satisfied, move to the next one

            # If x is placed and we couldn't find any y in y_list that satisfies
            # the constraint, the arrangement is invalid.
            if not is_satisfied_for_x and any(y in pos for y in y_list):
                return False

        return True

    def calculate_distance_score(self, arrangement: List[str]) -> float:
        """Calculate score based on distance maximization constraints (higher is better)."""
        pos = {elem: i for i, elem in enumerate(arrangement)}
        total_distance = 0

        for x, y in self.maximize_distance:
            if x in pos and y in pos:
                distance = abs(pos[x] - pos[y])
                total_distance += distance

        return total_distance

    def generate_random_valid_arrangement(self, max_attempts: int = 1000) -> List[str]:
        """Generate a random valid arrangement that satisfies all forbidden constraints."""
        for _ in range(max_attempts):
            arrangement = self.elements.copy()
            random.shuffle(arrangement)

            if self.is_valid_placement(arrangement):
                return arrangement

        # If we can't find a valid random arrangement, try a more systematic approach
        return self.greedy_placement()

    def greedy_placement(self) -> List[str]:
        """Try to place elements greedily to satisfy constraints."""
        arrangement = [None] * self.n
        remaining = set(self.elements)

        constrained_elements = set()
        for x, y, _ in self.forbidden_constraints:
            constrained_elements.add(x)
            constrained_elements.add(y)
        for x, y_list, _ in self.required_disjunctive_constraints:
            constrained_elements.add(x)
            constrained_elements.update(y_list)

        unconstrained = [elem for elem in self.elements if elem not in constrained_elements]
        positions = list(range(self.n))
        random.shuffle(positions)

        for i, elem in enumerate(unconstrained):
            if i < len(positions):
                arrangement[positions[i]] = elem
                remaining.remove(elem)

        for elem in list(remaining):
            placed = False
            shuffled_positions = list(range(self.n))
            random.shuffle(shuffled_positions)
            for pos in shuffled_positions:
                if arrangement[pos] is None:
                    arrangement[pos] = elem
                    # Check if the partial arrangement is valid
                    if self.is_valid_placement(arrangement):
                        placed = True
                        break
                    arrangement[pos] = None # Backtrack

            if not placed:
                 # Force placement if no valid spot is found (may result in invalid solution)
                 # A more robust implementation might raise an error or return None here.
                for pos in range(self.n):
                    if arrangement[pos] is None:
                        arrangement[pos] = elem
                        break
        return arrangement

    def local_search_optimization(self, initial_arrangement: List[str], max_iterations: int = 1000) -> List[str]:
        """Improve arrangement using local search while maintaining constraint satisfaction."""
        current = initial_arrangement.copy()
        current_score = self.calculate_distance_score(current)

        for _ in range(max_iterations):
            i, j = random.sample(range(self.n), 2)
            new_arrangement = current.copy()
            new_arrangement[i], new_arrangement[j] = new_arrangement[j], new_arrangement[i]

            if self.is_valid_placement(new_arrangement):
                new_score = self.calculate_distance_score(new_arrangement)
                if new_score > current_score:
                    current = new_arrangement
                    current_score = new_score

        return current

    def solve(self, max_attempts: int = 10, max_iterations: int = 1000) -> List[str]:
        """
        Solve the constraint satisfaction problem.
        Returns the best arrangement found.
        """
        best_arrangement = None
        best_score = -1

        for attempt in range(max_attempts):
            initial = self.generate_random_valid_arrangement()
            if initial is None or not self.is_valid_placement(initial):
                continue

            optimized = self.local_search_optimization(initial, max_iterations)

            score = self.calculate_distance_score(optimized)
            if score > best_score:
                # Final check to ensure the best one is always valid
                if self.is_valid_placement(optimized):
                    best_arrangement = optimized
                    best_score = score

        return best_arrangement


# Example usage:
if __name__ == "__main__":
    # Example with elements A, B, C, D, E, F, G, H, I, J
    elements = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    sorter = ConstraintSorter(elements)

    # --- Add Your Constraints Here ---

    # Element A cannot be in intervals [-10,-6], [-2, 4], [7, end] around element B
    sorter.add_forbidden_constraint('A', 'B', [(-10, -6), (-2, 4), (7, float('inf'))])

    # Element C cannot be in interval [-3, 2] around element D
    sorter.add_forbidden_constraint('C', 'D', [(-3, 2)])

    # NEW: Element 'E' must be placed immediately after 'F', 'G', or 'H'.
    # This means the relative position (pos(E) - pos(y)) must be 1.
    # So, we forbid all other positions: (-inf, 0) and (2, inf).
    sorter.add_forbidden_constraint_any_y('E', ['F', 'G', 'H'], [(-float('inf'), 0), (2, float('inf'))])

    # Maximize distance between A and E
    sorter.add_maximize_distance_constraint('A', 'E')

    # Maximize distance between B and C
    sorter.add_maximize_distance_constraint('B', 'C')

    # --- Solve the problem ---
    print("Solving constraint-based sorting problem...")
    solution = sorter.solve(max_attempts=100, max_iterations=5000)

    if solution:
        print(f"\nSolution found: {solution}")
        print(f"Is valid: {sorter.is_valid_placement(solution)}")
        print(f"Distance score: {sorter.calculate_distance_score(solution)}")

        print("\n--- Positions for Clarity ---")
        pos = {elem: i for i, elem in enumerate(solution)}
        for i, elem in enumerate(solution):
            print(f"Position {i}: {elem}")
        
        # Verification of the new constraint
        print("\n--- Verifying 'E' next to 'F', 'G', or 'H' ---")
        e_pos = pos.get('E')
        for y in ['F', 'G', 'H']:
            y_pos = pos.get(y)
            if e_pos is not None and y_pos is not None:
                print(f"Position of E: {e_pos}, Position of {y}: {y_pos}. Relative pos: {e_pos - y_pos}")

    else:
        print("\nNo valid solution found that satisfies all constraints!")