# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app, g, redirect, request, url_for

from ...database import db
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
from .models.category import Category
from .models.posting import Posting
from .models.topic import Topic
from . import service
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
    categories = Category.query \
        .for_brand(g.party.brand) \
        .options(
            db.joinedload(Category.last_posting_updated_by),
        ) \
        .all()
    return {'categories': categories}


@blueprint.route('/categories/<slug>', defaults={'page': 1})
@blueprint.route('/categories/<slug>/pages/<int:page>')
@templated
def category_view(slug, page):
    """List latest topics in the category."""
    category = Category.query \
        .for_brand(g.party.brand) \
        .filter_by(slug=slug) \
        .first_or_404()

    service.mark_category_as_just_viewed(category, g.current_user)

    topics_per_page = int(current_app.config['BOARD_TOPICS_PER_PAGE'])

    topics = Topic.query \
        .for_category(category) \
        .options(
            db.joinedload(Topic.category),
            db.joinedload(Topic.creator),
            db.joinedload(Topic.last_updated_by),
            db.joinedload(Topic.hidden_by),
            db.joinedload(Topic.locked_by),
            db.joinedload(Topic.pinned_by),
        ) \
        .only_visible_for_current_user() \
        .order_by(Topic.pinned.desc(), Topic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)

    return {
        'category': category,
        'topics': topics,
    }


# -------------------------------------------------------------------- #
# topic


@blueprint.route('/topics/<uuid:id>', defaults={'page': 0})
@blueprint.route('/topics/<uuid:id>/pages/<int:page>')
@templated
def topic_view(id, page):
    """List postings for the topic."""
    topic = Topic.query \
        .options(
            db.joinedload(Topic.category),
        ) \
        .only_visible_for_current_user() \
        .with_id_or_404(id)

    # Copy last view timestamp for later use to compare postings
    # against it.
    last_viewed_at = topic.last_viewed_at

    postings_per_page = int(current_app.config['BOARD_POSTINGS_PER_PAGE'])
    if page == 0:
        posting = service.find_default_posting_to_jump_to(topic, g.current_user,
                                                          last_viewed_at)

        if posting is None:
            page = 1
        else:
            page = posting.calculate_page_number()
            # Jump to a specific posting. This requires a redirect.
            url = url_for('.topic_view',
                          id=topic.id,
                          page=page,
                          _anchor=posting.anchor)
            return redirect(url, code=307)

    # Mark as viewed before aborting so a user can itself remove the
    # 'new' tag from a locked topic.
    service.mark_topic_as_just_viewed(topic, g.current_user)

    if topic.hidden:
        flash_notice('Das Thema ist versteckt.', icon='hidden')

    if topic.locked:
        flash_notice(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')

    postings = Posting.query \
        .options(
            db.joinedload(Posting.topic),
            db.joinedload('creator')
                .load_only('id', 'screen_name', 'avatar_image_created_at', '_avatar_image_type')
                .joinedload('orga_team_memberships'),
            db.joinedload(Posting.last_edited_by).load_only('screen_name'),
            db.joinedload(Posting.hidden_by).load_only('screen_name'),
        ) \
        .for_topic(topic) \
        .only_visible_for_current_user() \
        .earliest_to_latest() \
        .paginate(page, postings_per_page)

    add_unseen_flag_to_postings(postings.items, last_viewed_at)

    return {
        'topic': topic,
        'postings': postings,
    }


def add_unseen_flag_to_postings(postings, last_viewed_at):
    """Add the attribute 'unseen' to each posting."""
    def unseen(posting):
        # Don't display the author's own posting as new to him/her.
        if posting.creator == g.current_user:
            return False

        return last_viewed_at is None \
            or posting.created_at > last_viewed_at

    # Don't display any posting as new to a guest.
    if g.current_user.is_anonymous:
        def unseen(posting):
            return False

    for posting in postings:
        posting.unseen = unseen(posting)


@blueprint.route('/categories/<category_id>/create')
@permission_required(BoardTopicPermission.create)
@templated
def topic_create_form(category_id, erroneous_form=None):
    """Show a form to create a topic in the category."""
    category = Category.query.get_or_404(category_id)
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

    category = Category.query.get_or_404(category_id)
    creator = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()

    topic = service.create_topic(category, creator, title, body)

    flash_success('Das Thema "{}" wurde hinzugefügt.', topic.title)
    signals.topic_created.send(None, topic=topic)

    return redirect(topic.external_url)


@blueprint.route('/topics/<uuid:id>/update')
@permission_required(BoardTopicPermission.update)
@templated
def topic_update_form(id):
    """Show form to update a topic."""
    topic = Topic.query.get_or_404(id)
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

    posting = topic.get_body_posting()
    form = TopicUpdateForm(obj=topic, body=posting.body)

    return {
        'form': form,
        'topic': topic,
        'smileys': get_smileys(),
    }


@blueprint.route('/topics/<uuid:id>', methods=['POST'])
@permission_required(BoardTopicPermission.update)
def topic_update(id):
    """Update a topic."""
    topic = Topic.query.get_or_404(id)
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

    service.update_topic(topic, g.current_user, form.title.data, form.body.data)

    flash_success('Das Thema "{}" wurde aktualisiert.', topic.title)
    return redirect(url)


@blueprint.route('/topics/<uuid:id>/moderate')
@permission_required(BoardTopicPermission.hide)
@templated
def topic_moderate_form(id):
    """Show a form to moderate the topic."""
    topic = Topic.query.get_or_404(id)

    categories = Category.query \
        .for_brand(g.party.brand) \
        .filter(Category.id != topic.category_id) \
        .order_by(Category.position) \
        .all()

    return {
        'topic': topic,
        'categories': categories,
    }


@blueprint.route('/topics/<uuid:id>/flags/hidden', methods=['POST'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_hide(id):
    """Hide a topic."""
    topic = Topic.query.get_or_404(id)
    topic.hide(g.current_user)
    db.session.commit()

    service.aggregate_topic(topic)

    flash_success('Das Thema "{}" wurde versteckt.', topic.title, icon='hidden')
    signals.topic_hidden.send(None, topic=topic)
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_unhide(id):
    """Un-hide a topic."""
    topic = Topic.query.get_or_404(id)
    topic.unhide()
    db.session.commit()

    service.aggregate_topic(topic)

    flash_success(
        'Das Thema "{}" wurde wieder sichtbar gemacht.', topic.title, icon='view')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(id):
    """Lock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.lock(g.current_user)
    db.session.commit()

    flash_success('Das Thema "{}" wurde geschlossen.', topic.title, icon='lock')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(id):
    """Unlock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.unlock()
    db.session.commit()

    flash_success('Das Thema "{}" wurde wieder geöffnet.', topic.title,
                  icon='unlock')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(id):
    """Pin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.pin(g.current_user)
    db.session.commit()

    flash_success('Das Thema "{}" wurde angepinnt.', topic.title, icon='pin')
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(id):
    """Unpin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.unpin()
    db.session.commit()

    flash_success('Das Thema "{}" wurde wieder gelöst.', topic.title)
    return url_for('.category_view', slug=topic.category.slug, _anchor=topic.anchor)


@blueprint.route('/topics/<uuid:id>/move', methods=['POST'])
@permission_required(BoardTopicPermission.move)
def topic_move(id):
    """Move a topic from one category to another."""
    topic = Topic.query.get_or_404(id)

    old_category = topic.category

    new_category_id = request.form['category_id']
    new_category = Category.query.get_or_404(new_category_id)

    topic.category = new_category
    db.session.commit()

    for category in old_category, new_category:
        service.aggregate_category(category)

    flash_success('Das Thema "{}" wurde aus der Kategorie "{}" '
                  'in die Kategorie "{}" verschoben.',
                  topic.title, old_category.title, new_category.title,
                  icon='move')
    return redirect_to('.category_view',
                       slug=topic.category.slug,
                       _anchor=topic.anchor)


# -------------------------------------------------------------------- #
# posting


@blueprint.route('/postings/<uuid:id>')
def posting_view(id):
    """Show the page of the posting's topic that contains the posting,
    as seen by the current user.
    """
    posting = Posting.query.get_or_404(id)

    page = posting.calculate_page_number()

    return redirect_to('.topic_view',
                       id=posting.topic.id,
                       page=page,
                       _anchor=posting.anchor,
                       _external=True)


@blueprint.route('/topics/<uuid:topic_id>/create')
@permission_required(BoardPostingPermission.create)
@templated
def posting_create_form(topic_id, erroneous_form=None):
    """Show a form to create a posting to the topic."""
    topic = Topic.query.get_or_404(topic_id)
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

    posting = Posting.query.get(posting_id)
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

    topic = Topic.query.get_or_404(topic_id)
    creator = g.current_user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')
        return redirect(topic.external_url)

    posting = service.create_posting(topic, creator, body)

    service.mark_category_as_just_viewed(topic.category, g.current_user)

    flash_success('Deine Antwort wurde hinzugefügt.')
    signals.posting_created.send(None, posting=posting)

    return redirect_to('.topic_view',
                       id=topic.id,
                       page=topic.page_count,
                       _anchor=posting.anchor)


@blueprint.route('/postings/<uuid:id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(id):
    """Show form to update a posting."""
    posting = Posting.query.get_or_404(id)

    page = posting.calculate_page_number()
    url = url_for('.topic_view', id=posting.topic.id, page=page)

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


@blueprint.route('/postings/<uuid:id>', methods=['POST'])
@permission_required(BoardPostingPermission.update)
def posting_update(id):
    """Update a posting."""
    posting = Posting.query.get_or_404(id)

    page = posting.calculate_page_number()
    url = url_for('.topic_view', id=posting.topic.id, page=page)

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

    service.update_posting(posting, g.current_user, form.body.data)

    flash_success('Der Beitrag wurde aktualisiert.')
    return redirect(url)


@blueprint.route('/postings/<uuid:id>/moderate')
@permission_required(BoardPostingPermission.hide)
@templated
def posting_moderate_form(id):
    """Show a form to moderate the posting."""
    posting = Posting.query.get_or_404(id)
    return {
        'posting': posting,
    }


@blueprint.route('/postings/<uuid:id>/flags/hidden', methods=['POST'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_hide(id):
    """Hide a posting."""
    posting = Posting.query.get_or_404(id)
    posting.hide(g.current_user)
    db.session.commit()

    service.aggregate_topic(posting.topic)

    page = posting.calculate_page_number()

    flash_success('Der Beitrag wurde versteckt.', icon='hidden')
    signals.posting_hidden.send(None, posting=posting)
    return url_for('.topic_view', id=posting.topic.id, page=page, _anchor=posting.anchor)


@blueprint.route('/postings/<uuid:id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_unhide(id):
    """Un-hide a posting."""
    posting = Posting.query.get_or_404(id)
    posting.unhide()
    db.session.commit()

    service.aggregate_topic(posting.topic)

    page = posting.calculate_page_number()

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.', icon='view')
    return url_for('.topic_view', id=posting.topic.id, page=page, _anchor=posting.anchor)
