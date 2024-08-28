#!/bin/python
#
# To use this without root, also add the following in /etc/udev/rules.d/99-custom.rules -
# SUBSYSTEM=="usb", ATTRS{idVendor}=="03f0", ATTRS{idProduct}=="3e41", MODE="0666"

import argparse
import json
import re
import usb.core
import usb.util

# This is the preamble, rest will be computed.
# Note:
# 6th byte is speed, from '00' to '09'.
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
        # print(thisbytes)
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
        # print(interface[0].bEndpointAddress)
        for ep_index in range(interface.bNumEndpoints):
            # print(
            #     f"{interface.bInterfaceNumber} {interface[ep_index].bEndpointAddress}"
            # )
            if interface[ep_index].bEndpointAddress == _IN_ID:
                endpoint_in = interface[ep_index]
            if interface[ep_index].bEndpointAddress == _OUT_ID:
                endpoint_out = interface[ep_index]
        if endpoint_in is not None and endpoint_out is not None:
            return interface.bInterfaceNumber, endpoint_in, endpoint_out
    raise RuntimeError("Endpoint not found in device")


def static_json_iterate(static: list[list[int | list[str]]]):
    for keycode, colors in static:
        assert isinstance(keycode, int)
        assert isinstance(colors, list)
        for color in colors:
            yield (keycode, color)
            keycode += 1


def encode_static(brightness: int, static):
    preamble = _parse_hexdump(_STATIC)[0]
    result = []
    assert 0 <= brightness <= 9
    preamble[7] = brightness
    for keycode, color in static_json_iterate(static):
        if not result or len(result[-1]) >= 16 * 4 - 3:
            result.append(preamble.copy())
        current = result[-1]
        current.append(keycode)
        color_bytes = bytes.fromhex(color)
        assert len(color_bytes) == 3
        current += color_bytes
    for payload in result[2:]:
        if len(payload) <= 16 * 4 - 3:
            payload += b"\xff\x00\x00"
        payload += b"\x00" * (16 * 4 - len(payload))
    return result


def _apply_to_device(brighness: int, static_json: dict[str, str]):
    device = usb.core.find(idVendor=0x352D, idProduct=0x2382)
    if device is None:
        raise RuntimeError("The USB device was not found")
    assert isinstance(device, usb.core.Device)

    config = device.get_active_configuration()

    interface, endpoint_in, endpoint = _find_interface_endpoint(config)

    reattach = False
    if device.is_kernel_driver_active(interface):
        # print("kernel driver is active, detaching")
        device.detach_kernel_driver(interface)
        reattach = True

    bytes_array_to_write = encode_static(brightness=brighness, static=static_json)

    # init_bytes = _parse_hexdump(_INIT)
    # endpoint.write(init_bytes[0])
    # endpoint_in.read(endpoint_in.wMaxPacketSize)

    for bytes_to_write in bytes_array_to_write:
        print(bytes_to_write)
        endpoint.write(bytes_to_write)

        try:
            endpoint_in.read(endpoint_in.wMaxPacketSize)
            print("Read")
        except usb.core.USBTimeoutError:
            print("Timed out")

    if reattach:
        print("Reattaching...")
        usb.util.dispose_resources(device)
        device.attach_kernel_driver(interface)


def main():
    parser = argparse.ArgumentParser(description="DrunkDeer USB driver")
    parser.add_argument(
        "-b",
        "--brightness",
        type=int,
        required=True,
        help="Brightness - 0 to 9; 0 is off",
    )
    parser.add_argument(
        "--color-config",
        type=str,
        help="A file with the json for color.",
    )
    args = parser.parse_args()
    with open(args.color_config) as f:
        static_json = json.load(f)
    _apply_to_device(args.brightness, static_json)


if __name__ == "__main__":
    main()
