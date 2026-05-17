**Pythagoras Theorem Implementation**
=====================================

### Code

```python
def calculate_hypotenuse(a: float, b: float) -> float:
    """
    Calculate the hypotenuse of a right-angled triangle using the Pythagorean theorem.

    Args:
        a (float): The length of one side of the triangle.
        b (float): The length of the other side of the triangle.

    Returns:
        float: The length of the hypotenuse.
    """
    if a < 0 or b < 0:
        raise ValueError("Side lengths cannot be negative.")
    return (a ** 2 + b ** 2) ** 0.5

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate the distance between two points in a 2D plane using the Pythagorean theorem.

    Args:
        x1 (float): The x-coordinate of the first point.
        y1 (float): The y-coordinate of the first point.
        x2 (float): The x-coordinate of the second point.
        y2 (float): The y-coordinate of the second point.

    Returns:
        float: The distance between the two points.
    """
    return calculate_hypotenuse(abs(x2 - x1), abs(y2 - y1))
```

### Example Use Cases

```python
print(calculate_hypotenuse(3, 4))  # Output: 5.0
print(calculate_distance(1, 2, 4, 6))  # Output: 5.0
```

This implementation includes:

*   Type hints for function arguments and return types
*   Docstrings for function documentation
*   Input validation to prevent negative side lengths
*   A separate function for calculating the distance between two points
*   Example use cases to demonstrate the usage of the functions