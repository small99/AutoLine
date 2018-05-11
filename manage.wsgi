import os

os.environ["PATH"] = os.environ["PATH"] + ";" + os.getcwd() + "/bin"

from .manage import app as application
