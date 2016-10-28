# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, current_app, g, redirect, request, url_for

from ...services.board import service as board_service
from ...services.user_badge import service as badge_service
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import BoardPostingPermission, BoardTopicPermission
from .formatting import get_smileys, render_html
from .forms import PostingCreateForm, PostingUpdateForm, TopicCreateForm, \
    TopicUpdateForm
from . import signals


blueprint = create_blueprint('board', __name__)


permission_registry.register_enum(BoardTopicPermission)
permission_registry.register_enum(BoardPostingPermission)


blueprint.add_app_template_filter(render_html, 'bbcode')


# -------------------------------------------------------------------- #
# category


@blueprint.route('/categories')
@templated
def category_index():
    """List categories."""
    brand_id = g.party.brand.id
    categories = board_service.get_categories_with_last_updates(brand_id)

    return {
        'categories': categories,
    }


@blueprint.route('/categories/<slug>', defaults={'page': 1})
@blueprint.route('/categories/<slug>/pages/<int:page>')
@templated
def category_view(slug, page):
    """List latest topics in the category."""
    category = board_service.find_category_by_slug(g.party.brand.id, slug)
    if category is None:
        abort(404)

    board_service.mark_category_as_just_viewed(category, g.current_user)

    topics_per_page = _get_topics_per_page_value()

    topics = board_service.paginate_topics(category, g.current_user, page,
                                           topics_per_page)

    return {
        'category': category,
        'topics': topics,
    }


# -------------------------------------------------------------------- #
# topic


@blueprint.route('/topics/<uuid:topic_id>', defaults={'page': 0})
@blueprint.route('/topics/<uuid:topic_id>/pages/<int:page>')
@templated
def topic_view(topic_id, page):
    """List postings for the topic."""
    topic = board_service.find_topic_visible_for_user(topic_id, g.current_user)
    if topic is None:
        abort(404)

    # Copy last view timestamp for later use to compare postings
    # against it.
    last_viewed_at = topic.find_last_viewed_at(g.current_user)

    postings_per_page = _get_postings_per_page_value()
    if page == 0:
        posting = board_service.find_default_posting_to_jump_to(topic,
                                                                g.current_user,
                                                                last_viewed_at)

        if posting is None:
            page = 1
        else:
            page = calculate_posting_page_number(posting)
            # Jump to a specific posting. This requires a redirect.
            url = url_for('.topic_view',
                          topic_id=topic.id,
                          page=page,
                          _anchor=posting.anchor)
            return redirect(url, code=307)

    # Mark as viewed before aborting so a user can itself remove the
    # 'new' tag from a locked topic.
    board_service.mark_topic_as_just_viewed(topic, g.current_user)

    if topic.hidden:
        flash_notice('Das Thema ist versteckt.', icon='hidden')

    if topic.locked:
        flash_notice(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')

    postings = board_service.paginate_postings(topic, g.current_user, page,
                                               postings_per_page)

    add_unseen_flag_to_postings(postings.items, g.current_user, last_viewed_at)

    creator_ids = {posting.creator.id for posting in postings.items}
    badges_by_user_id = badge_service.get_badges_for_users(creator_ids)

    return {
        'topic': topic,
        'postings': postings,
        'badges_by_user_id': badges_by_user_id,
    }


def add_unseen_flag_to_postings(postings, user, last_viewed_at):
    """Add the attribute 'unseen' to each posting."""
    for posting in postings:
        posting.unseen = posting.is_unseen(user, last_viewed_at)


@blueprint.route('/categories/<category_id>/create')
@permission_required(BoardTopicPermission.create)
@templated
def topic_create_form(category_id, erroneous_form=None):
    """Show a form to create a topic in the category."""
    category = board_service.find_category_by_id(category_id)
    if category is None:
        abort(404)

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
    form = TopicCreateForm(request.form)

    category = board_service.find_category_by_id(category_id)
    if category is None:
        abort(404)

    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()

    topic = board_service.create_topic(category, creator, title, body)

    flash_success('Das Thema "{}" wurde hinzugefügt.', topic.title)
    signals.topic_created.send(None, topic=topic)

    return redirect(topic.external_url)


@blueprint.route('/topics/<uuid:topic_id>/update')
@permission_required(BoardTopicPermission.update)
@templated
def topic_update_form(topic_id):
    """Show form to update a topic."""
    topic = _get_topic_or_404(topic_id)
    url = topic.external_url

    if topic.locked:
        flash_error(
            'Das Thema darf nicht bearbeitet werden weil es gesperrt ist.')
        return redirect(url)

    if topic.hidden:
        flash_error('Das Thema darf nicht bearbeitet werden.')
        return redirect(url)

    if not topic.may_be_updated_by_user(g.current_user):
        flash_error('Du darfst dieses Thema nicht bearbeiten.')
        return redirect(url)

    form = TopicUpdateForm(obj=topic, body=topic.initial_posting.body)

    return {
        'form': form,
        'topic': topic,
        'smileys': get_smileys(),
    }

@blueprint.route('/topics/<uuid:topic_id>', methods=['POST'])
@permission_required(BoardTopicPermission.update)
def topic_update(topic_id):
    """Update a topic."""
    topic = _get_topic_or_404(topic_id)
    url = topic.external_url

    if topic.locked:
        flash_error(
            'Das Thema darf nicht bearbeitet werden weil es gesperrt ist.')
        return redirect(url)

    if topic.hidden:
        flash_error('Das Thema darf nicht bearbeitet werden.')
        return redirect(url)

    if not topic.may_be_updated_by_user(g.current_user):
        flash_error('Du darfst dieses Thema nicht bearbeiten.')
        return redirect(url)

    form = TopicUpdateForm(request.form)

    board_service.update_topic(topic, g.current_user, form.title.data,
                               form.body.data)

    flash_success('Das Thema "{}" wurde aktualisiert.', topic.title)
    return redirect(url)


@blueprint.route('/topics/<uuid:topic_id>/moderate')
@permission_required(BoardTopicPermission.hide)
@templated
def topic_moderate_form(topic_id):
    """Show a form to moderate the topic."""
    topic = _get_topic_or_404(topic_id)

    categories = board_service.get_categories_excluding(g.party.brand.id,
                                                        topic.category_id)

    return {
        'topic': topic,
        'categories': categories,
    }


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['POST'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_hide(topic_id):
    """Hide a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.hide_topic(topic, g.current_user)

    flash_success('Das Thema "{}" wurde versteckt.', topic.title, icon='hidden')
    signals.topic_hidden.send(None, topic=topic)
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_unhide(topic_id):
    """Un-hide a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.unhide_topic(topic, g.current_user)

    flash_success(
        'Das Thema "{}" wurde wieder sichtbar gemacht.', topic.title, icon='view')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(topic_id):
    """Lock a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.lock_topic(topic, g.current_user)

    flash_success('Das Thema "{}" wurde geschlossen.', topic.title, icon='lock')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(topic_id):
    """Unlock a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.unlock_topic(topic, g.current_user)

    flash_success('Das Thema "{}" wurde wieder geöffnet.', topic.title,
                  icon='unlock')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(topic_id):
    """Pin a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.pin_topic(topic, g.current_user)

    flash_success('Das Thema "{}" wurde angepinnt.', topic.title, icon='pin')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(topic_id):
    """Unpin a topic."""
    topic = _get_topic_or_404(topic_id)

    board_service.unpin_topic(topic, g.current_user)

    flash_success('Das Thema "{}" wurde wieder gelöst.', topic.title)
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:topic_id>/move', methods=['POST'])
@permission_required(BoardTopicPermission.move)
def topic_move(topic_id):
    """Move a topic from one category to another."""
    topic = _get_topic_or_404(topic_id)

    new_category_id = request.form['category_id']
    new_category = board_service.find_category_by_id(new_category_id)
    if new_category is None:
        abort(404)

    old_category = topic.category

    board_service.move_topic(topic, new_category)

    flash_success('Das Thema "{}" wurde aus der Kategorie "{}" '
                  'in die Kategorie "{}" verschoben.',
                  topic.title, old_category.title, new_category.title,
                  icon='move')
    return redirect_to('.category_view',
                       slug=topic.category.slug,
                       _anchor=topic.anchor)


# -------------------------------------------------------------------- #
# posting


@blueprint.route('/postings/<uuid:posting_id>')
def posting_view(posting_id):
    """Show the page of the posting's topic that contains the posting,
    as seen by the current user.
    """
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)

    return redirect_to('.topic_view',
                       topic_id=posting.topic.id,
                       page=page,
                       _anchor=posting.anchor,
                       _external=True)


@blueprint.route('/topics/<uuid:topic_id>/create')
@permission_required(BoardPostingPermission.create)
@templated
def posting_create_form(topic_id, erroneous_form=None):
    """Show a form to create a posting to the topic."""
    topic = _get_topic_or_404(topic_id)

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

    posting = board_service.find_posting_by_id(posting_id)
    if posting is None:
        flash_error('Der zu zitierende Beitrag wurde nicht gefunden.')
        return

    return '[quote author="{}"]{}[/quote]'.format(
        posting.creator.screen_name, posting.body)


@blueprint.route('/topics/<uuid:topic_id>/create', methods=['POST'])
@permission_required(BoardPostingPermission.create)
def posting_create(topic_id):
    """Create a posting to the topic."""
    form = PostingCreateForm(request.form)

    topic = _get_topic_or_404(topic_id)
    creator = g.current_user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')
        return redirect(topic.external_url)

    posting = board_service.create_posting(topic, creator, body)

    board_service.mark_category_as_just_viewed(topic.category, g.current_user)

    flash_success('Deine Antwort wurde hinzugefügt.')
    signals.posting_created.send(None, posting=posting)

    postings_per_page = _get_postings_per_page_value()
    page_count = topic.count_pages(postings_per_page)

    return redirect_to('.topic_view',
                       topic_id=topic.id,
                       page=page_count,
                       _anchor=posting.anchor)


@blueprint.route('/postings/<uuid:posting_id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(posting_id):
    """Show form to update a posting."""
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)
    url = url_for('.topic_view', topic_id=posting.topic.id, page=page)

    if posting.topic.locked:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    if not posting.may_be_updated_by_user(g.current_user):
        flash_error('Du darfst diesen Beitrag nicht bearbeiten.')
        return redirect(url)

    form = PostingUpdateForm(obj=posting)

    return {
        'form': form,
        'posting': posting,
        'smileys': get_smileys(),
    }


@blueprint.route('/postings/<uuid:posting_id>', methods=['POST'])
@permission_required(BoardPostingPermission.update)
def posting_update(posting_id):
    """Update a posting."""
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)
    url = url_for('.topic_view', topic_id=posting.topic.id, page=page)

    if posting.topic.locked:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    if not posting.may_be_updated_by_user(g.current_user):
        flash_error('Du darfst diesen Beitrag nicht bearbeiten.')
        return redirect(url)

    form = PostingUpdateForm(request.form)

    board_service.update_posting(posting, g.current_user, form.body.data)

    flash_success('Der Beitrag wurde aktualisiert.')
    return redirect(url)


@blueprint.route('/postings/<uuid:posting_id>/moderate')
@permission_required(BoardPostingPermission.hide)
@templated
def posting_moderate_form(posting_id):
    """Show a form to moderate the posting."""
    posting = _get_posting_or_404(posting_id)

    return {
        'posting': posting,
    }


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_hide(posting_id):
    """Hide a posting."""
    posting = _get_posting_or_404(posting_id)

    board_service.hide_posting(posting, g.current_user)

    page = calculate_posting_page_number(posting)

    flash_success('Der Beitrag wurde versteckt.', icon='hidden')
    signals.posting_hidden.send(None, posting=posting)
    return url_for('.topic_view',
                   topic_id=posting.topic.id,
                   page=page,
                   _anchor=posting.anchor)


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_unhide(posting_id):
    """Un-hide a posting."""
    posting = _get_posting_or_404(posting_id)

    board_service.unhide_posting(posting, g.current_user)

    page = calculate_posting_page_number(posting)

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.', icon='view')
    return url_for('.topic_view',
                   topic_id=posting.topic.id,
                   page=page,
                   _anchor=posting.anchor)


def _get_topic_or_404(topic_id):
    topic = board_service.find_topic_by_id(topic_id)

    if topic is None:
        abort(404)

    return topic


def _get_posting_or_404(posting_id):
    posting = board_service.find_posting_by_id(posting_id)

    if posting is None:
        abort(404)

    return posting


def calculate_posting_page_number(posting):
    postings_per_page = _get_postings_per_page_value()

    return board_service.calculate_posting_page_number(posting, g.current_user,
                                                       postings_per_page)


def _get_topics_per_page_value():
    return int(current_app.config['BOARD_TOPICS_PER_PAGE'])


def _get_postings_per_page_value():
    return int(current_app.config['BOARD_POSTINGS_PER_PAGE'])
