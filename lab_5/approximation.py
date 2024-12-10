"""
Module for approximating sympy expressions using the Taylor series and Chebyshev polynomials.
"""

import logging

from sympy import Poly, series, Expr
from sympy.plotting.plot import Plot, plot
from sympy.abc import x
from numpy import polyval
from polynomial import lower_degree_to
from typing import Tuple, Callable, List

logging.basicConfig(
    filename="prog-instruments-labs-yakovleva/lab_4/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Approximation:
    """
    Class for approximating sympy expressions using the Taylor series and Chebyshev polynomials.
    """

    def __init__(self,
                 function: Expr,
                 interval: Tuple[float, float],
                 polynomial_degree: int,
                 taylor_degree: int = 20,
                 point: float = 0) -> None:
        """
        Creates a new Approximation of the given expression which is approximated with a polynomial of
            degree `polynomial_degree`.

        First it creates a Taylor polynomial of the given `function` with `taylor_degree` degree around
            `point`. Then it lowers the polynomial degree using Chebyshev polynomials until the approximated
            polynomial degree is less than or equal to `polynomial_degree`.

        :param function: sympy expression to approximate
        :param interval: interval on which to approximate (used for calculating error and plotting)
        :param polynomial_degree: maximum degree of the approximation polynomial
        :param taylor_degree: degree of the starting Taylor polynomial
        :param point: point around which to create the Taylor polynomial
        :rtype: None
        """

        self.function = function
        self.interval = interval
        self.polynomial_degree = polynomial_degree

        logging.info("Initializing Approximation with function: %s", self.function)
        logging.info("Interval: %s, Polynomial degree: %d, Taylor degree: %d, Point: %f", 
                     interval, polynomial_degree, taylor_degree, point)

        try:
            self.__approximate_function(taylor_degree, point)
        except Exception as e:
            logging.error("Error during approximation: %s", str(e))

    def __approximate_function(self,
                               taylor_degree: int,
                               point: float) -> None:
        """
        Private function for approximating the sympy expression and lowering the Taylor polynomial's degree.

        :param taylor_degree: degree of the starting Taylor polynomial
        :param point: point around which to create the Taylor polynomial
        :rtype: None
        """

        logging.info("Creating Taylor approximation of degree %d around point %f", taylor_degree, point)
        try:
            taylor_approximation = Poly(series(self.function, x, point, n=taylor_degree).removeO())
            self.approximation = lower_degree_to(taylor_approximation, self.polynomial_degree)
            logging.info("Lowered polynomial degree to %d", self.approximation.degree())
        except Exception as e:
            logging.error("Error in creating Taylor approximation: %s", str(e))

    @property
    def coeffs(self) -> List[float]:
        """
        Function to get coefficients of the approximation polynomial.

        :return: list of coefficients of the approximation polynomial
        :rtype: List[float]
        """

        coeffs = [float(coeff) for coeff in self.approximation.all_coeffs()]
        logging.info("Coefficients of the approximation polynomial: %s", coeffs)
        return coeffs

    def get_coeffs_as_table(self) -> str:
        """
        Returns coefficients of the approximation polynomial in a simple markdown table with two columns,
            first column contains the coefficients and the second the terms.

        :return: coefficients in a simple markdown table with two columns
        :rtype: str
        """

        table = ''

        table += '|        Coefficient        |  Term  |\n'
        table += '|---------------------------|--------|\n'

        for (term, coeff) in Poly(self.approximation).all_terms():
            if coeff == 0:
                continue

            xpow = term[0]

            if xpow == 0:
                xterm = '1'
            elif xpow == 1:
                xterm = 'x'
            else:
                xterm = f'x<sup>{term[0]}</sup>'

            fcoeff = coeff.evalf(20)

            table += f'| `{fcoeff:+1.20f}` | <code>{xterm}</code> |\n'

        logging.info("Generated coefficient table:\n%s", table)
        return table

    def get_error(self,
                  step: float = 0.01) -> float:
        """
        Calculates the maximum absolute error between the given function and the approximation polynomial on the
            interval `interval` with the `step` step.

        :param step: step for calculating error
        :return: maximum error calculated using sympy on the given interval, with the given step
        :rtype: float
        """

        error = 0
        curr_x = self.interval[0]

        while curr_x <= (self.interval[1] + step):
            try:
                error = max(abs((self.function.as_poly() - self.approximation.as_expr()).subs({x: curr_x})), error)
            except Exception as e:
                logging.error("Error calculating error at x=%f: %s", curr_x, str(e))
            curr_x += step

        logging.info("Calculated max error: %f", error)
        return float(error)

    def get_numpy_error(self,
                        function: Callable,
                        step: float = 0.01) -> float:
        """
        Calculates the maximum absolute error between the given function and the approximation polynomial on the
            interval `interval` with the `step` step.

        :param function: a callable function which returns the same result as `function`
        :param step: step for calculating error
        :return: maximum error calculated using numpy on the given interval, with the given step
        :rtype: float
        """
        coeffs = self.coeffs
        error = 0
        curr_x = self.interval[0]

        while curr_x <= (self.interval[1] + step):
            try:
                error = max(abs(function(curr_x) - polyval(coeffs, curr_x)), error)
            except Exception as e:
                logging.error("Error calculating numpy error at x=%f: %s", curr_x, str(e))
            curr_x += step

        logging.info("Calculated numpy error: %f", error)
        return error

    def plot_approximation(self,
                           title: str = None,
                           nb_of_points: int = 400,
                           show: bool = True) -> Plot:
        """
        Plots the approximation polynomial using sympy's plot function on the given interval.

        :param title: title for the plot
        :param nb_of_points: number of points
        :param show: whether to show the plot
        :return: plot of the approximation
        :rtype: Plot
        """

        if title is None:
            title = f'f(x) $\\approx$ {self.function}'
        logging.info("Plotting approximation with title: %s", title)
        return plot(self.approximation.as_expr(),
                    (x, self.interval[0], self.interval[1]),
                    title=title,
                    adaptive=False,
                    nb_of_points=nb_of_points,
                    show=show,
                    ylabel='')

    def plot_absolute_error(self,
                            title: str = None,
                            nb_of_points: int = 400,
                            show: bool = True) -> Plot:
        """
        Plots the absolute error between the function and the approximation polynomial using sympy's plot
            on the given interval.

        :param title: title for the plot
        :param nb_of_points: number of points
        :param show: whether to show the plot
        :return: plot of the absolute error
        :rtype: Plot
        """

        if title is None:
            title = f'y = |f(x) - {self.function}|'
        logging.info("Plotting absolute error with title: %s", title)
        return plot(abs(self.function - self.approximation),
                    (x, self.interval[0], self.interval[1]),
                    title=title,
                    adaptive=False,
                    nb_of_points=nb_of_points,
                    ylabel='',
                    show=show)


def get_best_approximation(function: Expr,
                           interval: Tuple[float, float],
                           polynomial_degree: int,
                           start_taylor_degree: int = None,
                           point: float = 0) -> Approximation:
    """
    Finds the best approximation by increasing the starting Taylor polynomial degree until the maximum absolute error
        stops decreasing.

    :param function: sympy expression to approximate
    :param interval: interval on which to approximate (used for calculating error and plotting)
    :param polynomial_degree: maximum degree of the approximation polynomial
    :param start_taylor_degree: degree of the starting Taylor polynomial
    :param point: point around which to create the Taylor polynomial
    :return: the approximation with the smallest maximum absolute error
    :rtype: Approximation
    """

    if start_taylor_degree is None:
        start_taylor_degree = polynomial_degree + 1

    logging.info("Finding best approximation with start Taylor degree: %d", start_taylor_degree)
    
    try:
        prev_approximation = Approximation(function, interval, polynomial_degree, start_taylor_degree, point)
        curr_approximation = Approximation(function, interval, polynomial_degree, start_taylor_degree + 1, point)
        taylor_degree = start_taylor_degree + 2

        while prev_approximation.get_error() > curr_approximation.get_error():
            prev_approximation = curr_approximation
            curr_approximation = Approximation(function, interval, polynomial_degree, taylor_degree, point)
            taylor_degree += 1

        logging.info("Best approximation found with max error: %f", prev_approximation.get_error())
        return prev_approximation
    except Exception as e:
        logging.error("Error finding best approximation: %s", str(e))
        raise