import pandas as pd


def open_csv(
    csv_path: str,
    delimiter: str = ",",
    column_names: list = None,
    remove_column: str = None,
) -> pd.DataFrame:
    """
    Open a CSV file and return it as a DataFrame

    Args:
        csv_path (str): the path to csv file
        delimiter (str, optional): the delimiter used in the csv file
        column_names (list, optional): list of column names to use
        remove_column (str, optional): name of the column to remove from the DataFrame

    Returns:
        pd.DataFrame: dataFrame containing the data from the csv file
    """
    if column_names is not None:
        df = pd.read_csv(csv_path, delimiter=delimiter, names=column_names)
    else:
        df = pd.read_csv(csv_path, delimiter=delimiter)
    if remove_column is not None:
        df = df.drop(remove_column, axis=1)
    return df


def save_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Save the DataFrame to a csv file

    Args:
        df (pd.DataFrame): the DataFrame to save
        file_path (str): the path where the csv file will be saved
    """
    df.to_csv(file_path, index=False)
