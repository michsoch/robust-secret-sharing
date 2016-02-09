import pytest
from numbers import primes
from customexceptions import custom_exceptions

# test by batch


def test_get_prime_pos_single():
    batch = [44]
    assert primes.get_prime_by_batch(batch) == 127


def test_get_prime_by_batch_pos_multiple():
    batch = [100, 112358, 655, 9000]
    assert primes.get_prime_by_batch(batch) == 131071


def test_get_prime_by_batch_equal_prime():
    batch = [2**521 - 1]
    assert primes.get_prime_by_batch(batch) == 2**607 - 1


def test_get_prime_by_batch_neg_single():
    batch = [-44]
    assert primes.get_prime_by_batch(batch) == 3


def test_get_prime_by_batch_neg_multiple():
    batch = [-44, -66, -11]
    assert primes.get_prime_by_batch(batch) == 3


def test_get_prime_by_batch_very_large():
    batch = [2**107 - 1, 2**4253 - 1, 11, 2**4000]
    assert primes.get_prime_by_batch(batch) == 2**4423 - 1


def test_get_prime_by_batch_too_large():
    batch = [2**107 - 1, 2**4423 - 1, 11, 2**4000]
    assert primes.get_prime_by_batch(batch) is None


# test by bitlength


def test_get_prime_by_bitlength_standard():
    secret_size = 61
    assert primes.get_prime_by_bitlength(secret_size) == 2**89 - 1


def test_get_prime_by_bitlength_prime():
    secret_size = 17
    assert primes.get_prime_by_bitlength(secret_size) == 2**19 - 1


def test_get_prime_by_bitlength_zero():
    secret_size = 0
    assert primes.get_prime_by_bitlength(secret_size) == 2**2 - 1


def test_get_prime_by_bitlength_very_large():
    secret_size = 4400
    assert primes.get_prime_by_bitlength(secret_size) == 2**4423 - 1


def test_get_prime_by_bitlength_too_large():
    secret_size = 4444
    assert primes.get_prime_by_bitlength(secret_size) is None


def test_get_prime_by_bitlength_negative():
    secret_size = -7
    with pytest.raises(custom_exceptions.IllegalArgumentException):
        primes.get_prime_by_bitlength(secret_size)
