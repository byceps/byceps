babel-extract:
    pybabel extract -F babel.cfg -k lazy_gettext -k lazy_pgettext -o messages.pot . && pybabel update -i messages.pot -d byceps/translations

babel-compile:
    pybabel compile -d byceps/translations
