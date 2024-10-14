from multilingualprogramming.numeral.mp_numeral import MPNumeral

## Roman numerals
num1 = MPNumeral("VII")
num2 = MPNumeral("III")

print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)


## Unicode numerals
num1 = MPNumeral("١٢٣٤٥")
num2 = MPNumeral("൧൩")
print(num1 + num2)
print(num1 - num2)
print(num1 * num2)
print(num1 // num2)
print(num1 % num2)
print(num1**num2)
