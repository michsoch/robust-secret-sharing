# TODO: different functionality for calculating allowed small vs suitably large p?
# TODO: for now, primes code based on https://github.com/blockstack/secret-sharing/blob/master/secretsharing/primes.py


def mersenne_primes():
    '''
    Returns all the mersenne primes with less than 2000 digits.
    '''
    mersenne_prime_exponents = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279,
                                2203, 2281, 3217, 4253, 4423]
    primes = []

    for exp in mersenne_prime_exponents:
        prime = 2**exp - 1
        primes.append(prime)
    return primes


def get_prime(batch):
    max_item = max(batch)
    primes = mersenne_primes()

    for prime in primes:
        if prime > max_item:
            return prime
    return None
