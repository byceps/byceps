"""
byceps.announce.text_assembly.auth
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce auth events.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.auth import UserLoggedIn
from ...services.site import service as site_service

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_user_logged_in(event: UserLoggedIn) -> str:
    screen_name = get_screen_name_or_fallback(event.initiator_screen_name)

    site = None
    if event.site_id:
        site = site_service.find_site(event.site_id)

    if site:
        return gettext(
            '%(screen_name)s has logged in on site "%(site_title)s".',
            screen_name=screen_name,
            site_title=site.title,
        )
    else:
        return gettext(
            '%(screen_name)s has logged in.', screen_name=screen_name
        )
