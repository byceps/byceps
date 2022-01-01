"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from freezegun import freeze_time
import pytest

from byceps.services.shop.order.email import example_service

from tests.helpers import current_user_set

from .helpers import get_current_user_for_user


ORDER_PLACED_AT = '2021-10-12 12:34:56'


@freeze_time(ORDER_PLACED_AT)
@pytest.mark.parametrize(
    'locale, expected',
    [
        (
            'de',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: Deine Bestellung (AWSM-ORDR-9247) ist eingegangen.


Hallo Orderer,

vielen Dank für deine Bestellung mit der Nummer AWSM-ORDR-9247 am 12.10.2021 über unsere Website.

Folgende Artikel hast du bestellt:

  Gesamtbetrag: 42,95\xa0€

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AWSM-ORDR-9247

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
        (
            'en',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: Your order (AWSM-ORDR-9247) has been received.


Hello Orderer,

thank you for your order AWSM-ORDR-9247 on Oct 12, 2021 through our website.

You have ordered these items:

  Total amount: €42.95

Bitte überweise den Gesamtbetrag auf folgendes Konto:

  Zahlungsempfänger: <Name>
  IBAN: <IBAN>
  BIC: <BIC>
  Bank: <Kreditinstitut>
  Verwendungszweck: AWSM-ORDR-9247

Wir werden dich informieren, sobald wir deine Zahlung erhalten haben.

Hier kannst du deine Bestellungen einsehen: https://www.acmecon.test/shop/orders

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
    ],
)
def test_example_placed_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
    locale,
    expected,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin, locale)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_placed_order_message_text(
            shop.id, locale
        )

    assert actual == expected


@freeze_time(ORDER_PLACED_AT)
@pytest.mark.parametrize(
    'locale, expected',
    [
        (
            'de',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: ✅ Deine Bestellung (AWSM-ORDR-9247) ist bezahlt worden.


Hallo Orderer,

vielen Dank für deine Bestellung mit der Nummer AWSM-ORDR-9247 am 12.10.2021 über unsere Website.

Wir haben deine Zahlung erhalten und deine Bestellung als bezahlt markiert.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
        (
            'en',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: ✅ Your order (AWSM-ORDR-9247) has been paid.


Hello Orderer,

thank you for your order AWSM-ORDR-9247 on Oct 12, 2021 through our website.

We have received your payment and have marked your order as paid.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
    ],
)
def test_example_paid_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
    locale,
    expected,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin, locale)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_paid_order_message_text(
            shop.id, locale
        )

    assert actual == expected


@freeze_time(ORDER_PLACED_AT)
@pytest.mark.parametrize(
    'locale, expected',
    [
        (
            'de',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: ❌ Deine Bestellung (AWSM-ORDR-9247) ist storniert worden.


Hallo Orderer,

deine Bestellung mit der Nummer AWSM-ORDR-9247 vom 12.10.2021 wurde von uns aus folgendem Grund storniert:

Kein fristgerechter Geldeingang feststellbar.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
        (
            'en',
            '''\
From: NameAndAddress(name=None, address='noreply@acmecon.test')
To: ['orderer@example.com']
Subject: ❌ Your order (AWSM-ORDR-9247) has been canceled.


Hello Orderer,

your order AWSM-ORDR-9247 on Oct 12, 2021 has been canceled by us for this reason:

Kein fristgerechter Geldeingang feststellbar.

Für Fragen stehen wir gerne zur Verfügung.

Viele Grüße,
das Team der Acme Entertainment Convention

-- 
Acme Entertainment Convention

E-Mail: noreply@acmecon.test
''',
        ),
    ],
)
def test_example_canceled_order_message_text(
    admin_app,
    order_admin,
    shop,
    email_payment_instructions_snippet_id,
    email_footer_snippet_id,
    locale,
    expected,
):
    app = admin_app
    current_user = get_current_user_for_user(order_admin, locale)

    with current_user_set(app, current_user), app.app_context():
        actual = example_service.build_example_canceled_order_message_text(
            shop.id, locale
        )

    assert actual == expected
