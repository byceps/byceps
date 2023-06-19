"""
byceps.services.news.news_html_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render HTML fragments from news items and images.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from functools import partial
from typing import Any

from flask import current_app
from flask_babel import gettext
from markupsafe import Markup
import mistletoe

from byceps.util.iterables import find
from byceps.util.templating import load_template

from .models import BodyFormat, NewsImage, NewsItem, NewsItemHtml


def render_html(
    item: NewsItem, raw_body: str, body_format: BodyFormat
) -> NewsItemHtml:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    render_image = partial(_render_image_by_number, item.images)
    body_html = template.render(render_image=render_image)

    if body_format == BodyFormat.markdown:
        body_html = mistletoe.markdown(body_html)

    featured_image_html = None
    if item.featured_image_id:
        featured_image = find(
            item.images, lambda image: image.id == item.featured_image_id
        )

        if featured_image:
            featured_image_html = _render_image(featured_image)

    return NewsItemHtml(
        body=body_html,
        featured_image=featured_image_html,
    )


def _render_image_by_number(
    images: list[NewsImage],
    number: int,
    *,
    width: int | None = None,
    height: int | None = None,
) -> Markup:
    """Render HTML for image."""
    image = _get_image_by_number(images, number)
    html = _render_image(image, width=width, height=height)
    return Markup(html)


def _get_image_by_number(images: list[NewsImage], number: int) -> NewsImage:
    """Return the image with that number."""
    image = find(images, lambda image: image.number == number)

    if image is None:
        raise Exception(f'Unknown image number "{number}"')

    return image


def _render_image(
    image: NewsImage,
    *,
    width: int | None = None,
    height: int | None = None,
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
