"""
byceps.blueprints.shop_order_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict

from ...services.shop.article.models.article import Article, ArticleNumber
from ...services.shop.article import service as article_service
from ...services.shop.order.models.order import OrderTuple
from ...services.shop.order.models.order_event import OrderEvent, OrderEventData
from ...services.shop.order import service as order_service
from ...services.user.models.user import User, UserTuple
from ...services.user import service as user_service
from ...services.user_badge import service as user_badge_service
from ...typing import UserID


def get_articles_by_item_number(order: OrderTuple
                               ) -> Dict[ArticleNumber, Article]:
    numbers = {item.article_number for item in order.items}

    articles = article_service.get_articles_by_numbers(numbers)

    return {article.item_number: article for article in articles}


def get_events(order_id):
    events = order_service.get_order_events(order_id)

    user_ids = {event.data['initiator_id'] for event in events
                if 'initiator_id' in event.data}
    users = user_service.find_users(user_ids)
    users_by_id = {str(user.id): user for user in users}

    for event in events:
        data = {
            'event': event.event_type,
            'occured_at': event.occured_at,
            'data': event.data,
        }

        if event.event_type == 'badge-awarded':
            additional_data = _provide_additional_data_for_badge_awarded(event)
        elif event.event_type == 'ticket-created':
            additional_data = _provide_additional_data_for_ticket_created(event)
        else:
            additional_data = _provide_additional_data_for_standard_event(
                event, users_by_id)

        data.update(additional_data)

        yield data


def _provide_additional_data_for_standard_event(
        event: OrderEvent, users_by_id: Dict[UserID, UserTuple]
        ) -> OrderEventData:
    initiator_id = event.data['initiator_id']

    return {
        'initiator': users_by_id[initiator_id],
    }


def _provide_additional_data_for_badge_awarded(event: OrderEvent
                                              ) -> OrderEventData:
    badge_id = event.data['badge_id']
    badge = user_badge_service.find_badge(badge_id)

    recipient_id = event.data['recipient_id']
    recipient = user_service.find_user(recipient_id)
    recipient = _to_user_tuple(recipient)

    return {
        'badge_label': badge.label,
        'recipient': recipient,
    }


def _provide_additional_data_for_ticket_created(event: OrderEvent
                                               ) -> OrderEventData:
    ticket_id = event.data['ticket_id']
    ticket_code = event.data['ticket_code']
    category_id = event.data['ticket_category_id']
    owner_id = event.data['ticket_owner_id']

    return {
        'ticket_code': ticket_code,
    }


def _to_user_tuple(user: User) -> UserTuple:
    """Create an immutable tuple with selected values from user entity."""
    avatar_url = user.avatar.url if user.avatar else None
    is_orga = False

    return UserTuple(
        user.id,
        user.screen_name,
        user.deleted,
        avatar_url,
        is_orga,
    )
