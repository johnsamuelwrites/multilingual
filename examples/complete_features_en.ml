import math
from math import sqrt as root_fn

let shared_counter = 3

def bump_global():
    global shared_counter
    shared_counter = shared_counter + 2
    return shared_counter

def make_counter(start):
    let total = start
    def step():
        nonlocal total
        total = total + 1
        return total
    return step

let next_count = make_counter(5)
let first_step = next_count()
let second_step = next_count()

with open("tmp_complete_en.txt", "w", encoding="utf-8") as handle_w:
    handle_w.write("ok")

let file_text = ""
with open("tmp_complete_en.txt", "r", encoding="utf-8") as handle_r:
    file_text = handle_r.read()

let zipped_pairs = list(zip([1, 2, 3], [4, 5, 6]))
let unique_values = set([1, 1, 2, 3])
let fixed_values = tuple([10, 20, 30])
let first_item, *middle_items, last_item = [1, 2, 3, 4]
let merged_map = {**{"x": 1}, **{"y": 2}}

def format_tag(a, /, *, b):
    return f"{a}-{b:.1f}"

let formatted = format_tag(7, b=3.5)
let seed = 0
let walrus_value = (seed := seed + 9)

class CounterBox:
    def __init__(self, start_base):
        self.value = start_base

class CounterBoxChild(CounterBox):
    def __init__(self, start_base):
        super(CounterBoxChild, self).__init__(start_base)
        self.value = self.value + 1

def produce_three():
    for idx in range(3):
        yield idx

let produced_total = sum(produce_three())
let handled = False

try:
    if len(unique_values) > 2:
        raise ValueError("boom")
except ValueError as handled_error:
    handled = True
finally:
    let root_value = int(root_fn(16))

let temp_value = 99
del temp_value

let loop_acc = 0
for n in range(6):
    if n == 0:
        pass
    if n == 4:
        break
    if n % 2 == 0:
        continue
    loop_acc = loop_acc + n

let flag_ok = True and not False
assert flag_ok

let child_box = CounterBoxChild(40)

print(bump_global())
print(first_step, second_step)
print(file_text)
print(len(zipped_pairs), len(unique_values), fixed_values[1])
print(first_item, middle_items, last_item)
print(child_box.value)
print(produced_total, root_value, handled)
print(merged_map["x"] + merged_map["y"], formatted, walrus_value)
print(loop_acc)
print(shared_counter is None)

# Loop else clauses
let items_found = False
for item in range(3):
    if item == 10:
        items_found = True
        break
else:
    items_found = "not_found"

let while_else_val = 0
while while_else_val < 2:
    while_else_val = while_else_val + 1
else:
    while_else_val = while_else_val + 10

# Starred unpacking variations
let a, *rest = [10, 20, 30, 40]
let *init, b = [10, 20, 30, 40]
let c, *middle, d = [10, 20, 30, 40]

# Set comprehension
let squared_set = {x * x for x in range(5)}

# Extended builtins
let power_result = pow(2, 8)
let divmod_result = divmod(17, 5)

# Yield from generator
def delegating_gen():
    yield from range(3)

let delegated = list(delegating_gen())

print(items_found, while_else_val)
print(a, rest, init, b, c, middle, d)
print(sorted(squared_set))
print(power_result, divmod_result)
print(delegated)
