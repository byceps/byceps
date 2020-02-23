"""
byceps.blueprints.admin.news.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import date

from flask import abort, g, request

from ....services.brand import service as brand_service
from ....services.news import channel_service as news_channel_service
from ....services.news import image_service as news_image_service
from ....services.news import service as news_item_service
from ....services.news.transfer.models import Channel
from ....services.text_diff import service as text_diff_service
from ....util.datetime.format import format_datetime_short
from ....util.framework.blueprint import create_blueprint
from ....util.framework.flash import flash_success
from ....util.framework.templating import templated
from ....util.iterables import pairwise
from ....util.views import redirect_to, respond_no_content

from ...authorization.decorators import permission_required
from ...authorization.registry import permission_registry
from ...news import signals

from .authorization import NewsChannelPermission, NewsItemPermission
from .forms import (
    ChannelCreateForm,
    ImageCreateForm,
    ItemCreateForm,
    ItemUpdateForm,
)


blueprint = create_blueprint('news_admin', __name__)


permission_registry.register_enum(NewsChannelPermission)
permission_registry.register_enum(NewsItemPermission)


# -------------------------------------------------------------------- #
# channels


@blueprint.route('/brands/<brand_id>')
@permission_required(NewsItemPermission.view)
@templated
def channel_index_for_brand(brand_id):
    """List channels for that brand."""
    brand = _get_brand_or_404(brand_id)

    channels = news_channel_service.get_channels_for_brand(brand.id)

    item_count_by_channel_id = news_item_service.get_item_count_by_channel_id()

    return {
        'brand': brand,
        'channels': channels,
        'item_count_by_channel_id': item_count_by_channel_id,
    }


@blueprint.route('/for_brand/<brand_id>/channels/create')
@permission_required(NewsChannelPermission.create)
@templated
def channel_create_form(brand_id, erroneous_form=None):
    """Show form to create a channel."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else ChannelCreateForm()

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.route('/for_brand/<brand_id>/channels', methods=['POST'])
@permission_required(NewsChannelPermission.create)
def channel_create(brand_id):
    """Create a channel."""
    brand = _get_brand_or_404(brand_id)

    form = ChannelCreateForm(request.form)
    if not form.validate():
        return channel_create_form(brand.id, form)

    channel_id = form.channel_id.data.strip().lower()
    url_prefix = form.url_prefix.data.strip()

    channel = news_channel_service.create_channel(
        brand.id, channel_id, url_prefix
    )

    flash_success(f'Der News-Kanal mit der ID "{channel.id}" wurde angelegt.')
    return redirect_to('.channel_view', channel_id=channel.id)


@blueprint.route('/channels/<channel_id>', defaults={'page': 1})
@blueprint.route('/channels/<channel_id>/pages/<int:page>')
@permission_required(NewsItemPermission.view)
@templated
def channel_view(channel_id, page):
    """View that channel and list its news items."""
    channel = _get_channel_or_404(channel_id)

    brand = brand_service.find_brand(channel.brand_id)

    per_page = request.args.get('per_page', type=int, default=15)

    items = news_item_service.get_items_paginated(channel.id, page, per_page)

    return {
        'channel': channel,
        'brand': brand,
        'items': items,
    }


# -------------------------------------------------------------------- #
# images


@blueprint.route('/for_item/<item_id>/create')
@permission_required(NewsItemPermission.update)
@templated
def image_create_form(item_id, erroneous_form=None):
    """Show form to create a news image."""
    item = _get_item_or_404(item_id)

    form = erroneous_form if erroneous_form else ImageCreateForm()

    return {
        'item': item,
        'form': form,
    }


@blueprint.route('/for_item/<item_id>', methods=['POST'])
@permission_required(NewsItemPermission.update)
def image_create(item_id):
    """Create a news image."""
    item = _get_item_or_404(item_id)

    form = ImageCreateForm(request.form)
    if not form.validate():
        return image_create_form(item.id, form)

    creator_id = g.current_user.id
    filename = form.filename.data.strip()
    alt_text = form.alt_text.data.strip()
    caption = form.caption.data.strip()
    attribution = form.attribution.data.strip()

    image = news_image_service.create_image(
        creator_id,
        item.id,
        filename,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    flash_success(f'Das Newsbild "{image.filename}" wurde hinzugefügt.')

    return redirect_to('.item_view', item_id=image.item_id)


# -------------------------------------------------------------------- #
# items


@blueprint.route('/items/<uuid:item_id>')
@permission_required(NewsItemPermission.view)
@templated('admin/news/item_view_version')
def item_view(item_id):
    """Show the current version of the news item."""
    item = _get_item_or_404(item_id)

    version = news_item_service.get_current_item_version(item.id)

    return _render_item_version(version)


@blueprint.route('/versions/<uuid:version_id>')
@permission_required(NewsItemPermission.view)
@templated
def item_view_version(version_id):
    """Show the news item with the given version."""
    version = _find_version(version_id)

    return _render_item_version(version)


def _render_item_version(version):
    """Render the news item version."""
    brand_id = version.item.channel.brand_id
    brand = brand_service.find_brand(brand_id)

    context = {
        'version': version,
        'brand': brand,
    }

    try:
        rendered_body = news_item_service.render_body(version.body)

        context.update({
            'rendered_body': rendered_body,
            'error_occurred': False,
        })
    except Exception as e:
        context.update({
            'error_occurred': True,
            'error_message': str(e),
        })

    return context


@blueprint.route('/items/<uuid:item_id>/versions')
@permission_required(NewsItemPermission.view)
@templated
def item_list_versions(item_id):
    """List news item's versions."""
    item = _get_item_or_404(item_id)

    channel = item.channel
    brand = brand_service.find_brand(channel.brand_id)

    versions = news_item_service.get_item_versions(item.id)
    versions_pairwise = list(pairwise(versions + [None]))

    return {
        'item': item,
        'brand': brand,
        'versions_pairwise': versions_pairwise,
    }


@blueprint.route(
    '/items/<uuid:from_version_id>/compare_to/<uuid:to_version_id>'
)
@permission_required(NewsItemPermission.view)
@templated
def item_compare_versions(from_version_id, to_version_id):
    """Show the difference between two news item versions."""
    from_version = _find_version(from_version_id)
    to_version = _find_version(to_version_id)

    if from_version.item_id != to_version.item_id:
        abort(400, 'The versions do not belong to the same item.')

    item = news_item_service.find_item(from_version.item_id)
    channel = item.channel
    brand = brand_service.find_brand(channel.brand_id)

    html_diff_title = _create_html_diff(from_version, to_version, 'title')
    html_diff_body = _create_html_diff(from_version, to_version, 'body')
    html_diff_image_url_path = _create_html_diff(
        from_version, to_version, 'image_url_path'
    )

    return {
        'brand': brand,
        'diff_title': html_diff_title,
        'diff_body': html_diff_body,
        'diff_image_url_path': html_diff_image_url_path,
    }


@blueprint.route('/for_channel/<channel_id>/create')
@permission_required(NewsItemPermission.create)
@templated
def item_create_form(channel_id, erroneous_form=None):
    """Show form to create a news item."""
    channel = _get_channel_or_404(channel_id)

    if erroneous_form:
        form = erroneous_form
    else:
        slug_prefix = date.today().strftime('%Y-%m-%d-')
        form = ItemCreateForm(slug=slug_prefix)

    return {
        'channel': channel,
        'form': form,
    }


@blueprint.route('/for_channel/<channel_id>', methods=['POST'])
@permission_required(NewsItemPermission.create)
def item_create(channel_id):
    """Create a news item."""
    channel = _get_channel_or_404(channel_id)

    form = ItemCreateForm(request.form)
    if not form.validate():
        return item_create_form(channel.id, form)

    slug = form.slug.data.strip().lower()
    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    item = news_item_service.create_item(
        channel.id, slug, creator.id, title, body, image_url_path=image_url_path
    )

    flash_success(f'Die News "{item.title}" wurde angelegt.')

    return redirect_to('.channel_view', channel_id=channel.id)


@blueprint.route('/items/<uuid:item_id>/update')
@permission_required(NewsItemPermission.update)
@templated
def item_update_form(item_id, erroneous_form=None):
    """Show form to update a news item."""
    item = _get_item_or_404(item_id)

    current_version = news_item_service.get_current_item_version(item.id)

    form = erroneous_form if erroneous_form \
            else ItemUpdateForm(obj=current_version, slug=item.slug)

    return {
        'item': item,
        'form': form,
    }


@blueprint.route('/items/<uuid:item_id>', methods=['POST'])
@permission_required(NewsItemPermission.update)
def item_update(item_id):
    """Update a news item."""
    item = _get_item_or_404(item_id)

    form = ItemUpdateForm(request.form)
    if not form.validate():
        return item_update_form(item.id, form)

    creator = g.current_user
    slug = form.slug.data.strip().lower()
    title = form.title.data.strip()
    body = form.body.data.strip()
    image_url_path = form.image_url_path.data.strip()

    news_item_service.update_item(
        item.id, slug, creator.id, title, body, image_url_path=image_url_path
    )

    flash_success(f'Die News "{item.title}" wurde aktualisiert.')
    return redirect_to('.channel_view', channel_id=item.channel.id)


@blueprint.route('/items/<uuid:item_id>/publish', methods=['POST'])
@permission_required(NewsItemPermission.publish)
@respond_no_content
def item_publish(item_id):
    """Publish a news item."""
    item = _get_item_or_404(item_id)

    event = news_item_service.publish_item(item.id)

    signals.item_published.send(None, event=event)

    flash_success(f'Die News "{item.title}" wurde veröffentlicht.')


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_channel_or_404(channel_id) -> Channel:
    channel = news_channel_service.find_channel(channel_id)

    if channel is None:
        abort(404)

    return channel


def _get_item_or_404(item_id):
    item = news_item_service.find_item(item_id)

    if item is None:
        abort(404)

    return item


def _find_version(version_id):
    version = news_item_service.find_item_version(version_id)

    if version is None:
        abort(404)

    return version


def _create_html_diff(from_version, to_version, attribute_name):
    """Create an HTML diff between the named attribute's value of each
    of the two versions.
    """
    from_description = format_datetime_short(from_version.created_at)
    to_description = format_datetime_short(to_version.created_at)

    from_text = getattr(from_version, attribute_name)
    to_text = getattr(to_version, attribute_name)

    return text_diff_service.create_html_diff(
        from_text, to_text, from_description, to_description
    )
