# This file provides the functionality required for operations on polynomials
# Here a polynomial is defined as a list of coefficients
    # [a_0, a_1, ..., a_n] where a_0 = s in the case of shamir secret sharing
from custom_exceptions import exceptions


def get_polynomial(coefficients, prime):
    if (len(coefficients) == 0):
        raise exceptions.IllegalArgumentException

    def P(x):
        sum = 0
        for i in range(len(coefficients)):
            sum += (coefficients[i] * pow(x, i, prime)) % prime
        return sum % prime
    return P


def evaluate(coefficients, xlist, prime):
    '''
    Args:
        coefficients: a list holding the coefficients of the polynomial
        xlist: a list of points at which to evaluate the polynomial
        prime: arithmetic is done mod this prime
    Returns:
        a list of points, evaluated at the x values given
    Raises:
        IllegalArgumentException, does not accept empty coefficients
    '''
    f = get_polynomial(coefficients, prime)
    return [(x, f(x)) for x in xlist]


def interpolate(points, prime):
    '''
    Args:
        points: list of size t + 1 of tuples, (x, f(x))
                the algorithm assumes that exactly t + 1 points are provided
        prime: arithmetic is done mod this prime
    Returns:
        the polynomial f (list of coefficients)
    Raises:
        IllegalArgumentException, does not accept empty points
    See https://en.wikipedia.org/wiki/Lagrange_polynomial
    '''
    # we have k data points, (x_0, y_0),...,(x_k, y_k)

    # each l_j is formed as 


    # the result is the sum from 0 to k of y_j * l_j
    pass
