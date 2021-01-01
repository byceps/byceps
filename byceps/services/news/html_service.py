"""
byceps.services.news.html_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render HTML fragments from news items and images.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
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
    image = find(images, lambda image: image.number == number)

    if image is None:
        raise Exception(f'Unknown image number "{number}"')

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

    caption_elem = _render_image_caption(image, figcaption_attrs)

    html = f"""\
<figure{figure_attrs}>
  <img src="{image.url_path}"{img_attrs}>
  {caption_elem}
</figure>"""

    return Markup(html)


def _render_image_caption(image: Image, attrs: str) -> str:
    caption = image.caption or ''

    if image.attribution:
        if caption:
            caption += ' '
        caption += f'<small>Bild: {image.attribution}</small>'

    if not caption:
        return ''

    return f'<figcaption{attrs}>{caption}</figcaption>'
