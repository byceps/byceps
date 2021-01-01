"""
tests.api.helpers
~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from base64 import b64encode
from typing import Tuple


def assemble_authorization_header(api_token: str) -> Tuple[str, str]:
    """Assemble header to authorize against the API."""
    encoded_token = b64encode(api_token.encode('ascii')).decode('ascii')

    name = 'Authorization'
    value = 'Bearer ' + encoded_token

    return name, value
