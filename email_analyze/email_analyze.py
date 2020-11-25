import subprocess



subprocess.call(['python3','outlook_to_mbox.py'])

subprocess.call(['python3','mbox_parser.py'])

subprocess.call(['python3','eml_parser.py'])
