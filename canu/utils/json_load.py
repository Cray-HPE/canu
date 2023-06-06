import os
import sys
import json


def load_json(file):
    """Load JSON file and return dictionary.

    Args:
        file: JSON file.

    Returns:
        Loaded JSON file.
    """
    try:
        with open(os.path.join(file.name), "r") as f:
            json_file = json.load(f)
    except FileNotFoundError:
        print(f"The {file} file was not found, check that you entered the right file name and path")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{str(e)}, JSON error parsing {file}")
        sys.exit(1)
    return json_file