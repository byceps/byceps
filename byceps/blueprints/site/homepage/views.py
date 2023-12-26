"""
byceps.blueprints.site.homepage.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import g

from byceps.services.news import news_item_service
from byceps.services.news.models import NewsTeaser
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.templating import templated


blueprint = create_blueprint('homepage', __name__)


@blueprint.get('')
@templated
def index():
    """Show homepage."""
    news_teasers = _get_news_teasers()

    return {
        'news_teasers': news_teasers,
    }


def _get_news_teasers() -> list[NewsTeaser] | None:
    """Return the most recent news teasers.

    Returns `None` if no news channels are configured for this site.
    """
    channel_ids = g.site.news_channel_ids
    if not channel_ids:
        return None

    return news_item_service.get_recent_teasers(channel_ids, limit=3)
