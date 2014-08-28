# -*- coding: utf-8 -*-

"""
byceps.blueprints.board.views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from flask import g, request, url_for

from ...database import db
from ...util.framework import create_blueprint, flash_error, flash_notice, \
    flash_success
from ...util.templating import templated
from ...util.views import redirect_to, respond_no_content_with_location

from ..authorization.decorators import permission_required
from ..authorization.registry import permission_registry

from .authorization import BoardPostingPermission, BoardTopicPermission
from .formatting import render_html
from .forms import PostingCreateForm, TopicCreateForm
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


@blueprint.route('/categories/<id>')
@templated
def category_view(id):
    """List latest topics in the category."""
    category = Category.query.get_or_404(id)

    topics = Topic.query \
        .filter_by(category=category) \
        .order_by(Topic.pinned.desc(), Topic.last_updated_at.desc()) \
        .all()

    return {
        'category': category,
        'topics': topics,
    }


# -------------------------------------------------------------------- #
# topic


@blueprint.route('/topics/<id>')
@templated
def topic_view(id):
    """List postings for the topic."""
    topic = Topic.query.get_or_404(id)

    if topic.locked:
        flash_notice(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.')

    return {'topic': topic}


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
    author = g.current_user
    title = form.title.data.strip()
    body = form.body.data.strip()

    topic = Topic.create(category, author, title, body)

    flash_success('Das Thema wurde hinzugefügt.')
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

    flash_success('Das Thema "{}" wurde versteckt.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


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
        'Das Thema "{}" wurde wieder sichtbar gemacht.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


@blueprint.route('/topics/<id>/flags/locked', methods=['POST'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_lock(id):
    """Lock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.locked = True
    topic.locked_by = g.current_user
    db.session.commit()

    flash_success('Das Thema "{}" wurde geschlossen.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


@blueprint.route('/topics/<id>/flags/locked', methods=['DELETE'])
@permission_required(BoardTopicPermission.lock)
@respond_no_content_with_location
def topic_unlock(id):
    """Unlock a topic."""
    topic = Topic.query.get_or_404(id)
    topic.locked = False
    topic.locked_by = None
    db.session.commit()

    flash_success(
        'Das Thema "{}" wurde wieder geöffnet.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


@blueprint.route('/topics/<id>/flags/pinned', methods=['POST'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_pin(id):
    """Pin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.pinned = True
    topic.pinned_by = g.current_user
    db.session.commit()

    flash_success('Das Thema "{}" wurde angepinnt.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


@blueprint.route('/topics/<id>/flags/pinned', methods=['DELETE'])
@permission_required(BoardTopicPermission.pin)
@respond_no_content_with_location
def topic_unpin(id):
    """Unpin a topic."""
    topic = Topic.query.get_or_404(id)
    topic.pinned = False
    topic.pinned_by = None
    db.session.commit()

    flash_success(
        'Das Thema "{}" wurde wieder gelöst.'.format(topic.title))
    anchor = 'topic-{}'.format(topic.id)
    return url_for('.category_view', id=topic.category.id, _anchor=anchor)


# -------------------------------------------------------------------- #
# posting


@blueprint.route('/topics/<topic_id>/create')
@permission_required(BoardPostingPermission.create)
@templated
def posting_create_form(topic_id, errorneous_form=None):
    """Show a form to create a posting to the topic."""
    topic = Topic.query.get_or_404(topic_id)
    form = errorneous_form if errorneous_form else PostingCreateForm()
    return {
        'topic': topic,
        'form': form,
    }


@blueprint.route('/topics/<topic_id>/create', methods=['POST'])
@permission_required(BoardPostingPermission.create)
def posting_create(topic_id):
    """Create a posting to the topic."""
    form = PostingCreateForm(request.form)

    topic = Topic.query.get_or_404(topic_id)
    author = g.current_user
    body = form.body.data.strip()

    if topic.locked:
        flash_error(
            'Das Thema ist geschlossen. '
            'Es können keine Beiträge mehr hinzugefügt werden.')
        return redirect_to('.topic_view', id=topic.id)

    posting = Posting.create(topic, author, body)

    flash_success('Deine Antwort wurde hinzugefügt.')
    return redirect_to('.topic_view', id=topic.id)


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

    flash_success('Der Beitrag wurde versteckt.')
    anchor = 'posting-{}'.format(posting.id)
    return url_for('.topic_view', id=posting.topic.id, _anchor=anchor)


@blueprint.route('/postings/<id>/flags/hidden', methods=['DELETE'])
@permission_required(BoardPostingPermission.hide)
@respond_no_content_with_location
def posting_unhide(id):
    """Un-hide a posting."""
    posting = Posting.query.get_or_404(id)
    posting.hidden = False
    posting.hidden_by = None
    db.session.commit()

    flash_success('Der Beitrag wurde wieder sichtbar gemacht.')
    anchor = 'posting-{}'.format(posting.id)
    return url_for('.topic_view', id=posting.topic.id, _anchor=anchor)
