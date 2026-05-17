**Fibonacci Series in Python**
================================

### Recursive Implementation

```python
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number recursively.

    Args:
    n (int): The position of the Fibonacci number to calculate.

    Returns:
    int: The nth Fibonacci number.
    """
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Iterative Implementation

```python
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number iteratively.

    Args:
    n (int): The position of the Fibonacci number to calculate.

    Returns:
    int: The nth Fibonacci number.
    """
    if n <= 1:
        return n

    fib_prev = 0
    fib_curr = 1

    for _ in range(2, n+1):
        fib_next = fib_prev + fib_curr
        fib_prev = fib_curr
        fib_curr = fib_next

    return fib_curr
```

### Memoization Implementation

```python
def fibonacci(n: int, memo: dict = {}) -> int:
    """
    Calculate the nth Fibonacci number using memoization.

    Args:
    n (int): The position of the Fibonacci number to calculate.
    memo (dict): A dictionary to store previously calculated Fibonacci numbers.

    Returns:
    int: The nth Fibonacci number.
    """
    if n <= 1:
        return n
    elif n in memo:
        return memo[n]
    else:
        fib = fibonacci(n-1, memo) + fibonacci(n-2, memo)
        memo[n] = fib
        return fib
```

### Example Usage

```python
n = 10
print(f"The {n}th Fibonacci number is: {fibonacci(n)}")
```

Note: The recursive implementation has an exponential time complexity, making it inefficient for large values of `n`. The iterative implementation has a linear time complexity, making it more efficient. The memoization implementation also has a linear time complexity, but with the added benefit of storing previously calculated Fibonacci numbers to avoid redundant calculations.