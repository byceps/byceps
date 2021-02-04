"""
byceps.blueprints.site.board.views_topic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from datetime import datetime
from typing import Optional

from flask import abort, g, redirect, request
from flask_babel import gettext

from ....services.authentication.session.models.current_user import CurrentUser
from ....services.board import (
    category_query_service as board_category_query_service,
    last_view_service as board_last_view_service,
    posting_query_service as board_posting_query_service,
    topic_command_service as board_topic_command_service,
    topic_query_service as board_topic_query_service,
)
from ....services.board.transfer.models import TopicID
from ....services.text_markup.service import get_smileys
from ....services.user import service as user_service
from ....signals import board as board_signals
from ....util.framework.flash import flash_error, flash_success
from ....util.framework.templating import templated
from ....util.views import permission_required, respond_no_content_with_location

from .authorization import BoardPermission, BoardTopicPermission
from .blueprint import blueprint
from .forms import PostingCreateForm, TopicCreateForm, TopicUpdateForm
from . import _helpers as h, service


@blueprint.route('/topics', defaults={'page': 1})
@blueprint.route('/topics/pages/<int:page>')
@templated
def topic_index(page):
    """List latest topics in all categories."""
    board_id = h.get_board_id()
    user = g.user

    h.require_board_access(board_id, user.id)

    include_hidden = service.may_current_user_view_hidden()
    topics_per_page = service.get_topics_per_page_value()

    topics = board_topic_query_service.paginate_topics(
        board_id, include_hidden, page, topics_per_page
    )

    service.add_topic_creators(topics.items)
    service.add_topic_unseen_flag(topics.items, user)

    return {
        'topics': topics,
    }


@blueprint.route('/topics/<uuid:topic_id>', defaults={'page': 0})
@blueprint.route('/topics/<uuid:topic_id>/pages/<int:page>')
@templated
def topic_view(topic_id, page):
    """List postings for the topic."""
    user = g.user

    include_hidden = service.may_current_user_view_hidden()

    topic = board_topic_query_service.find_topic_visible_for_user(
        topic_id, include_hidden
    )

    if topic is None:
        abort(404)

    board_id = h.get_board_id()

    if topic.category.hidden or (topic.category.board_id != board_id):
        abort(404)

    h.require_board_access(board_id, user.id)

    # Copy last view timestamp for later use to compare postings
    # against it.
    last_viewed_at = board_last_view_service.find_topic_last_viewed_at(
        topic.id, user.id
    )

    postings_per_page = service.get_postings_per_page_value()
    if page == 0:
        posting_url_to_redirect_to = _find_posting_url_to_redirect_to(
            topic.id, user, include_hidden, last_viewed_at
        )

        if posting_url_to_redirect_to is not None:
            # Jump to a specific posting. This requires a redirect.
            return redirect(posting_url_to_redirect_to, code=307)

        page = 1

    if user.authenticated:
        # Mark as viewed before aborting so a user can itself remove the
        # 'new' tag from a locked topic.
        board_last_view_service.mark_topic_as_just_viewed(topic.id, user.id)

    postings = board_posting_query_service.paginate_postings(
        topic.id, include_hidden, g.party_id, page, postings_per_page
    )

    service.add_unseen_flag_to_postings(postings.items, user, last_viewed_at)

    is_last_page = not postings.has_next

    service.enrich_creators(postings.items, g.brand_id, g.party_id)

    context = {
        'topic': topic,
        'postings': postings,
        'is_last_page': is_last_page,
    }

    if is_last_page:
        context.update(
            {
                'form': PostingCreateForm(),
                'smileys': get_smileys(),
            }
        )

    return context


def _find_posting_url_to_redirect_to(
    topic_id: TopicID,
    user: CurrentUser,
    include_hidden: bool,
    last_viewed_at: Optional[datetime],
) -> Optional[str]:
    posting = board_topic_query_service.find_default_posting_to_jump_to(
        topic_id, user, include_hidden, last_viewed_at
    )

    if posting is None:
        return None

    page = service.calculate_posting_page_number(posting)

    return h.build_url_for_posting_in_topic_view(posting, page)


@blueprint.route('/categories/<category_id>/create')
@permission_required(BoardTopicPermission.create)
@templated
def topic_create_form(category_id, erroneous_form=None):
    """Show a form to create a topic in the category."""
    category = h.get_category_or_404(category_id)

    form = erroneous_form if erroneous_form else TopicCreateForm()

    return {
        'category': category,
        'form': form,
        'smileys': get_smileys(),
    }


@blueprint.route('/categories/<category_id>/create', methods=['POST'])
@permission_required(BoardTopicPermission.create)
def topic_create(category_id):
    """Create a topic in the category."""
    category = h.get_category_or_404(category_id)

    form = TopicCreateForm(request.form)
    if not form.validate():
        return topic_create_form(category.id, form)

    creator = g.user
    title = form.title.data.strip()
    body = form.body.data.strip()

    topic, event = board_topic_command_service.create_topic(
        category.id, creator.id, title, body
    )
    topic_url = h.build_external_url_for_topic(topic.id)

    flash_success(
        gettext('Topic "%(title)s" has been created.', title=topic.title)
    )

    event = dataclasses.replace(event, url=topic_url)
    board_signals.topic_created.send(None, event=event)

    return redirect(topic_url)


@blueprint.route('/topics/<uuid:topic_id>/update')
@permission_required(BoardTopicPermission.update)
@templated
def topic_update_form(topic_id, erroneous_form=None):
    """Show form to update a topic."""
    topic = h.get_topic_or_404(topic_id)
    url = h.build_url_for_topic(topic.id)

    user_may_update = topic.may_be_updated_by_user(g.user)

    if topic.locked and not user_may_update:
        flash_error(
            gettext('The topic must not be updated because it is locked.')
        )
        return redirect(url)

    if topic.hidden:
        flash_error(gettext('The topic must not be updated.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to update this topic.'))
        return redirect(url)

    form = (
        erroneous_form
        if erroneous_form
        else TopicUpdateForm(obj=topic, body=topic.initial_posting.body)
    )

    return {
        'form': form,
        'topic': topic,
        'smileys': get_smileys(),
    }


@blueprint.route('/topics/<uuid:topic_id>', methods=['POST'])
@permission_required(BoardTopicPermission.update)
def topic_update(topic_id):
    """Update a topic."""
    topic = h.get_topic_or_404(topic_id)
    url = h.build_url_for_topic(topic.id)

    user_may_update = topic.may_be_updated_by_user(g.user)

    if topic.locked and not user_may_update:
        flash_error(
            gettext('The topic must not be updated because it is locked.')
        )
        return redirect(url)

    if topic.hidden:
        flash_error(gettext('The topic must not be updated.'))
        return redirect(url)

    if not user_may_update:
        flash_error(gettext('You are not allowed to update this topic.'))
        return redirect(url)

    form = TopicUpdateForm(request.form)
    if not form.validate():
        return topic_update_form(topic_id, form)

    board_topic_command_service.update_topic(
        topic.id, g.user.id, form.title.data, form.body.data
    )

    flash_success(
        gettext('Topic "%(title)s" has been updated.', title=topic.title)
    )
    return redirect(url)


@blueprint.route('/topics/<uuid:topic_id>/moderate')
@permission_required(BoardPermission.hide)
@templated
def topic_moderate_form(topic_id):
    """Show a form to moderate the topic."""
    board_id = h.get_board_id()
    topic = h.get_topic_or_404(topic_id)

    topic.creator = user_service.get_user(topic.creator_id)

    categories = board_category_query_service.get_categories_excluding(
        board_id, topic.category_id
    )

    return {
        'topic': topic,
        'categories': categories,
    }


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def topic_hide(topic_id):
    """Hide a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.hide_topic(topic.id, moderator_id)

    flash_success(
        gettext('Topic "%(title)s" has been hidden.', title=topic.title),
        icon='hidden',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_hidden.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def topic_unhide(topic_id):
    """Un-hide a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.unhide_topic(topic.id, moderator_id)

    flash_success(
        gettext(
            'Topic "%(title)s" has been made visible again.',
            title=topic.title,
        ),
        icon='view',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_unhidden.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(topic_id):
    """Lock a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.lock_topic(topic.id, moderator_id)

    flash_success(
        gettext('Topic "%(title)s" has been locked.', title=topic.title),
        icon='lock',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_locked.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(topic_id):
    """Unlock a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.unlock_topic(topic.id, moderator_id)

    flash_success(
        gettext('Topic "%(title)s" has been unlocked.', title=topic.title),
        icon='unlock',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_unlocked.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(topic_id):
    """Pin a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.pin_topic(topic.id, moderator_id)

    flash_success(
        gettext('Topic "%(title)s" has been pinned.', title=topic.title),
        icon='pin',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_pinned.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(topic_id):
    """Unpin a topic."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    event = board_topic_command_service.unpin_topic(topic.id, moderator_id)

    flash_success(
        gettext('Topic "%(title)s" has been unpinned.', title=topic.title)
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_unpinned.send(None, event=event)

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/move', methods=['POST'])
@permission_required(BoardTopicPermission.move)
def topic_move(topic_id):
    """Move a topic from one category to another."""
    topic = h.get_topic_or_404(topic_id)
    moderator_id = g.user.id

    new_category_id = request.form.get('category_id')
    if not new_category_id:
        abort(400, 'No target category ID given.')

    new_category = h.get_category_or_404(new_category_id)

    old_category = topic.category

    event = board_topic_command_service.move_topic(
        topic.id, new_category.id, moderator_id
    )

    flash_success(
        gettext(
            'Topic "%(topic_title)s" has been moved from category '
            '"%(old_category_title)s" to category "%(new_category_title)s".',
            topic_title=topic.title,
            old_category_title=old_category.title,
            new_category_title=new_category.title,
        ),
        icon='move',
    )

    event = dataclasses.replace(
        event, url=h.build_external_url_for_topic(topic.id)
    )
    board_signals.topic_moved.send(None, event=event)

    return redirect(h.build_url_for_topic_in_category_view(topic))


@blueprint.route(
    '/topics/<uuid:topic_id>/flags/announcements', methods=['POST']
)
@permission_required(BoardPermission.announce)
@respond_no_content_with_location
def topic_limit_to_announcements(topic_id):
    """Limit posting in the topic to moderators."""
    topic = h.get_topic_or_404(topic_id)

    board_topic_command_service.limit_topic_to_announcements(topic.id)

    flash_success(
        gettext(
            'Topic "%(title)s" has been limited to announcements.',
            title=topic.title,
        ),
        icon='announce',
    )

    return h.build_url_for_topic_in_category_view(topic)


@blueprint.route(
    '/topics/<uuid:topic_id>/flags/announcements', methods=['DELETE']
)
@permission_required(BoardPermission.announce)
@respond_no_content_with_location
def topic_remove_limit_to_announcements(topic_id):
    """Allow non-moderators to post in the topic again."""
    topic = h.get_topic_or_404(topic_id)

    board_topic_command_service.remove_limit_of_topic_to_announcements(topic.id)

    flash_success(
        gettext(
            'Topic "%(title)s" has been reopened for regular replies.',
            title=topic.title,
        )
    )

    return h.build_url_for_topic_in_category_view(topic)
