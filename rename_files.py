import os,sys

directory = r'D:\projects\dmtalents\static\faq\mqa\cornerOnly'


def renameIt(dir):
    files = os.listdir(dir)
    for f in files:
        path = dir+'/'+f
        #print(path)
        if os.path.isdir(path):
            renameIt(path)
        elif os.path.isfile(path):
            if f.index(r'-min') > 0:
                print(f)
                idx = f.index(r'-min')
                newF = f[0:idx] + '.png'
                newpath = dir + '/' + newF
                os.rename(path, newpath)


renameIt(directory)

#print(sys.platform)
