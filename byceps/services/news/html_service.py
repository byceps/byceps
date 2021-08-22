"""
byceps.services.news.html_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render HTML fragments from news items and images.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from functools import partial
from typing import Optional

from flask_babel import gettext
from markupsafe import Markup

from ...util.iterables import find
from ...util.templating import load_template

from .transfer.models import Image, Item


def render_body(item: Item, raw_body: str) -> str:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    render_image = partial(_render_image_by_number, item.images)
    html = template.render(render_image=render_image)

    if item.featured_image_id:
        featured_image = find(
            item.images, lambda image: image.id == item.featured_image_id
        )

        if featured_image:
            featured_image_html = _render_image(featured_image)
            html = featured_image_html + '\n\n' + html

    return html


def _render_image_by_number(
    images: list[Image],
    number: int,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Markup:
    """Render HTML for image."""
    image = _get_image_by_number(images, number)
    html = _render_image(image, width=width, height=height)
    return Markup(html)


def _get_image_by_number(images: list[Image], number: int) -> Image:
    """Return the image with that number."""
    image = find(images, lambda image: image.number == number)

    if image is None:
        raise Exception(f'Unknown image number "{number}"')

    return image


def _render_image(
    image: Image,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """Render HTML for image."""
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

    return f"""\
<figure{figure_attrs}>
  <img src="{image.url_path}"{img_attrs}>
  {caption_elem}
</figure>"""


def _render_image_caption(image: Image, attrs: str) -> str:
    """Render HTML for image caption."""
    caption = image.caption or ''

    if image.attribution:
        if caption:
            caption += ' '
        credit_label = gettext('Image credit')
        caption += f'<small>{credit_label}: {image.attribution}</small>'

    if not caption:
        return ''

    return f'<figcaption{attrs}>{caption}</figcaption>'
