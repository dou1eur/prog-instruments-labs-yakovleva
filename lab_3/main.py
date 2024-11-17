import re
import os

import pandas as pd

import checksum

FORMATS = {
    "telephone": r"^\+7-\(9\d{2}\)-\d{3}-\d{2}-\d{2}$", 
    "height": r"^[1-2]\.\d{2}$", 
    "inn": r"^\d{12}$",
    "identifier": r"^\d{2}-\d{2}/\d{2}$",
    "occupation": r"^[а-яА-Яa-zA-ZёЁ\s-]+$", 
    "latitude": r"^-?([0-9]|[1-8][0-9])\.\d{1,6}$",
    "blood_type": r"^(A|B|AB|O)[+−]$", 
    "issn": r"^\d{4}-\d{4}$", 
    "uuid": r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$",
    "date": r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|1\d{1}|2\d{1}|3[01])$"
}


def open_csv(path: str) -> pd.DataFrame:
    """
    Opens a csv file and returns its contents as a DataFrame

    Args:
        path (str): path to the source csv file
    
    Returns:
        pd.DataFrame: a DataFrame object
    """
    data = pd.read_csv(path, encoding="utf-16", sep=";")
    return data


def search_valid_row(row: pd.Series) -> bool:
    """
    Checks whether a string conforms to the given formats

    Args:
        row (pd.Series): the DataFrame row that will be checked
    
    Returns:
        bool: True if all values in the string match the formats, otherwise False
    """
    for column in FORMATS:
        format = FORMATS[column]
        value = str(row[column])
        if not re.match(format, value):
            return False
    return True


def get_invalid_idx(path: str) -> list:
    """
    gets the indexes of rows that do not conform to the given formats

    Args:
        path (str): path to the source csv file
    
    Returns:
        list: list of row indices that are invalid
    """
    rows = pd.read_csv(path, delimiter=";", encoding="utf-16")
    invalid_idx = [idx for idx, row in rows.iterrows() if not search_valid_row(row)]
    return invalid_idx


if __name__ == "__main__":
    list_invalid_idx = get_invalid_idx(
        os.path.join("prog-instruments-labs-yakovleva", "lab_3", "88.csv")
    )
    checksum.serialize_result(88, checksum.calculate_checksum(list_invalid_idx))
