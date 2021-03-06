from robustsecretsharing.crypto_tools import random, primes

PRIME_EXP = 107  # default to sufficiently large Mersenne prime


def get_large_prime(max_length):
    '''
    Generate a large prime that accommodates the max message length or defaults to a large prime
    Args:
        integer value of maximum digit-length for a message
    Returns:
        a sufficiently large prime to be used in the check vector authentication scheme
    '''
    bitlength = max(PRIME_EXP, max_length * 8)
    return primes.get_prime_by_bitlength(bitlength)


def generate_check_vector(message, max_length):
    '''
    Args:
        message, the integer to be authenticated
        max_length, a value greater than or equal to len(str(message))
    Returns:
        (key, vector) where key is the integer MAC key and vector is the tuple MAC tag
    '''
    prime = get_large_prime(max_length)  # the probability of failure for prime p is 1/2^p

    b = random.get_random_positive_int_in_field(prime)
    y = random.get_random_int_in_field(prime)

    return y, (b, (message + b * y) % prime)


def validate(key, vector, message, max_length):
    '''
    Args:
        key, the integer key as returned by generate_check_vector[0]
        vector, the tuple as returned by generate_check_vector[1]
        message, the integer that was authenticated by generate_check_vector
        max_length, a value greater than or equal to len(str(message))
    Returns:
        True if the provided key and vector validate the given message,
        False otherwise
    '''
    return (message + vector[0] * key) % get_large_prime(max_length) == vector[1]


def generate_batch(num_macs, message, max_length):
    '''
    Args:
        num_macs, the number of (key, vector) pairs to return for the given message
        message, the integer to be authenticated
        max_length, a value greater than or equal to len(str(message))
    Return:
        a tuple of two parallel lists, which hold keys (integers) and vectors (tuples)
            such that each keys[i], vectors[i] pair authenticate the given message
    '''
    return zip(*[generate_check_vector(message, max_length) for _ in xrange(num_macs)])
