"""
byceps.blueprints.board.views_posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import dataclasses

from flask import g, redirect, request

from ...services.board import (
    last_view_service as board_last_view_service,
    posting_command_service as board_posting_command_service,
    posting_query_service as board_posting_query_service,
)
from ...services.text_markup.service import get_smileys
from ...services.user import service as user_service
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import respond_no_content_with_location

from ..authorization.decorators import permission_required

from .authorization import BoardPermission, BoardPostingPermission
from .blueprint import blueprint
from .forms import PostingCreateForm, PostingUpdateForm
from . import _helpers as h, service, signals


@blueprint.route('/postings/<uuid:posting_id>')
def posting_view(posting_id):
    """Show the page of the posting's topic that contains the posting,
    as seen by the current user.
    """
    posting = h.get_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(posting, g.current_user)

    return redirect(
        h.build_url_for_posting_in_topic_view(posting, page, _external=True)
    )


@blueprint.route('/topics/<uuid:topic_id>/create')
@permission_required(BoardPostingPermission.create)
@templated
def posting_create_form(topic_id, erroneous_form=None):
    """Show a form to create a posting to the topic."""
    topic = h.get_topic_or_404(topic_id)

    form = erroneous_form if erroneous_form else PostingCreateForm()

    quoted_posting_bbcode = quote_posting_as_bbcode()
    if quoted_posting_bbcode:
        form.body.data = quoted_posting_bbcode

    return {
        'topic': topic,
        'form': form,
        'smileys': get_smileys(),
    }


def quote_posting_as_bbcode():
    posting_id = request.args.get('quote', type=str)
    if not posting_id:
        return

    posting = board_posting_query_service.find_posting_by_id(posting_id)
    if posting is None:
        flash_error('Der zu zitierende Beitrag wurde nicht gefunden.')
        return

    creator = user_service.find_user(posting.creator_id)

    return f'[quote author="{creator.screen_name}"]{posting.body}[/quote]'


@blueprint.route('/topics/<uuid:topic_id>/create', methods=['POST'])
@permission_required(BoardPostingPermission.create)
def posting_create(topic_id):
    """Create a posting to the topic."""
    topic = h.get_topic_or_404(topic_id)

    form = PostingCreateForm(request.form)
    if not form.validate():
        return posting_create_form(topic_id, form)

    creator = g.current_user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock',
        )
        return redirect(h.build_url_for_topic(topic.id))

    if topic.posting_limited_to_moderators \
            and not g.current_user.has_permission(BoardPermission.announce):
        flash_error(
            'In diesem Thema dürfen nur Moderatoren Beiträge hinzufügen.',
            icon='announce',
        )
        return redirect(h.build_url_for_topic(topic.id))

    posting, event = board_posting_command_service.create_posting(
        topic, creator.id, body
    )

    if not g.current_user.is_anonymous:
        board_last_view_service.mark_category_as_just_viewed(
            topic.category.id, g.current_user.id
        )

    flash_success('Deine Antwort wurde hinzugefügt.')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    signals.posting_created.send(None, event=event)

    postings_per_page = service.get_postings_per_page_value()
    page_count = topic.count_pages(postings_per_page)

    return redirect(h.build_url_for_posting_in_topic_view(posting, page_count))


@blueprint.route('/postings/<uuid:posting_id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(posting_id, erroneous_form=None):
    """Show form to update a posting."""
    posting = h.get_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(posting, g.current_user)
    url = h.build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.current_user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.'
        )
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    if not user_may_update:
        flash_error('Du darfst diesen Beitrag nicht bearbeiten.')
        return redirect(url)

    form = erroneous_form if erroneous_form else PostingUpdateForm(obj=posting)

    return {
        'form': form,
        'posting': posting,
        'smileys': get_smileys(),
    }


@blueprint.route('/postings/<uuid:posting_id>', methods=['POST'])
@permission_required(BoardPostingPermission.update)
def posting_update(posting_id):
    """Update a posting."""
    posting = h.get_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(posting, g.current_user)
    url = h.build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.current_user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.'
        )
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    if not user_may_update:
        flash_error('Du darfst diesen Beitrag nicht bearbeiten.')
        return redirect(url)

    form = PostingUpdateForm(request.form)
    if not form.validate():
        return posting_update_form(posting_id, form)

    event = board_posting_command_service.update_posting(
        posting, g.current_user.id, form.body.data
    )

    flash_success('Der Beitrag wurde aktualisiert.')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    signals.posting_updated.send(None, event=event)

    return redirect(url)


@blueprint.route('/postings/<uuid:posting_id>/moderate')
@permission_required(BoardPermission.hide)
@templated
def posting_moderate_form(posting_id):
    """Show a form to moderate the posting."""
    posting = h.get_posting_or_404(posting_id)

    posting.creator = user_service.find_user(posting.creator_id)

    return {
        'posting': posting,
    }


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_hide(posting_id):
    """Hide a posting."""
    posting = h.get_posting_or_404(posting_id)
    moderator_id = g.current_user.id

    event = board_posting_command_service.hide_posting(posting, moderator_id)

    page = service.calculate_posting_page_number(posting, g.current_user)

    flash_success('Der Beitrag wurde versteckt.', icon='hidden')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    signals.posting_hidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(posting, page)


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_unhide(posting_id):
    """Un-hide a posting."""
    posting = h.get_posting_or_404(posting_id)
    moderator_id = g.current_user.id

    event = board_posting_command_service.unhide_posting(posting, moderator_id)

    page = service.calculate_posting_page_number(posting, g.current_user)

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.', icon='view')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    signals.posting_unhidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(posting, page)
