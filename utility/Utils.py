import os
import sys
from pathlib import Path

def get_project_root() -> Path:
    """
    Get the root directory of the project.

    Returns:
    Path: The root directory of the project.
    """

    global application_path
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(os.path.dirname(__file__))
    return Path(application_path)


def dict_to_string(dict):
    """
    Convert a dictionary to a string.

    Args:
    - dict (dict): The dictionary to be converted.

    Returns:
    str: The string representation of the dictionary.
    """

    string = ", ".join([f"{k} : {v}" for k, v in dict.items()])
    return string