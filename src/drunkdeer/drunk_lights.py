# Generates a drunkdeer 65 static color config json.
#
# The config can be applied with drunk_apply.

import argparse
import json

from . import constants


def _parse_directives(directives: str):
    tokens = [x.strip() for x in directives.split() if x.strip()]
    if len(tokens) % 2 != 0:
        raise ValueError("Directives must come in pairs: group color [group color ...]")
    index = 0
    while index < len(tokens):
        keygroups = tokens[index]
        index += 1
        argument = tokens[index]
        index += 1
        for keygroup in keygroups.split(","):
            yield (keygroup, argument)


def _adjust_brightness(color: str, brightness: float) -> str:
    if not len(color) == 6:
        raise ValueError(f"Color is {color=}, but must be of length 6, e.g. ff4100.")
    values = (brightness * int(color[2 * n : 2 * n + 2], 16) for n in range(3))
    values = (max(0, min(255, int(x + 0.5))) for x in values)
    return "".join(f"{x:02x}" for x in values)


def _get_rgb_color(color: str) -> str:
    brightness = 1
    if "@" in color:
        color, brightness = color.split("@")
        if not brightness.endswith("%"):
            raise ValueError("Color brightness must be percentage, e.g. ff4100@50%")
        brightness = float(brightness[:-1]) / 100
    return _adjust_brightness(color, brightness)


def _generate(directives: str):
    brightness = 9
    key_colors = dict.fromkeys(constants.G65_KEYNUMS, "000000")
    for command, argument in _parse_directives(directives):
        if command == "_b":
            brightness = int(argument)
            continue
        if command == "all":
            keys = list(key_colors.keys())
        else:
            keys = constants.G65_KEYGROUPS[command]
        for key in keys:
            key_colors[key] = _get_rgb_color(argument)

    # Generate json.
    color_json: list[tuple[int, list[str]]] = []
    next_keynum = -1
    for keynum, argument in sorted(key_colors.items()):
        if next_keynum != keynum:
            next_keynum = keynum
            color_json.append((keynum, []))
        color_json[-1][-1].append(argument)
        next_keynum += 1
    print(json.dumps({"bright": brightness, "colors": color_json}))


def main():
    parser = argparse.ArgumentParser("DrunkDeer 65 static config generator")
    parser.add_argument("directives")
    directives: str = parser.parse_args().directives
    _generate(directives)


if __name__ == "__main__":
    main()
