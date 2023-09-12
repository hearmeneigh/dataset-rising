import subprocess
import os

subprocess.run('start-mongodb.sh', shell=True, cwd=os.path.dirname(__file__))
