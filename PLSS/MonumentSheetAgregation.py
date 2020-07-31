def file_copy_bydate(srcDir, dstDir, dateLastMoved, olderThan=0):
#Copies all files in srcDir and all its sub-directories than are younger than dateLastMoved and older than olderThan
    import shutil, sys, time, os
    src = srcDir
    dst = dstDir
    dateMoved = dateLastMoved
    olderThn = olderThan
    os.mkdir(os.path.join(dst, "File_Copy_Dup"))


#function to test the date of a file
    def test_dates(days,ftime):
        return (time.mktime(time.strptime(dateMoved, "%d %B %y")) < ftime < (time.time() - days * 86400))
#Loop walks through directories, creates path to files and copies them to src directory
    for path, subdirs, files in os.walk(src):
        for name in files:
            if test_dates(olderThn, os.stat(os.path.join(path, name)).st_mtime):

                if os.path.exists(os.path.join(dst, name)):
                    print("DUP  ", os.path.join(path, name))
                    shutil.copy2(os.path.join(path, name), os.path.join(dst, "File_Copy_Dup"))

                else:
                    print(os.path.join(path, name))
                    shutil.copy2(os.path.join(path, name), os.path.join(dst, name))

def resubmit_mover(inDir):
    import Folder_Op, shutil, os
    os.mkdir(os.path.join(inDir, "resubmittal_check"))
    fileList = Folder_Op.File_Lists(inDir)
    #print(fileList.name_list)
    y = fileList.no_ext
    #print(y)
    for name in y:
        nameAndExt = name + fileList.ext
        if len(name) > 22:
            dupName = name[:(22-len(name))] + fileList.ext
            shutil.move(os.path.join(inDir, nameAndExt), os.path.join(inDir, "resubmittal_check"))
            print("Moved resubmittal: ", nameAndExt)
            if os.path.exists(os.path.join(inDir, dupName)):
                shutil.move(os.path.join(inDir, dupName), os.path.join(inDir, "resubmittal_check"))
                print("Moved resubmittal: ", dupName)






param1 = input("Source directory to search")
param2 = input("Destination directory")
param3 = input("Date to search from in format \n 01 December 11" )

file_copy_bydate(param1, param2, param3)
resubmit_mover(param2)