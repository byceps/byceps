"""
byceps.services.board.blueprints.site.views_posting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses

from flask import abort, g, redirect, request
from flask_babel import gettext

from byceps.services.board import (
    board_last_view_service,
    board_posting_command_service,
    board_posting_query_service,
    signals as board_signals,
)
from byceps.services.board.errors import (
    ReactionDeniedError,
    ReactionExistsError,
)
from byceps.services.site.blueprints.site.navigation import (
    subnavigation_for_view,
)
from byceps.services.text_markup import text_markup_service
from byceps.services.user import user_service
from byceps.util.authz import has_current_user_permission
from byceps.util.framework.flash import flash_error, flash_success
from byceps.util.framework.templating import templated
from byceps.util.result import Err
from byceps.util.views import (
    permission_required,
    respond_no_content,
    respond_no_content_with_location,
)

from . import _helpers as h, service
from .blueprint import blueprint
from .forms import PostingCreateForm, PostingUpdateForm


@blueprint.get('/postings/<uuid:posting_id>')
def posting_view(posting_id):
    """Show the page of the post's topic that contains the post, as seen
    by the current user.
    """
    db_posting = h.get_db_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(db_posting)

    return redirect(
        h.build_url_for_posting_in_topic_view(db_posting, page, _external=True)
    )


@blueprint.get('/topics/<uuid:topic_id>/create')
@permission_required('board_posting.create')
@templated
@subnavigation_for_view('board')
def posting_create_form(topic_id, erroneous_form=None):
    """Show a form to create a post to the topic."""
    db_topic = h.get_db_topic_or_404(topic_id)

    form = erroneous_form if erroneous_form else PostingCreateForm()

    quoted_posting_bbcode = quote_posting_as_bbcode()
    if quoted_posting_bbcode:
        form.body.data = quoted_posting_bbcode

    return {
        'topic': db_topic,
        'form': form,
        'smileys': text_markup_service.get_smileys(),
    }


def quote_posting_as_bbcode():
    posting_id = request.args.get('quote', type=str)
    if not posting_id:
        return

    db_posting = board_posting_query_service.find_db_posting(posting_id)
    if db_posting is None:
        flash_error(gettext('The post to quote has not been found.'))
        return

    creator = user_service.get_user(db_posting.creator_id)

    return f'[quote author="{creator.screen_name}"]{db_posting.body}[/quote]'


@blueprint.post('/topics/<uuid:topic_id>/create')
@permission_required('board_posting.create')
def posting_create(topic_id):
    """Create a post to the topic."""
    db_topic = h.get_db_topic_or_404(topic_id)

    form = PostingCreateForm(request.form)
    if not form.validate():
        return posting_create_form(topic_id, form)

    creator = g.user
    body = form.body.data.strip()

    if db_topic.locked:
        flash_error(
            gettext('This topic is locked. It cannot be replied to.'),
            icon='lock',
        )
        return redirect(h.build_url_for_topic(db_topic.id))

    if (
        db_topic.posting_limited_to_moderators
        and not has_current_user_permission('board.announce')
    ):
        flash_error(
            gettext('Only moderators are allowed to reply in this topic.'),
            icon='announce',
        )
        return redirect(h.build_url_for_topic(db_topic.id))

    db_posting, event = board_posting_command_service.create_posting(
        db_topic.id, creator, body
    )

    if g.user.authenticated:
        board_last_view_service.mark_category_as_just_viewed(
            db_topic.category.id, g.user.id
        )

    flash_success(gettext('Your reply has been added.'))

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(db_posting.id)
    )
    board_signals.posting_created.send(None, event=event)

    postings_per_page = service.get_postings_per_page_value()
    page_count = db_topic.count_pages(postings_per_page)

    return redirect(
        h.build_url_for_posting_in_topic_view(db_posting, page_count)
    )


@blueprint.get('/postings/<uuid:posting_id>/update')
@permission_required('board_posting.update')
@templated
@subnavigation_for_view('board')
def posting_update_form(posting_id, erroneous_form=None):
    """Show form to update a post."""
    db_posting = h.get_db_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(db_posting)
    url = h.build_url_for_posting_in_topic_view(db_posting, page)

    user_may_update = service.may_posting_be_updated_by_current_user(db_posting)

    if db_posting.topic.locked and not user_may_update:
        flash_error(
            gettext(
                'The post must not be edited because '
                'the topic it belongs to is locked.'
            )
        )
        return redirect(url)

    if db_posting.topic.hidden or db_posting.hidden:
        flash_error(gettext('The post must not be edited.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to edit this post.'))
        return redirect(url)

    form = (
        erroneous_form if erroneous_form else PostingUpdateForm(obj=db_posting)
    )

    return {
        'form': form,
        'posting': db_posting,
        'smileys': text_markup_service.get_smileys(),
    }


@blueprint.post('/postings/<uuid:posting_id>')
@permission_required('board_posting.update')
def posting_update(posting_id):
    """Update a post."""
    db_posting = h.get_db_posting_or_404(posting_id)

    page = service.calculate_posting_page_number(db_posting)
    url = h.build_url_for_posting_in_topic_view(db_posting, page)

    user_may_update = service.may_posting_be_updated_by_current_user(db_posting)

    if db_posting.topic.locked and not user_may_update:
        flash_error(
            gettext(
                'The post must not be edited because '
                'the topic it belongs to is locked.'
            )
        )
        return redirect(url)

    if db_posting.topic.hidden or db_posting.hidden:
        flash_error(gettext('The post must not be edited.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to edit this post.'))
        return redirect(url)

    form = PostingUpdateForm(request.form)
    if not form.validate():
        return posting_update_form(posting_id, form)

    event = board_posting_command_service.update_posting(
        db_posting.id, g.user, form.body.data
    )

    flash_success(gettext('The post has been updated.'))

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(db_posting.id)
    )
    board_signals.posting_updated.send(None, event=event)

    return redirect(url)


@blueprint.get('/postings/<uuid:posting_id>/moderate')
@permission_required('board.hide')
@templated
@subnavigation_for_view('board')
def posting_moderate_form(posting_id):
    """Show a form to moderate the post."""
    db_posting = h.get_db_posting_or_404(posting_id)

    db_posting.creator = user_service.get_user(db_posting.creator_id)

    return {
        'posting': db_posting,
    }


@blueprint.post('/postings/<uuid:posting_id>/flags/hidden')
@permission_required('board.hide')
@respond_no_content_with_location
def posting_hide(posting_id):
    """Hide a post."""
    db_posting = h.get_db_posting_or_404(posting_id)
    moderator = g.user

    event = board_posting_command_service.hide_posting(db_posting.id, moderator)

    page = service.calculate_posting_page_number(db_posting)

    flash_success(gettext('The post has been hidden.'), icon='hidden')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(db_posting.id)
    )
    board_signals.posting_hidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(db_posting, page)


@blueprint.delete('/postings/<uuid:posting_id>/flags/hidden')
@permission_required('board.hide')
@respond_no_content_with_location
def posting_unhide(posting_id):
    """Un-hide a post."""
    db_posting = h.get_db_posting_or_404(posting_id)
    moderator = g.user

    event = board_posting_command_service.unhide_posting(
        db_posting.id, moderator
    )

    page = service.calculate_posting_page_number(db_posting)

    flash_success(gettext('The post has been made visible again.'), icon='view')

    event = dataclasses.replace(
        event, url=h.build_external_url_for_posting(db_posting.id)
    )
    board_signals.posting_unhidden.send(None, event=event)

    return h.build_url_for_posting_in_topic_view(db_posting, page)


@blueprint.post('/postings/<uuid:posting_id>/reactions/<kind>')
@permission_required('board_posting.create')
@respond_no_content
def add_reaction(posting_id, kind):
    """Add a reaction to a post."""
    db_posting = h.get_db_posting_or_404(posting_id)

    result = board_posting_command_service.add_reaction(
        db_posting, g.user, kind
    )

    match result:
        case Err(e):
            if isinstance(e, ReactionDeniedError):
                abort(403)
            elif isinstance(e, ReactionExistsError):
                abort(409)
            else:
                abort(500)


@blueprint.delete('/postings/<uuid:posting_id>/reactions/<kind>')
@permission_required('board_posting.create')
@respond_no_content
def remove_reaction(posting_id, kind):
    """Remove a reaction from a post."""
    db_posting = h.get_db_posting_or_404(posting_id)

    result = board_posting_command_service.remove_reaction(
        db_posting, g.user, kind
    )

    match result:
        case Err(e):
            if isinstance(e, ReactionDeniedError):
                abort(403)
            elif isinstance(e, ReactionExistsError):
                abort(409)
            else:
                abort(500)
