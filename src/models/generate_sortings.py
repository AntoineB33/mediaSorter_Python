import re
import random
from typing import List, Tuple, Dict, Set
from collections import defaultdict


class ConstraintSorter:
    def __init__(self, elements: List[str]):
        self.elements = elements
        self.n = len(elements)
        self.forbidden_constraints = []  # (x, y, intervals) where x cannot be in intervals around y
        self.maximize_distance = []      # (x, y) where distance between x and y should be maximized
        
    def add_forbidden_constraint(self, x: str, y: str, intervals: List[Tuple[int, int]]):
        """
        Add a constraint that element x cannot be placed in specified intervals around element y.
        Intervals are relative positions: [-10,-6] means x cannot be 10 to 6 positions before y.
        Use float('inf') for 'end of list' in intervals.
        """
        self.forbidden_constraints.append((x, y, intervals))
    
    def add_maximize_distance_constraint(self, x: str, y: str):
        """
        Add a constraint that elements x and y should be as far apart as possible.
        """
        self.maximize_distance.append((x, y))
    
    def is_valid_placement(self, arrangement: List[str]) -> bool:
        """Check if an arrangement satisfies all forbidden constraints."""
        pos = {elem: i for i, elem in enumerate(arrangement)}
        
        for x, y, intervals in self.forbidden_constraints:
            if x not in pos or y not in pos:
                continue
                
            x_pos, y_pos = pos[x], pos[y]
            relative_pos = x_pos - y_pos
            
            # Check if x is in any forbidden interval around y
            for start, end in intervals:
                if end == float('inf'):
                    end = self.n - 1 - y_pos  # relative to end of list
                
                if start <= relative_pos <= end:
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
        
        # Create a mapping of elements involved in constraints
        constrained_elements = set()
        for x, y, _ in self.forbidden_constraints:
            constrained_elements.add(x)
            constrained_elements.add(y)
        
        # Place unconstrained elements first
        unconstrained = [elem for elem in self.elements if elem not in constrained_elements]
        positions = list(range(self.n))
        random.shuffle(positions)
        
        for i, elem in enumerate(unconstrained):
            if i < len(positions):
                arrangement[positions[i]] = elem
                remaining.remove(elem)
        
        # Place constrained elements
        for elem in remaining:
            placed = False
            for pos in range(self.n):
                if arrangement[pos] is None:
                    arrangement[pos] = elem
                    if self.is_valid_placement([e for e in arrangement if e is not None]):
                        placed = True
                        break
                    arrangement[pos] = None
            
            if not placed:
                # Force placement if necessary
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
            # Try random swaps
            i, j = random.sample(range(self.n), 2)
            
            # Create new arrangement with swap
            new_arrangement = current.copy()
            new_arrangement[i], new_arrangement[j] = new_arrangement[j], new_arrangement[i]
            
            # Check if new arrangement is valid
            if self.is_valid_placement(new_arrangement):
                new_score = self.calculate_distance_score(new_arrangement)
                
                # Accept if better score
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
            # Generate initial valid arrangement
            initial = self.generate_random_valid_arrangement()
            
            if initial is None:
                continue
            
            # Optimize using local search
            optimized = self.local_search_optimization(initial, max_iterations)
            
            # Check if this is the best solution so far
            if self.is_valid_placement(optimized):
                score = self.calculate_distance_score(optimized)
                if score > best_score:
                    best_arrangement = optimized
                    best_score = score
        
        return best_arrangement


def order_table(res, table):
    old_to_new = {old_index: new_index for new_index, old_index in enumerate(res)}
    new_table = []
    for old_index in res:
        original_row = table[old_index]
        new_row = []
        for cell in original_row:
            if isinstance(cell, str):
                updated_cell = re.sub(r'\[(\d+)\]', lambda m: '[' + str(old_to_new[int(m.group(1))]) + ']', cell)
                updated_cell = re.sub(r'as far as possible from (\d+)', lambda m: "as far as possible from " + str(old_to_new[int(m.group(1))]), updated_cell)
                new_row.append(updated_cell)
            else:
                new_row.append(cell)
        new_table.append(new_row)
    return new_table