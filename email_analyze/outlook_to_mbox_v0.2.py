import subprocess
import os
import sys

def convert_pst_to_mbox(pstfilename, outputfolder):


    folder_name = pstfilename.split('/')[5]

    if not os.path.exists(os.path.join(outputfolder,folder_name)):
        os.makedirs(os.path.join(outputfolder,folder_name))

    print("debug",outputfolder,pstfilename)
    subprocess.call(['readpst', '-o', os.path.join(outputfolder,folder_name), '-r',pstfilename])


if __name__=='__main__':
    root_dir='/hdfs'
    ext_dir=''
    if os.path.isdir(root_dir):
        for (root, dirs, files) in os.walk(root_dir):
            try:
                if dirs[dirs.index('outlook')] and not os.path.isdir(root+'/mbox'):
                    root_dir = os.path.join(root,dirs[dirs.index('outlook')])
                    ext_dir=root+'/mbox'
                    break
            except:
                pass
    try:
        if not os.path.exists(ext_dir):
            os.makedirs(ext_dir)
    except:
        pass
    
    if os.path.isdir(root_dir):
        for(root,dirs,files) in os.walk(root_dir):
            if len(files) >0:
                for file_name in files:
                    convert_pst_to_mbox(os.path.join(root,file_name), ext_dir)



