# Fibonacci sequence — multilingual source compiled to WASM
# No JavaScript host functions required: only WASI fd_write for stdout.

def fibonacci(n):
    let a = 0
    let b = 1
    let count = 0
    while count < n:
        let temp = b
        b = a + b
        a = temp
        count = count + 1
    return a

let i = 0
while i < 15:
    print(fibonacci(i))
    i = i + 1
