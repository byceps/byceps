_default:
    @just --list

babel-extract:
    pybabel extract -F babel.cfg -k lazy_gettext -k lazy_ngettext -k lazy_pgettext -k lazy_npgettext -o messages.pot . && pybabel update -i messages.pot -d byceps/translations

babel-compile:
    pybabel compile -d byceps/translations
