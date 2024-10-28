_default:
    @just --list

babel-extract:
    pybabel extract -F babel.cfg -k lazy_gettext -k lazy_ngettext -k lazy_pgettext -k lazy_npgettext -o messages.pot . && pybabel update --ignore-pot-creation-date -i messages.pot -d byceps/translations

babel-init locale:
    pybabel init -i messages.pot -d byceps/translations -l {{locale}}

babel-compile:
    pybabel compile -d byceps/translations

export-requirements-core:
    uv export --format requirements-txt --frozen --quiet --output-file requirements/core.txt

export-requirements-dev:
    uv export --format requirements-txt --frozen --quiet --only-group dev --output-file requirements/dev.txt

export-requirements-docs:
    uv export --format requirements-txt --frozen --quiet --only-group docs --output-file requirements/docs.txt

export-requirements-test:
    uv export --format requirements-txt --frozen --quiet --only-group test --output-file requirements/test.txt
