import sys
import os

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_app_path():
    """ Get the directory where the app is running (where config/output should go) """
    if getattr(sys, 'frozen', False):
        # The application is frozen (exe)
        return os.path.dirname(sys.executable)
    # The application is not frozen (script)
    return os.path.dirname(os.path.abspath(__file__))
