import subprocess
import os
import sys

def convert_pst_to_mbox(pstfilename, outputfolder):
    subprocess.call(['readpst', '-o', outputfolder, '-r', pstfilename])

if __name__=='__main__':
    argv=sys.argv
    rood_dir=argv[1]

    try:
        if not os.path.exists('mbox'):
            os.makedirs('mbox')
    except:
        pass
    try:
        if os.path.isdir('mbox'):
            convert_pst_to_mbox(argv[1], 'mbox') 
    except:
        pass
