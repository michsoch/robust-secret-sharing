import pytest
from customexceptions import custom_exceptions
from numbers import random


def test_random_big_single():
    prime = 2**4253 - 1
    random_values = random.get_distinct_random_ints_in_field(1, prime)
    assert len(random_values) == 1 and \
        random_values[0].bit_length() < prime and \
        len(random_values) == len(set(random_values))  # check distinct


def test_random_small_single():
    prime = 2**3 - 1
    random_values = random.get_distinct_random_ints_in_field(1, prime)
    assert len(random_values) == 1 and \
        random_values[0] < prime and\
        random_values[0].bit_length > 0 and \
        len(random_values) == len(set(random_values))  # check distinct


def test_random_big_multiple():
    prime = 2**4253 - 1
    num = 5
    random_values = random.get_distinct_random_ints_in_field(num, prime)
    assert len(random_values) == num and \
        len([value for value in random_values if value < prime]) == num and \
        len(random_values) == len(set(random_values))  # check distinct


def test_random_small_multiple():
    prime = 2**3 - 1
    num = 5
    random_values = random.get_distinct_random_ints_in_field(num, prime)
    assert len(random_values) == num and \
        len([value for value in random_values if value < prime]) == 5 and \
        len(random_values) == len(set(random_values))  # check distinct


def test_random_empty():
    prime = 71
    random_values = random.get_distinct_random_ints_in_field(0, prime)
    assert random_values == []


def test_random_distinct():
    prime = 11
    num = 7
    random_values = random.get_distinct_random_ints_in_field(num, prime)
    assert len(random_values) == num and \
        len([value for value in random_values if value < prime]) == num and \
        len(random_values) == len(set(random_values))  # check distinct


def test_random_size_of_field():
    prime = 31
    num = prime
    random_values = random.get_distinct_random_ints_in_field(num, prime)
    assert len(random_values) == num and \
        len([value for value in random_values if value < prime]) == num and \
        len(random_values) == len(set(random_values))  # check distinct


# error cases #
def test_random_too_many():
    prime = 7
    num = 10  # test the case where there are too many requested integers for the prime selected
    with pytest.raises(custom_exceptions.FatalConfigurationError):
        random.get_distinct_random_ints_in_field(num, prime)
