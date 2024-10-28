_default:
    @just --list

babel-extract:
    pybabel extract -F babel.cfg -k lazy_gettext -k lazy_ngettext -k lazy_pgettext -k lazy_npgettext -o messages.pot . && pybabel update --ignore-pot-creation-date -i messages.pot -d byceps/translations

babel-init locale:
    pybabel init -i messages.pot -d byceps/translations -l {{locale}}

babel-compile:
    pybabel compile -d byceps/translations

export-requirements-core:
    uv export --format requirements-txt --frozen --no-header --quiet --output-file requirements/core.txt

export-requirements-dev:
    uv export --format requirements-txt --frozen --no-header --quiet --output-file requirements/dev.txt --only-group dev

export-requirements-docs:
    uv export --format requirements-txt --frozen --no-header --quiet --output-file requirements/docs.txt --only-group docs

export-requirements-test:
    uv export --format requirements-txt --frozen --no-header --quiet --output-file requirements/test.txt --only-group test
