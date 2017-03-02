import os,sys

directory = r'D:\projects\dmtalents\static\blog\ftfmax'


def renameIt(dir):
    files = os.listdir(dir)
    for f in files:
        path = dir+'/'+f
        #print(path)
        if os.path.isdir(path):
            renameIt(path)
        elif os.path.isfile(path):
            if f.find(r'-min') > 0:
                print(f)
                idx = f.index(r'-min')
                if f.endswith('jpg'):
                    newF = f[0:idx] + '.jpg'
                elif f.endswith('png'):
                    newF = f[0:idx] + '.png'

                newpath = dir + '/' + newF
                os.rename(path, newpath)
            else:
                continue


renameIt(directory)

#print(sys.platform)
