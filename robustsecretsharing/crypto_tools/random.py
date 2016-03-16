import os
import math
from robustsecretsharing.crypto_tools import serialization


def _get_byte_length(value):
    bitlength = value.bit_length()
    return int(math.ceil((bitlength / 8.0)))


def get_random_int_in_field(prime):
    '''
    Args:
        prime, specifies the upper bound (exclusive) for the random values
    Returns:
        a cryptographically-secure random integer within the specified field
    Raises:
        ValueError, OS does not provide a source of entropy
    '''
    try:
        bytelength = _get_byte_length(prime)
        random_int = serialization.convert_bytestring_to_int(os.urandom(bytelength))
        return random_int % prime
    except NotImplementedError:
        raise ValueError("no found implementation for entropy")


def get_random_positive_int_in_field(prime):
    '''
    Args:
        prime, specifies the upper bound (exclusive) for the random values
    Returns:
        a positive cryptographically-secure random integer within the specified field
    '''
    random_int = 0
    while random_int == 0:
        random_int = get_random_int_in_field(prime)
    return random_int


def get_distinct_positive_random_ints_in_field(num_ints, prime):
    '''
    Args:
        num_ints, the number of random values to return
        prime, specifies the upper bound (exclusive) for the random values
    Returns:
        a list of distinct, positive, and randomly generated values
    '''
    if num_ints >= prime:
        raise ValueError("selected field is too small")

    random_values = set()
    while len(random_values) < num_ints:
        random_values.add(get_random_positive_int_in_field(prime))
    return list(random_values)
