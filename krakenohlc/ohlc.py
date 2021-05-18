import datetime
import pandas as pd


def check_trades_ohlc_start_end_dates(
    date: datetime, start: bool, frequency: str
) -> bool:
    """
    Check for a specified frequency if the passed datetime
    is a correct start date or end date.

    :param date: Date to check as datetime.
    :param start: True if start date, false if end date.
    :param frequency: Frequency to check date on.
    :return: True if correct date, False otherwise.
    """
    try:
        correct_date = True if date == date.round(frequency) else False
    except ValueError:  # Frequency = "1W"
        day_of_week = 0 if start else 6
        correct_date = True if date.dayofweek == day_of_week else False
    return correct_date


def adjust_ohlc_frequency_dates(
    start_datetime: datetime,
    end_datetime: datetime,
    frequency: str,
    df: pd.DataFrame,
    pair: str,
) -> pd.DataFrame:
    """
    Adjust the OHLCV pandas DataFrame by removing rows with uncompleted frequency.
    Is called by download_historic_data

    :param start_datetime: Data start date as datetime object.
    :param end_datetime: Data end date as datetime object.
    :param frequency: Frequency or period in string.
    :param df: OHLCV pandas DataFrame.
    :param pair: OHLCV pair.
    :return: Frequency adjusted pandas DataFrame.
    """
    start_datetime = pd.to_datetime(start_datetime)
    correct_start_date = check_trades_ohlc_start_end_dates(
        start_datetime, True, frequency
    )
    if not correct_start_date:
        df = df[1:]

    end_datetime = pd.to_datetime(end_datetime)
    correct_end_date = check_trades_ohlc_start_end_dates(end_datetime, False, frequency)
    if not correct_end_date:
        df = df[:-1]

    if not correct_start_date or not correct_end_date:
        if df.empty:
            print(f"{pair} {frequency}: Not enough data.")
        else:
            print(
                f"{pair} {frequency}: Data truncated from {df.index[0]} to"
                f" {df.index[-1]}."
            )
    return df


def trades_to_ohlc(df_trades: pd.DataFrame, frequency: str) -> pd.DataFrame:
    """
    Resamples the trades pandas DataFrame to an OHLCV DataFrame in specified timeline.

    :param df_trades: Trades pandas DataFrame.
    :param frequency:  Frequency to resample in string.
    :return: OHLC DataFrame in specified frequency.
    """
    df_ohlc = df_trades.resample(
        frequency, closed="left", label="left", origin="epoch"
    ).agg({"price": "ohlc", "volume": "sum"})
    # Remove multi-indexed columns
    df_ohlc.columns = [i[1] for i in df_ohlc.columns]
    return df_ohlc
