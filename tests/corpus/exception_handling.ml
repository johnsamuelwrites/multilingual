# -*- coding: utf-8 -*-
# Exception Handling: Try/except/finally blocks
# Demonstrates exception catching and cleanup

def divide_by_zero():
    try:
        let result = 10 / 0
    except ZeroDivisionError:
        print("Error caught")
    finally:
        print("Cleanup")

divide_by_zero()

# Normal execution after exception
try:
    let x = 5
    print("Success")
except:
    print("Unexpected error")
