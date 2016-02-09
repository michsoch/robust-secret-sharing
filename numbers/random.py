import os
import math
import codecs
from customexceptions import custom_exceptions


def get_distinct_random_ints_in_field(num, prime):
    '''
    Args:
        num, the number of values to return
        prime, defines the field
    Returns:
        a list of distinct, randomly generated values
    '''
    if (num > prime):  # we can never get num distinct integers in this field
        raise custom_exceptions.FatalConfigurationError

    bitlength = prime.bit_length()
    bytelength = int(math.ceil((bitlength / 8.0)))
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


def convert_bytestring_to_int(bytestring):
    # TODO: test
    return int(codecs.encode(bytestring, 'hex'), 16)


def convert_int_to_bytestring():
    # TODO: write and test
    pass


def get_random_int(bytelength):
    '''
    Args:
        bits, random value returned should have the specified number of bits
    Returns:
        a cryptographically-secure random integer that has the specified number of bits
    Raises:
        NotImplementedError, no source of randomness found
    See:
        https://docs.python.org/3/library/os.html#os.urandom
        https://cryptography.io/en/latest/random-numbers/
    '''
    return convert_bytestring_to_int(os.urandom(bytelength))
