"""
byceps.announce.text_assembly.page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce page events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.page import PageCreated, PageDeleted, PageUpdated

from ._helpers import get_screen_name_or_fallback, with_locale


@with_locale
def assemble_text_for_page_created(event: PageCreated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has created page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )


@with_locale
def assemble_text_for_page_updated(event: PageUpdated) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has updated page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )


@with_locale
def assemble_text_for_page_deleted(event: PageDeleted) -> str:
    initiator_screen_name = get_screen_name_or_fallback(
        event.initiator_screen_name
    )

    return gettext(
        '%(initiator_screen_name)s has deleted page "%(page_name)s" in site "%(site_id)s".',
        initiator_screen_name=initiator_screen_name,
        page_name=event.page_name,
        site_id=event.site_id,
    )
