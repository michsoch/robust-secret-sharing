from numbers import primes


def test_get_prime_pos_single():
    batch = [44]
    assert primes.get_prime(batch) == 127


def test_get_prime_pos_multiple():
    batch = [100, 112358, 655, 9000]
    assert primes.get_prime(batch) == 131071


def test_get_prime_equal_prime():
    batch = [2**521 - 1]
    assert primes.get_prime(batch) == 2**607 - 1


def test_get_prime_neg_single():
    batch = [-44]
    assert primes.get_prime(batch) == 3


def test_get_prime_neg_multiple():
    batch = [-44, -66, -11]
    assert primes.get_prime(batch) == 3


def test_get_prime_very_large():
    batch = [2**107 - 1, 2**4253 - 1, 11, 2**4000]
    assert primes.get_prime(batch) == 2**4423 - 1


def test_get_prime_too_large():
    batch = [2**107 - 1, 2**4423 - 1, 11, 2**4000]
    assert primes.get_prime(batch) is None
