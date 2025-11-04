"""
byceps.config.parser
~~~~~~~~~~~~~~~~~~~~

Configuration parser

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

import rtoml

from byceps.util.result import Err, Ok, Result

from .models import (
    AdminAppConfig,
    ApiAppConfig,
    AppsConfig,
    BycepsConfig,
    DatabaseConfig,
    DevelopmentConfig,
    DiscordConfig,
    InvoiceNinjaConfig,
    JobsConfig,
    MetricsConfig,
    PaymentGatewaysConfig,
    PaypalConfig,
    RedisConfig,
    SiteAppConfig,
    SmtpConfig,
    StripeConfig,
    TurnstileConfig,
)
from .util import find_duplicate_server_names, iterate_app_configs


Data = dict[str, Any]

C = TypeVar('C')
T = TypeVar('T')

ParsingResult = Result[T, list[str]]

Value = bool | int | str

ValueType = Enum('ValueType', ['Boolean', 'Integer', 'String'])

CollectionType = Enum('CollectionType', ['List'])

Validator = Callable[[C], ParsingResult[None]]


@dataclass(frozen=True, kw_only=True, slots=True)
class Section:
    name: str
    fields: list[Field]
    config_class: type[C]
    required: bool
    collection_type: CollectionType | None = None
    default: C | None = None
    subsections: list[Subsection] = dataclass_field(default_factory=list)
    validator: Validator | None = None


@dataclass(frozen=True, slots=True)
class Field:
    key: str
    type_: ValueType = ValueType.String
    required: bool = True
    default: Value | None = None


@dataclass(frozen=True, slots=True)
class Subsection:
    section: Section
    collection_type: CollectionType | None = None


def _validate_apps_config(apps_config: AppsConfig) -> ParsingResult[None]:
    app_configs = list(iterate_app_configs(apps_config))
    if not app_configs:
        return Err(['No applications configured'])

    duplicate_server_names = find_duplicate_server_names(apps_config)
    if duplicate_server_names:
        server_names_str = ', '.join(sorted(duplicate_server_names))
        return Err([f'Non-unique server names configured: {server_names_str}'])

    return Ok(None)


_TOPLEVEL_FIELDS = [
    Field('locale', required=True),
    Field('propagate_exceptions', required=False, default=None),
    Field('secret_key', required=True),
    Field('timezone', required=True),
]


_SECTION_DEFINITIONS = [
    Section(
        name='apps',
        subsections=[
            Subsection(
                Section(
                    name='admin',
                    fields=[
                        Field('server_name', required=True),
                    ],
                    config_class=AdminAppConfig,
                    required=False,
                    default=None,
                ),
            ),
            Subsection(
                Section(
                    name='api',
                    fields=[
                        Field('server_name', required=True),
                    ],
                    config_class=ApiAppConfig,
                    required=False,
                    default=None,
                ),
            ),
            Subsection(
                Section(
                    name='sites',
                    fields=[
                        Field('server_name', required=True),
                        Field('site_id', required=True),
                    ],
                    config_class=SiteAppConfig,
                    collection_type=CollectionType.List,
                    required=False,
                ),
                collection_type=CollectionType.List,
            ),
        ],
        fields=[],
        config_class=AppsConfig,
        required=True,
        validator=_validate_apps_config,
    ),
    Section(
        name='database',
        fields=[
            Field('host', required=False, default='localhost'),
            Field(
                'port', required=False, type_=ValueType.Integer, default=5432
            ),
            Field('username', required=True),
            Field('password', required=True),
            Field('database', required=True),
        ],
        config_class=DatabaseConfig,
        required=True,
    ),
    Section(
        name='development',
        fields=[
            Field(
                'style_guide_enabled',
                type_=ValueType.Boolean,
                required=False,
                default=False,
            ),
            Field(
                'toolbar_enabled',
                type_=ValueType.Boolean,
                required=False,
                default=False,
            ),
        ],
        config_class=DevelopmentConfig,
        required=False,
        default=DevelopmentConfig(
            style_guide_enabled=False,
            toolbar_enabled=False,
        ),
    ),
    Section(
        name='discord',
        fields=[
            Field('enabled', type_=ValueType.Boolean, required=True),
            Field('client_id', required=True),
            Field('client_secret', required=True),
        ],
        config_class=DiscordConfig,
        required=False,
    ),
    Section(
        name='invoiceninja',
        fields=[
            Field('enabled', type_=ValueType.Boolean, required=True),
            Field('base_url', required=True),
            Field('api_key', required=True),
        ],
        config_class=InvoiceNinjaConfig,
        required=False,
    ),
    Section(
        name='jobs',
        fields=[
            Field('asynchronous', type_=ValueType.Boolean, required=True),
        ],
        config_class=JobsConfig,
        required=False,
        default=JobsConfig(
            asynchronous=True,
        ),
    ),
    Section(
        name='metrics',
        fields=[
            Field('enabled', type_=ValueType.Boolean, required=True),
        ],
        config_class=MetricsConfig,
        required=False,
        default=MetricsConfig(
            enabled=False,
        ),
    ),
    Section(
        name='payment_gateways',
        subsections=[
            Subsection(
                Section(
                    name='paypal',
                    fields=[
                        Field(
                            'enabled', type_=ValueType.Boolean, required=True
                        ),
                        Field('client_id', required=True),
                        Field('client_secret', required=True),
                        Field('environment', required=True),
                    ],
                    config_class=PaypalConfig,
                    required=False,
                    default=None,
                ),
            ),
            Subsection(
                Section(
                    name='stripe',
                    fields=[
                        Field(
                            'enabled', type_=ValueType.Boolean, required=True
                        ),
                        Field('secret_key', required=True),
                        Field('publishable_key', required=True),
                        Field('webhook_secret', required=True),
                    ],
                    config_class=StripeConfig,
                    required=False,
                ),
            ),
        ],
        fields=[],
        config_class=PaymentGatewaysConfig,
        required=False,
        default=PaymentGatewaysConfig(
            paypal=None,
            stripe=None,
        ),
    ),
    Section(
        name='redis',
        fields=[
            Field('url', required=True),
        ],
        config_class=RedisConfig,
        required=True,
    ),
    Section(
        name='smtp',
        fields=[
            Field('host', required=False, default='localhost'),
            Field('port', type_=ValueType.Integer, required=False, default=25),
            Field(
                'starttls',
                type_=ValueType.Boolean,
                required=False,
                default=False,
            ),
            Field(
                'use_ssl',
                type_=ValueType.Boolean,
                required=False,
                default=False,
            ),
            Field('username', required=False, default=''),
            Field('password', required=False, default=''),
            Field(
                'suppress_send',
                type_=ValueType.Boolean,
                required=False,
                default=False,
            ),
        ],
        config_class=SmtpConfig,
        required=True,
    ),
    # --- NEU: Cloudflare Turnstile (optional, default: disabled) ---
    Section(
        name='turnstile',
        fields=[
            Field('enabled', type_=ValueType.Boolean, required=False, default=False),
            # Wenn enabled=false, sind Strings egal; wir setzen leere Defaults,
            # damit der Parser nicht meckert, wenn die Keys fehlen.
            Field('sitekey', required=False, default=''),
            Field('secret',  required=False, default=''),
        ],
        config_class=TurnstileConfig,
        required=False,
        default=TurnstileConfig(
            enabled=False,
            sitekey='',
            secret='',
        ),
    ),
]


def parse_config(toml: str) -> ParsingResult[BycepsConfig]:
    """Parse configuration in TOML format."""
    data = rtoml.loads(toml)
    return _parse_config_dict(data)


def _parse_config_dict(data: Data) -> ParsingResult[BycepsConfig]:
    """Parse configuration from dictionary."""
    entries: Data = {}
    errors: list[str] = []

    for field in _TOPLEVEL_FIELDS:
        result: Result[Data | Value | None, str]
        if field.required:
            result = _get_required_value(data, field.key)
        else:
            result = _get_optional_value(data, field.key, field.default)

        match result:
            case Ok(toplevel_value):
                entries[field.key] = toplevel_value
            case Err(toplevel_err):
                errors.append(toplevel_err)

    for section in _SECTION_DEFINITIONS:
        match _parse_section(data, section):
            case Ok(section_value):
                entries[section.name] = section_value
            case Err(section_err):
                if isinstance(section_err, list):
                    errors.extend(section_err)
                else:
                    errors.append(section_err)

    if errors:
        return Err(errors)

    entries['data_path'] = Path('./data')
    entries['testing'] = False

    config = BycepsConfig(**entries)
    return Ok(config)


def _parse_section(data: Data, section: Section) -> ParsingResult[T | None]:
    def parse(section_data: Data) -> ParsingResult[C]:
        return _parse_section_fields(
            section_data,
            section.name,
            section.fields,
            section.subsections,
            section.config_class,
            section.validator,
        )

    if section.required:
        return _parse_required_section(data, section, parse)
    else:
        return _parse_optional_section(data, section, parse)


def _parse_required_section(
    data: Data,
    section: Section,
    parse: Callable[[Data], ParsingResult[T]],
) -> ParsingResult[T]:
    key = section.name
    return (
        _get_required_value(data, key)
        .map_err(lambda _: f'Section "{key}" missing')
        .map_err(lambda x: [x])
        .and_then(parse)
    )


def _parse_optional_section(
    data: Data,
    section: Section,
    parse: Callable[[Data], ParsingResult[T | None]],
) -> ParsingResult[T | None]:
    key = section.name

    section_data = data.get(key, None)

    if section_data is None:
        if section.default:
            return Ok(section.default)
        else:
            return Ok(None)

    return parse(section_data)


def _parse_section_fields(
    section_data: Data,
    section_name: str,
    fields: list[Field],
    subsections: list[Subsection],
    config_class: type[C],
    validator: Validator[C] | None,
) -> ParsingResult[C]:
    entries: Data = {}
    errors: list[str] = []

    for field in fields:
        section_value = _get_section_value(
            section_data,
            section_name,
            field.key,
            field.type_,
            default=field.default,
        )
        match section_value:
            case Ok(value):
                entries[field.key] = value
            case Err(err):
                errors.append(err)

    for subsection in subsections:
        match subsection.collection_type:
            case CollectionType.List:
                key = subsection.section.name
                subsection_data = section_data.get(key)

                if subsection_data is None:
                    entries[key] = []
                    continue

                if not isinstance(subsection_data, list):
                    errors.append(
                        f'Value "{subsection_data!r}" for key "{key}" in section "{section_name}" is not of type list'
                    )
                    continue

                values = []
                for data in subsection_data:
                    match _parse_section({key: data}, subsection.section):
                        case Ok(value):
                            values.append(value)
                        case Err(err):
                            errors.append(err)
                entries[key] = values
            case None:
                match _parse_section(section_data, subsection.section):
                    case Ok(value):
                        entries[subsection.section.name] = value
                    case Err(err):
                        errors.append(err)
            case _:
                raise Exception(
                    f'Invalid value collection type "{subsection.collection_type}"'
                )

    if errors:
        return Err(errors)

    config = config_class(**entries)

    if validator:
        match validator(config):
            case Err(e):
                return Err(e)

    return Ok(config)


def _get_section_value(
    section_data: Data,
    section_name: str,
    key: str,
    type_: ValueType,
    *,
    default: Value | None = None,
) -> Result[Value, str]:
    value = section_data.get(key, default)

    if value is None:
        return Err(f'Key "{key}" missing in section "{section_name}"')

    match type_:
        case ValueType.Boolean:
            if not isinstance(value, bool):
                return Err(
                    f'Value "{value!r}" for key "{key}" in section "{section_name}" is not of type boolean'
                )
        case ValueType.Integer:
            if not isinstance(value, int):
                return Err(
                    f'Value "{value!r}" for key "{key}" in section "{section_name}" is not of type integer'
                )
        case ValueType.String:
            if not isinstance(value, str):
                return Err(
                    f'Value "{value!r}" for key "{key}" in section "{section_name}" is not of type string'
                )
        case _:
            raise Exception(f'Invalid value type "{type_}"')

    return Ok(value)


def _get_required_value(
    data: Data, key: str
) -> Result[Data | Value | None, str]:
    try:
        value = data[key]
    except KeyError:
        return Err(f'Key "{key}" missing')

    return Ok(value)


def _get_optional_value(
    data: Data, key: str, default: Value | None = None
) -> Result[Data | Value | None, str]:
    try:
        value = data.get(key, default)
    except KeyError:
        value = default

    return Ok(value)
