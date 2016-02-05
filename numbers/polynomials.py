# This file provides the functionality required for operations on polynomials
# Here a polynomial is defined as a list of coefficients
    # [a_0, a_1, ..., a_n] where a_0 = s in the case of shamir secret sharing
from custom_exceptions import exceptions


def evaluate(coefficients, x, prime):
    '''
    Args:
        coefficients: list representing a polynomial
        x: the point at which to evaluate the polynomial
        prime: arithmetic is done mod this prime
    Returns:
        the value of the polynomial at the given point x.
    Raises:
        IllegalArgumentException, does not accept empty coefficients
    '''
    if (len(coefficients) == 0):
        raise exceptions.IllegalArgumentException

    sum = 0
    for i in range(len(coefficients)):
        sum += (coefficients[i] * pow(x, i, prime)) % prime
    return sum % prime


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
    '''
    pass
