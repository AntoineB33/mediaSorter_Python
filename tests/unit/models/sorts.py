from src.models.generate_sortings import order_table
from src.models.find_valid_sortings import find_valid_sortings

table = [
    ["_[1]-3_", "as far as possible from 2"],
    ["_[2]-"],
    [],
    []
]
table = [
    ["_[1]-1_"],
    []
]
res = find_valid_sortings(table)
if type(res) is str:
    print(res)
else:
    print("Found valid sortings:", res)
    ordered_res = order_table(res[0], table)
    print(ordered_res)
