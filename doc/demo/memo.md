# Record Demo
```bash
# start record
asciinema rec doc/demo/demo.cast

# demo operations
#...

# end record
exit
```

# Convert to SVG

```bash
cat doc/demo/demo.cast | svg-term --window --width 120 --height 30 --out doc/demo/demo.svg
```
