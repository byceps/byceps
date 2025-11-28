"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.board import board_posting_domain_service
from byceps.services.board.errors import (
    ReactionDeniedError,
    ReactionDoesNotExistError,
    ReactionExistsError,
)
from byceps.services.board.models import PostingID, ReactionKind
from byceps.services.user.models.user import UserID
from byceps.util.result import Ok

from tests.helpers import generate_uuid


def test_add_reaction_success(
    posting_id, posting_creator_id, user, kind: ReactionKind
):
    reaction_exists = False

    result = board_posting_domain_service.add_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert result.is_ok()
    actual = result.unwrap()

    assert actual.id is not None
    assert actual.created_at is not None
    assert actual.posting_id == posting_id
    assert actual.user_id == user.id
    assert actual.kind == kind


def test_add_reaction_reaction_denied_error(
    posting_id, user, kind: ReactionKind
):
    posting_creator_id = user.id
    reaction_exists = False

    actual = board_posting_domain_service.add_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert actual.is_err()
    assert isinstance(actual.unwrap_err(), ReactionDeniedError)


def test_add_reaction_reaction_exists_error(
    posting_id, posting_creator_id, user, kind: ReactionKind
):
    reaction_exists = True

    actual = board_posting_domain_service.add_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert actual.is_err()
    assert isinstance(actual.unwrap_err(), ReactionExistsError)


def test_remove_reaction_success(
    posting_id, posting_creator_id, user, kind: ReactionKind
):
    reaction_exists = True

    actual = board_posting_domain_service.remove_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert actual == Ok(None)


def test_remove_reaction_reaction_denied_error(
    posting_id, user, kind: ReactionKind
):
    posting_creator_id = user.id
    reaction_exists = True

    actual = board_posting_domain_service.remove_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert actual.is_err()
    assert isinstance(actual.unwrap_err(), ReactionDeniedError)


def test_remove_reaction_reaction_does_not_exist_error(
    posting_id, posting_creator_id, user, kind: ReactionKind
):
    reaction_exists = False

    actual = board_posting_domain_service.remove_reaction(
        posting_id, posting_creator_id, user, kind, reaction_exists
    )

    assert actual.is_err()
    assert isinstance(actual.unwrap_err(), ReactionDoesNotExistError)


@pytest.fixture(scope='module')
def posting_id():
    return PostingID(generate_uuid())


@pytest.fixture(scope='module')
def posting_creator_id():
    return UserID(generate_uuid())


@pytest.fixture(scope='module')
def user(make_user):
    return make_user()


@pytest.fixture(scope='module')
def kind() -> ReactionKind:
    return ReactionKind('heart')
