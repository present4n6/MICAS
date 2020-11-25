import subprocess
import os
import sys

def convert_pst_to_mbox(pstfilename, outputfolder):
    subprocess.call(['readpst', '-o', outputfolder, '-r',pstfilename])


if __name__=='__main__':
    root_dir='email/outlook'

    try:
        if not os.path.exists('email/mbox'):
            os.makedirs('email/mbox')
    except:
        pass
    if os.path.isdir(root_dir):
        for(root,dirs,files) in os.walk(root_dir):
            if len(files) >0:
                for file_name in files:
                    convert_pst_to_mbox(os.path.join(root,file_name), 'email/mbox')


