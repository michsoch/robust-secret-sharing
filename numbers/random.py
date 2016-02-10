import os
import math
from numbers import utilities
from customexceptions import custom_exceptions


def get_distinct_random_ints_in_field(num, prime):
    '''
    Args:
        num, the number of random values to return
        prime, specifies the upper bound (exclusive) for the random values
    Returns:
        a list of distinct, randomly generated values
    Raises:
        FatalConfigurationError, cannot return the requested number of values given the upper bound
        EntropyNotFound, OS does not provide a source of entropy
    '''
    if (num > prime):  # we can never get num distinct integers in this field
        raise custom_exceptions.FatalConfigurationError

    bitlength = prime.bit_length()
    bytelength = int(math.ceil((bitlength / 8.0)))  # round up bitlength to byteelength conversion
    random_values = []
    for i in range(num):
        try:
            value = get_random_int(bytelength) % prime
            while value in random_values:  # ensure distinct values
                value = get_random_int(bytelength) % prime
            random_values.append(value)
        except NotImplementedError:
            raise custom_exceptions.EntropyNotFound
    return random_values


def get_random_int(bytelength):
    '''
    Returns:
        a cryptographically-secure random integer that has the specified number of bytes
    Raises:
        NotImplementedError, no source of randomness found
    See:
        https://docs.python.org/3/library/os.html#os.urandom
        https://cryptography.io/en/latest/random-numbers/
    '''
    return utilities.convert_bytestring_to_int(os.urandom(bytelength))
