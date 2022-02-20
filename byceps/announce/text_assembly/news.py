"""
byceps.announce.text_assembly.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask_babel import gettext

from ...events.news import NewsItemPublished

from ._helpers import with_locale


@with_locale
def assemble_text_for_news_item_published(event: NewsItemPublished) -> str:
    text = gettext(
        'The news "%(title)s" has been published.', title=event.title
    )

    if event.external_url is not None:
        text += f' {event.external_url}'

    return text
