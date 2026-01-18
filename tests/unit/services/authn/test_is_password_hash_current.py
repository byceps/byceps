"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest
from secret_type import secret

from byceps.services.authn.password import authn_password_domain_service


@pytest.mark.parametrize(
    ('password_hash', 'expected'),
    [
        (
            # wrong method
            'pbkdf2:sha1:1000$JDbgv2Sk0yDVFCFM$ecfd05f5922d820d6ead9af3b3e70a501c1b4ae7',
            False,
        ),
        (
            # does not match parameters
            'scrypt:16384:8:1$lO4EJiUvVS0i0nYK$c3b4f9ec05be23145c18e6cb3dc5df4d95b70653eb009785f8a85011db9ea5046be611bdbccbcd6cd1c2c1dba3b6f8adca2b51117ad81ace5af6593c6405569e',
            False,
        ),
        (
            'scrypt:32768:8:1$lO4EJiUvVS0i0nYK$c3b4f9ec05be23145c18e6cb3dc5df4d95b70653eb009785f8a85011db9ea5046be611bdbccbcd6cd1c2c1dba3b6f8adca2b51117ad81ace5af6593c6405569e',
            True,
        ),
    ],
)
def test_is_password_hash_current(password_hash, expected):
    pw_hash = secret(password_hash)
    assert (
        authn_password_domain_service.is_password_hash_current(pw_hash)
        == expected
    )
