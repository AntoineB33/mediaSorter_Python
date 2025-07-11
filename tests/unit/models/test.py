def process_table(table):
    output_lines = []
    n = len(table)
    
    for i in range(n):
        row = table[i]
        if not row:
            output_lines.append("")
            continue
            
        current_label = row[0]
        found = False
        if len(row) > 1:
            for j in range(1, len(row)):
                content = row[j].strip()
                if content.startswith('['):
                    end_bracket = content.find(']')
                    if end_bracket == -1:
                        continue
                    index_str = content[1:end_bracket].strip()
                    try:
                        index_num = int(index_str)
                    except ValueError:
                        continue
                    if index_num < 1 or index_num > n:
                        continue
                    target_label = table[index_num-1][0]
                    intervals_str = content[end_bracket+1:].strip()
                    list_str = '[' + intervals_str + ']'
                    func_call = f"add_forbidden_constraint({repr(current_label)}, {repr(target_label)}, {list_str})"
                    output_lines.append(func_call)
                    found = True
                    break
                elif "as far as possible from" in content:
                    tokens = content.split()
                    if not tokens:
                        continue
                    last_token = tokens[-1]
                    try:
                        index_num = int(last_token)
                    except ValueError:
                        continue
                    if index_num < 1 or index_num > n:
                        continue
                    target_label = table[index_num-1][0]
                    func_call = f"add_maximize_distance_constraint({repr(current_label)}, {repr(target_label)})"
                    output_lines.append(func_call)
                    found = True
                    break
        if not found:
            output_lines.append("")
    return output_lines

print(process_table([
    ["[3] (-10, -6), (-2, 4), (7, float('inf'))", "[2] (-3, 2)"],
    ["[2] (-3, 2)"],
    ["as far as possible from 1"],
    ["as far as possible from 2"],
    [""],
    ["[3] (-5, 0)"],
    ["as far as possible from 4"]
]))