இறக்கு math
இருந்து math இறக்கு sqrt ஆக root_fn

இருக்கட்டும் பகிரப்பட்ட_எண்ணி = 3

வரையறு அதிகரிப்பு_உலகளாவிய():
    உலகளாவிய பகிரப்பட்ட_எண்ணி
    பகிரப்பட்ட_எண்ணி = பகிரப்பட்ட_எண்ணி + 2
    திருப்பு பகிரப்பட்ட_எண்ணி

வரையறு உருவாக்கு_எண்ணி(தொடக்கம்):
    இருக்கட்டும் total = தொடக்கம்
    வரையறு படி():
        உள்ளூரல்லாத total
        total = total + 1
        திருப்பு total
    திருப்பு படி

இருக்கட்டும் அடுத்த_எண்ணி = உருவாக்கு_எண்ணி(5)
இருக்கட்டும் முதல்_படி = அடுத்த_எண்ணி()
இருக்கட்டும் இரண்டாம்_படி = அடுத்த_எண்ணி()

உடன் திற("tmp_complete_en.txt", "w", encoding="utf-8") ஆக எழுது_கைப்பிடி:
    எழுது_கைப்பிடி.write("ok")

இருக்கட்டும் கோப்பு_உரை = ""
உடன் திற("tmp_complete_en.txt", "r", encoding="utf-8") ஆக படி_கைப்பிடி:
    கோப்பு_உரை = படி_கைப்பிடி.read()

இருக்கட்டும் இணைக்கப்பட்ட_ஜோடி = பட்டியல்(இணை([1, 2, 3], [4, 5, 6]))
இருக்கட்டும் தனித்துவமான_மதிப்புகள் = தொகுப்பு([1, 1, 2, 3])
இருக்கட்டும் நிலையான_மதிப்புகள் = டப்பிள்([10, 20, 30])
இருக்கட்டும் முதல்_உறுப்பு, *நடுவண்_உறுப்பு, கடைசி_உறுப்பு = [1, 2, 3, 4]
இருக்கட்டும் இணைக்கப்பட்ட_வரைபடம் = {**{"x": 1}, **{"y": 2}}

வரையறு குறி_வடிவம்(a, /, *, b):
    திருப்பு f"{a}-{b:.1f}"

இருக்கட்டும் குறி_வடிவமாக்கப்பட்ட = குறி_வடிவம்(7, b=3.5)
இருக்கட்டும் விதை = 0
இருக்கட்டும் மீசை_மதிப்பு = (விதை := விதை + 9)

வகுப்பு எண்ணி_பெட்டி:
    வரையறு __init__(self, அடிப்படை_தொடக்கம்):
        self.மதிப்பு = அடிப்படை_தொடக்கம்

வகுப்பு எண்ணி_குழந்தை_பெட்டி(எண்ணி_பெட்டி):
    வரையறு __init__(self, அடிப்படை_தொடக்கம்):
        மேற்கிளை(எண்ணி_குழந்தை_பெட்டி, self).__init__(அடிப்படை_தொடக்கம்)
        self.மதிப்பு = self.மதிப்பு + 1

வரையறு உற்பத்தி_மூன்று():
    ஒவ்வொரு சுட்டி இல் வரம்பு(3):
        விளை சுட்டி

இருக்கட்டும் மொத்த_உற்பத்தி = கூட்டுத்தொகை(உற்பத்தி_மூன்று())
இருக்கட்டும் கையாளப்பட்ட = பொய்

முயற்சி:
    என்றால் நீளம்(தனித்துவமான_மதிப்புகள்) > 2:
        எழுப்பு ValueError("boom")
விதிவிலக்கு ValueError ஆக கையாளப்பட்ட_பிழை:
    கையாளப்பட்ட = உண்மை
இறுதியாக:
    இருக்கட்டும் மூல_மதிப்பு = முழு(root_fn(16))

இருக்கட்டும் தற்காலிக_மதிப்பு = 99
அழி தற்காலிக_மதிப்பு

இருக்கட்டும் வளைய_தொகுப்பு = 0
ஒவ்வொரு n இல் வரம்பு(6):
    என்றால் n == 0:
        தாண்டு
    என்றால் n == 4:
        நிறுத்து
    என்றால் n % 2 == 0:
        தொடர்
    வளைய_தொகுப்பு = வளைய_தொகுப்பு + n

இருக்கட்டும் கொடி_சரி = உண்மை மற்றும் அல்லை பொய்
உறுதி கொடி_சரி

இருக்கட்டும் குழந்தை_பெட்டி = எண்ணி_குழந்தை_பெட்டி(40)

அச்சிடு(அதிகரிப்பு_உலகளாவிய())
அச்சிடு(முதல்_படி, இரண்டாம்_படி)
அச்சிடு(கோப்பு_உரை)
அச்சிடு(நீளம்(இணைக்கப்பட்ட_ஜோடி), நீளம்(தனித்துவமான_மதிப்புகள்), நிலையான_மதிப்புகள்[1])
அச்சிடு(முதல்_உறுப்பு, நடுவண்_உறுப்பு, கடைசி_உறுப்பு)
அச்சிடு(குழந்தை_பெட்டி.மதிப்பு)
அச்சிடு(மொத்த_உற்பத்தி, மூல_மதிப்பு, கையாளப்பட்ட)
அச்சிடு(இணைக்கப்பட்ட_வரைபடம்["x"] + இணைக்கப்பட்ட_வரைபடம்["y"], குறி_வடிவமாக்கப்பட்ட, மீசை_மதிப்பு)
அச்சிடு(வளைய_தொகுப்பு)
அச்சிடு(பகிரப்பட்ட_எண்ணி ஆகும் ஒன்றுமில்லை)

# Loop else clauses
இருக்கட்டும் உறுப்புகள்_கண்டுபிடிக்கப்பட்ட = பொய்
ஒவ்வொரு உறுப்பு இல் வரம்பு(3):
    என்றால் உறுப்பு == 10:
        உறுப்புகள்_கண்டுபிடிக்கப்பட்ட = உண்மை
        நிறுத்து
இல்லை:
    உறுப்புகள்_கண்டுபிடிக்கப்பட்ட = "not_found"

இருக்கட்டும் வரை_மற்றும்_மதிப்பு = 0
வரை வரை_மற்றும்_மதிப்பு < 2:
    வரை_மற்றும்_மதிப்பு = வரை_மற்றும்_மதிப்பு + 1
இல்லை:
    வரை_மற்றும்_மதிப்பு = வரை_மற்றும்_மதிப்பு + 10

# Starred unpacking variations
இருக்கட்டும் a, *மீதம் = [10, 20, 30, 40]
இருக்கட்டும் *init, b = [10, 20, 30, 40]
இருக்கட்டும் c, *நடு, d = [10, 20, 30, 40]

# Set comprehension
இருக்கட்டும் வர்க்க_தொகுப்பு = {x * x ஒவ்வொரு x இல் வரம்பு(5)}

# Extended builtins
இருக்கட்டும் சக்தி_முடிவு = அடுக்கு(2, 8)
இருக்கட்டும் divmod_முடிவு = வகுமீதி(17, 5)

# Yield from generator
வரையறு பிரதிநிதி_உருவாக்கி():
    விளை இருந்து வரம்பு(3)

இருக்கட்டும் பிரதிநிதியாக்கப்பட்ட = பட்டியல்(பிரதிநிதி_உருவாக்கி())

அச்சிடு(உறுப்புகள்_கண்டுபிடிக்கப்பட்ட, வரை_மற்றும்_மதிப்பு)
அச்சிடு(a, மீதம், init, b, c, நடு, d)
அச்சிடு(வரிசைப்படுத்து(வர்க்க_தொகுப்பு))
அச்சிடு(சக்தி_முடிவு, divmod_முடிவு)
அச்சிடு(பிரதிநிதியாக்கப்பட்ட)

# Numeric literals
இருக்கட்டும் hex_en = 0xFF
இருக்கட்டும் oct_en = 0o17
இருக்கட்டும் bin_en = 0b1010
இருக்கட்டும் ariviyal_en = 1.5e3

# Augmented assignments
இருக்கட்டும் adhigarippu = 10
adhigarippu += 5
adhigarippu -= 2
adhigarippu *= 3
adhigarippu //= 4
adhigarippu %= 3

# Bitwise operators
இருக்கட்டும் bit_matrum = 0b1010 & 0b1100
இருக்கட்டும் bit_allathu = 0b1010 | 0b0101
இருக்கட்டும் bit_xor = 0b1010 ^ 0b1111
இருக்கட்டும் bit_idam = 1 << 3
இருக்கட்டும் bit_valam = 64 >> 2

# Chained assignment
இருக்கட்டும் saram_a = saram_aa = saram_i = 0

# Type annotations
இருக்கட்டும் vakaiyitta: int = 99

வரையறு kurippitta(x: int, y: float) -> str:
    திருப்பு str(x + y)

# Ternary expression
இருக்கட்டும் mummunai = "yes" என்றால் vakaiyitta > 0 இல்லை "no"

# Default params, *args, **kwargs
வரையறு pala_alavurukkal(base, extra=1, *args, **kwargs):
    திருப்பு base + extra + sum(args)
இருக்கட்டும் pala_mudivu = pala_alavurukkal(10, 2, 3, 4, key=5)

# Lambda
இருக்கட்டும் vargam = லாம்டா x: x * x

# List/dict comprehensions மற்றும் generator expression
இருக்கட்டும் pattiyal_c = [x * 2 ஒவ்வொரு x இல் range(4)]
இருக்கட்டும் akarathi_c = {str(k): k * k ஒவ்வொரு k இல் range(3)}
இருக்கட்டும் uruvakki_c = list(x + 1 ஒவ்வொரு x இல் range(3))
இருக்கட்டும் utpothi_c = [i + j ஒவ்வொரு i இல் range(2) ஒவ்வொரு j இல் range(2)]
இருக்கட்டும் vadikatti_c = [x ஒவ்வொரு x இல் range(6) என்றால் x % 2 == 0]

# முயற்சி/விதிவிலக்கு/இல்லை
இருக்கட்டும் muyarchi_illaiyenil = 0
முயற்சி:
    muyarchi_illaiyenil = int("7")
விதிவிலக்கு ValueError:
    muyarchi_illaiyenil = -1
இல்லை:
    muyarchi_illaiyenil += 1

# Exception chaining
இருக்கட்டும் sangili = பொய்
முயற்சி:
    முயற்சி:
        எழுப்பு ValueError("v")
    விதிவிலக்கு ValueError ஆக ve:
        எழுப்பு RuntimeError("r") இருந்து ve
விதிவிலக்கு RuntimeError:
    sangili = உண்மை

# Multiple விதிவிலக்கு handlers
இருக்கட்டும் pala_vidivilakku = 0
முயற்சி:
    எழுப்பு TypeError("t")
விதிவிலக்கு ValueError:
    pala_vidivilakku = 1
விதிவிலக்கு TypeError:
    pala_vidivilakku = 2

# Match/நிலை உடன் இயல்பு
இருக்கட்டும் poruththa_madhippu = 2
இருக்கட்டும் poruththa_mudivu = "other"
பொருத்து poruththa_madhippu:
    நிலை 1:
        poruththa_mudivu = "one"
    நிலை 2:
        poruththa_mudivu = "two"
    இயல்பு:
        poruththa_mudivu = "இயல்பு"

# Decorator
வரையறு irattippan(func):
    வரையறு moodu(*args, **kwargs):
        திருப்பு func(*args, **kwargs) * 2
    திருப்பு moodu

@irattippan
வரையறு pathu():
    திருப்பு 10

இருக்கட்டும் alangara_mudivu = pathu()

# Multiple inheritance, static/வகுப்பு methods, property
வகுப்பு Kalavai:
    வரையறு kalakku(self):
        திருப்பு 1

வகுப்பு AdipadaiIrandu:
    வரையறு __init__(self, start):
        self.value = start

வகுப்பு Inaindha(AdipadaiIrandu, Kalavai):
    @staticmethod
    வரையறு peyarsutti():
        திருப்பு "combined"
    @classmethod
    வரையறு uruvakku(cls, v):
        திருப்பு cls(v)
    @property
    வரையறு irattippu(self):
        திருப்பு self.value * 2

இருக்கட்டும் inaindha_porul = Inaindha.uruvakku(3)
இருக்கட்டும் panbu = inaindha_porul.irattippu

# Docstring
வரையறு aavanathudan():
    """Has a docstring."""
    திருப்பு உண்மை

print(hex_en, oct_en, bin_en, ariviyal_en)
print(adhigarippu, bit_matrum, bit_allathu, bit_xor, bit_idam, bit_valam)
print(saram_a, saram_aa, saram_i)
print(vakaiyitta, kurippitta(3, 1.5), mummunai)
print(pala_mudivu, vargam(5))
print(pattiyal_c, akarathi_c, uruvakki_c)
print(utpothi_c, vadikatti_c)
print(muyarchi_illaiyenil, sangili, pala_vidivilakku)
print(poruththa_mudivu, alangara_mudivu, panbu)
print(aavanathudan())
