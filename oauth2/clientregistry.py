"""
    oauth2.clientregistry
    ~~~~~~~~~~~~~~~~~~~~~

    Convenient placeholder during developement. Will be replaced by an actual
    (database?) backend down the road.
"""
import collections.abc
from oauth2.rfc6749 import types


# A registry to loop over (O(N) lookups)
_registry = (
    types.Client(
        identifier=b'NOadtMwDSQKmw30l4l2xxQ.data.amsterdam',
        name='Atlas',
        secret=None,  # Atlas is an untrusted client
        owner_id='datapunt',
        redirect_uris=(
            'http://localhost',
        ),
    ),
)


class _Registry(collections.abc.Mapping):

    __len__ = _registry.__len__

    def __getitem__(self, key):
        """ Get client information from the client registry based on a client
        identifier.
        """
        result = tuple(c for c in _registry if c.identifier == key)
        if len(result) == 0:
            raise KeyError('Unknown client identifier')
        return result[0]

    def __iter__(self):
        for c in _registry:
            yield c.identifier


instance = _Registry()


def get():
    return instance
