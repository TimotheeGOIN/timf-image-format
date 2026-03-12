
"""
This file contains some functions that are used in the converter.py and the timf_visualizer.py files.
Those are basic functions.
"""

def rgba_to_hex(rgba: tuple[int, int, int, int]) -> str:
    """ Convert RGBA color to HEX format.
    Explanation of {:02x}:
    - the ':' indicates the start of the format specifier.
    - the '0' means to pad with zeros if the number is less than 2 digits.
    - the '2' means to use at least 2 digits.
    - the 'x' means to format the number as hexadecimal.
    Returns ex: #rrggbb and if alpha is not 255, #rrggbbaa
    So #rrggbb means #rrggbbaa with aa = ff (full opacity)
    :return: An hexadecimal value as a str. The format is #rrggbbaa (or #rrggbb if alpha is 255)

    """

    hex_color = "#{:02x}{:02x}{:02x}".format(rgba[0], rgba[1], rgba[2])

    if rgba[3] != 255: # If alpha is not fully opaque, include it in the hex
        hex_color += "{:02x}".format(rgba[3])

    return hex_color


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """ Convert HEX color to RGBA format.
    :return: An integer tuple (r, g, b, a), the RGBA color.
    """

    # cut out the # in the left part of the hex string
    hex_color = hex_color.lstrip('#')

    # if the hex str doesn't contain the alpha value, it's only 6 chars long
    if len(hex_color) == 6:
        hex_color += 'ff'  # so we do explicit the full opacity

    r, g, b, a = hex_color[0:2], hex_color[2:4], hex_color[4:6], hex_color[6:8]
    # convert each color value in decimal from hex with the int(hex, 16)
    rgba = (int(r, 16), int(g, 16), int(b, 16), int(a, 16))

    return rgba


def format_hex_for_timf(hex_value: str) -> str: # find a name for my file format
    """ This function formats a hex value to the format used in .timf files.
    This consists of removing the # and explicit the alpha value.
    :return: A clean str, for example, #rrggbb -> rrggbbaa.
    """

    # remove the # in the hex str
    formatted_hex = hex_value.lstrip('#')

    # explicit the alpha value if not already in the hex str (fully opaque case)
    if len(formatted_hex) == 6:
        formatted_hex += "ff"

    return formatted_hex
