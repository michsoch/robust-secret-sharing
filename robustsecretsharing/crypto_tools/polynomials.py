def _egcd(a, b):
    '''
    Implements the extended euclidean algorithm
    Returns:
        the tuple (g, x, y), such that ax + by = g = gcd(a, b)
    '''
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = _egcd(b % a, a)
        return g, x - (b // a) * y, y


def _inverse_mod(k, prime):
    '''
    Returns:
        the inverse mod of k within the field defined by the prime
    '''
    k = k % prime
    if k < 0:
        r = _egcd(prime, -k)[2]
    else:
        r = _egcd(prime, k)[2]
    return (prime + r) % prime


def get_polynomial(coefficients, prime):
    '''
    Args:
        coefficients: a list of integers holding the coefficients of the polynomial
        prime: arithmetic is done mod this prime
    Returns:
        P: a function that takes an integer x and returns the evaluation of the polynomial at that point
    Raises:
        ValueError, passed an empty coefficients list
    '''
    if len(coefficients) <= 1:
        raise ValueError("too few coefficients to construct a polynomial")

    def P(x):
        sum = 0
        for i in xrange(len(coefficients)):
            sum += (coefficients[i] * pow(x, i, prime)) % prime
        return sum % prime
    return P


def evaluate(coefficients, xlist, prime):
    '''
    Args:
        coefficients: a list of integers holding the coefficients of the polynomial
        xlist: a list of integer points at which to evaluate the polynomial
        prime: arithmetic is done mod this prime
    Returns:
        a list of integer points, evaluated at the x values given
    Raises:
        ValueError, propagates from get_polynomial
    '''
    f = get_polynomial(coefficients, prime)
    return [(x, f(x)) for x in xlist]


def interpolate(points, prime):
    '''
    Args:
        points: list of tuples, (x, f(x)), where both values are integers
                the number of points given is assumed to be the degree of the polynomial
        prime: arithmetic is done mod this prime
    Returns:
        P: a function that takes a value x and returns the evaluation of the polynomial at that point
    Raises:
        ValueError, passed too few points

    See https://en.wikipedia.org/wiki/Lagrange_polynomial
    '''
    degree = len(points)
    if degree <= 1:
        raise ValueError("too few points to recover a polynomial")

    # convert t + 1 data points, (x_0, y_0),...,(x_{t+1}, y_{t+1}) into lists of x and y
    x_vals, y_vals = map(list, zip(*points))

    def P(x):
        basis = []
        for j in xrange(degree):  # the jth basis is the product over m from 0 to degree with m != j
            numerator, denominator = 1, 1   # of (x - x_m) / (x_j - x_m)
            for m in range(j) + range(j + 1, degree):
                numerator = (numerator * (x - x_vals[m])) % prime
                denominator = (denominator * (x_vals[j] - x_vals[m])) % prime
            basis.append((numerator * _inverse_mod(denominator, prime)) % prime)

        # return the sum of the product of each y value which its corresponding basis polynomial
        result = 0
        for i in xrange(degree):
            result += y_vals[i] * basis[i]
        return result % prime
    return P
