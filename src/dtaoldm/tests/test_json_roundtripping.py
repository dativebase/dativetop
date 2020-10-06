"""Tests for converting AOLs to and from JSON

In the context of the DativeTop Server, a GET request to the root path / should
return a JSON string that encodes an array of length-3 arrays (encoding
"appendables")::

    GET /
    [[[E, A, V, T], HASH, INTEG_HASH]
     [[E, A, V, T], HASH, INTEG_HASH]
     [[E, A, V, T], HASH, INTEG_HASH]
     ...
    ]

"""

import dtaoldm.aol as aol_mod
import tests.utils as utils


def test_aol_json_roundtripping():
    """Test that we can serialize an AOL to JSON and correctly deserialize it
    back again to an AOL.
    """
    aol = utils.generate_large_test_aol(100)
    serialized_aol = aol_mod.aol_to_json(aol)
    deserialized_aol = aol_mod.json_to_aol(serialized_aol)
    assert deserialized_aol == aol
