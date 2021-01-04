# Nintendo darc tool
![Python](https://img.shields.io/badge/Python-2.7-blue)

The "darc" file format was found in the early version of Nintendo Ware for CTR (nw4c).

This tool can help you extract existing darc files and create new darc files.

# Usage samples
Extract "input.arc" to "output" folder:

``` shell
python darc.py -xf input.arc -d output
```

Change directory to "input/" and add entries recursively to "output.arc":
``` shell
python darc.py -cf output.arc -d input dirs files ...
```

Create darc with all file data align to 32:
``` shell
python darc.py -c -a 0x20 -f output.arc -d input dirs files ...
```

Create darc with *.bcfnt files data align to 128, other files align to 32:
``` shell
python darc.py -c -a 0x20 -t *.bcfnt:0x80 -f output.arc -d input dirs files ...
```

# Notes
By default, this tool creates archives without the "." entry, which is commonly found in many games.
If you need that entry, you just need to add a "." as the input entry. For example:
``` shell
python darc.py -c -f output.arc -d input .
```
Note that there's a dot at the end of the command