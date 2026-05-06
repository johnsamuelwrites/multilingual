import math
from math import sqrt as root_fn
import asyncio

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

# Numeric literals
let hex_num = 0xFF
let oct_num = 0o17
let bin_num = 0b1010
let sci_num = 1.5e3

# Augmented assignments
let aug = 10
aug += 5
aug -= 2
aug *= 3
aug //= 4
aug %= 3

# Bitwise operators
let bit_a = 0b1010 & 0b1100
let bit_o = 0b1010 | 0b0101
let bit_x = 0b1010 ^ 0b1111
let bit_l = 1 << 3
let bit_r = 64 >> 2

# Chained assignment
let ca = cb = cc = 0

# Type annotations
let typed: int = 99

def annotated(x: int, y: float) -> str:
    return str(x + y)

# Ternary expression
let ternary = "yes" if typed > 0 else "no"

# Default params, *args, **kwargs
def multi_params(base, extra=1, *args, **kwargs):
    return base + extra + sum(args)
let multi_result = multi_params(10, 2, 3, 4, key=5)

# Lambda
let sq = lambda x: x * x

# List/dict comprehensions and generator expression
let list_c = [x * 2 for x in range(4)]
let dict_c = {str(k): k * k for k in range(3)}
let gen_c = list(x + 1 for x in range(3))
let nested_c = [i + j for i in range(2) for j in range(2)]
let filter_c = [x for x in range(6) if x % 2 == 0]

# try/except/else
let try_else = 0
try:
    try_else = int("7")
except ValueError:
    try_else = -1
else:
    try_else += 1

# Exception chaining
let chained = False
try:
    try:
        raise ValueError("v")
    except ValueError as ve:
        raise RuntimeError("r") from ve
except RuntimeError:
    chained = True

# Multiple except handlers
let multi_exc = 0
try:
    raise TypeError("t")
except ValueError:
    multi_exc = 1
except TypeError:
    multi_exc = 2

# Match/case with default
let mv = 2
let mr = "other"
match mv:
    case 1:
        mr = "one"
    case 2:
        mr = "two"
    default:
        mr = "default"

# Decorator
def doubler(func):
    def wrap(*args, **kwargs):
        return func(*args, **kwargs) * 2
    return wrap

@doubler
def ten():
    return 10

let dec_r = ten()

# Multiple inheritance, static/class methods, property
class Mixin:
    def mix(self):
        return 1

class BaseTwo:
    def __init__(self, start):
        self.value = start

class Combined(BaseTwo, Mixin):
    @staticmethod
    def label():
        return "combined"
    @classmethod
    def build(cls, v):
        return cls(v)
    @property
    def doubled(self):
        return self.value * 2

let comb = Combined.build(3)
let prop = comb.doubled

# Docstring
def with_doc():
    """Has a docstring."""
    return True

print(hex_num, oct_num, bin_num, sci_num)
print(aug, bit_a, bit_o, bit_x, bit_l, bit_r)
print(ca, cb, cc)
print(typed, annotated(3, 1.5), ternary)
print(multi_result, sq(5))
print(list_c, dict_c, gen_c)
print(nested_c, filter_c)
print(try_else, chained, multi_exc)
print(mr, dec_r, prop)
print(with_doc())

# Bitwise and power augmented assignments (v0.6.0)
let bau = 0b1111
bau &= 0b1010
bau |= 0b0100
bau ^= 0b0011
bau <<= 1
bau >>= 2
let pow_aug = 2
pow_aug **= 4

# Bytes literal (v0.6.0)
let bdata = b"hello"
let blen = len(bdata)

# String concatenation, indexing, slicing (v0.6.0)
let str_a = "hello"
let str_b = " world"
let str_cat = str_a + str_b
let str_idx = str_a[1]
let str_slc = str_a[1:3]

# Tuple literal (v0.6.0)
let tup_lit = (10, 20, 30)
let tup_elem = tup_lit[1]

# for loop and comprehension over list variable (v0.6.0)
let iter_list = [10, 20, 30]
let iter_sum = 0
for iter_val in iter_list:
    iter_sum = iter_sum + iter_val

let comp_list = [1, 2, 3, 4]
let doubled_list = [v * 2 for v in comp_list]

# Extended match/case: string, None, capture, and tuple patterns (v0.6.0)
let ms = "hello"
let msr = "none"
match ms:
    case "hello":
        msr = "hi"
    case "bye":
        msr = "goodbye"
    default:
        msr = "unknown"

let mn = None
let mnr = "defined"
match mn:
    case None:
        mnr = "null"
    default:
        mnr = "other"

let mc = 42
let mcr = 0
match mc:
    case 42:
        mcr = mc
    default:
        mcr = 0

let mt = (1, 2)
let mtr = "no"
match mt:
    case (1, 2):
        mtr = "yes"
    default:
        mtr = "no"

# async def, await, async for, async with (v0.6.0)
async def async_double(n):
    await asyncio.sleep(0)
    return n * 2

async def async_gen():
    for v in range(3):
        yield v

async def async_for_task():
    let total = 0
    async for av in async_gen():
        total = total + av
    return total

class AsyncCtxEn:
    async def __aenter__(self):
        return 5
    async def __aexit__(self, exc_type, exc, tb):
        return False

async def async_with_task():
    async with AsyncCtxEn() as value:
        return value

let async_result = asyncio.run(async_double(5))
let async_for_result = asyncio.run(async_for_task())
let async_with_result = asyncio.run(async_with_task())

print(bau, pow_aug)
print(blen)
print(str_cat, str_idx, str_slc)
print(tup_elem, iter_sum)
print(doubled_list)
print(msr, mnr, mcr, mtr)
print(async_result, async_for_result, async_with_result)
