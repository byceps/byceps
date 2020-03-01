"""
byceps.services.news.html_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render HTML fragments from news items and images.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from functools import partial
from typing import List, Optional

from jinja2 import Markup

from ...util.iterables import find
from ...util.templating import load_template

from .transfer.models import ChannelID, Image


def render_body(
    raw_body: str, channel_id: ChannelID, images: List[Image]
) -> str:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    render_image = partial(_render_image, channel_id, images)
    return template.render(render_image=render_image)


def _render_image(
    channel_id: ChannelID,
    images: List[Image],
    number: int,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """Render HTML for image."""
    image = find(lambda image: image.number == number, images)

    if image is None:
        raise Exception(f'Unknown image number "{number}"')

    img_src = image.url_path

    figure_attrs = ''
    img_attrs = ''
    figcaption_attrs = ''

    if image.alt_text:
        img_attrs += f' alt="{image.alt_text}"'

    if width:
        img_attrs += f' width="{width}"'
        figcaption_attrs += f' style="max-width: {width}px;"'
    if height:
        img_attrs += f' height="{height}"'

    caption = image.caption
    if caption is None:
        caption = ''

    if image.attribution:
        if caption:
            caption += ' '
        caption += f'<small>Bild: {image.attribution}</small>'

    caption_elem = (
        f'<figcaption{figcaption_attrs}>{caption}</figcaption>'
        if caption
        else ''
    )

    html = f"""\
<figure{figure_attrs}>
  <img src="{img_src}"{img_attrs}>
  {caption_elem}
</figure>"""

    return Markup(html)
