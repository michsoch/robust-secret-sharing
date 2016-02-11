import os
import math
from crypto_tools import utilities
from customexceptions import custom_exceptions


def get_distinct_random_ints_in_field(num_ints, prime):
    '''
    Args:
        num_ints, the number of random values to return
        prime, specifies the upper bound (exclusive) for the random values
    Returns:
        a list of distinct, randomly generated values
    Raises:
        FatalConfigurationError, cannot return the requested number of values given the upper bound
        EntropyNotFound, OS does not provide a source of entropy
    '''
    if num_ints > prime:  # we can never get num distinct integers in this field
        raise custom_exceptions.FatalConfigurationError

    bitlength = prime.bit_length()
    bytelength = int(math.ceil((bitlength / 8.0)))  # round up bitlength to byteelength conversion
    random_values = []
    for i in range(num_ints):
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
    '''
    return utilities.convert_bytestring_to_int(os.urandom(bytelength))
