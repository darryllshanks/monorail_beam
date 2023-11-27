import math
import csv


def str_to_int(s: str) -> int|float:
    """
    Returns an integer from a numeric string, however; returns the
    original string if the data is not numeric.

    's' - Input string to be converted
    """
    try:
        return int(s)
    except ValueError:
        return s


def str_to_float(s: str) -> float|str:
    """
    Returns a float from a numeric string, however; returns the 
    original string if the data is not numeric.

    's' - Input string to be converted
    """
    try:
        return float(s)
    except ValueError:
        return s
    

def read_csv_file(filename: str) -> list[list[str]]:
    """
    Returns data contained in the file, 'filename' as a list of lists
    of strings. It is assumed the data is in a csv style format.
    e.g., separated by commas.
    """
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        csv_data = list(csv_reader)
    return csv_data