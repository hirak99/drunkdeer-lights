# Generate and apply static lighting configs

Examples -

```sh
# Orange-red.
# The "./" can be omitted in both places if this is in path.
./drunk-lights "all ff4100 wasd,numbers,arrows ff4100" | ./drunk-apply

# Orange-red with glowing WASD.
# Color can have an optional ...@[BRIGHTNESS]%.
./drunk-lights "all ff4100@35% wasd ff4100@75% numbers,arrows ff0000@35%" | ./drunk-apply

# Blue-green with brightness 5.
# _b [BRIGHTNESS] controls brightness through the keyboard firmware.
# Value can range between 0 to 9.
./drunk-lights "_b 5 all 0041ff wasd,numbers,arrows 41ff00" | ./drunk-apply

# Default is black.
# So empty string switches evertyhing off.
./drunk-lights "" | ./drunk-apply
# Equivalently setting brightness to zero switches colors off.
./drunk-lights "_b 0" | ./drunk-apply
```
