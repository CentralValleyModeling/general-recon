#from html_report import load_data_mult
from collections import namedtuple
import pandas as pd
import yaml

import pandas as pd
import matplotlib.pyplot as plt
import csv

from utils import generate_yaml_file


def read_csv_into_list(filename):
    data = []
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file,delimiter=',')
        for row in reader:
            data.append(row)
    return data

csv_data = read_csv_into_list('CS3 Variable list.csv')


def remove_duplicates_from_yaml(filename):
    """
    Remove duplicate entries from a YAML file.

    Args:
    - filename: Name of the YAML file to process.
    """
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)

    # Remove duplicates
    unique_data = remove_duplicates(data)

    # Write unique data back to the YAML file
    with open(filename, 'w') as file:
        yaml.dump(unique_data, file)

def remove_duplicates(data):
    """
    Remove duplicate entries with the same top-level keys from a nested dictionary.

    Args:
    - data: Nested dictionary to process.

    Returns:
    - Unique data (nested dictionary) without duplicates.
    """
    seen = {}
    unique_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursively process nested dictionaries
            unique_data[key] = remove_duplicates(value)
        elif key not in seen:
            # Add the first occurrence of the key
            seen[key] = value
            unique_data[key] = value
    return unique_data


filename = 'dictionary.yaml'
#generate_yaml_file(csv_data,filename)

remove_duplicates_from_yaml(filename)
print(f"Duplicate entries removed from '{filename}'.")
