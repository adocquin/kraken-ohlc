import datetime
from pathlib import Path

import pandas as pd

from .ohlc import FREQUENCIES_REPLACE


def define_filepath(
    folder: str,
    pair: str,
    start_datetime: datetime,
    end_datetime: datetime,
    frequency: str = "",
    volume_in_quote_asset: bool = None,
) -> str:
    """
    Generate file path to read and save files for specified folder name, pair,
    start date, end date and frequency.

    :param folder: Folder name as string.
    :param pair: Pair name as string.
    :param start_datetime: Start date as datetime.
    :param end_datetime: End date as datetime.
    :param frequency: Frequency as string for OHLC data.
    :param volume_in_quote_asset: If volume is aggregated in quote asset or not.
    :return: File path as string.
    """
    frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
    path_start_date = str(start_datetime).replace(" ", "T").replace(":", "-")
    path_end_date = str(end_datetime).replace(" ", "T").replace(":", "-")
    filepath = f"{folder}/{pair}_{path_start_date}_{path_end_date}"
    if frequency:
        for i in FREQUENCIES_REPLACE:
            frequency = frequency.replace(FREQUENCIES_REPLACE[i], i)
        filepath += f"_{frequency}"
    if volume_in_quote_asset is True:
        filepath += "_quote"
    filepath += ".csv"
    return filepath


def read_csv(filepath: str) -> pd.DataFrame:
    """
    Read CSV at specified file path and return it as pandas DataFrame.

    :param filepath: CSV file path as string.
    :return: CSV as pandas DataFrame.
    """
    try:
        df: pd.DataFrame = pd.read_csv(filepath, index_col="time", parse_dates=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame()
    except (ValueError, pd.errors.ParserError, IsADirectoryError) as e:
        raise ValueError(f"Can't read csv at {filepath} -> {e}")
    return df


def create_data_directory(data_folder_path: str) -> None:
    """
    Create trades and OHLC data output directories.

    :param data_folder_path: Data folder path as string.
    :return: None
    """
    Path(f"{data_folder_path}/ohlc").mkdir(parents=True, exist_ok=True)
    Path(f"{data_folder_path}/trade_history").mkdir(parents=True, exist_ok=True)
