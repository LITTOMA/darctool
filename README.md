# 3DS DARCTool
Unpack/repack DARC files for Nintendo3DS

#Platform
Python 2.7</br>
Compression only on WindowsXP+

# Update
Add inject feature.

# Usage
darc.py [option] 'object'</br>  
darc.py [option] -d 'directory'
### options:
* -u [darc file] ........... unpack darcfile</br>
* -i [orign darc file] ..... inject files to specified darc file</br>
* -p [directory] ........... packup specified directory</br>

####unessential option:
* -o [filename] ............ set output file name</br>
* -d [directory] ........... set work directory</br>

####compression:
* -evb ...... VRAM compatible, big-endian (LZ11)</br>
* -ewb ...... WRAM compatbile, big-endian (LZ11)</br>
* -evl ...... VRAM compatible, little-endian (LZ40)</br>
* -ewl ...... WRAM compatbile, little-endian (LZ40)

### How to use "-d" option
There is an example:
![example](http://imglf1.ph.126.net/AmNtRyKlwlwB6SGC60Y-HA==/2198601043187989225.jpg)

### drag & drop:</br>
You can drag & drop darc files to unpack. </br>  
To unpack compressed files by drag & drop, you should place lzx.exe into C:/Windows/</br>  
It dosen't support pack up for now, you must use -p command.

# Notice
This tool hasn't been tested completely, so it may not work in some cases,</br>  
please tell me while errors occur.
