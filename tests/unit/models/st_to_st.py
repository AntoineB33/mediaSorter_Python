import re
from math import inf
from typing import List, Tuple

def get_intervals(s: str) -> str:
    # 1) Split on '_' and drop empties
    parts = [p for p in s.split('_') if p]

    # 2) Find the bracketed center and its index
    center_idx = next(i for i, p in enumerate(parts) if '[' in p and ']' in p)

    # 3) Extract the bracket value and any trailing "-N" or "-" 
    m = re.match(r'\[(\-?\d+)\](?:-(\d*))?$', parts[center_idx])
    if not m:
        raise ValueError(f"cannot parse center segment {parts[center_idx]!r}")
    center_val = int(m.group(1))

    # 4) Collect exclusion intervals (inclusive) as integer offsets from center
    excl: List[Tuple[float, float]] = []

    # 4a) If the bracket part has a "-N" or "-" suffix, treat that as (1..N] or (1..∞)
    if m.group(2) is not None:
        if m.group(2) == '':
            b = inf
        else:
            b = int(m.group(2))
        # exclude offsets 1 through b
        excl.append((1, b))

    # 4b) Now handle every other segment
    for i, seg in enumerate(parts):
        if i == center_idx:
            continue
        ma = re.match(r'^(\d*)-(\d*)$', seg)
        if not ma:
            raise ValueError(f"cannot parse segment {seg!r}")
        a_str, b_str = ma.groups()
        a = -inf if a_str == '' else int(a_str)
        b = inf if b_str == '' else int(b_str)
        # convert to offsets relative to center
        if i < center_idx:
            a, b = -b, -a
        start, end = min(a, b), max(a, b)
        excl.append((start, end))

    # 5) Merge & sort exclusions
    excl.sort()
    merged: List[Tuple[float, float]] = []
    for st, en in excl:
        if not merged or st > merged[-1][1] + 1:
            merged.append((st, en))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], en))

    # 6) Compute complementary (allowed) intervals
    allowed: List[Tuple[float, float]] = []
    prev_end = -inf
    for st, en in merged:
        # gap before this exclusion
        if prev_end <= st - 1:
            allowed.append((prev_end, st - 1))
        prev_end = en + 1
    # final tail
    allowed.append((prev_end, inf))

    # 7) Drop any degenerate (inf, inf) tail
    allowed = [(a, b) for a, b in allowed if not (a == inf and b == inf)]

    # 8) Format
    def fmt(x):
        if x == inf:
            return "float('inf')"
        if x == -inf:
            return "-float('inf')"
        return str(int(x))

    intervals_str = ", ".join(f"({fmt(a)}, {fmt(b)})" for a, b in allowed)
    return f"[{center_val}] {intervals_str}"

print(get_intervals("_6-2_[55]_4-7_9-"))
# → "[55] (-float('inf'), -7), (-1, 3), (8, 8)"

print(get_intervals("_[140]-1_8-9_"))
# → "[140] (-float('inf'), 0), (2, 7), (10, float('inf'))"

print(get_intervals("_[140]-"))
# → "[140] (-float('inf'), 0)"