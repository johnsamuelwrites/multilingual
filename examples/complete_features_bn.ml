আমদানি math
থেকে math আমদানি sqrt হিসাবে root_fn

ধরি ভাগ_করা_গণক = 3

সংজ্ঞা বৃদ্ধি_বৈশ্বিক():
    বিশ্বব্যাপী ভাগ_করা_গণক
    ভাগ_করা_গণক = ভাগ_করা_গণক + 2
    ফেরত ভাগ_করা_গণক

সংজ্ঞা তৈরি_গণক(শুরু):
    ধরি total = শুরু
    সংজ্ঞা ধাপ():
        অস্থানীয় total
        total = total + 1
        ফেরত total
    ফেরত ধাপ

ধরি পরবর্তী_গণক = তৈরি_গণক(5)
ধরি প্রথম_ধাপ = পরবর্তী_গণক()
ধরি দ্বিতীয়_ধাপ = পরবর্তী_গণক()

সাথে খুলো("tmp_complete_en.txt", "w", encoding="utf-8") হিসাবে লেখা_হ্যান্ডেল:
    লেখা_হ্যান্ডেল.write("ok")

ধরি ফাইল_পাঠ্য = ""
সাথে খুলো("tmp_complete_en.txt", "r", encoding="utf-8") হিসাবে পড়া_হ্যান্ডেল:
    ফাইল_পাঠ্য = পড়া_হ্যান্ডেল.read()

ধরি যুক্ত_জোড় = তালিকা(জোড়া([1, 2, 3], [4, 5, 6]))
ধরি অনন্য_মূল্য = সেট([1, 1, 2, 3])
ধরি স্থির_মূল্য = টিউপল([10, 20, 30])
ধরি প্রথম_উপাদান, *মধ্য_উপাদান, শেষ_উপাদান = [1, 2, 3, 4]
ধরি একীভূত_মানচিত্র = {**{"x": 1}, **{"y": 2}}

সংজ্ঞা ট্যাগ_বিন্যাস(a, /, *, b):
    ফেরত f"{a}-{b:.1f}"

ধরি লেবেল_ফর্ম্যাট = ট্যাগ_বিন্যাস(7, b=3.5)
ধরি বীজ = 0
ধরি মোচ_মূল্য = (বীজ := বীজ + 9)

শ্রেণি গণক_বাক্স:
    সংজ্ঞা __init__(self, শুরু_ভিত্তি):
        self.মূল্য = শুরু_ভিত্তি

শ্রেণি গণক_বাক্স_শিশু(গণক_বাক্স):
    সংজ্ঞা __init__(self, শুরু_ভিত্তি):
        সুপার(গণক_বাক্স_শিশু, self).__init__(শুরু_ভিত্তি)
        self.মূল্য = self.মূল্য + 1

সংজ্ঞা উৎপাদন_তিন():
    জন্য সূচক মধ্যে পরিসর(3):
        উৎপন্ন সূচক

ধরি মোট_উৎপন্ন = যোগফল(উৎপাদন_তিন())
ধরি পরিচালনা = মিথ্যা

চেষ্টা:
    যদি দৈর্ঘ্য(অনন্য_মূল্য) > 2:
        তোলো ValueError("boom")
ব্যতিক্রম ValueError হিসাবে পরিচালিত_ত্রুটি:
    পরিচালনা = সত্য
অবশেষে:
    ধরি মূল_মূল্য = পূর্ণসংখ্যা(root_fn(16))

ধরি অস্থায়ী_মূল্য = 99
মুছো অস্থায়ী_মূল্য

ধরি লুপ_সংগ্রহ = 0
জন্য n মধ্যে পরিসর(6):
    যদি n == 0:
        ছাড়ো
    যদি n == 4:
        থামো
    যদি n % 2 == 0:
        চালাও
    লুপ_সংগ্রহ = লুপ_সংগ্রহ + n

ধরি পতাকা_ঠিক = সত্য এবং না মিথ্যা
নিশ্চিত পতাকা_ঠিক

ধরি শিশু_বাক্স = গণক_বাক্স_শিশু(40)

ছাপাও(বৃদ্ধি_বৈশ্বিক())
ছাপাও(প্রথম_ধাপ, দ্বিতীয়_ধাপ)
ছাপাও(ফাইল_পাঠ্য)
ছাপাও(দৈর্ঘ্য(যুক্ত_জোড়), দৈর্ঘ্য(অনন্য_মূল্য), স্থির_মূল্য[1])
ছাপাও(প্রথম_উপাদান, মধ্য_উপাদান, শেষ_উপাদান)
ছাপাও(শিশু_বাক্স.মূল্য)
ছাপাও(মোট_উৎপন্ন, মূল_মূল্য, পরিচালনা)
ছাপাও(একীভূত_মানচিত্র["x"] + একীভূত_মানচিত্র["y"], লেবেল_ফর্ম্যাট, মোচ_মূল্য)
ছাপাও(লুপ_সংগ্রহ)
ছাপাও(ভাগ_করা_গণক হলো কিছুনা)

# Loop else clauses
ধরি উপাদান_পাওয়া = মিথ্যা
জন্য উপাদান মধ্যে পরিসর(3):
    যদি উপাদান == 10:
        উপাদান_পাওয়া = সত্য
        থামো
নাহলে:
    উপাদান_পাওয়া = "not_found"

ধরি যখন_অন্যথা_val = 0
যতক্ষণ যখন_অন্যথা_val < 2:
    যখন_অন্যথা_val = যখন_অন্যথা_val + 1
নাহলে:
    যখন_অন্যথা_val = যখন_অন্যথা_val + 10

# Starred unpacking variations
ধরি a, *বাকি = [10, 20, 30, 40]
ধরি *init, b = [10, 20, 30, 40]
ধরি c, *মধ্য, d = [10, 20, 30, 40]

# Set comprehension
ধরি বর্গ_সেট = {x * x জন্য x মধ্যে পরিসর(5)}

# Extended builtins
ধরি শক্তি_ফলাফল = ঘাত(2, 8)
ধরি divmod_ফলাফল = ভাগশেষ(17, 5)

# Yield from generator
সংজ্ঞা প্রতিনিধি_জেন():
    উৎপন্ন থেকে পরিসর(3)

ধরি প্রতিনিধিত্ব = তালিকা(প্রতিনিধি_জেন())

ছাপাও(উপাদান_পাওয়া, যখন_অন্যথা_val)
ছাপাও(a, বাকি, init, b, c, মধ্য, d)
ছাপাও(সাজানো(বর্গ_সেট))
ছাপাও(শক্তি_ফলাফল, divmod_ফলাফল)
ছাপাও(প্রতিনিধিত্ব)

# Numeric literals
ধরি hex_sankhya = 0xFF
ধরি oct_sankhya = 0o17
ধরি bin_sankhya = 0b1010
ধরি bigganik_sankhya = 1.5e3

# Augmented assignments
ধরি bardhito = 10
bardhito += 5
bardhito -= 2
bardhito *= 3
bardhito //= 4
bardhito %= 3

# Bitwise operators
ধরি bit_ebong = 0b1010 & 0b1100
ধরি bit_othoba = 0b1010 | 0b0101
ধরি bit_xor = 0b1010 ^ 0b1111
ধরি bit_bam = 1 << 3
ধরি bit_dan = 64 >> 2

# Chained assignment
ধরি shrinkhal_a = shrinkhal_b = shrinkhal_c = 0

# Type annotations
ধরি typito: int = 99

সংজ্ঞা tika_jukto(x: int, y: float) -> str:
    ফেরত str(x + y)

# Ternary expression
ধরি trimukhi = "yes" যদি typito > 0 নাহলে "no"

# Default params, *args, **kwargs
সংজ্ঞা bohu_param(base, extra=1, *args, **kwargs):
    ফেরত base + extra + sum(args)
ধরি bohu_fol = bohu_param(10, 2, 3, 4, key=5)

# Lambda
ধরি borgo = ল্যাম্বডা x: x * x

# List/dict comprehensions এবং generator expression
ধরি talika_c = [x * 2 জন্য x মধ্যে range(4)]
ধরি abhidhan_c = {str(k): k * k জন্য k মধ্যে range(3)}
ধরি gen_c = list(x + 1 জন্য x মধ্যে range(3))
ধরি nested_c = [i + j জন্য i মধ্যে range(2) জন্য j মধ্যে range(2)]
ধরি filter_c = [x জন্য x মধ্যে range(6) যদি x % 2 == 0]

# চেষ্টা/ব্যতিক্রম/নাহলে
ধরি chesta_na_hole = 0
চেষ্টা:
    chesta_na_hole = int("7")
ব্যতিক্রম ValueError:
    chesta_na_hole = -1
নাহলে:
    chesta_na_hole += 1

# Exception chaining
ধরি shrinkhalito = মিথ্যা
চেষ্টা:
    চেষ্টা:
        তোলো ValueError("v")
    ব্যতিক্রম ValueError হিসাবে ve:
        তোলো RuntimeError("r") থেকে ve
ব্যতিক্রম RuntimeError:
    shrinkhalito = সত্য

# Multiple ব্যতিক্রম handlers
ধরি bohu_byatikrom = 0
চেষ্টা:
    তোলো TypeError("t")
ব্যতিক্রম ValueError:
    bohu_byatikrom = 1
ব্যতিক্রম TypeError:
    bohu_byatikrom = 2

# Match/ক্ষেত্র সাথে পূর্বনির্ধারিত
ধরি match_man = 2
ধরি match_fol = "other"
মিলাও match_man:
    ক্ষেত্র 1:
        match_fol = "one"
    ক্ষেত্র 2:
        match_fol = "two"
    পূর্বনির্ধারিত:
        match_fol = "পূর্বনির্ধারিত"

# Decorator
সংজ্ঞা dwigunok(func):
    সংজ্ঞা morok(*args, **kwargs):
        ফেরত func(*args, **kwargs) * 2
    ফেরত morok

@dwigunok
সংজ্ঞা dosh():
    ফেরত 10

ধরি sajja_fol = dosh()

# Multiple inheritance, static/শ্রেণি methods, property
শ্রেণি Mishran:
    সংজ্ঞা mishao(self):
        ফেরত 1

শ্রেণি BhittiDui:
    সংজ্ঞা __init__(self, start):
        self.value = start

শ্রেণি Somonnito(BhittiDui, Mishran):
    @staticmethod
    সংজ্ঞা lebel():
        ফেরত "combined"
    @classmethod
    সংজ্ঞা nirman(cls, v):
        ফেরত cls(v)
    @property
    সংজ্ঞা dwigun(self):
        ফেরত self.value * 2

ধরি somonnito_obj = Somonnito.nirman(3)
ধরি gun = somonnito_obj.dwigun

# Docstring
সংজ্ঞা doc_soho():
    """Has a docstring."""
    ফেরত সত্য

print(hex_sankhya, oct_sankhya, bin_sankhya, bigganik_sankhya)
print(bardhito, bit_ebong, bit_othoba, bit_xor, bit_bam, bit_dan)
print(shrinkhal_a, shrinkhal_b, shrinkhal_c)
print(typito, tika_jukto(3, 1.5), trimukhi)
print(bohu_fol, borgo(5))
print(talika_c, abhidhan_c, gen_c)
print(nested_c, filter_c)
print(chesta_na_hole, shrinkhalito, bohu_byatikrom)
print(match_fol, sajja_fol, gun)
print(doc_soho())
