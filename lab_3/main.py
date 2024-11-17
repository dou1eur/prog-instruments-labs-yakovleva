import csv
import re
import os
import pandas as pd

FORMATS = {
    "telephone": "^\+7-\(\d{3}\)-\d{3}-\d{2}-\d{2}$",
    "height": "^\d+\.\d{2}$",
    "inn": "^\d{12}$",
    "identifier": "^\d{2}-\d{2}/\d{2}$",
    "occupation": "^[\w\s-]+$",
    "latitude": "^-?\d+\.\d+$",
    "blood_type": "^(AB|O|A|B)[+-]$",
    "issn": "^\d{4}-\d{4}$",
    "uuid": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "date": "^\d{4}-\d{2}-\d{2}$"
}


def open_csv(path: str) -> pd.DataFrame:
    data = pd.read_csv(path, encoding="utf-16", sep=";")
    return data


def search_valid_row(row: pd.Series) -> bool:
    for column in FORMATS:
        format = FORMATS[column]
        value = str(row[column])
        if not re.match(format, value):
            return False
    return True


def get_invalid_idx(path: str) -> list:
    rows = pd.read_csv(path, delimiter=";", encoding="utf-16")
    invalid_idx = [idx for idx, row in rows.iterrows() if not search_valid_row(row)]
    return invalid_idx


if __name__ == "__main__":
    list_invalid_idx = get_invalid_idx(os.path.join("prog-instruments-labs-yakovleva", "lab_3", "88.csv"))
    print("invalid", list_invalid_idx)

