from sympy import symbols, sin
from approximation import Approximation 

x = symbols('x')
function = sin(x) 
interval = (0, 1)
polynomial_degree = 7
approx = Approximation(function, interval, polynomial_degree)

print("Coefficients:", approx.coeffs)
print("Max error:", approx.get_error())
