import re
from math import inf

def get_intervals(s: str) -> str:
    # find all the pieces between underscores
    pieces = re.findall(r'_(.*?)_', s)
    if not pieces:
        raise ValueError("no underscore‑delimited pieces found")

    # extract the bracketed pivot, and separate it from any trailing/leading dash‑nums
    pivot = None
    raw_segs = []
    for piece in pieces:
        m = re.search(r'\[(-?\d+)\]', piece)
        if m:
            pivot = int(m.group(1))
            # keep only the parts outside the brackets (e.g. "6-2", "-1", "8-9", etc.)
            outside = piece[:m.start()] + piece[m.end():]
            if outside:
                raw_segs.append(outside)
        else:
            raw_segs.append(piece)
    if pivot is None:
        raise ValueError("no [number] found in any underscore‑section")

    intervals = []
    for seg in raw_segs:
        # parse up to two ints
        nums = re.findall(r'-?\d+', seg)
        if len(nums) == 2:
            a, b = map(int, nums)
            lo, hi = a + 1, b - 1
        elif len(nums) == 1:
            n = int(nums[0])
            if seg.startswith('-') and not seg.endswith('-'):
                # form "-N"
                lo, hi = -inf, n - 1
            else:
                # form "N-"
                lo, hi = n + 1, inf
        else:
            continue
        intervals.append((lo, hi))

    # format as requested
    intervals_str = ', '.join(
        f"({repr(lo)}, {repr(hi)})" for lo, hi in intervals
    )
    return f"[{pivot}] {intervals_str}"



print(get_intervals("_6-2_[55]_4-7_9-"))
# → "[55] (-float('inf'), -7), (-1, 3), (8, 8)"

print(get_intervals("_[140]-1_8-9_"))
# → "[140] (-float('inf'), 0), (2, 7), (10, float('inf'))"

print(get_intervals("_[78]-"))
# → "[78] (-float('inf'), 0)"

print(get_intervals("_5-[2]_"))
# → "[2] (-float('inf'), 6), (1, float('inf'))"