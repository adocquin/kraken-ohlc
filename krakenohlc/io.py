from pathlib import Path
import datetime
import pandas as pd


def define_filepath(
    folder: str,
    pair: str,
    start_datetime: datetime,
    end_datetime: datetime,
    frequency: str = "",
) -> str:
    """
    Generate file path to read and save files for specified folder name, pair,
    start date, end date and frequency.

    :param folder: Folder name as string.
    :param pair: Pair name as string.
    :param start_datetime: Start date as datetime.
    :param end_datetime: End date as datetime.
    :param frequency: Frequency as string for OHLC data.
    :return: File path as string.
    """
    path_start_date = str(start_datetime).replace(" ", "T").replace(":", "-")
    path_end_date = str(end_datetime).replace(" ", "T").replace(":", "-")
    if frequency:
        filepath = f"{folder}/{pair}_{path_start_date}_{path_end_date}_{frequency}.csv"
    else:
        filepath = f"{folder}/{pair}_{path_start_date}_{path_end_date}.csv"
    return filepath


def read_csv(filepath: str) -> pd.DataFrame:
    """
    Read CSV at specified file path and return it as pandas DataFrame.

    :param filepath: CSV file path as string.
    :return: CSV as pandas DataFrame.
    """
    try:
        df = pd.read_csv(filepath, index_col="time", parse_dates=["time"])
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame()
    except (ValueError, pd.errors.ParserError, IsADirectoryError) as e:
        raise ValueError(f"Can't read csv at {filepath} -> {e}")
    return df


def create_data_directory() -> None:
    """
    Create trades and OHLC data output directories.

    :return: None
    """
    Path("data/ohlc").mkdir(parents=True, exist_ok=True)
    Path("data/trade_history").mkdir(parents=True, exist_ok=True)
