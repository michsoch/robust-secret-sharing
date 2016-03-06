import decimal


def _set_precision(precision):
    '''
    Args:
        precision, the digit-length precision to be used in Decimal computations
    Returns:
        None
    '''
    decimal.getcontext().prec = precision


def _sqrt_floor(dec_val):
    '''
    Args:
        dec_val, a Decimal value
    Returns:
        the Decimal value of floor(sqrt(dec_val)) with precision determined by _set_precision
    '''
    return dec_val.sqrt().to_integral_value(rounding=decimal.ROUND_FLOOR)


def _validate_pair(x, y):
    return x >= 0 and y >= 0


def elegant_pair(x, y):
    '''
    Combine two nonnegative integers to create a new, unique nonnegative integer using the Szudzik pairing function
    Args:
        x, y: two nonnegative integers
    Returns:
        z: a nonnegative integer uniquely associated with the pair (x, y)
        such that the pair can be recovered by elegant_unpair and
        the size of z will be no greater than the 2 * max(x, y)
    '''
    if not _validate_pair(x, y):
        raise ValueError("pairing integers must be nonnegative")

    if x < y:
        return y**2 + x
    else:
        return x**2 + x + y


def elegant_unpair(z):
    '''
    Recover the two nonnegative integers passed to elegant_pair
    Args:
        z, the output of elegant_pair
    Returns:
        pair: a tuple holding the nonnegative integers x and y that are uniquely associated with z
        these were the integers passed to elegant_pair
    '''
    _set_precision(len(str(z)))

    z = decimal.Decimal(z)
    intermediate = _sqrt_floor(z)
    cutoff = z - intermediate**2

    if cutoff < intermediate:
        return long(cutoff), long(intermediate)
    else:
        return long(intermediate), long(cutoff - intermediate)
