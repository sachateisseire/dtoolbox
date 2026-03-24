import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))

def get_data_path(filename):
    return os.path.join(get_base_path(), "data", filename)