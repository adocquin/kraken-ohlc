import datetime
import pandas as pd


def pandas_to_kraken_ohlc_frequencies(ohlc_frequencies: list) -> list:
    """
    Convert configuration file frequencies to pandas frequencies format.

    :param ohlc_frequencies: List of pandas ohlc frequencies to convert.
    :return: List of converted frequencies.
    """
    supported_frequencies = [
        "1M",
        "3M",
        "5M",
        "15M",
        "30M",
        "1H",
        "2H",
        "4H",
        "6H",
        "8H",
        "12H",
        "1D",
        "3D",
        "1W",
    ]
    frequencies = list()
    for frequency in ohlc_frequencies:
        if frequency not in supported_frequencies:
            raise ValueError(
                f"Unsupported frequency {frequency}. Supported "
                f"frequencies: {supported_frequencies}"
            )
        frequency = frequency.replace("M", "T").replace("1W", "1W-MON")
        frequencies.append(frequency)
    return frequencies


def check_trades_ohlc_start_end_dates(
    config_date: pd.Timestamp, ohlc_date: pd.Timestamp, frequency: str
) -> bool:
    """
    Check for a specified frequency if the passed date
    is a correct start date or end date.

    :param config_date: Configuration start or end download date as Pandas Timestamp.
    :param ohlc_date: OHLC date to check as Pandas Timestamp.
    :param frequency: Frequency to check date on.
    :return: True if correct date, False otherwise.
    """
    if frequency == "1W-MON":
        rounded_date = pd.to_datetime(config_date).to_period("W-SUN").start_time
    else:
        rounded_date = config_date.floor(freq=frequency)
    if config_date != rounded_date and ohlc_date == rounded_date:
        return False
    return True


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
    start_date = pd.Timestamp(start_datetime, tz=None)
    end_date = pd.Timestamp(end_datetime, tz=None)

    if not df.empty:
        first_date = df.iloc[0].name
        if not check_trades_ohlc_start_end_dates(
            start_date, first_date, frequency
        ):
            df = df[1:]
        last_date = df.iloc[-1].name
        if not check_trades_ohlc_start_end_dates(
            end_date, last_date, frequency
        ):
            df = df[:-1]

    if df.empty:
        print(f"{pair} {frequency}: Not enough data.")
    else:
        frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
        print(
            f"{pair} {frequency}: OHLC data saved from {df.index[0]} to {df.index[-1]}."
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
