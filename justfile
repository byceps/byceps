_default:
    @just --list

babel-extract:
    uv run pybabel extract -F babel.cfg -k lazy_gettext -k lazy_ngettext -k lazy_pgettext -k lazy_npgettext -o messages.pot . && uv run pybabel update --ignore-pot-creation-date -i messages.pot -d byceps/translations

babel-init locale:
    uv run pybabel init -i messages.pot -d byceps/translations -l {{locale}}

babel-compile:
    uv run pybabel compile -d byceps/translations

docs-build-clean:
    cd ./docs && uv run make clean && cd ..

docs-build-html:
    cd ./docs && uv run make html && cd ..
