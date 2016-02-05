import pytest
from custom_exceptions import exceptions
import numbers.polynomials


# test standard cases #

    # evaluate tests #
# TODO: continue to assume integer coeffs?

def test_evaluate_pos_point_pos_coef():
    polynomial = [9, 7, 4, 2]
    x = [5, 11]
    p = 71
    # 9 + 7 * 5 + 4 * 5^2 + 2 * 5^3 = 394
    # 9 + 7 * 11 + 4 * 11^2 + 2 * 11^3 = 3,232
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(5, 39), (11, 37)]


def test_evaluate_neg_point_pos_coef():
    polynomial = [9, 7, 4, 2]
    x = [-6, -7, -2]
    p = 71
    # 9 + 7 * (-6) + 4 * (-6)^2 + 2 * (-6)^3 = -321
    # 9 + 7 * (-7) + 4 * (-7)^2 + 2 * (-7)^3 = -530
    # 9 + 7 * (-2) + 4 * (-2)^2 + 2 * (-2)^3 = -5
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(-6, 34), (-7, 38), (-2, 66)]


def test_evaluate_pos_point_neg_coef():
    polynomial = [-2, 5, -3, 0, 7]
    x = [12, 5, 11]
    p = 991
    # -2 + 5 * 12 + -3 * 12^2 + 0 + 7 * 12^4 = 144,778
    # -2 + 5 * 5 + -3 * 5^2 + 0 + 7 * 5^4 = 4,323
    # -2 + 5 * 11 + -3 * 11^2 + 0 + 7 * 11^4 = 102,177
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(12, 92), (5, 359), (11, 104)]


def test_evaluate_neg_point_neg_coef():
    polynomial = [-2, 5, -3, 7, 0]
    x = [-12, -5, -11]
    p = 991
    # -2 + 5 * -12 + -3 * (-12)^2 + 7 * (-12)^3 + 0 = -12,590
    # -2 + 5 * -5 + -3 * (-5)^2 + 7 * (-5)^3 + 0 = -977
    # -2 + 5 * -11 + -3 * (-11)^2 + 7 * (-11)^3 + 0 = -9,737
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(-12, 293), (-5, 14), (-11, 173)]


def test_evaluate_pos_secret_below_p():
    polynomial = [15, -5, 33]
    x = [2, 5, 8]
    p = 71
    # 15 + (-10) + 33 * 4 = 137
    # 15 + (-25) + 33 * 25 = 815
    # 15 + (-40) + 33 * 8^2 = 2,087
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(2, 66), (5, 34), (8, 28)]


def test_evaluate_pos_secret_above_p():
    polynomial = [88, -5, 33]
    x = [5, 8]
    p = 71
    # 88 - 5 * 5 + 33 * 5^2 = 888
    # 88 - 5 * 8 + 33 * 8^2 = 2,160
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(5, 36), (8, 30)]


def test_evaluate_pos_result_below_p():
    polynomial = [7, 88, -5, 33]
    x = [4, 3]
    p = 3643
    # 7 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = 2,391
    # 7 + 88 * 3 +  -5 * 3^2 + 33 * 3^3 = 1,117
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(4, 2391), (3, 1117)]


def test_evaluate_pos_result_above_p():
    polynomial = [7, 88, -5, 33]
    x = [4, 5]
    p = 1013
    # 7 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = 2,391
    # 7 + 88 * 5 +  -5 * 5^2 + 33 * 5^3 = 4,447
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(4, 365), (5, 395)]


def test_evaluate_neg_secret_below_p():
    polynomial = [-7, 88, -5, 33]
    x = [4, -3, 7]
    p = 71
    # -7 + 88 * 4 + -5 * 4^2 + 33 * 4^3 = 2,377
    # -7 + 88 * (-3) + -5 * (-3)^2 + 33 * (-3)^3 = -1,207
    # -7 + 88 * 7 + -5 * 7^2 + 33 * 7^3 = 11,683
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(4, 34), (-3, 0), (7, 39)]


def test_evaluate_neg_secret_above_p():
    polynomial = [-3643, 88, -5, 33]
    x = [4, -3, 7]
    p = 1013
    # -3643 + 88 * 4 +  -5 * 4^2 + 33 * 4^3 = -1,259
    # -3643 + 88 * (-3) + -5 * (-3)^2 + 33 * (-3)^3 = -4,843
    # -3643 + 88 * 7 + -5 * 7^2 + 33 * 7^3 = 8,047
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(4, 767), (-3, 222), (7, 956)]


def test_evaluate_neg_result_below_p():
    polynomial = [-3, 8, -5, -6]
    x = [10, -7, 3]
    p = 11443
    # -3 + 8 * 10 +  -5 * 10^2 + -6 * 10^3 = -6,423
    # -3 + 8 * (-7) +  -5 * (-7)^2 + -6 * (-7)^3 = 1,754
    # -3 + 8 * 3 +  -5 * 3^2 + -6 * 3^3 = -186
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(10, 5020), (-7, 1754), (3, 11257)]


def test_evaluate_neg_result_above_p():
    polynomial = [-36, 88, -5, -33]
    x = [10, 11]
    p = 1013
    # -36 + 88 * 10 +  -5 * 10^2 + -33 * 10^3 = -32,656
    # -36 + 88 * 11 +  -5 * 11^2 + -33 * 11^3 = -43,596
    assert numbers.polynomials.evaluate(polynomial, x, p) == [(10, 773), (11, 976)]


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
    x = [12]
    p = 71
    with pytest.raises(exceptions.IllegalArgumentException):
        numbers.polynomials.evaluate(polynomial, x, p)


    # interpolate tests #

def test_error_interpolate():
    pass
