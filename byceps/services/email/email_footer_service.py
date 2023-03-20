"""
byceps.services.email.email_footer_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...typing import BrandID

from ..snippet.models import SnippetScope
from ..snippet import snippet_service


def get_footer(brand_id: BrandID, language_code: str) -> str:
    """Return the email footer for that brand and language.

    Raise error if not found.
    """
    scope = SnippetScope.for_brand(brand_id)

    return snippet_service.get_snippet_body(
        scope, 'email_footer', language_code
    )
