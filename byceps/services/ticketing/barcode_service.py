"""
byceps.services.ticketing.barcode_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Render Code 128 (set B) barcodes as SVG images.

This implementation only supports code set B.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from jinja2 import Template


# As seen on https://en.wikipedia.org/wiki/Code_128#Bar_code_widths
#
# (Value, 128B,      Widths)
VALUES_CHARS_WIDTHS = [
    (  0, ' ',       '212222' ),
    (  1, '!',       '222122' ),
    (  2, '"',       '222221' ),
    (  3, '#',       '121223' ),
    (  4, '$',       '121322' ),
    (  5, '%',       '131222' ),
    (  6, '&',       '122213' ),
    (  7, '\'',      '122312' ),
    (  8, '(',       '132212' ),
    (  9, ')',       '221213' ),
    ( 10, '*',       '221312' ),
    ( 11, '+',       '231212' ),
    ( 12, ',',       '112232' ),
    ( 13, '-',       '122132' ),
    ( 14, '.',       '122231' ),
    ( 15, '/',       '113222' ),
    ( 16, '0',       '123122' ),
    ( 17, '1',       '123221' ),
    ( 18, '2',       '223211' ),
    ( 19, '3',       '221132' ),
    ( 20, '4',       '221231' ),
    ( 21, '5',       '213212' ),
    ( 22, '6',       '223112' ),
    ( 23, '7',       '312131' ),
    ( 24, '8',       '311222' ),
    ( 25, '9',       '321122' ),
    ( 26, ':',       '321221' ),
    ( 27, ';',       '312212' ),
    ( 28, '<',       '322112' ),
    ( 29, '=',       '322211' ),
    ( 30, '>',       '212123' ),
    ( 31, '?',       '212321' ),
    ( 32, '@',       '232121' ),
    ( 33, 'A',       '111323' ),
    ( 34, 'B',       '131123' ),
    ( 35, 'C',       '131321' ),
    ( 36, 'D',       '112313' ),
    ( 37, 'E',       '132113' ),
    ( 38, 'F',       '132311' ),
    ( 39, 'G',       '211313' ),
    ( 40, 'H',       '231113' ),
    ( 41, 'I',       '231311' ),
    ( 42, 'J',       '112133' ),
    ( 43, 'K',       '112331' ),
    ( 44, 'L',       '132131' ),
    ( 45, 'M',       '113123' ),
    ( 46, 'N',       '113321' ),
    ( 47, 'O',       '133121' ),
    ( 48, 'P',       '313121' ),
    ( 49, 'Q',       '211331' ),
    ( 50, 'R',       '231131' ),
    ( 51, 'S',       '213113' ),
    ( 52, 'T',       '213311' ),
    ( 53, 'U',       '213131' ),
    ( 54, 'V',       '311123' ),
    ( 55, 'W',       '311321' ),
    ( 56, 'X',       '331121' ),
    ( 57, 'Y',       '312113' ),
    ( 58, 'Z',       '312311' ),
    ( 59, '[',       '332111' ),
    ( 60, '\\',      '314111' ),
    ( 61, ']',       '221411' ),
    ( 62, '^',       '431111' ),
    ( 63, '_',       '111224' ),
    ( 64, '`',       '111422' ),
    ( 65, 'a',       '121124' ),
    ( 66, 'b',       '121421' ),
    ( 67, 'c',       '141122' ),
    ( 68, 'd',       '141221' ),
    ( 69, 'e',       '112214' ),
    ( 70, 'f',       '112412' ),
    ( 71, 'g',       '122114' ),
    ( 72, 'h',       '122411' ),
    ( 73, 'i',       '142112' ),
    ( 74, 'j',       '142211' ),
    ( 75, 'k',       '241211' ),
    ( 76, 'l',       '221114' ),
    ( 77, 'm',       '413111' ),
    ( 78, 'n',       '241112' ),
    ( 79, 'o',       '134111' ),
    ( 80, 'p',       '111242' ),
    ( 81, 'q',       '121142' ),
    ( 82, 'r',       '121241' ),
    ( 83, 's',       '114212' ),
    ( 84, 't',       '124112' ),
    ( 85, 'u',       '124211' ),
    ( 86, 'v',       '411212' ),
    ( 87, 'w',       '421112' ),
    ( 88, 'x',       '421211' ),
    ( 89, 'y',       '212141' ),
    ( 90, 'z',       '214121' ),
    ( 91, '{',       '412121' ),
    ( 92, '|',       '111143' ),
    ( 93, '}',       '111341' ),
    ( 94, '~',       '131141' ),
    ( 95, 'DEL',     '114113' ),
    ( 96, 'FNC_3',   '114311' ),
    ( 97, 'FNC_2',   '411113' ),
    ( 98, 'Shift_A', '411311' ),
    ( 99, 'Code_C',  '113141' ),
    (100, 'FNC_4',   '114131' ),
    (101, 'Code_A',  '311141' ),
    (102, 'FNC_1',   '411131' ),
    (103, 'Start_A', '211412' ),
    (104, 'Start_B', '211214' ),
    (105, 'Start_C', '211232' ),
    (106, 'Stop',    '2331112'),
]


VALUES_TO_WIDTHS = {value: width for value, _, width in VALUES_CHARS_WIDTHS}
CHARS_TO_VALUES = {char: value for value, char, _ in VALUES_CHARS_WIDTHS}


SVG_TEMPLATE = Template(
    '''
<svg xmlns="http://www.w3.org/2000/svg" width="{{ image_width }}" height="{{ image_height }}" viewBox="0 0 {{ image_width }} {{ image_height }}">
  <rect width="{{ image_width }}" height="{{ image_height }}" fill="white"/>
  {%- for bar_x, bar_width in bars %}
  <rect x="{{ bar_x }}" width="{{ bar_width }}" height="{{ image_height }}"/>
  {%- endfor %}
</svg>
'''.strip()
)


def render_svg(text, *, thickness=3):
    values = list(_generate_values(text))
    bar_widths = list(_generate_bars(values, thickness))
    return _generate_svg(bar_widths)


def _generate_values(text):
    check_digit_calculation_values = []

    # start symbol
    start_symbol_value = _to_value('Start_B')
    yield start_symbol_value
    check_digit_calculation_values.append(start_symbol_value)

    text_values = list(map(_to_value, text))
    yield from text_values
    check_digit_calculation_values.extend(text_values)

    # check digit symbol
    check_digit_value = _calculate_check_digit_value(
        check_digit_calculation_values
    )
    yield check_digit_value

    # stop symbol
    stop_symbol_value = _to_value('Stop')
    yield stop_symbol_value


def _to_value(char):
    return CHARS_TO_VALUES[char]


def _calculate_check_digit_value(values):
    # Important: *Both* the start code *and* the
    # first encoded symbol are in position 1.
    symbol_products_sum = sum(
        max(1, position) * value for position, value in enumerate(values)
    )

    return symbol_products_sum % 103


def _generate_bars(values, thickness):
    for value in values:
        for width in VALUES_TO_WIDTHS[value]:
            bar_width = int(width) * thickness
            yield bar_width


def _generate_svg(bar_widths, *, image_height=100):
    image_width = sum(bar_widths)
    x = 0

    # Calculate where the individual bars are positioned
    # horizontally and how wide they are.
    bar_positions_and_widths = list(
        _calculate_bar_positions_and_widths(x, bar_widths)
    )

    # Render template.
    return SVG_TEMPLATE.render(
        image_width=image_width,
        image_height=image_height,
        bars=bar_positions_and_widths,
    )


def _calculate_bar_positions_and_widths(start_x, bar_widths):
    """Yield a (horizontal position, width) pair for each bar."""
    x = start_x

    draw_bar = True
    for width in bar_widths:
        if draw_bar:
            yield x, width

        draw_bar = not draw_bar
        x += width
