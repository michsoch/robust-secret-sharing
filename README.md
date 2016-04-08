# robust-secret-sharing
A python library implementing the Rabin Ben-Or Robust Secret Sharing (RSS) scheme: https://cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf

## Compatibility
This library is compatable with Python 2.7 and is cross-platform.

## Installation & Usage

#### Robust Secret Sharing
The outermost layer of this library can be found in rss.py. The methods exposed in this library allow for full robust secret sharing. 
That is, assuming the number of honest players reaches the threshold and the number of dishonest players is strictly less than that, this library guarantees that the secret that is reconstructed will be the one that was originally shared. This property is not found in standalone Shamir secret sharing implementations, in which incorrect secrets can be induced by malicious players.

In order to achieve verificaiton, additional metadata is used that surrounds shares that are used in this scheme. Additionally, the authenticated sharing and reconstruction algorithms are less asympotically efficient than standard sharing. The rss module therefore offers one sharing function and two reconstruction functions (see below). 

In order to use the authentication capabilities of the library, share and reconstruct as follows:

```python
from robustsecretsharing import rss

num_players = 5  # the total number of players (the number of shares to create)
players = [id for id in range(num_players)]  # unique ids for each player
reconstruction_threshold = 3  # the number of honest players required for recovery of the secret
secret = "mysupersecretswordfishstring"
max_secret_length = len(secret)

serialized_map = rss.share_authenticated_secret(players, reconstruction_threshold, max_secret_length, secret)
reconstructed_secret = rss.reconstruct_authenticated_secret(num_players, reconstruction_threshold, max_secret_length, serialized_map)
```

In order to call standard reconstruction without authentication or guarentees on the secret, it is possible to pass shares with metadata from serialized_map to 

```python
rss.reconstruct_unauthenticated_secret(num_players, max_secret_length, serialized_map)
```

### Standard Secret Sharing
Since the robust layer of this library surrounds standard Shamir Secret Sharing, this library can be used without the protection or features offered by the robust layer.

When interacted with directly, the standard Shamir secret sharing segment of this library deals only with erasures and treats all shares provided to it as valid.

Example Usage (Distribute Shares):

```python
from robustsecretsharing.schemes import sss

num_players = 5  # the total number of players (the number of shares to create)
reconstruction_threshold = 3  # the number of honest players required for recovery of the secret
secret = "mysupersecretswordfishstring"
max_secret_length = len(secret)

shares = sss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)  # shares to distribute
```
Example Usage (Recover Shares):

```python

# recollect shares such that len(shares) >= reconstruction_threshold
# pass in the same values for num_players and max_secret_length as used for sharing

secret = sss.reconstruct_secret(num_players, max_secret_length, shares)
```

## License

Sections of this library are derived from https://github.com/blockstack/secret-sharing with notable modications made to allow for robust sharing.
This library is licensed under the [MIT License](./LICENSE).
