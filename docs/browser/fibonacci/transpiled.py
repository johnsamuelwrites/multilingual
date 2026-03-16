def fibonacci(n):
    a = 0
    b = 1
    count = 0
    while (count < n):
        temp = b
        b = (a + b)
        a = temp
        count = (count + 1)
    return a
i = 0
while (i < 15):
    print(fibonacci(i))
    i = (i + 1)
