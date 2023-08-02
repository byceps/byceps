"""
byceps.services.email.email_footer_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.brand.models import Brand
from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetScope
from byceps.services.user.models.user import User


SIGNATURE_SEPARATOR = '-- '


def create_footers(
    brand: Brand,
    creator: User,
    contact_address: str,
) -> None:
    """Create email footer snippets for that brand in the supported
    languages.
    """
    scope = SnippetScope.for_brand(brand.id)

    language_codes_and_bodies = [
        (
            'en',
            f'''
We are happy to answer your questions.

Have a nice day,
the team of {brand.title}

{SIGNATURE_SEPARATOR}
{brand.title}

Email: {contact_address}
        '''.strip(),
        ),
        (
            'de',
            f'''
Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der {brand.title}

{SIGNATURE_SEPARATOR}
{brand.title}

E-Mail: {contact_address}
        '''.strip(),
        ),
    ]

    for language_code, body in language_codes_and_bodies:
        snippet_service.create_snippet(
            scope, 'email_footer', language_code, creator.id, body
        )


def get_footer(brand: Brand, language_code: str) -> str:
    """Return the email footer for that brand and language.

    Raise error if not found.
    """
    scope = SnippetScope.for_brand(brand.id)

    return snippet_service.get_snippet_body(
        scope, 'email_footer', language_code
    )
