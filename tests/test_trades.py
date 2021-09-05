import datetime
import vcr
import json
import pandas as pd
from krakenapi import KrakenApi
from krakenohlc import datetime_as_utc_unix, trades_as_dataframe, download_trades


def test_datetime_as_utc_unix():
    date = datetime.datetime(2021, 3, 28, 0, 0)
    utc = datetime_as_utc_unix(date)
    utc_test = 1616889600
    assert utc == utc_test


def test_trades_as_dataframe():
    with open("tests/fixtures/tests_data/trades.json", 'r') as f:
        trades = json.load(f)
    df_trades_test = pd.read_csv(
        "tests/fixtures/tests_data/trades.csv",
        index_col="time",
        parse_dates=True
    )
    df_trades = trades_as_dataframe(trades)
    df_trades_test["miscellaneous"].fillna('', inplace=True)
    assert df_trades.equals(df_trades_test)


@vcr.use_cassette("tests/fixtures/vcr_cassettes/test_download_trades.yaml")
def test_download_trades():
    ka = KrakenApi()
    pair = "GRTETH"
    start_datetime = datetime.datetime(2021, 3, 28, 0, 0)
    end_datetime = datetime.datetime(2021, 5, 4, 15, 0)
    df_trades = download_trades(ka, pair, start_datetime, end_datetime)
    df_trades_test = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00.csv",
        index_col="time",
        parse_dates=True
    )
    df_trades_test["miscellaneous"].fillna('', inplace=True)
    assert df_trades.equals(df_trades_test)

