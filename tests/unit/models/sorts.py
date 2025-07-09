from src.models.generate_sortings import find_valid_sortings, order_table

table = [
    ["_[1]-3_", "as far as possible from 2"],
    ["_[2]-"],
    [],
    []
]
res = find_valid_sortings(table)
if type(res) is str:
    print(res)
else:
    print("Found valid sortings:", res)
    ordered_res = order_table(res, table)
    print(ordered_res)
