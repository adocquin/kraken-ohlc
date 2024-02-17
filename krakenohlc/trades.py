from datetime import datetime, timezone

import pandas as pd
from krakenapi import KrakenApi


def datetime_as_utc_unix(date: datetime) -> int:
    """
    Transform passed datetime to utc unix time as int.

    :param date: Date to transform as datetime.
    :return: Date as int unix time.
    """
    return int(date.replace(tzinfo=timezone.utc).timestamp())


def trades_as_dataframe(trades: list) -> pd.DataFrame:
    """
    Convert Kraken api downloaded trades as pandas DataFrame.
    Is called by get_trades function.

    :param trades: Downloaded data from kraken api as dictionary.
    :return: Pandas DataFrame of trades data.
    """
    # Trade id was added to the response since the first version of the
    # API. We remove it to keep compatibility. See:
    # https://docs.kraken.com/rest/#tag/Market-Data/operation/getRecentTrades
    trades = [i[:6] for i in trades]
    df = pd.DataFrame(
        data=trades,
        columns=[
            "price",
            "volume",
            "time",
            "buy/sell",
            "market/limit",
            "miscellaneous",
        ],
    )
    df["price"] = df["price"].astype(float)
    df["volume"] = df["volume"].astype(float)
    # Set time as index
    df["time"] = pd.to_datetime(df["time"], unit="s").dt.round("us")
    df.set_index(["time"], drop=True, inplace=True)
    return df


def download_trades(
    ka: KrakenApi, pair: str, start_datetime: datetime, end_datetime: datetime
) -> pd.DataFrame:
    """
    Call KrakenAPI get_trades_history method to download trades for a specified
    pair from start to end dates.

    :param ka: KrakenAPI object.
    :param pair: Pair to download trades history.
    :param start_datetime: Trades start date as datetime.
    :param end_datetime: Trades end date as datetime.
    :return: Trade history as pandas DataFrame.
    """
    start_unix_time = datetime_as_utc_unix(start_datetime)
    end_unix_time = datetime_as_utc_unix(end_datetime)
    trades = ka.get_trades_history(pair, start_unix_time, end_unix_time, True)
    df_trades = trades_as_dataframe(trades)
    df_trades = df_trades[df_trades.index < end_datetime]
    return df_trades
