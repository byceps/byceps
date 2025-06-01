"""
byceps.services.news.blueprints.admin.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime

from flask import abort, g, request
from flask_babel import format_datetime, gettext, to_utc

from byceps.services.brand import brand_service
from byceps.services.news import (
    news_channel_service,
    news_image_service,
    news_item_service,
    signals as news_signals,
)
from byceps.services.news.models import BodyFormat, NewsChannel
from byceps.services.site import site_service
from byceps.services.text_diff import text_diff_service
from byceps.services.user import user_service
from byceps.util.framework.blueprint import create_blueprint
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.image.image_type import get_image_type_names
from byceps.util.iterables import pairwise
from byceps.util.views import (
    permission_required,
    redirect_to,
    respond_no_content,
)

from .forms import (
    ChannelCreateForm,
    ChannelUpdateForm,
    ImageCreateForm,
    ImageUpdateForm,
    ItemCreateForm,
    ItemPublishLaterForm,
    ItemUpdateForm,
)


blueprint = create_blueprint('news_admin', __name__)


# -------------------------------------------------------------------- #
# channels


@blueprint.get('/brands/<brand_id>')
@permission_required('news_item.view')
@templated
def channel_index_for_brand(brand_id):
    """List channels for that brand."""
    brand = _get_brand_or_404(brand_id)

    channels = news_channel_service.get_channels_for_brand(brand.id)

    announcement_site_ids = {
        channel.announcement_site_id for channel in channels
    }
    announcement_sites_by_channel_id = {
        site.id: site for site in site_service.get_sites(announcement_site_ids)
    }

    item_count_by_channel_id = news_item_service.get_item_count_by_channel_id()

    return {
        'brand': brand,
        'channels': channels,
        'announcement_sites_by_channel_id': announcement_sites_by_channel_id,
        'item_count_by_channel_id': item_count_by_channel_id,
    }


@blueprint.get('/channels/<channel_id>', defaults={'page': 1})
@blueprint.get('/channels/<channel_id>/pages/<int:page>')
@permission_required('news_item.view')
@templated
def channel_view(channel_id, page):
    """View that channel and list its news items."""
    channel = _get_channel_or_404(channel_id)

    brand = brand_service.get_brand(channel.brand_id)
    if channel.announcement_site_id is not None:
        announcement_site = site_service.get_site(channel.announcement_site_id)
    else:
        announcement_site = None

    channel_ids = {channel.id}
    per_page = request.args.get('per_page', type=int, default=15)

    items = news_item_service.get_admin_list_items_paginated(
        channel_ids, page, per_page
    )

    return {
        'channel': channel,
        'brand': brand,
        'announcement_site': announcement_site,
        'items': items,
        'per_page': per_page,
    }


@blueprint.get('/for_brand/<brand_id>/channels/create')
@permission_required('news_channel.administrate')
@templated
def channel_create_form(brand_id, erroneous_form=None):
    """Show form to create a channel."""
    brand = _get_brand_or_404(brand_id)

    form = erroneous_form if erroneous_form else ChannelCreateForm()
    form.set_announcement_site_id_choices(brand.id)

    return {
        'brand': brand,
        'form': form,
    }


@blueprint.post('/for_brand/<brand_id>/channels')
@permission_required('news_channel.administrate')
def channel_create(brand_id):
    """Create a channel."""
    brand = _get_brand_or_404(brand_id)

    form = ChannelCreateForm(request.form)
    form.set_announcement_site_id_choices(brand.id)

    if not form.validate():
        return channel_create_form(brand.id, form)

    channel_id = form.channel_id.data.strip().lower()
    announcement_site_id = form.announcement_site_id.data or None

    channel = news_channel_service.create_channel(
        brand, channel_id, announcement_site_id=announcement_site_id
    )

    flash_success(
        gettext(
            'News channel "%(channel_id)s" has been created.',
            channel_id=channel.id,
        )
    )

    return redirect_to('.channel_view', channel_id=channel.id)


@blueprint.get('/channels/<channel_id>/update')
@permission_required('news_channel.administrate')
@templated
def channel_update_form(channel_id, erroneous_form=None):
    """Show form to update a channel."""
    channel = _get_channel_or_404(channel_id)

    brand = brand_service.get_brand(channel.brand_id)

    form = erroneous_form if erroneous_form else ChannelUpdateForm(obj=channel)
    form.set_announcement_site_id_choices(brand.id)

    return {
        'brand': brand,
        'channel': channel,
        'form': form,
    }


@blueprint.post('/channels/<channel_id>')
@permission_required('news_channel.administrate')
def channel_update(channel_id):
    """Update a channel."""
    channel = _get_channel_or_404(channel_id)

    brand = brand_service.get_brand(channel.brand_id)

    form = ChannelUpdateForm(request.form)
    form.set_announcement_site_id_choices(brand.id)

    if not form.validate():
        return channel_update_form(channel.id, form)

    announcement_site_id = form.announcement_site_id.data or None
    archived = form.archived.data

    channel = news_channel_service.update_channel(
        channel.id, announcement_site_id, archived
    )

    flash_success(gettext('Changes have been saved.'))

    return redirect_to('.channel_view', channel_id=channel.id)


@blueprint.delete('/channels/<channel_id>')
@permission_required('news_channel.administrate')
@respond_no_content
def channel_delete(channel_id):
    """Delete the channel."""
    channel = _get_channel_or_404(channel_id)

    if news_item_service.has_channel_items(channel.id):
        flash_error(
            gettext(
                'News channel "%(channel_id)s" cannot be deleted because it contains news items.',
                channel_id=channel.id,
            )
        )
        return

    sites_for_brand = site_service.get_sites_for_brand(channel.brand_id)
    linked_sites = {
        site for site in sites_for_brand if channel.id in site.news_channel_ids
    }
    if linked_sites:
        flash_error(
            gettext(
                'News channel "%(channel_id)s" cannot be deleted because it is referenced by %(site_count)s site(s).',
                channel_id=channel.id,
                site_count=len(linked_sites),
            )
        )
        return

    news_channel_service.delete_channel(channel.id)

    flash_success(
        gettext(
            'News channel "%(channel_id)s" has been deleted.',
            channel_id=channel_id,
        )
    )


# -------------------------------------------------------------------- #
# images


@blueprint.get('/for_item/<item_id>/create')
@permission_required('news_item.update')
@templated
def image_create_form(item_id, erroneous_form=None):
    """Show form to create a news image."""
    item = _get_item_or_404(item_id)

    form = erroneous_form if erroneous_form else ImageCreateForm()

    image_type_names = get_image_type_names(
        news_image_service.ALLOWED_IMAGE_TYPES
    )

    return {
        'item': item,
        'form': form,
        'allowed_types': image_type_names,
        'maximum_dimensions': news_image_service.MAXIMUM_DIMENSIONS,
    }


@blueprint.post('/for_item/<item_id>')
@permission_required('news_item.update')
def image_create(item_id):
    """Create a news image."""
    item = _get_item_or_404(item_id)

    # Make `InputRequired` work on `FileField`.
    form_fields = request.form.copy()
    if request.files:
        form_fields.update(request.files)

    form = ImageCreateForm(form_fields)
    if not form.validate():
        return image_create_form(item.id, form)

    creator = g.user
    image = request.files.get('image')
    alt_text = form.alt_text.data.strip()
    caption = form.caption.data.strip()
    attribution = form.attribution.data.strip()

    if not image or not image.filename:
        abort(400, 'No file to upload has been specified.')

    try:
        creation_result = news_image_service.create_image(
            creator,
            item,
            image.stream,
            alt_text=alt_text,
            caption=caption,
            attribution=attribution,
        )
        if creation_result.is_err():
            abort(400, creation_result.unwrap_err())

        image = creation_result.unwrap()
    except FileExistsError:
        abort(409, 'File already exists, not overwriting.')

    flash_success(
        gettext(
            'News image #%(image_number)s has been created.',
            image_number=image.number,
        )
    )

    return redirect_to('.item_view', item_id=image.item_id)


@blueprint.get('/images/<uuid:image_id>/update')
@permission_required('news_item.update')
@templated
def image_update_form(image_id, erroneous_form=None):
    """Show form to update a news image."""
    image = _get_image_or_404(image_id)
    item = news_item_service.find_item(image.item_id)

    form = erroneous_form if erroneous_form else ImageUpdateForm(obj=image)

    return {
        'image': image,
        'item': item,
        'form': form,
    }


@blueprint.post('/images/<uuid:image_id>')
@permission_required('news_item.update')
def image_update(image_id):
    """Update a news image."""
    image = _get_image_or_404(image_id)

    form = ImageUpdateForm(request.form)
    if not form.validate():
        return image_update_form(image.id, form)

    alt_text = form.alt_text.data.strip()
    caption = form.caption.data.strip()
    attribution = form.attribution.data.strip()

    image = news_image_service.update_image(
        image.id,
        alt_text=alt_text,
        caption=caption,
        attribution=attribution,
    )

    flash_success(
        gettext(
            'News image #%(image_number)s has been updated.',
            image_number=image.number,
        )
    )

    return redirect_to('.item_view', item_id=image.item_id)


@blueprint.post('/images/<uuid:image_id>/featured')
@permission_required('news_item.update')
@respond_no_content
def image_set_featured(image_id):
    """Set the image as featured image."""
    image = _get_image_or_404(image_id)

    news_item_service.set_featured_image(image.item_id, image.id)

    flash_success(gettext('Featured image has been set.'))


@blueprint.delete('/items/<uuid:item_id>/featured')
@permission_required('news_item.update')
@respond_no_content
def image_unset_featured(item_id):
    """Unset the item's featured image."""
    item = _get_item_or_404(item_id)

    news_item_service.unset_featured_image(item.id)

    flash_success(gettext('Featured image has been unset.'))


@blueprint.delete('/images/<uuid:image_id>')
@permission_required('news_item.update')
@respond_no_content
def image_delete(image_id):
    """Delete a news image."""
    image = _get_image_or_404(image_id)

    result = news_image_service.delete_image(image.id)

    flash_success(gettext('News image has been deleted.'))


# -------------------------------------------------------------------- #
# items


@blueprint.get('/items/<uuid:item_id>')
@permission_required('news_item.view')
def item_view(item_id):
    """Show the current version of the news item."""
    item = _get_item_or_404(item_id)

    version = news_item_service.get_current_item_version(item.id)

    return item_view_version(version.id)


@blueprint.get('/versions/<uuid:version_id>')
@permission_required('news_item.view')
@templated
def item_view_version(version_id):
    """Show the news item with the given version."""
    version = _find_version(version_id)

    item = news_item_service.find_item(version.item_id)

    channel = item.channel
    brand = brand_service.find_brand(channel.brand_id)

    creator = user_service.get_user(version.creator_id, include_avatar=True)

    current_version = news_item_service.get_current_item_version(item.id)
    is_current_version = version.id == current_version.id

    return {
        'item': item,
        'version': version,
        'brand': brand,
        'creator': creator,
        'is_current_version': is_current_version,
    }


@blueprint.get('/versions/<uuid:version_id>/preview')
@permission_required('news_item.view')
@templated
def item_view_version_preview(version_id):
    """Show a preview of the news item with the given version."""
    version = _find_version(version_id)

    item = news_item_service.find_item(version.item_id)

    item = dataclasses.replace(
        item,
        title=version.title,
        body=version.body,
        body_format=version.body_format,
    )

    rendered_item = news_item_service.render_html(item)

    return {
        'item': rendered_item,
    }


@blueprint.get('/items/<uuid:item_id>/versions')
@permission_required('news_item.view')
@templated
def item_list_versions(item_id):
    """List news item's versions."""
    item = _get_item_or_404(item_id)

    channel = item.channel
    brand = brand_service.find_brand(channel.brand_id)

    versions = news_item_service.get_item_versions(item.id)
    versions_pairwise = list(pairwise(versions + [None]))

    user_ids = {version.creator_id for version in versions}
    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    return {
        'item': item,
        'brand': brand,
        'versions_pairwise': versions_pairwise,
        'users_by_id': users_by_id,
    }


@blueprint.get('/items/<uuid:from_version_id>/compare_to/<uuid:to_version_id>')
@permission_required('news_item.view')
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

    html_diff_title = _create_html_diff(
        from_version, to_version, lambda version: version.title
    )
    html_diff_body = _create_html_diff(
        from_version, to_version, lambda version: version.body
    )
    html_diff_body_format = _create_html_diff(
        from_version, to_version, lambda version: version.body_format.name
    )

    return {
        'brand': brand,
        'diff_title': html_diff_title,
        'diff_body': html_diff_body,
        'diff_body_format': html_diff_body_format,
    }


@blueprint.get('/for_channel/<channel_id>/create')
@permission_required('news_item.create')
@templated
def item_create_form(channel_id, erroneous_form=None):
    """Show form to create a news item."""
    channel = _get_channel_or_404(channel_id)

    if erroneous_form:
        form = erroneous_form
    else:
        form = ItemCreateForm(
            channel.brand_id, body_format=BodyFormat.markdown.name
        )

    return {
        'channel': channel,
        'form': form,
    }


@blueprint.post('/for_channel/<channel_id>')
@permission_required('news_item.create')
def item_create(channel_id):
    """Create a news item."""
    channel = _get_channel_or_404(channel_id)

    form = ItemCreateForm(channel.brand_id, request.form)
    if not form.validate():
        return item_create_form(channel.id, form)

    slug = form.slug.data.strip().lower()
    creator = g.user
    title = form.title.data.strip()
    body = form.body.data.strip()
    body_format = form.body_format.data

    item = news_item_service.create_item(
        channel,
        slug,
        creator,
        title,
        body,
        body_format,
    )

    flash_success(
        gettext('News item "%(title)s" has been created.', title=item.title)
    )

    return redirect_to('.item_view', item_id=item.id)


@blueprint.get('/items/<uuid:item_id>/update')
@permission_required('news_item.update')
@templated
def item_update_form(item_id, erroneous_form=None):
    """Show form to update a news item."""
    item = _get_item_or_404(item_id)

    current_version = news_item_service.get_current_item_version(item.id)

    data = {
        'slug': item.slug,
        'title': current_version.title,
        'body_format': current_version.body_format.name,
        'body': current_version.body,
    }
    form = (
        erroneous_form
        if erroneous_form
        else ItemUpdateForm(item.brand_id, item.slug, data=data)
    )

    return {
        'item': item,
        'form': form,
    }


@blueprint.post('/items/<uuid:item_id>')
@permission_required('news_item.update')
def item_update(item_id):
    """Update a news item."""
    item = _get_item_or_404(item_id)

    form = ItemUpdateForm(item.brand_id, item.slug, request.form)
    if not form.validate():
        return item_update_form(item.id, form)

    creator = g.user
    slug = form.slug.data.strip().lower()
    title = form.title.data.strip()
    body = form.body.data.strip()
    body_format = form.body_format.data

    item = news_item_service.update_item(
        item.id,
        slug,
        creator,
        title,
        body,
        body_format,
    )

    flash_success(
        gettext('News item "%(title)s" has been updated.', title=item.title)
    )

    return redirect_to('.item_view', item_id=item.id)


@blueprint.get('/items/<uuid:item_id>/publish_later')
@permission_required('news_item.publish')
@templated
def item_publish_later_form(item_id, erroneous_form=None):
    """Show form to publish a news item at a time in the future."""
    item = _get_item_or_404(item_id)

    form = erroneous_form if erroneous_form else ItemPublishLaterForm()

    return {
        'item': item,
        'form': form,
    }


@blueprint.post('/items/<uuid:item_id>/publish_later')
@permission_required('news_item.publish')
def item_publish_later(item_id):
    """Publish a news item at a time in the future."""
    item = _get_item_or_404(item_id)

    form = ItemPublishLaterForm(request.form)
    if not form.validate():
        return item_publish_later_form(item.id, form)

    publish_at = to_utc(
        datetime.combine(form.publish_on.data, form.publish_at.data)
    )

    result = news_item_service.publish_item(
        item.id, publish_at=publish_at, initiator=g.user
    )

    if result.is_err():
        flash_error(result.unwrap_err())
        return redirect_to('.item_view', item_id=item.id)

    event = result.unwrap()

    news_signals.item_published.send(None, event=event)

    flash_success(
        gettext(
            'News item "%(title)s" will be published later.', title=item.title
        )
    )

    return redirect_to('.item_view', item_id=item.id)


@blueprint.post('/items/<uuid:item_id>/publish_now')
@permission_required('news_item.publish')
@respond_no_content
def item_publish_now(item_id):
    """Publish a news item now."""
    item = _get_item_or_404(item_id)

    result = news_item_service.publish_item(item.id, initiator=g.user)

    if result.is_err():
        flash_error(result.unwrap_err())
        return

    event = result.unwrap()

    news_signals.item_published.send(None, event=event)

    flash_success(
        gettext('News item "%(title)s" has been published.', title=item.title)
    )


@blueprint.post('/items/<uuid:item_id>/unpublish')
@permission_required('news_item.publish')
@respond_no_content
def item_unpublish(item_id):
    """Unpublish a news item."""
    item = _get_item_or_404(item_id)

    result = news_item_service.unpublish_item(item.id)

    if result.is_err():
        flash_error(result.unwrap_err())
        return

    flash_success(
        gettext('News item "%(title)s" has been unpublished.', title=item.title)
    )


# -------------------------------------------------------------------- #
# helpers


def _get_brand_or_404(brand_id):
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        abort(404)

    return brand


def _get_channel_or_404(channel_id) -> NewsChannel:
    channel = news_channel_service.find_channel(channel_id)

    if channel is None:
        abort(404)

    return channel


def _get_item_or_404(item_id):
    item = news_item_service.find_item(item_id)

    if item is None:
        abort(404)

    return item


def _get_image_or_404(image_id):
    image = news_image_service.find_image(image_id)

    if image is None:
        abort(404)

    return image


def _find_version(version_id):
    version = news_item_service.find_item_version(version_id)

    if version is None:
        abort(404)

    return version


def _create_html_diff(from_version, to_version, attribute_getter):
    """Create an HTML diff between the named attribute's value of each
    of the two versions.
    """
    from_description = format_datetime(from_version.created_at)
    to_description = format_datetime(to_version.created_at)

    from_text = attribute_getter(from_version)
    to_text = attribute_getter(to_version)

    return text_diff_service.create_html_diff(
        from_text, to_text, from_description, to_description
    )
