# To use this without root, also add the following in /etc/udev/rules.d/99-custom.rules -
# SUBSYSTEM=="usb", ATTRS{idVendor}=="03f0", ATTRS{idProduct}=="3e41", MODE="0666"

import argparse
import json
import re
import sys
import usb.core
import usb.util

from . import constants

# This is the preamble, rest will be computed.
# Note:
# 6th byte is speed, from '00' to '09' - not used for static.
# 7th byte is brightness, from '00' to '09'.
_STATIC = """
0040   04 ae 01 00 00 13 06 09 ff
"""

def _parse_hexdump(hexdump: str) -> list[bytearray]:
    array: list[bytearray] = [bytearray()]
    for line in hexdump.splitlines():
        line = line.strip()
        if not line:
            array.append(bytearray())
            continue
        m = re.fullmatch(r"^\d{4}\s+(?P<bytes>.*)", line)
        thisbytes = m.group("bytes")
        array[-1].extend(bytes.fromhex(thisbytes.replace(" ", "")))
    return [x for x in array if len(x) > 0]


_IN_ID = 0x82
_OUT_ID = 0x03


def _find_interface_endpoint(
    configuration: usb.core.Configuration,
) -> tuple[int, int, int]:
    for interface in configuration.interfaces():
        endpoint_in = None
        endpoint_out = None
        for ep_index in range(interface.bNumEndpoints):
            if interface[ep_index].bEndpointAddress == _IN_ID:
                endpoint_in = interface[ep_index]
            if interface[ep_index].bEndpointAddress == _OUT_ID:
                endpoint_out = interface[ep_index]
        if endpoint_in is not None and endpoint_out is not None:
            return interface.bInterfaceNumber, endpoint_in, endpoint_out
    raise RuntimeError("Endpoint not found in device")


def _apply_bytes_array(bytes_array_to_write: list[bytearray]):
    device = usb.core.find(idVendor=0x352D, idProduct=0x2382)
    if device is None:
        raise RuntimeError("The USB device was not found")
    assert isinstance(device, usb.core.Device)

    config = device.get_active_configuration()

    interface, endpoint_in, endpoint = _find_interface_endpoint(config)

    reattach = False
    if device.is_kernel_driver_active(interface):
        print("kernel driver is active, detaching")
        device.detach_kernel_driver(interface)
        reattach = True

    try:
        for bytes_to_write in bytes_array_to_write:
            endpoint.write(bytes_to_write)

            try:
                endpoint_in.read(endpoint_in.wMaxPacketSize)
            except usb.core.USBTimeoutError:
                print("Read timed out")
    finally:
        if reattach:
            print("Reattaching...")
            usb.util.dispose_resources(device)
            device.attach_kernel_driver(interface)


def _static_json_iterate(static: list[list[int | list[str]]]):
    for keycode, colors in static:
        assert isinstance(keycode, int)
        assert isinstance(colors, list)
        for color in colors:
            yield (keycode, color)
            keycode += 1


def _encode_static(brightness: int, static):
    preamble = _parse_hexdump(_STATIC)[0]
    result = []
    assert 0 <= brightness <= 9
    preamble[7] = brightness
    keycodes_found: set[int] = set()
    for keycode, color in _static_json_iterate(static):
        keycodes_found.add(keycode)
        if not result or len(result[-1]) >= 16 * 4 - 3:
            result.append(preamble.copy())
        current = result[-1]
        current.append(keycode)
        color_bytes = bytes.fromhex(color)
        assert len(color_bytes) == 3
        current += color_bytes
    unexpected_keycodes = keycodes_found - constants.G65_KEYNUMS
    if unexpected_keycodes:
        raise RuntimeError(f"Unknown keycodes: {sorted(unexpected_keycodes)}")
    for payload in result[2:]:
        if len(payload) <= 16 * 4 - 3:
            payload += b"\xff\x00\x00"
        payload += b"\x00" * (16 * 4 - len(payload))
    return result


def _apply(brighness: int, static_json: dict[str, str]):
    bytes_array_to_write = _encode_static(brightness=brighness, static=static_json)
    _apply_bytes_array(bytes_array_to_write)


def main():
    if len(sys.argv) > 2:
        raise ValueError("Need only one argument, the name of a json file.")

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            parsed_json = json.load(f)
    else:
        parsed_json = json.loads(sys.stdin.read())

    _apply(parsed_json["bright"], parsed_json["colors"])


if __name__ == "__main__":
    main()
