from unittest.mock import Mock

import pytest
from sympy import sin, cos, Poly, symbols
from sympy.plotting.plot import Plot

from approximation import Approximation, get_best_approximation
from polynomial import (
    get_nth_chebyshev_polynomial,
    normalise_polynomial,
    get_normalised_nth_chebyshev_polynomial,
    lower_degree_to,
    computed_polynomials,
)

X = symbols('x')


@pytest.fixture
def approximation():
    return Approximation(sin(X), (0, 1), 7)


def test_approximation_init(approximation):
    """Checks whether an object is initialized correctly"""
    assert approximation.function == sin(X)
    assert approximation.interval == (0, 1)
    assert approximation.polynomial_degree == 7


def test_approximation_coeffs(approximation):
    """Checks that the approximation factors are a list and have the
    correct length"""
    coeffs = approximation.coeffs
    assert isinstance(coeffs, list)
    assert len(coeffs) <= 8


@pytest.mark.parametrize(
    "function, interval, expected_error",
    [
        (sin(X), (0, 1), 0.01),
        (cos(X), (0, 1), 0.01),
    ],
)
def test_approximation_get_error(function, interval, expected_error):
    """Checks that the approximation error does not exceed the expected value
    for a given function and interval"""
    approx = Approximation(function, interval, 5)
    error = approx.get_error()
    assert error <= expected_error


def test_approximation_get_numpy_error(approximation):
    """Checks that the method returns an error less than or equal to 0.01"""
    mock_function = Mock(side_effect=lambda x: sin(x))
    error = approximation.get_numpy_error(mock_function)
    assert error <= 0.01


def test_approximation_plot_absolute_error():
    """Checks that the plot_absolute_error method returns a Plot object with
    correct data"""
    approx = Approximation(sin(X), (0, 1), 5)
    plot = approx.plot_absolute_error(show=False)
    assert isinstance(plot, Plot)
    assert plot is not None


def test_approximation_plot_approximation(approximation):
    """Checks that the method returns a Plot object"""
    plot = approximation.plot_approximation(show=False)
    assert isinstance(plot, Plot)


def test_get_best_approximation():
    """Verifies that a function returns a valid Approximation object"""
    function = sin(X)
    interval = (0, 1)
    polynomial_degree = 8
    approx = get_best_approximation(function, interval, polynomial_degree)
    
    assert isinstance(approx, Approximation)
    assert approx.function == function
    assert approx.interval == interval
    assert approx.polynomial_degree == polynomial_degree


def test_normalise_polynomial():
    """Checks that polynomials are normalized correctly"""
    poly = Poly(X**2 + 2*X + 1, X)
    normalised_poly = normalise_polynomial(poly)
    expected_poly = Poly(X**2 + 2*X + 1, X).as_expr().expand()
    assert normalised_poly.as_expr().expand() == expected_poly

    poly = Poly(2*X**2 + 4*X + 2, X)
    normalised_poly = normalise_polynomial(poly)
    expected_poly = Poly(X**2 + 2*X + 1, X)
    assert normalised_poly.as_expr().expand() == expected_poly.as_expr().expand()


def test_get_normalised_nth_chebyshev_polynomial():
    """Checks that correct normalized Chebyshev polynomials are returned"""
    normalised_poly = get_normalised_nth_chebyshev_polynomial(0)
    expected_poly = Poly(1, X)
    assert normalised_poly.as_expr() == expected_poly.as_expr()

    normalised_poly = get_normalised_nth_chebyshev_polynomial(3)
    expected_poly = Poly(4*X**3 - 3*X, X)
    expected_normalised_poly = normalise_polynomial(expected_poly)
    assert normalised_poly.as_expr() == expected_normalised_poly.as_expr()


def test_get_nth_chebyshev_polynomial_caching():
    """Checks the correctness of caching"""
    assert computed_polynomials[0] == Poly(1, X)
    assert computed_polynomials[1] == Poly(X, X)
    T_2 = get_nth_chebyshev_polynomial(2)

    assert T_2 == 2 * X * Poly(X, X) - Poly(1, X)
    assert computed_polynomials[2] == T_2


def test_get_nth_chebyshev_polynomial_recursion():
    """Checks that recursive computation of Chebyshev
    polynomials works correctly"""
    T_3 = get_nth_chebyshev_polynomial(3)
    T_4 = get_nth_chebyshev_polynomial(4)

    assert T_3.as_expr() == 4 * X**3 - 3 * X
    assert T_4.as_expr() == 8 * X**4 - 8 * X**2 + 1


@pytest.mark.parametrize(
    "polynomial, max_degree, expected_degree",
    [
        (Poly(X**4 + X**3 + X**2 + X + 1, X), 2, 2),
        (Poly(X**5 + X**4 + X**3 + X**2 + X + 1, X), 3, 3),
        (Poly(X**3 + X**2 + X + 1, X), 5, 3),
    ],
)
def test_lower_degree_to_parametrized(polynomial, max_degree, expected_degree):
    """Checks whether the degree reduction of a polynomial is correct in the
    parameterized case"""
    lowered = lower_degree_to(polynomial, max_degree)
    assert lowered.degree() <= expected_degree
