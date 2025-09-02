_default:
    @just --list

babel-extract:
    uv run pybabel extract -F babel.cfg --keywords 'lazy_gettext lazy_ngettext:1,2 lazy_pgettext:1c,2 lazy_npgettext:1c,2,3' -o messages.pot . && uv run pybabel update --ignore-pot-creation-date -i messages.pot -d byceps/translations

babel-init locale:
    uv run pybabel init -i messages.pot -d byceps/translations -l {{locale}}

babel-compile:
    uv run pybabel compile -d byceps/translations

deps-outdated:
    uv tree --all-groups --depth 1 --no-dev --outdated

docs-build-clean:
    cd ./docs && uv run make clean && cd ..

docs-build-html:
    cd ./docs && uv run make html && cd ..
