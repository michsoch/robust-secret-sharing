# Shamir Secret Sharing with an honest dealer

# Refer to the corresponding section in the Rabin Ben-Or paper:
    # https://cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf

# guarantee: "When the secret is revealed we want that
    # all knights will agree on the same value and
    # that it will be the original secret the dealer shared."

# parameters:
    # n: number of providers (n >= 2t + 1)
    # t: t players get no info, t + 1 can reconstruct
    # s: the secret
    # k is a security parameter
        # selected so that the probability of error is 2^(-k)
    # ps: a (potentially small) pubic prime used for defining polynomial coefficients
    # pv: a large, private prime used for check vectors

# sharing the secret (Phase 1) -
    # fix a small prime ps > n, and assume that s is in Z_ps (public)

    # fix n distinct points, alpha_1,...,alpha_n in Z_ps  (public)

    # choose at random t points, a_1,...,a_t in Z_ps (private)

    # use the a values to define the polynomial f(x) = (a_t x^t) + ... + (a_1 x) + s

    # for values of i from 1 to n, calculate f(alpha_i)

    # for each f(alpha_i) generate a check vector
        # generate a prime pv > 2^k and assume s is in Z_pv
        # generate random values in Z_pv for tuples (b_i1, y_i1), ... ,(b_in, y_in)
            # the b_i values are not equal to zero
        # compute c_ij = s_j + b_ij y_ij
        # (b_ij, c_ij) will be the check vector

    # disperse values to each player, Pi
        # f(alpha_i), the players share
        # y_i1, ..., y_in which the y_ij are the "tags" for Pi
        # (b1i, c_1i), ..., (bni, c_ni)
            # the (b_ji, c_ji) values are used by Pi to authenticate players Pj's tag

# recovering the secret (Phase 2) -
    # TODO: some thinking that needs to be done here
        # this algorithm assumes that all honest players should ultimately be able to agree on the secret
        # we only want the dealer in our case to determine the secret
        # it is easy to prevent players from calculating by doing the checks below ourselves
            # and not sending the data out
        # the only possible change will be to how the secret is ultimately decided on
            # currently thinking majority vote but will have to prove this works


    # retrieve values from all players

    # calculate all pairs (f(alpha_i), y_ij), i != j

    # verify with all (b_ji, c_ji) that c_ji = f(alpha_j) + b_ji y_ji
        # accept or reject accordingly

    # if pieces f(alpha_i1), ..., f(alpha_ir), r >= t + 1 are accepted for player Pi
    # then s can be calculated with these r shares
