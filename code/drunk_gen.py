# Generates a drunkdeer 65 static color config json.
#
# The config can be applied with drunkapply.
#
# Example -
# drunk-gen "_b 9 all ff0000 wasd,numbers,arrows ff4100" | drunk-apply-json

import argparse
import json

from . import constants


def _parse_directives(directives: str):
    tokens = [x.strip() for x in directives.split() if x.strip()]
    index = 0
    while index < len(tokens):
        keygroups = tokens[index]
        index += 1
        argument = tokens[index]
        index += 1
        for keygroup in keygroups.split(","):
            yield (keygroup, argument)


def _generate(directives: str):
    brightness = 9
    key_colors = {x: "000000" for x in constants.G65_KEYNUMS}
    for command, argument in _parse_directives(directives):
        if command == "_b":
            brightness = int(argument)
            continue
        if command == "all":
            keys = list(key_colors.keys())
        else:
            keys = constants.G65_KEYGROUPS[command]
        for key in keys:
            key_colors[key] = argument
    lastkey = 0

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
