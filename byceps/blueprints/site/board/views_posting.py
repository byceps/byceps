"""
byceps.blueprints.site.board.views_posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import g, redirect, request
from flask_babel import gettext

from ....services.board import (
    last_view_service as board_last_view_service,
    posting_command_service as board_posting_command_service,
    posting_query_service as board_posting_query_service,
)
from ....services.text_markup.service import get_smileys
from ....services.user import service as user_service
from ....signals import board as board_signals
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content_with_location

from .authorization import BoardPermission, BoardPostingPermission
from .blueprint import blueprint
from .forms import PostingCreateForm, PostingUpdateForm
from . import _helpers as h, service


@blueprint.route('/postings/<uuid:posting_id>')
def posting_view(posting_id):
    """Show the page of the posting's topic that contains the posting,
    as seen by the current user.
    """
    posting = h.get_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(posting, g.user)

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
        flash_error(gettext('The posting to quote has not been found.'))
        return

    creator = user_service.get_user(posting.creator_id)

    return f'[quote author="{creator.screen_name}"]{posting.body}[/quote]'


@blueprint.route('/topics/<uuid:topic_id>/create', methods=['POST'])
@permission_required(BoardPostingPermission.create)
def posting_create(topic_id):
    """Create a posting to the topic."""
    topic = h.get_topic_or_404(topic_id)

    form = PostingCreateForm(request.form)
    if not form.validate():
        return posting_create_form(topic_id, form)

    creator = g.user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            gettext('This topic is locked. It cannot be replied to.'),
            icon='lock',
        )
        return redirect(h.build_url_for_topic(topic.id))

    if topic.posting_limited_to_moderators and not g.user.has_permission(
        BoardPermission.announce
    ):
        flash_error(
            gettext('Only moderators are allowed to reply in this topic.'),
            icon='announce',
        )
        return redirect(h.build_url_for_topic(topic.id))

    posting, event = board_posting_command_service.create_posting(
        topic.id, creator.id, body
    )

    if not g.user.is_anonymous:
        board_last_view_service.mark_category_as_just_viewed(
            topic.category.id, g.user.id
        )

    flash_success(gettext('Your reply has been added.'))

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    board_signals.posting_created.send(None, event=event)

    postings_per_page = service.get_postings_per_page_value()
    page_count = topic.count_pages(postings_per_page)

    return redirect(h.build_url_for_posting_in_topic_view(posting, page_count))


@blueprint.route('/postings/<uuid:posting_id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(posting_id, erroneous_form=None):
    """Show form to update a posting."""
    posting = h.get_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(posting, g.user)
    url = h.build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            gettext(
                'The posting must not be edited because '
                'the topic it belongs to is locked.'
            )
        )
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error(gettext('The posting must not be edited.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to edit this posting.'))
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

    page = service.calculate_posting_page_number(posting, g.user)
    url = h.build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            gettext(
                'The posting must not be edited because '
                'the topic it belongs to is locked.'
            )
        )
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error(gettext('The posting must not be edited.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to edit this posting.'))
        return redirect(url)

    form = PostingUpdateForm(request.form)
    if not form.validate():
        return posting_update_form(posting_id, form)

    event = board_posting_command_service.update_posting(
        posting.id, g.user.id, form.body.data
    )

    flash_success(gettext('The posting has been updated.'))

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    board_signals.posting_updated.send(None, event=event)

    return redirect(url)


@blueprint.route('/postings/<uuid:posting_id>/moderate')
@permission_required(BoardPermission.hide)
@templated
def posting_moderate_form(posting_id):
    """Show a form to moderate the posting."""
    posting = h.get_posting_or_404(posting_id)

    posting.creator = user_service.get_user(posting.creator_id)

    return {
        'posting': posting,
    }


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_hide(posting_id):
    """Hide a posting."""
    posting = h.get_posting_or_404(posting_id)
    moderator_id = g.user.id

    event = board_posting_command_service.hide_posting(posting.id, moderator_id)

    page = service.calculate_posting_page_number(posting, g.user)

    flash_success(gettext('The posting has been hidden.'), icon='hidden')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    board_signals.posting_hidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(posting, page)


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_unhide(posting_id):
    """Un-hide a posting."""
    posting = h.get_posting_or_404(posting_id)
    moderator_id = g.user.id

    event = board_posting_command_service.unhide_posting(
        posting.id, moderator_id
    )

    page = service.calculate_posting_page_number(posting, g.user)

    flash_success(
        gettext('The posting has been made visible again.'), icon='view'
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(posting.id)
    )
    board_signals.posting_unhidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(posting, page)
