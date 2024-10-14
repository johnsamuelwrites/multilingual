# multilingual
Python application for multilingual programming

## Usage
To use `multilingual`, check the following example for handling arithmetic
operations

```python
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
```

This will give the following output:

```bash
X
IV
XXI
II
I
```

## Resources
[Resources](resources/README.md): Resources and references to sources in different languages

## Contribute
There are two ways to contribute:
* Add a missing language in [resources](./resources) folder.
* Update resources related to the already existing languages. For example, in [English](./resources/en/README.md).

## Author
* John Samuel

## Licence
All code are released under GPLv3+ licence. The associated documentation and other content are released under [CC-BY-SA](http://creativecommons.org/licenses/by-sa/4.0/).
