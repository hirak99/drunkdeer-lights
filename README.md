# Generate and apply static lighting configs

Examples -

```sh
# Orange-red.
# The "./" can be omitted in both places if this is in path.
./drunk-lights "all ff4100 wasd,numbers,arrows ff4100" | ./drunk-apply

# Orange-red with glowing WASD.
./drunk-lights "_b 9 all 591700 wasd c93300 numbers,arrows 590000" | ./drunk-apply

# Blue-green with brightness 5.
./drunk-lights "_b 5 all 0041ff wasd,numbers,arrows 41ff00" | ./drunk-apply
```
