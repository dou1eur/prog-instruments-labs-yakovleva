import csv
import re
import os
import pandas as pd

FORMAT = {
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