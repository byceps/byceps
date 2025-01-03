_default:
    @just --list

babel-extract:
    pybabel extract -F babel.cfg -k lazy_gettext -k lazy_ngettext -k lazy_pgettext -k lazy_npgettext -o messages.pot . && pybabel update --ignore-pot-creation-date -i messages.pot -d byceps/translations

babel-init locale:
    pybabel init -i messages.pot -d byceps/translations -l {{locale}}

babel-compile:
    pybabel compile -d byceps/translations

export-requirements-core:
    uv export --format requirements-txt --frozen --no-header --quiet --output-file requirements/core.txt --no-emit-project --no-dev
