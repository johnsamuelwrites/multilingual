import math
from math import sqrt as root_fn

let acc_total = 0
let numbers = [1, 2, 3, 4]

for num_item in numbers:
    acc_total = acc_total + num_item

let idx_counter = 0
while idx_counter < 2:
    idx_counter = idx_counter + 1
    acc_total = acc_total + idx_counter

def adjust_val(value):
    if value > 5:
        return value - 1
    else:
        return value + 1

let adjusted = [adjust_val(v_item) for v_item in numbers if v_item > 2]
let flag_ok = True and not False
assert flag_ok

try:
    let root_value = root_fn(16)
except Exception as handled_error:
    let root_value = 0
finally:
    acc_total = acc_total + int(root_value)

class CounterBox:
    def __init__(self, start_value):
        self.value = start_value

    def bump(self):
        self.value = self.value + 1
        return self.value

let box = CounterBox(acc_total)
let bumped_value = box.bump()

print(acc_total)
print(len(adjusted))
print(bumped_value)
print(acc_total is None)
