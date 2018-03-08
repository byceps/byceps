"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import abort, current_app, g, redirect, request, url_for

from ...services.board import \
    category_service as board_category_service, \
    last_view_service as board_last_view_service, \
    posting_service as board_posting_service, \
    topic_service as board_topic_service
from ...services.text_markup.service import get_smileys, render_html
from ...services.user_badge import service as badge_service
from ...util.framework.blueprint import create_blueprint
from ...util.framework.flash import flash_error, flash_success
from ...util.framework.templating import templated
from ...util.views import respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import BoardPermission, BoardPostingPermission, \
    BoardTopicPermission
from .forms import PostingCreateForm, PostingUpdateForm, TopicCreateForm, \
    TopicUpdateForm
from . import signals


blueprint = create_blueprint('board', __name__)


permission_registry.register_enum(BoardPermission)
permission_registry.register_enum(BoardTopicPermission)
permission_registry.register_enum(BoardPostingPermission)


blueprint.add_app_template_filter(render_html, 'bbcode')


# -------------------------------------------------------------------- #
# category


@blueprint.route('/')
@templated
def category_index():
    """List categories."""
    board_id = _get_board_id()
    categories = board_category_service.get_categories_with_last_updates(
        board_id)

    user = g.current_user

    for category in categories:
        category.contains_unseen_postings = not user.is_anonymous \
            and board_last_view_service.contains_category_unseen_postings(
                category, user.id)

    return {
        'categories': categories,
    }


@blueprint.route('/categories/<slug>', defaults={'page': 1})
@blueprint.route('/categories/<slug>/pages/<int:page>')
@templated
def category_view(slug, page):
    """List latest topics in the category."""
    board_id = _get_board_id()
    category = board_category_service.find_category_by_slug(board_id, slug)
    if category is None:
        abort(404)

    user = g.current_user

    if not user.is_anonymous:
        board_last_view_service.mark_category_as_just_viewed(category.id,
                                                             user.id)

    topics_per_page = _get_topics_per_page_value()

    topics = board_topic_service.paginate_topics(category.id, user._user, page,
                                                 topics_per_page)

    for topic in topics.items:
        topic.contains_unseen_postings = not user.is_anonymous \
            and board_last_view_service.contains_topic_unseen_postings(
                topic, user.id)

    return {
        'category': category,
        'topics': topics,
    }


@blueprint.route('/categories/<category_id>/mark_all_topics_as_read', methods=['POST'])
@respond_no_content_with_location
def mark_all_topics_in_category_as_viewed(category_id):
    category = board_category_service.find_category_by_id(category_id)
    if category is None:
        abort(404)

    board_last_view_service.mark_all_topics_in_category_as_viewed(
        category_id, g.current_user.id)

    return url_for('.category_view', slug=category.slug)


# -------------------------------------------------------------------- #
# topic


@blueprint.route('/topics/<uuid:topic_id>', defaults={'page': 0})
@blueprint.route('/topics/<uuid:topic_id>/pages/<int:page>')
@templated
def topic_view(topic_id, page):
    """List postings for the topic."""
    user = g.current_user

    topic = board_topic_service.find_topic_visible_for_user(topic_id,
        user._user)

    if topic is None:
        abort(404)

    if topic.category.board_id != _get_board_id():
        abort(404)

    # Copy last view timestamp for later use to compare postings
    # against it.
    last_viewed_at = board_last_view_service.find_topic_last_viewed_at(
        topic.id, user.id)

    postings_per_page = _get_postings_per_page_value()
    if page == 0:
        posting = board_topic_service.find_default_posting_to_jump_to(
            topic.id, user._user, last_viewed_at)

        if posting is None:
            page = 1
        else:
            page = calculate_posting_page_number(posting)
            # Jump to a specific posting. This requires a redirect.
            url = _build_url_for_posting_in_topic_view(posting, page)
            return redirect(url, code=307)

    if not user.is_anonymous:
        # Mark as viewed before aborting so a user can itself remove the
        # 'new' tag from a locked topic.
        board_last_view_service.mark_topic_as_just_viewed(topic.id, user.id)

    postings = board_posting_service.paginate_postings(topic.id, user._user,
                                                       page, postings_per_page)

    add_unseen_flag_to_postings(postings.items, user._user, last_viewed_at)

    is_last_page = not postings.has_next

    creator_ids = {posting.creator_id for posting in postings.items}
    badges_by_user_id = badge_service.get_badges_for_users(creator_ids,
                                                           featured_only=True)
    badges_by_user_id = _select_global_and_brand_badges(badges_by_user_id,
                                                        g.brand_id)

    context = {
        'topic': topic,
        'postings': postings,
        'is_last_page': is_last_page,
        'badges_by_user_id': badges_by_user_id,
    }

    if is_last_page:
        context.update({
            'form': PostingCreateForm(),
            'smileys': get_smileys(),
        })

    return context


def _select_global_and_brand_badges(badges_by_user_id, brand_id):
    """Keep only badges that are global or belong to the given brand."""
    def generate_items():
        for user_id, badges in badges_by_user_id.items():
            selected_badges = {badge for badge in badges
                               if badge.brand_id in {None, brand_id}}
            yield user_id, selected_badges

    return dict(generate_items())


def add_unseen_flag_to_postings(postings, user, last_viewed_at):
    """Add the attribute 'unseen' to each posting."""
    for posting in postings:
        posting.unseen = posting.is_unseen(user, last_viewed_at)


@blueprint.route('/categories/<category_id>/create')
@permission_required(BoardTopicPermission.create)
@templated
def topic_create_form(category_id, erroneous_form=None):
    """Show a form to create a topic in the category."""
    category = board_category_service.find_category_by_id(category_id)
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
    if not form.validate():
        return topic_create_form(category_id, form)

    category = board_category_service.find_category_by_id(category_id)
    if category is None:
        abort(404)

    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()

    topic = board_topic_service.create_topic(category.id, creator.id, title, body)

    flash_success('Das Thema "{}" wurde hinzugefügt.', topic.title)
    signals.topic_created.send(None, topic_id=topic.id, url=topic.external_url)

    return redirect(topic.external_url)


@blueprint.route('/topics/<uuid:topic_id>/update')
@permission_required(BoardTopicPermission.update)
@templated
def topic_update_form(topic_id, erroneous_form=None):
    """Show form to update a topic."""
    topic = _get_topic_or_404(topic_id)
    url = topic.external_url

    user_may_update = topic.may_be_updated_by_user(g.current_user._user)

    if topic.locked and not user_may_update:
        flash_error(
            'Das Thema darf nicht bearbeitet werden weil es gesperrt ist.')
        return redirect(url)

    if topic.hidden:
        flash_error('Das Thema darf nicht bearbeitet werden.')
        return redirect(url)

    if not user_may_update:
        flash_error('Du darfst dieses Thema nicht bearbeiten.')
        return redirect(url)

    form = erroneous_form if erroneous_form \
            else TopicUpdateForm(obj=topic, body=topic.initial_posting.body)

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

    user_may_update = topic.may_be_updated_by_user(g.current_user._user)

    if topic.locked and not user_may_update:
        flash_error(
            'Das Thema darf nicht bearbeitet werden weil es gesperrt ist.')
        return redirect(url)

    if topic.hidden:
        flash_error('Das Thema darf nicht bearbeitet werden.')
        return redirect(url)

    if not user_may_update:
        flash_error('Du darfst dieses Thema nicht bearbeiten.')
        return redirect(url)

    form = TopicUpdateForm(request.form)
    if not form.validate():
        return topic_update_form(topic_id, form)

    board_topic_service.update_topic(topic, g.current_user.id, form.title.data,
                                     form.body.data)

    flash_success('Das Thema "{}" wurde aktualisiert.', topic.title)
    return redirect(url)


@blueprint.route('/topics/<uuid:topic_id>/moderate')
@permission_required(BoardPermission.hide)
@templated
def topic_moderate_form(topic_id):
    """Show a form to moderate the topic."""
    board_id = _get_board_id()
    topic = _get_topic_or_404(topic_id)

    categories = board_category_service.get_categories_excluding(board_id,
        topic.category_id)

    return {
        'topic': topic,
        'categories': categories,
    }


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def topic_hide(topic_id):
    """Hide a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.hide_topic(topic, moderator_id)

    flash_success('Das Thema "{}" wurde versteckt.', topic.title, icon='hidden')

    signals.topic_hidden.send(None, topic_id=topic.id,
                              moderator_id=moderator_id,
                              url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def topic_unhide(topic_id):
    """Un-hide a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.unhide_topic(topic, moderator_id)

    flash_success(
        'Das Thema "{}" wurde wieder sichtbar gemacht.', topic.title, icon='view')

    signals.topic_unhidden.send(None, topic_id=topic.id,
                                moderator_id=moderator_id,
                                url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(topic_id):
    """Lock a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.lock_topic(topic, moderator_id)

    flash_success('Das Thema "{}" wurde geschlossen.', topic.title, icon='lock')

    signals.topic_locked.send(None, topic_id=topic.id,
                              moderator_id=moderator_id,
                              url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(topic_id):
    """Unlock a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.unlock_topic(topic, moderator_id)

    flash_success('Das Thema "{}" wurde wieder geöffnet.', topic.title,
                  icon='unlock')

    signals.topic_unlocked.send(None, topic_id=topic.id,
                                moderator_id=moderator_id,
                                url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(topic_id):
    """Pin a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.pin_topic(topic, moderator_id)

    flash_success('Das Thema "{}" wurde angepinnt.', topic.title, icon='pin')

    signals.topic_pinned.send(None, topic_id=topic.id,
                              moderator_id=moderator_id,
                              url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(topic_id):
    """Unpin a topic."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    board_topic_service.unpin_topic(topic, moderator_id)

    flash_success('Das Thema "{}" wurde wieder gelöst.', topic.title)

    signals.topic_unpinned.send(None, topic_id=topic.id,
                                moderator_id=moderator_id,
                                url=topic.external_url)

    return _build_url_for_topic_in_category_view(topic)


@blueprint.route('/topics/<uuid:topic_id>/move', methods=['POST'])
@permission_required(BoardTopicPermission.move)
def topic_move(topic_id):
    """Move a topic from one category to another."""
    topic = _get_topic_or_404(topic_id)
    moderator_id = g.current_user.id

    new_category_id = request.form.get('category_id')
    if not new_category_id:
        abort(400, 'No target category ID given.')

    new_category = board_category_service.find_category_by_id(new_category_id)
    if new_category is None:
        abort(404)

    old_category = topic.category

    board_topic_service.move_topic(topic, new_category)

    flash_success('Das Thema "{}" wurde aus der Kategorie "{}" '
                  'in die Kategorie "{}" verschoben.',
                  topic.title, old_category.title, new_category.title,
                  icon='move')

    signals.topic_moved.send(None, topic_id=topic.id,
                             old_category_id=old_category.id,
                             new_category_id=new_category.id,
                             moderator_id=moderator_id,
                             url=topic.external_url)

    return redirect(_build_url_for_topic_in_category_view(topic))


# -------------------------------------------------------------------- #
# posting


@blueprint.route('/postings/<uuid:posting_id>')
def posting_view(posting_id):
    """Show the page of the posting's topic that contains the posting,
    as seen by the current user.
    """
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)

    return redirect(
        _build_url_for_posting_in_topic_view(posting, page, _external=True))


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

    posting = board_posting_service.find_posting_by_id(posting_id)
    if posting is None:
        flash_error('Der zu zitierende Beitrag wurde nicht gefunden.')
        return

    return '[quote author="{}"]{}[/quote]'.format(
        posting.creator.screen_name, posting.body)


@blueprint.route('/topics/<uuid:topic_id>/create', methods=['POST'])
@permission_required(BoardPostingPermission.create)
def posting_create(topic_id):
    """Create a posting to the topic."""
    topic = _get_topic_or_404(topic_id)

    form = PostingCreateForm(request.form)
    if not form.validate():
        return posting_create_form(topic_id, form)

    creator = g.current_user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')
        return redirect(topic.external_url)

    posting = board_posting_service.create_posting(topic, creator.id, body)

    if not g.current_user.is_anonymous:
        board_last_view_service.mark_category_as_just_viewed(topic.category.id,
                                                             g.current_user.id)

    flash_success('Deine Antwort wurde hinzugefügt.')
    signals.posting_created.send(None, posting_id=posting.id,
                                 url=posting.external_url)

    postings_per_page = _get_postings_per_page_value()
    page_count = topic.count_pages(postings_per_page)

    return redirect(_build_url_for_posting_in_topic_view(posting, page_count))


@blueprint.route('/postings/<uuid:posting_id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(posting_id, erroneous_form=None):
    """Show form to update a posting."""
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)
    url = _build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.current_user._user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
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
    posting = _get_posting_or_404(posting_id)

    page = calculate_posting_page_number(posting)
    url = _build_url_for_posting_in_topic_view(posting, page)

    user_may_update = posting.may_be_updated_by_user(g.current_user._user)

    if posting.topic.locked and not user_may_update:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
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

    board_posting_service.update_posting(posting, g.current_user.id,
        form.body.data)

    flash_success('Der Beitrag wurde aktualisiert.')
    return redirect(url)


@blueprint.route('/postings/<uuid:posting_id>/moderate')
@permission_required(BoardPermission.hide)
@templated
def posting_moderate_form(posting_id):
    """Show a form to moderate the posting."""
    posting = _get_posting_or_404(posting_id)

    return {
        'posting': posting,
    }


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['POST'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_hide(posting_id):
    """Hide a posting."""
    posting = _get_posting_or_404(posting_id)
    moderator_id = g.current_user.id

    board_posting_service.hide_posting(posting, moderator_id)

    page = calculate_posting_page_number(posting)

    flash_success('Der Beitrag wurde versteckt.', icon='hidden')

    signals.posting_hidden.send(None, posting_id=posting.id,
                                moderator_id=moderator_id,
                                url=posting.external_url)

    return _build_url_for_posting_in_topic_view(posting, page)


@blueprint.route('/postings/<uuid:posting_id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPermission.hide)
@respond_no_content_with_location
def posting_unhide(posting_id):
    """Un-hide a posting."""
    posting = _get_posting_or_404(posting_id)
    moderator_id = g.current_user.id

    board_posting_service.unhide_posting(posting, moderator_id)

    page = calculate_posting_page_number(posting)

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.', icon='view')

    signals.posting_unhidden.send(None, posting_id=posting.id,
                                  moderator_id=moderator_id,
                                  url=posting.external_url)

    return _build_url_for_posting_in_topic_view(posting, page)


def _get_board_id():
    return current_app.config['BOARD_ID']


def _get_topic_or_404(topic_id):
    topic = board_topic_service.find_topic_by_id(topic_id)

    if topic is None:
        abort(404)

    if topic.category.board_id != _get_board_id():
        abort(404)

    return topic


def _get_posting_or_404(posting_id):
    posting = board_posting_service.find_posting_by_id(posting_id)

    if posting is None:
        abort(404)

    return posting


def calculate_posting_page_number(posting):
    postings_per_page = _get_postings_per_page_value()

    return board_posting_service.calculate_posting_page_number(
        posting, g.current_user._user, postings_per_page)


def _get_topics_per_page_value():
    return int(current_app.config['BOARD_TOPICS_PER_PAGE'])


def _get_postings_per_page_value():
    return int(current_app.config['BOARD_POSTINGS_PER_PAGE'])


def _build_url_for_topic_in_category_view(topic):
    return url_for('.category_view',
                   slug=topic.category.slug,
                   _anchor=topic.anchor)


def _build_url_for_posting_in_topic_view(posting, page, **kwargs):
    return url_for('.topic_view',
                   topic_id=posting.topic.id,
                   page=page,
                   _anchor=posting.anchor,
                   **kwargs)
