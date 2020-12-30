# Nintendo darc tool
![Python](https://img.shields.io/badge/Python-2.7-blue)

The "darc" file format was found in the early version of Nintendo Ware for CTR (nw4c).

This tool can help you extract existing darc files and create new darc files.

# Usage samples
Extract "input.arc" to "output" folder:

``` shell
python darc.py -xf input.arc -d output
```

Change directory to "input/" and add "files" folder recursively to "output.arc":
``` shell
python darc.py -cf output.arc -d input files
```

Create darc with all file data align to 32:
``` shell
python darc.py -c -a 0x20 -f output.arc -d input files
```

Create darc with *.bcfnt files data align to 128, other files align to 32:
``` shell
python darc.py -c -a 0x20 -t *.bcfnt:0x80 -f output.arc -d input files
```