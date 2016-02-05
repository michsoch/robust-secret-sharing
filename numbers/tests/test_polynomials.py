import pytest
from custom_exceptions import exceptions
import numbers.polynomials


# test standard cases #

    # evaluate tests #

def test_evaluate_pos_point_pos_coef():
    polynomial = [9, 7, 4, 2]
    x = 5
    p = 71
    # 9 + 7 * 5 + 4 * 5^2 + 2 * 5^3 = 394
    assert numbers.polynomials.evaluate(polynomial, x, p) == 39


def test_evaluate_neg_point_pos_coef():
    polynomial = [9, 7, 4, 2]
    x = -6
    p = 71
    # 9 + 7 * (-6) + 4 * (-6)^2 + 2 * (-6)^3 = -321
    assert numbers.polynomials.evaluate(polynomial, x, p) == 34


def test_evaluate_pos_point_neg_coef():
    polynomial = [-2, 5, -3, 0, 7]
    x = 12
    p = 991
    # -2 + 5 * 12 + -3 * 12^2 + 0 + 7 * 12^4 = 144,778
    assert numbers.polynomials.evaluate(polynomial, x, p) == 92


def test_evaluate_neg_point_neg_coef():
    polynomial = [-2, 5, -3, 7, 0]
    x = -12
    p = 991
    # -2 + 5 * -12 + -3 * (-12)^2 + 7 * (-12)^3 + 0 = -12,590
    assert numbers.polynomials.evaluate(polynomial, x, p) == 293


def test_evaluate_pos_secret_below_p():
    polynomial = [15, -5, 33]
    x = 2
    p = 71
    # 15 + (-10) + 33 * 4 = 137
    assert numbers.polynomials.evaluate(polynomial, x, p) == 66


def test_evaluate_pos_secret_above_p():
    polynomial = [88, -5, 33]
    x = 2
    p = 71
    # 88 + (-10) + 33 * 4 = 137
    assert numbers.polynomials.evaluate(polynomial, x, p) == 68


def test_evaluate_pos_result_below_p():
    polynomial = [7, 88, -5, 33]
    x = 4
    p = 3643
    # 7 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = 2,391
    assert numbers.polynomials.evaluate(polynomial, x, p) == 2391


def test_evaluate_pos_result_above_p():
    polynomial = [7, 88, -5, 33]
    x = 4
    p = 1013
    # 7 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = 2,391
    assert numbers.polynomials.evaluate(polynomial, x, p) == 365


def test_evaluate_neg_secret_below_p():
    polynomial = [-7, 88, -5, 33]
    x = 4
    p = 71
    # -7 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = 2,377
    assert numbers.polynomials.evaluate(polynomial, x, p) == 34


def test_evaluate_neg_secret_above_p():
    polynomial = [-3643, 88, -5, 33]
    x = 4
    p = 1013
    # -3643 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = -1,259
    assert numbers.polynomials.evaluate(polynomial, x, p) == 767


def test_evaluate_neg_result_below_p():
    polynomial = [-3, 8, -5, -6]
    x = 10
    p = 11443
    # -3 + 8 * 10 +  -5 * 10^2 + -6 * 10^3 = -6,423
    assert numbers.polynomials.evaluate(polynomial, x, p) == 5020


def test_evaluate_neg_result_above_p():
    polynomial = [-36, 88, -5, -33]
    x = 10
    p = 1013
    # -36 + 88 * 10 +  -5 * 10^2 + -33 * 10^3 = -32,656
    assert numbers.polynomials.evaluate(polynomial, x, p) == 773


    # interpolate tests #

def test_interpolate_pos():
    pass


def test_interpolate_neg():
    pass


def test_interpolate_mix():
    pass


# test error cases #

    # evaluate tests #

def test_evaluate_empty_coef():
    polynomial = []
    x = 12
    p = 71
    with pytest.raises(exceptions.IllegalArgumentException):
        numbers.polynomials.evaluate(polynomial, x, p)


    # interpolate tests #

def test_error_interpolate():
    pass
