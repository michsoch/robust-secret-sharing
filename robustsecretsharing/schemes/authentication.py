from robustsecretsharing.crypto_tools import random, primes

PRIME_EXP = 107


def get_large_prime(max_length):
    bitlength = max(PRIME_EXP, max_length * 8)  # accommodate secret length or default to large exponent
    return primes.get_prime_by_bitlength(bitlength)


def generate_check_vector(message, max_length):
    '''
    Args:
        message, the integer to be authenticated
        max_length, a value greater than or equal to len(str(message))
    Returns:
        (key, vector) where key is the integer MAC key and vector is the tuple MAC tag
    '''
    prime = get_large_prime(max_length)

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
    prime = get_large_prime(max_length)

    return (message + vector[0] * key) % prime == vector[1]


def generate_batch(num_macs, message, max_length):
    '''
    Args:
        num_macs, the number of (key, vector) pairs to return for the given message
        message, the integer to be authenticated
        max_length, a value greater than or equal to len(str(message))
    Return:
        keys, vectors give parallel lists of keys (integers) and vectors (tuples)
            such that each keys[i], vectors[i] pair authenticate the given message
    '''
    keys = []
    vectors = []
    for n in xrange(num_macs):
        key, vector = generate_check_vector(message, max_length)
        keys.append(key)
        vectors.append(vector)
    return keys, vectors


def validate_batch(keys, vectors, message, max_length):
    '''
    Args:
        keys, a list of integer values
        vectors, a list of tuple values
        message, the message to verify for each keys[i], vectors[i] pair
        max_length, value greater than or equal to len(str(message))
    Returns:
        validated, a list of True or False values in parallel with keys and vectors
            such that validated[i] indicates if the keys[i], vectors[i] pair validated the message
    '''
    return [validate(key, vector, message, max_length) for (key, vector) in zip(keys, vectors)]
