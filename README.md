# Save and apply static lighting configs for the DrunkDeer keyboard

DrunkDeer's web driver can't store or switch between lighting setups: changing one means hunting and pecking through the GUI to recreate it. I wanted to swap or revert configs as I try out new color setups.

Since the RGB protocol has no vendor documentation, I reverse-engineered it for the DrunkDeer G65 from USB traffic captured in Wireshark, and wrote this CLI.

Each config is just text you can save as a file or script, then re-apply whenever you like. The Examples below are just such text.

Demo: https://youtu.be/A7czXJXqMb0

## Prerequisites

- Python 3.12+
- pyusb: `pip install pyusb`

## USB Permissions

To use without root, add a udev rule (e.g. in `/etc/udev/rules.d/99-custom.rules`):

```udev
SUBSYSTEM=="usb", ATTRS{idVendor}=="352d", ATTRS{idProduct}=="2382", MODE="0666"
```

Then reload: `sudo udevadm control --reload-rules && sudo udevadm trigger`

## Examples


```sh
# Run from the src/ directory, or add it to your PATH.

# Orange-red with darker red WASD, numbers, and arrows.
# Color can have an optional ...@[BRIGHTNESS]%.
./drunk-lights "all ff4100@75% wasd,numbers,arrows ff0000@35%" | ./drunk-apply

# Blue-green with brightness 5.
# _b [BRIGHTNESS] controls brightness through the keyboard firmware.
# Value can range between 0 to 9.
./drunk-lights "_b 5 all 0041ff wasd,numbers,arrows 41ff00" | ./drunk-apply

# 3-zone gradient.
./drunk-lights "zone1of3 ff7f00 zone2of3 ff4100 zone3of3 ff0000" | ./drunk-apply

# Individual buttons. Note that `arrows` is also included in `zone1of3`.
# The latest assignment takes priority.
./drunk-lights "_b 5 zone1of3 ff7f00 zone2of3 ff4100 zone3of3,caps ff0000 arrows ff4100" | ./drunk-apply

# Default is black.
# So empty string switches everything off.
./drunk-lights "" | ./drunk-apply
# Equivalently setting brightness to zero switches colors off.
./drunk-lights "_b 0" | ./drunk-apply
```
