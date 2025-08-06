import re
import math

def add_forbidden_constraint(current, target, intervals):
    print(f"add_forbidden_constraint({current!r}, {target!r}, {intervals})")

def add_maximize_distance_constraint(current, target):
    print(f"add_maximize_distance_constraint({current!r}, {target!r})")

def parse_intervals(intervals_part: str):
    """
    Given a string like "(-10, -6), (-2, 4), (7, float('inf')), (-float('inf'), 2)",
    returns a list of (lo, hi) tuples, with ±math.inf if 'inf' is present.
    """
    def to_num(s: str) -> float:
        s = s.strip()
        if 'inf' in s:
            return -math.inf if s.startswith('-') else math.inf
        return float(s)

    intervals = []
    i = 0
    n = len(intervals_part)
    while i < n:
        if intervals_part[i] == '(':
            depth = 1
            start = i + 1
            i += 1
            while i < n and depth > 0:
                if intervals_part[i] == '(':
                    depth += 1
                elif intervals_part[i] == ')':
                    depth -= 1
                i += 1
            chunk = intervals_part[start:i-1].strip()

            # Split on the top‑level comma
            depth2 = 0
            for j, c in enumerate(chunk):
                if c == '(':
                    depth2 += 1
                elif c == ')':
                    depth2 -= 1
                elif c == ',' and depth2 == 0:
                    lo_str, hi_str = chunk[:j], chunk[j+1:]
                    break
            else:
                raise ValueError(f"Malformed interval (no top-level comma): {chunk!r}")

            lo = to_num(lo_str)
            hi = to_num(hi_str)
            intervals.append((lo, hi))
        else:
            i += 1
    return intervals

def go(strings, instructions):
    for idx, inst_list in enumerate(instructions):
        current = strings[idx]
        for inst in inst_list:
            inst = inst.strip()
            if not inst:
                continue

            # Forbidden constraint
            m = re.match(r"^\[(\d+)\]\s*(.*)$", inst)
            if m:
                tgt_idx = int(m.group(1)) - 1
                target = strings[tgt_idx]
                intervals = parse_intervals(m.group(2))
                add_forbidden_constraint(current, target, intervals)
                continue

            # Maximize distance
            m2 = re.match(r"^as far as possible from\s+(\d+)$", inst)
            if m2:
                tgt_idx = int(m2.group(1)) - 1
                target = strings[tgt_idx]
                add_maximize_distance_constraint(current, target)
                continue

            raise ValueError(f"Unrecognized instruction: {inst}")

# Example usage
test_strings = ['a','b','c','d','e','f','g']
test_instructions = [
    ["[3] (-10, -6), (-2, 4), (7, float('inf'))", "[2] (-3, 2)"],
    ["[2] (-float('inf'), 2)"],
    ["as far as possible from 1"],
    ["as far as possible from 2"],
    [""],
    ["[3] (-5, 0)"],
    ["as far as possible from 4"]
]

go(test_strings, test_instructions)
