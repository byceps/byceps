# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
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
from .formatting import render_html
from .forms import PostingCreateForm, PostingUpdateForm, TopicCreateForm
from .models import Category, Posting, Topic


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
    categories = Category.query.for_current_brand().all()
    return {'categories': categories}


@blueprint.route('/categories/<slug>', defaults={'page': 1})
@blueprint.route('/categories/<slug>/pages/<int:page>')
@templated
def category_view(slug, page):
    """List latest topics in the category."""
    category = Category.query \
        .for_current_brand() \
        .filter_by(slug=slug) \
        .first_or_404()

    category.mark_as_viewed()

    topics_per_page = int(current_app.config['BOARD_TOPICS_PER_PAGE'])

    topics = Topic.query \
        .filter_by(category=category) \
        .only_visible() \
        .order_by(Topic.pinned.desc(), Topic.last_updated_at.desc()) \
        .paginate(page, topics_per_page)

    return {
        'category': category,
        'topics': topics,
    }


# -------------------------------------------------------------------- #
# topic


@blueprint.route('/topics/<id>', defaults={'page': 1})
@blueprint.route('/topics/<id>/pages/<int:page>')
@templated
def topic_view(id, page):
    """List postings for the topic."""
    topic = Topic.query.only_visible().with_id_or_404(id)

    # Copy last view timestamp for later use to compare postings
    # against it.
    last_viewed_at = topic.last_viewed_at

    # Mark as viewed before aborting so a user can itself remove the
    # 'new' tag from a locked topic.
    topic.mark_as_viewed()

    if topic.hidden:
        flash_notice('Das Thema ist versteckt.', icon='hidden')

    if topic.locked:
        flash_notice(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.',
            icon='lock')

    postings_per_page = int(current_app.config['BOARD_POSTINGS_PER_PAGE'])

    postings = Posting.query \
        .filter_by(topic=topic) \
        .only_visible() \
        .order_by(Posting.created_at.asc()) \
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
def topic_create_form(category_id, errorneous_form=None):
    """Show a form to create a topic in the category."""
    category = Category.query.get_or_404(category_id)
    form = errorneous_form if errorneous_form else TopicCreateForm()
    return {
        'category': category,
        'form': form,
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

    topic = Topic.create(category, creator, title, body)

    flash_success('Das Thema "{}" wurde hinzugefügt.', topic.title)
    return redirect_to('.topic_view', id=topic.id)


@blueprint.route('/topics/<id>/flags')
@permission_required(BoardTopicPermission.hide)
@templated
def topic_flags_form(id):
    """Show a form to change the topic's flags."""
    topic = Topic.query.get_or_404(id)
    return {
        'topic': topic,
    }


@blueprint.route('/topics/<id>/flags/hidden', methods=['POST'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_hide(id):
    """Hide a topic."""
    topic = Topic.query.get_or_404(id)
    topic.hidden = True
    topic.hidden_by = g.current_user
    db.session.commit()

    flash_success('Das Thema "{}" wurde versteckt.', topic.title, icon='hidden')
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


@blueprint.route('/topics/<id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardTopicPermission.hide)
@respond_no_content_with_location
def topic_unhide(id):
    """Un-hide a topic."""
    topic = Topic.query.get_or_404(id)
    topic.hidden = False
    topic.hidden_by = None
    db.session.commit()

    flash_success(
        'Das Thema "{}" wurde wieder sichtbar gemacht.', topic.title, icon='view')
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


@blueprint.route('/topics/<id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(id):
    """Lock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.locked = True
    topic.locked_by = g.current_user
    db.session.commit()

    flash_success('Das Thema "{}" wurde geschlossen.', topic.title, icon='lock')
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


@blueprint.route('/topics/<id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(id):
    """Unlock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.locked = False
    topic.locked_by = None
    db.session.commit()

    flash_success('Das Thema "{}" wurde wieder geöffnet.', topic.title,
                  icon='unlock')
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


@blueprint.route('/topics/<id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(id):
    """Pin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.pinned = True
    topic.pinned_by = g.current_user
    db.session.commit()

    flash_success('Das Thema "{}" wurde angepinnt.', topic.title, icon='pin')
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


@blueprint.route('/topics/<id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(id):
    """Unpin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.pinned = False
    topic.pinned_by = None
    db.session.commit()

    flash_success('Das Thema "{}" wurde wieder gelöst.', topic.title)
    return url_for('.category_view', id=topic.category.id, _anchor=topic.anchor)


# -------------------------------------------------------------------- #
# posting


@blueprint.route('/topics/<topic_id>/create')
@permission_required(BoardPostingPermission.create)
@templated
def posting_create_form(topic_id, errorneous_form=None):
    """Show a form to create a posting to the topic."""
    topic = Topic.query.get_or_404(topic_id)
    form = errorneous_form if errorneous_form else PostingCreateForm()

    quoted_posting_bbcode = quote_posting_as_bbcode()
    if quoted_posting_bbcode:
        form.body.data = quoted_posting_bbcode

    return {
        'topic': topic,
        'form': form,
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


@blueprint.route('/topics/<topic_id>/create', methods=['POST'])
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
        return redirect_to('.topic_view', id=topic.id)

    posting = Posting.create(topic, creator, body)

    flash_success('Deine Antwort wurde hinzugefügt.')
    return redirect_to('.topic_view',
                       id=topic.id,
                       page=topic.page_count,
                       _anchor=posting.anchor)


@blueprint.route('/postings/<id>/update')
@permission_required(BoardPostingPermission.update)
@templated
def posting_update_form(id):
    """Show form to update a posting."""
    posting = Posting.query.get_or_404(id)
    url = url_for('.topic_view', id=posting.topic.id, _anchor=posting.anchor)

    if posting.creator != g.current_user:
        flash_error('Du bist nicht der Autor dieses Beitrags, '
                    'deshalb darfst du ihn nicht bearbeiten.')
        return redirect(url)

    if posting.topic.locked:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    form = PostingUpdateForm(obj=posting)

    return {
        'form': form,
        'posting': posting,
    }


@blueprint.route('/postings/<id>', methods=['POST'])
@permission_required(BoardPostingPermission.update)
def posting_update(id):
    """Update a posting."""
    posting = Posting.query.get_or_404(id)
    url = url_for('.topic_view', id=posting.topic.id, _anchor=posting.anchor)

    if posting.creator != g.current_user:
        flash_error('Du bist nicht der Autor dieses Beitrags, '
                    'deshalb darfst du ihn nicht bearbeiten.')
        return redirect(url)

    if posting.topic.locked:
        flash_error(
            'Der Beitrag darf nicht bearbeitet werden weil das Thema, '
            'zu dem dieser Beitrag gehört, gesperrt ist.')
        return redirect(url)

    if posting.topic.hidden or posting.hidden:
        flash_error('Der Beitrag darf nicht bearbeitet werden.')
        return redirect(url)

    form = PostingUpdateForm(request.form)

    posting.body = form.body.data.strip()
    posting.last_edited_by = g.current_user
    posting.edit_count += 1
    db.session.commit()

    flash_success('Der Beitrag wurde aktualisiert.')
    return redirect(url)


@blueprint.route('/postings/<id>/flags')
@permission_required(BoardPostingPermission.hide)
@templated
def posting_flags_form(id):
    """Show a form to change the posting's flags."""
    posting = Posting.query.get_or_404(id)
    return {
        'posting': posting,
    }


@blueprint.route('/postings/<id>/flags/hidden', methods=['POST'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_hide(id):
    """Hide a posting."""
    posting = Posting.query.get_or_404(id)
    posting.hidden = True
    posting.hidden_by = g.current_user
    db.session.commit()

    flash_success('Der Beitrag wurde versteckt.', icon='hidden')
    return url_for('.topic_view', id=posting.topic.id, _anchor=posting.anchor)


@blueprint.route('/postings/<id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_unhide(id):
    """Un-hide a posting."""
    posting = Posting.query.get_or_404(id)
    posting.hidden = False
    posting.hidden_by = None
    db.session.commit()

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.', icon='view')
    return url_for('.topic_view', id=posting.topic.id, _anchor=posting.anchor)
