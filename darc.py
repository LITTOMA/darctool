#darc format
#
### Header ###
#  4 byte  'darc'
#  2 byte  Endianess
#  2 byte  Header's length
#  4 byte  Version(unsure)
#  4 byte  File size
#  4 byte  File table offset
#  4 byte  File table length
#  4 byte  File data offset
#
### File table ###
## if folder ##
#  4 byte  Folder name offset(From the beginning of the name table)
#  4 byte  Index number
#  4 byte  Number of files(Count from the beginning of the file table,3*4 byte is a group.
#          For example,if index number is 0,this value is the number of all groups.)
## if file ##
#  4 byte  File name offset(From the beginning of the name table)
#  4 byte  File offset(From the beginning of the file)
#  4 byte  File size
#
#Files in darc store with padding.
#The darc file compress with LZ11 in some cases.

import os,codecs,sys,struct

def getfilesize(filename):
    file = open(filename,'rb')
    file.seek(0,2)
    fsize = file.tell()
    file.close()
    return fsize

def IsDir(er):
    if (er>16777215):
        return True
    else:
        return False

def mkdir(path):
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

def walk(dirname):
    filelist = []
    for root,dirs,files in os.walk(dirname):
        for filename in files:
            fullname=os.path.join(root,filename)
            filelist.append(fullname)
    return filelist

def getnameinpath(pathlist):
    name = ''
    namelist = []
    i = 0
    for string in pathlist:
        for char in string:
            i+=1
            if not char=='\\':
                name+=char
                if not i<len(string):
                    if not name in namelist:
                        namelist.append(name)
                    name = ''
                    i = 0
            else:
                if not name in namelist:
                    namelist.append(name)
                name = ''
            
    return namelist

def com(filename):
    if '-evb' in sys.argv:
        os.system('lzx -evb '+filename)
    elif '-ewb' in sys.argv:
        os.system('lzx -ewb '+filename)
    elif '-evl' in sys.argv:
        os.system('lzx -evl '+filename)
    elif '-ewl' in sys.argv:
        os.system('lzx -ewl '+filename)

class DecompressionError(ValueError):
    pass

def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            (byte) & 1)

def decompress_lz11(filename):
    infile = open(filename,'rb')
    header = infile.read(4)
    if not header[0] == '\x11':
        raise DecompressionError("not as lzss-compressed file")
    orgin_size, = struct.unpack("<L", header[1:]+'\x00')
    data = bytearray()
    
    def writebyte(b):
        data.append(b)
    def readbyte():
        return ord(infile.read(1))
    def copybyte():
        data.append(infile.read(1))
        
    while len(data) < orgin_size:
        b = readbyte()
        flags = bits(b)
        for flag in flags:
            if flag == 0:
                copybyte()
            elif flag == 1:
                b = readbyte()
                indicator = b >> 4

                if indicator == 0:
                    count = (b << 4)
                    b = readbyte()
                    count += b >> 4
                    count += 0x11
                elif indicator == 1:
                    count = ((b & 0xf) << 12) + (readbyte() << 4)
                    b = readbyte()
                    count += b >> 4
                    count += 0x111
                else:
                    count = indicator
                    count += 1
                disp = ((b & 0xf) << 8) + readbyte()
                disp += 1
                try:
                    for _ in range(count):
                        writebyte(data[-disp])
                except IndexError:
                    raise Exception(count, disp, len(data))
            else:
                raise ValueError(flag)
            if orgin_size <= len(data):
                break
    if len(data) != orgin_size:
        raise DecompressionError("decompressed size does not match the expected size")
    infile.close()
    filename = os.path.split(filename)[0]+'\\dec_'+os.path.split(filename)[1]
    outfile = open(filename,'wb')
    outfile.write(data)
    outfile.close()
    return (filename)
    
def unpack(filename):
    a = open(filename,'rb')
    b = a.read(1)
    if b=='\x11':
        filename = decompress_lz11(filename)
        print ''
    a.close()
    infile = open(filename,'rb')
    magic = infile.read(4)
    if not (magic=='darc'):
        print ('"'+filename+'" is not a darc file')
        return False

    infilec = codecs.open(filename,'r','utf-16le')
    
    infile.seek(16)
    ftablepos,ftablelength,fdatapos = struct.unpack('3I',infile.read(12))
    
    nameposlist = []
    dataposlist = []
    datalenlist = []
    namelist = []
    rawname = os.path.splitext(filename)[0]
    if rawname==filename:
        rawname = '_'+rawname
    i = 0
    infile.seek(ftablepos)
    while i<ftablelength:
        namepos,index,nrfiles = struct.unpack('3I',infile.read(12))
        if IsDir(namepos):
            if index==0:
                break
        i+=12
    i = 0
    infile.seek(ftablepos)
    while i<nrfiles:
        namepos,datapos,datalen = struct.unpack('3I',infile.read(12))
        nameposlist.append(namepos)
        dataposlist.append(datapos)
        datalenlist.append(datalen)
        i+=1
    nametablepos = infile.tell()
    infilec.seek(nametablepos)

    name = ''
    while infilec.tell()<fdatapos:
        tmp = infilec.read(1)
        if tmp=='\x00':
            namelist.append(name)
            name = ''
        else:
            name = name+tmp

    infilec.close()

    i = 0
    index = 0
    if '-o' in sys.argv:
        mainpath = sys.argv[sys.argv.index('-o')+1]+'\\'
    else:
        mainpath = rawname+'\\'
    while i<len(nameposlist):
        if IsDir(nameposlist[i]):
            if dataposlist[i]>index:
                mainpath = mainpath+namelist[i]+'\\'
                index = dataposlist[i]
                i+=1
                mkdir(mainpath)
            elif dataposlist[i]==index:
                if not (namelist[i]==''or namelist[i]=='.'):
                    mainpath = mainpath[:os.path.split(mainpath)[0].rfind('\\')+1]+namelist[i]+'\\'
                    if (mainpath!=(rawname+'\\'))and(mainpath.count('\\')==1):
                        mainpath = rawname+'\\'+mainpath
                    i+=1
                    mkdir(mainpath)
                else:
                    mkdir(mainpath)
                    i+=1
        else:
            filepath = mainpath+namelist[i]
            infile.seek(dataposlist[i])
            outdata = infile.read(datalenlist[i])
            outfile = open(filepath,'wb')
            outfile.write(outdata)
            print 'saving: '+filepath+'...'
            outfile.close()
            i+=1
    infile.close()

def packup(dirname):
    filelist = walk(dirname)
    namelist = ['']
    namelist.extend(getnameinpath(filelist))
    if '-o' in sys.argv:
        outfilename = sys.argv[sys.argv.index('-o')+1]
    else:
        outfilename = dirname+'.darc'
    darc = open(outfilename,'wb')
    darc.write('darc\xff\xfe\x1c\x00\x00\x00\x00\x01\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    nametable = ''
    fnoffsetlist = []
    fileoffsetlist = []
    filesizelist = []
    fileoffset = 0
    for name in namelist:
        for path in filelist:
            if not path.find(name)==-1:
                if not path.find(name)==(len(path)-len(name)):
                    fnoffsetlist.append(len(nametable)+16777216)
                    fileoffsetlist.append(path[:path.find(name)].count('\\'))
                    i = 0
                    for filepath in filelist:
                        if filepath.find(name)!=-1:
                            i+=1
                    if i==len(filelist):
                        nrfiles = '\xff\xff\xff\xff'
                    else:
                        nrfiles = namelist.index(name)+i+1
                    filesizelist.append(nrfiles)
                    if name==dirname:
                        name = '.'
                    nametable+=(name+'\x00').encode('utf-16le')
                    break
                elif path.find(name)==(len(path)-len(name)):
                    fnoffsetlist.append(len(nametable))
                    fileoffsetlist.append(fileoffset)
                    filesize = getfilesize(path)
                    filesizelist.append(filesize)
                    if not filesize%16==0:
                        filesize+=16-(filesize%16)
                    fileoffset+=filesize
                    nametable+=(name+'\x00').encode('utf-16le')
                    break

    filedataoffset = 28+len(fnoffsetlist)*12+len(nametable)
    filetablelength = len(fnoffsetlist)*12+len(nametable)
    i = 0
    while i<len(fnoffsetlist):
        if not IsDir(fnoffsetlist[i]):
            fileoffsetlist[i]+=filedataoffset
        i+=1

    i = 0
    while i<len(fileoffsetlist):
        if filesizelist[i]=='\xff\xff\xff\xff':
            filesizelist[i] = len(filesizelist)
        darc.write(struct.pack('I',fnoffsetlist[i]))
        darc.write(struct.pack('I',fileoffsetlist[i]))
        darc.write(struct.pack('I',filesizelist[i]))
        i+=1
    darc.write(nametable)
    for filename in filelist:
        infile = open(filename,'rb')
        indata = infile.read()
        darc.write(indata)
        print 'Packing: '+filename+'...'
    darc.seek(0,2)
    darcsize = darc.tell()
    darc.seek(12)
    darc.write(struct.pack('I',darcsize))
    darc.seek(20)
    darc.write(struct.pack('I',filetablelength))
    darc.write(struct.pack('I',filedataoffset))
    darc.close()
    com(dirname+'.darc')

def inject(darcname,iname,outfile):
    darc = open(darcname,'rb')
    darcd = codecs.open(darcname,'rb','utf-16le')
    infile = open(iname,'rb')
    infilesize = getfilesize(iname)
    darc.seek(16)
    ftablepos,ftablelength,fdatapos = struct.unpack('3I',darc.read(12))
    i = 0
    darc.seek(ftablepos)
    while i<ftablelength:
        namepos,index,nrfiles = struct.unpack('3I',darc.read(12))
        if IsDir(namepos):
            if index==0:
                break
        i+=12
    nametablepos = 28+nrfiles*12

    darcd.seek(nametablepos)
    nametable = darcd.read((ftablelength-(nrfiles*12))/2)
    namelist = []
    name = ''
    for char in nametable:
        if char=='\x00':
            namelist.append(name)
            name = ''
        else:
            name += char
    if os.path.split(iname)[1] in namelist:
        nr = namelist.index(os.path.split(iname)[1])
    else:
        print 'Input file is not in specified darc.\nPlease check your input.'
        return False
    print 'Injecting: '+iname
    outfile.seek(28+nr*12+4)
    dataoffset = struct.unpack('I',outfile.read(4))[0]
    datasize = struct.unpack('I',outfile.read(4))[0]
    dspos = outfile.tell()
    outfile.seek(0)
    data1 = outfile.read(dataoffset)
    data2 = infile.read()
    outfile.seek(datasize,1)
    data3 = outfile.read()
    outfile.seek(0)
    outfile.write(data1+data2+data3)
    outfile.seek(dspos-4)
    outfile.write(struct.pack('I',infilesize))
    offsetfix = infilesize-datasize
    outfile.seek(dspos+4)
    while outfile.tell()<nametablepos:
        fixed = struct.unpack('I',outfile.read(4))[0]+offsetfix
        outfile.seek(-4,1)
        outfile.write(struct.pack('I',fixed))
        outfile.seek(8,1)
    outfile.seek(0,2)
    outsize = outfile.tell()
    outfile.seek(12)
    outfile.write(struct.pack('I',outsize))
    darc.close()
    darcd.close()
    infile.close()

darchelp = ['Usage: [option] [object]\n\nOptions:','  -u [darc file] ........... unpack darcfile','  -i [darc file] ........... inject files to specified darc file','  -p [directory] ........... packup specified directory','  unessential option:\n   -o [file name] ........... set output file name','   -d [directory] .......... set work directory','   compression:\n   -evb ... VRAM compatible, big-endian (LZ11)','   -ewb ... WRAM compatbile, big-endian (LZ11)','   -evl ... VRAM compatible, little-endian (LZ40)','   -ewl ... WRAM compatbile, little-endian (LZ40)']
if '-u' in sys.argv:
    if '-d' in sys.argv:
        dirname = sys.argv[sys.argv.index('-d')+1]
        filelist = walk(dirname)
        for darcfile in filelist:
            unpack(darcfile)
    else:
        darcfile = sys.argv[sys.argv.index('-u')+1]
        unpack(darcfile)
    print 'done!'

elif '-p' in sys.argv:
    print 'Pack up feature still testing,\nit cannot build file work well ingame,\nuse inject feature("-i" option) instead is recommand!\ncontinue pack up?(Y/N)'
    yn = raw_input()
    if yn=='N'or yn=='n':
        exit
    elif yn=='Y'or yn=='y':
        if '-d' in sys.argv:
            workdir = sys.argv[sys.argv.index('-d')+1]
            if os.path.exists(wordir) and os.path.isdir(workdir):
                os.chdir(workdir)
            else:
                print 'Input dir is not exist!'
            nlist = os.listdir(os.getcwd())
            for name in nlist:
                if os.path.isdir(name):
                    packup(name)
        else:
            dirname = sys.argv[sys.argv.index('-p')+1]
            packup(dirname)
        print 'done!'

elif '-i' in sys.argv:
    darcname = sys.argv[sys.argv.index('-i')+1]
    darc = open(darcname,'rb')
    if '-o' in sys.argv:
        if sys.argv[sys.argv.index('-o')+1]==darcname:
            print 'Input name is same as orign name!'
            exit
        else:
            outfilename = sys.argv[sys.argv.index('-o')+1]
    else:
        outfilename = 'new_'+darcname
    outfile = open(outfilename,'wb+')
    outfile.write(darc.read())
    darc.close()
    if '-d' in sys.argv:
        workdir = sys.argv[sys.argv.index('-d')+1]
        if os.path.exists(workdir) and os.path.isdir(workdir):
            filelist = walk(workdir)
        else:
            print 'Input dir is not exist!'
        for iname in filelist:
            inject(darcname,iname,outfile)
    else:
        iname = sys.argv[sys.argv.index('-i')+2]
        inject(darcname,iname,outfile)
    outfile.close()
    com(outfilename)
    print 'done!'

elif len(sys.argv)==1 or '-h' in sys.argv:
    for s in darchelp:
        print s
else :
    for argv in sys.argv:
        if argv!=sys.argv[0] and os.path.exists(argv):
            if os.path.isfile(argv):
                unpack(argv)
                print 'done!'