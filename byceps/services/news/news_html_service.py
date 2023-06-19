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
from byceps.util.result import Err, Ok, Result
from byceps.util.templating import load_template

from .models import BodyFormat, NewsImage, NewsItem, NewsItemHtml


def render_html(
    item: NewsItem, raw_body: str, body_format: BodyFormat
) -> Result[NewsItemHtml, str]:
    """Render item's raw body and featured image to HTML."""
    body_html_result = render_body_html(item, raw_body, body_format)
    if body_html_result.is_err():
        return Err(body_html_result.unwrap_err())

    body_html = body_html_result.unwrap()

    featured_image = _find_featured_image(item)
    if featured_image:
        featured_image_html_result = render_featured_image_html(featured_image)
        if featured_image_html_result.is_err():
            return Err(featured_image_html_result.unwrap_err())

        featured_image_html = featured_image_html_result.unwrap()
    else:
        featured_image_html = None

    return Ok(
        NewsItemHtml(
            body=body_html,
            featured_image=featured_image_html,
        )
    )


def render_body_html(
    item: NewsItem, raw_body: str, body_format: BodyFormat
) -> Result[str, str]:
    """Render item's raw body to HTML."""
    template = load_template(raw_body)
    render_image = partial(_render_image_by_number, item.images)

    try:
        html = template.render(render_image=render_image)
        if body_format == BodyFormat.markdown:
            html = mistletoe.markdown(html)
        return Ok(html)
    except Exception as exc:
        return Err(str(exc))


def render_featured_image_html(image: NewsImage) -> Result[str, str]:
    """Render item's featured image to HTML."""
    try:
        return Ok(_render_image(image))
    except Exception as exc:
        return Err(str(exc))


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


def _find_featured_image(item: NewsItem) -> NewsImage | None:
    if not item.featured_image_id:
        return None

    return find(item.images, lambda image: image.id == item.featured_image_id)
