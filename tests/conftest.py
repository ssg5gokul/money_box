import os
import sys

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0,PATH)

print(PATH)