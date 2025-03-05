import sys
import os
import importlib

from UI import chat

if __name__ == "__main__":
    # os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    chat.exec()