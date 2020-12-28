"""
byceps.announce.common.news
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce news events.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.news import NewsItemPublished


def assemble_text_for_news_item_published(event: NewsItemPublished) -> str:
    return (
        f'Die News "{event.title}" wurde veröffentlicht. {event.external_url}'
    )
