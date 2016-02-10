from customexceptions import custom_exceptions

MERSENNE_PRIME_EXPONENTS = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279,
                            2203, 2281, 3217, 4253, 4423]


def mersenne_primes():
    '''
    Returns:
        all the mersenne primes with less than 5000 digits.
    '''
    primes = []

    for exp in MERSENNE_PRIME_EXPONENTS:
        prime = 2**exp - 1
        primes.append(prime)
    return primes


def get_prime_by_bitlength(bitlength):
    '''
    Returns:
        a prime with strictly more bits than the specified size
        or None if no such prime is found in hardcoded list
    Raises:
        IllegalArgumentException, size is negative
    '''
    if (bitlength < 0):
        raise custom_exceptions.IllegalArgumentException

    for exp in MERSENNE_PRIME_EXPONENTS:
        if exp > bitlength:
            return 2**exp - 1
    return None


def get_prime_by_batch(batch):
    '''
    Returns:
        a prime strictly larger than all values in the list provided in batch
        or None if no such prime is found in hardcoded list
    '''
    max_item = max(batch)
    primes = mersenne_primes()

    for prime in primes:
        if prime > max_item:
            return prime
    return None
