import signal
import subprocess
import os
import sys

def readCard():
    print(sys.platform)
    if(sys.platform == "linux"):
        proc = subprocess.run('javac -cp .:./lib/pteidlibj.jar main.java', shell=True,         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc1 = subprocess.run('java -Djava.library.path=/usr/local/lib -cp lib/pteidlibj.jar:. main', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    elif(sys.platform == "win32"):
        proc = subprocess.run('javac -cp lib\pteidlibj.jar main.java',         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc1 = subprocess.run('java -cp lib/pteidlibj.jar;. main', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc1
        
    return proc1.stdout

def terminate(proc):
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    print("DEAD")

