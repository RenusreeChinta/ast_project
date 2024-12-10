import math

def calculate_area(radius):
    pi = math.pi
    area = pi * (radius ** 2)
    return area

def greet_user(name):
    print(f"Hello, {name}!")
    return len(name)
