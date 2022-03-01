"""
byceps.services.news.html_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render HTML fragments from news items and images.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from functools import partial
from typing import Any, Optional

from flask import current_app
from flask_babel import gettext
from markupsafe import Markup
import mistletoe

from ...util.iterables import find
from ...util.templating import load_template

from .transfer.models import BodyFormat, Image, Item


def render_body(item: Item, raw_body: str, body_format: BodyFormat) -> str:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    render_image = partial(_render_image_by_number, item.images)
    html = template.render(render_image=render_image)

    if body_format == BodyFormat.markdown:
        html = mistletoe.markdown(html)

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
    template_path = 'services/news/templates/_image.html'
    template_context = {
        'image': image,
        'width': width,
        'height': height,
        'image_credit_label': gettext('Image credit'),
    }
    return _render_template(template_path, template_context)


def _render_template(path: str, context: dict[str, Any]) -> str:
    """Load and render export template."""
    with current_app.open_resource(path, 'r') as f:
        source = f.read()

    template = load_template(source)
    return template.render(**context)
