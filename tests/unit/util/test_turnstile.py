"""Netsession: tests for the Cloudflare Turnstile verification."""

import io
import json

from flask import Flask
import pytest

from byceps.util import turnstile


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['CLOUDFLARE_TURNSTILE'] = {
        'enabled': True,
        'sitekey': 'site-key',
        'secret_key': 'secret-key',
    }
    return app


def _fake_urlopen(payload, calls):
    def fake_urlopen(req, timeout):
        calls.append(req)
        return io.BytesIO(json.dumps(payload).encode('utf-8'))

    return fake_urlopen


def test_verify_token_asks_cloudflare_and_rejects_invalid_token(app, monkeypatch):
    calls = []
    monkeypatch.setattr(
        turnstile, 'urlopen', _fake_urlopen({'success': False}, calls)
    )

    with app.app_context():
        assert not turnstile.verify_token('bogus')

    assert len(calls) == 1


def test_verify_token_accepts_valid_token(app, monkeypatch):
    calls = []
    monkeypatch.setattr(
        turnstile, 'urlopen', _fake_urlopen({'success': True}, calls)
    )

    with app.app_context():
        assert turnstile.verify_token('valid', expected_action='login')

    assert len(calls) == 1


def test_verify_token_rejects_missing_token(app):
    with app.app_context():
        assert not turnstile.verify_token('')


def test_verify_token_passes_when_disabled(monkeypatch):
    app = Flask(__name__)
    app.config['CLOUDFLARE_TURNSTILE'] = {'enabled': False}
    calls = []
    monkeypatch.setattr(
        turnstile, 'urlopen', _fake_urlopen({'success': False}, calls)
    )

    with app.app_context():
        assert turnstile.verify_token('anything')

    assert calls == []
