import re
import itertools

def _parse_segments(s):
    segments = []
    if not s:
        return segments
    current_type = None
    current_data = ""
    for c in s:
        if c in ['_', '-']:
            if current_type is None:
                current_type = c
                current_data = ""
            else:
                segments.append((current_type, current_data))
                current_type = c
                current_data = ""
        else:
            current_data += c
    segments.append((current_type, current_data))
    return segments

def find_valid_sortings(table):
    n = len(table)
    interval_constraints = {}
    far_constraints = {}
    
    for i in range(n):
        row = table[i]
        if not row:
            continue
        for constraint in row:
            if isinstance(constraint, str) and constraint.startswith('_'):
                match = re.search(r'\[(\d+)\]', constraint)
                if not match:
                    continue
                ref_row = int(match.group(1))
                if ref_row < 0 or ref_row >= n:
                    continue
                parts = constraint.split(match.group(0), 1)
                left_str = parts[0]
                right_str = parts[1] if len(parts) > 1 else ""
                
                allowed_intervals = []
                segments_left = _parse_segments(left_str)
                for seg_type, seg_data in segments_left:
                    if seg_type == '-':
                        if '-' in seg_data:
                            parts_data = seg_data.split('-', 1)
                            a_str, b_str = parts_data[0], parts_data[1]
                            try:
                                if a_str and b_str:
                                    a = int(a_str)
                                    b = int(b_str)
                                    start = -max(a, b)
                                    end = -min(a, b)
                                    allowed_intervals.append((start, end))
                                elif a_str:
                                    a = int(a_str)
                                    allowed_intervals.append((-a, -1))
                                elif b_str:
                                    b = int(b_str)
                                    allowed_intervals.append((-b, -1))
                            except ValueError:
                                pass
                        else:
                            try:
                                a = int(seg_data)
                                allowed_intervals.append((-a, -a))
                            except ValueError:
                                pass
                
                segments_right = _parse_segments(right_str)
                for seg_type, seg_data in segments_right:
                    if seg_type == '-':
                        if '-' in seg_data:
                            parts_data = seg_data.split('-', 1)
                            a_str, b_str = parts_data[0], parts_data[1]
                            try:
                                if a_str and b_str:
                                    a = int(a_str)
                                    b = int(b_str)
                                    start = min(a, b)
                                    end = max(a, b)
                                    allowed_intervals.append((start, end))
                                elif a_str:
                                    a = int(a_str)
                                    allowed_intervals.append((a, n-1))
                                elif b_str:
                                    b = int(b_str)
                                    allowed_intervals.append((0, b))
                            except ValueError:
                                pass
                        else:
                            try:
                                a = int(seg_data)
                                allowed_intervals.append((a, a))
                            except ValueError:
                                pass
                if i not in interval_constraints:
                    interval_constraints[i] = []
                interval_constraints[i].append((ref_row, allowed_intervals))
            elif isinstance(constraint, str) and constraint.startswith('as far as possible from'):
                parts = constraint.split()
                if parts:
                    try:
                        ref_row = int(parts[-1])
                        far_constraints[i] = ref_row
                    except:
                        pass
    
    all_perms = list(itertools.permutations(range(n)))
    valid_perms = []
    
    for perm in all_perms:
        pos_dict = {row: idx for idx, row in enumerate(perm)}
        valid = True
        for i, constraints_list in interval_constraints.items():
            for (ref_row, allowed_intervals) in constraints_list:
                if ref_row not in pos_dict or i not in pos_dict:
                    valid = False
                    break
                offset = pos_dict[i] - pos_dict[ref_row]
                found_interval = False
                for (a, b) in allowed_intervals:
                    if a <= offset <= b:
                        found_interval = True
                        break
                if not found_interval:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            valid_perms.append(perm)
    
    for i, ref_row in far_constraints.items():
        if not valid_perms:
            break
        max_dist = 0
        for perm in valid_perms:
            pos_dict = {row: idx for idx, row in enumerate(perm)}
            if i in pos_dict and ref_row in pos_dict:
                dist = abs(pos_dict[i] - pos_dict[ref_row])
                if dist > max_dist:
                    max_dist = dist
        if max_dist == 0:
            continue
        new_valid_perms = []
        for perm in valid_perms:
            pos_dict = {row: idx for idx, row in enumerate(perm)}
            if i in pos_dict and ref_row in pos_dict:
                dist = abs(pos_dict[i] - pos_dict[ref_row])
                if dist == max_dist:
                    new_valid_perms.append(perm)
        valid_perms = new_valid_perms
    
    if not valid_perms:
        return "No valid sorting exists."
    return [list(perm) for perm in valid_perms]