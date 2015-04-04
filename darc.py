import struct,os,codecs,fnmatch,sys

def getfilesize(Fname):
                file = open(Fname,'rb')
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

def unpack(filename):
                infile = open(filename,'rb')
                filesize=getfilesize(filename)
                
                magic = infile.read(4)
                if not (magic=='darc'):
                                print ('"'+filename+'" is not a darc file')
                                return False

                infilec = codecs.open(filename,'r','utf-16le')
                
                infile.seek(16)
                ftablepos = struct.unpack('I',infile.read(4))[0]
                ftablelength = struct.unpack('I',infile.read(4))[0]
                fdatapos = struct.unpack('I',infile.read(4))[0]
                
                nameposlist = []
                dataposlist = []
                datalenlist = []
                namelist = []
                rawname = os.path.splitext(filename)[0]
                
                i = 0
                infile.seek(ftablepos)
                while i<ftablelength:
                                namepos = struct.unpack('I',infile.read(4))[0]
                                index = struct.unpack('I',infile.read(4))[0]
                                nrfiles = struct.unpack('I',infile.read(4))[0]
                                if IsDir(namepos):
                                                if index==0:
                                                                break
                                i+=12
                i = 0
                infile.seek(ftablepos)
                while i<nrfiles:
                                namepos = struct.unpack('I',infile.read(4))[0]
                                datapos = struct.unpack('I',infile.read(4))[0]
                                datalen = struct.unpack('I',infile.read(4))[0]
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
                darc = open(dirname+'.darc','wb')
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

darchelp = ['Usage: [option] [object]\n    or [option] --d [Directory]\n[options:]',' -u        unpack',' -p        packup','--d        Directory']
if '-u' in sys.argv:
                if '--d' in sys.argv:
                                dirname = sys.argv[sys.argv.index('--d')+1]
                                filelist = walk(dirname)
                                for darcfile in filelist:
                                                unpack(darcfile)
                else:
                                darcfile = sys.argv[sys.argv.index('-u')+1]
                                unpack(darcfile)
elif '-p' in sys.argv:
                if '--d' in sys.argv:
                                dirname = sys.argv[sys.argv.index('--d')+1]
                                os.chdir(dirname)
                                nlist = os.listdir(os.getcwd())
                                for name in nlist:
                                                if os.path.isdir(name):
                                                                packup(name)
                else:
                                dirname = sys.argv[sys.argv.index('-p')+1]
                                packup(dirname)
else :
                for argv in sys.argv:
                                if argv==sys.argv[0]:
                                                for sentence in darchelp:
                                                                print sentence
                                elif os.path.exists(argv):
                                                if os.path.isfile(argv):
                                                                unpack(argv)
                































