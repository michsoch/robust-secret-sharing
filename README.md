# robust-secret-sharing     [![Build Status](https://travis-ci.com/michsoch/robust-secret-sharing.svg?token=LLp1Puu6pzofB9JCSiAR&branch=master)](https://travis-ci.com/michsoch/robust-secret-sharing)

A python library implementing the Rabin Ben-Or Robust Secret Sharing (RSS) scheme: https://cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf

## Compatibility
This library is compatable with Python 2.7 and is cross-platform.

## Installation & Usage

#### Robust Secret Sharing
The outermost layer of this library can be found in rss.py. The methods exposed in this library allow for full robust secret sharing. 
That is, assuming a valid number of honest players, this library can be used to detect cheating players in a Shamir secret sharing scheme.
It therefore ensures that if valid number of players are honest, any secret recovered will be the original, correct secret. 
This property is not found in standalone Shamir secret sharing implementations, in which incorrect secrets can be induced by malicious players.

### Standard Secret Sharing
Since the robust layer of this library surrounds standard Shamir Secret Sharing, this library can be used without the protection or features offered by the robust layer.
When interacted with directly, the standard Shamir secret sharing segment of this library deals only with erasures and treats all shares provided to it as valid.

Example Usage (Distribute Shares):

```python
from crypto_tools import serialization

num_players = 5  # the total number of players (the number of shares to create)
reconstruction_threshold = 3  # the number of honest players required for recovery of the secret
secret = "mysupersecretswordfishstring"
prime = 2**521 - 1  # the prime provided must be larger than the secret and num_players

shares = share_secret(num_players, reconstruction_threshold, secret, prime)
serialized_shares = [serialization.pack_tuple[share] for share in shares]  # shares to distribute
```
Example Usage (Recover Shares):

```python
from crypto_tools import serialization

# recollect shares such that len(shares) >= reconstruction_threshold
deserialized_shares = [serialization.unpack_tuple[share] for share in shares]
prime = 2**521 - 1  # the same prime used for secret dispersal

secret = reconstruct_secret(deserialized_shares, prime)
```

## License

Sections of this library are derived from https://github.com/blockstack/secret-sharing with notable modications made to allow for robust sharing.
This library is licensed under the [MIT License](./LICENSE).
