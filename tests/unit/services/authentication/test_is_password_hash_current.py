"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.password import authn_password_service


@pytest.mark.parametrize(
    'password_hash, expected',
    [
        (
            # matches neither configured algorithm nor iteration count
            'pbkdf2:sha1:1000$JDbgv2Sk0yDVFCFM$ecfd05f5922d820d6ead9af3b3e70a501c1b4ae7',
            False,
        ),
        (
            # matches configured iteration count but not algorithm
            'pbkdf2:sha1:100000$h2Kec422sB2TqJ1Q$5abca818362323e085057f430ae36870e296fdaa',
            False,
        ),
        (
            # matches configured algorithm but not iteration count
            'pbkdf2:sha256:100000$9gf08FbwILpoROvt$99805a27d6e6447db4af26832ba94c54032b5a94ce83d1d290165210176a8454',
            False,
        ),
        (
            # matches configured algorithm and iteration count
            'pbkdf2:sha256:390000$rNGHJHbqxDsNHHJr$e0fd1fe49f3d3aeda97f36af78283d2de557efa270ab6cb281ad6ca9879d7c2c',
            True,
        ),
        (
            # higher number of iterations, but not the one configured
            'pbkdf2:sha256:500000$hGZgOpv58UJaX91I$6f2afba4a2a1637cc25d2143de9ec91ce0897a79d79ce59ce85792e275be5418',
            False,
        ),
    ],
)
def test_is_password_hash_current(password_hash, expected):
    assert (
        authn_password_service.is_password_hash_current(password_hash)
        == expected
    )
