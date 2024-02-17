import datetime

import pandas as pd
import pytest

from krakenohlc import (adjust_ohlc_frequency_dates,
                        check_trades_ohlc_start_end_dates,
                        pandas_to_kraken_ohlc_frequencies, trades_to_ohlc)


def test_pandas_to_kraken_ohlc_frequencies():
    frequencies = [
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
    frequencies_test = [
        "1min",
        "3min",
        "5min",
        "15min",
        "30min",
        "1h",
        "2h",
        "4h",
        "6h",
        "8h",
        "12h",
        "1D",
        "3D",
        "1W-MON",
    ]
    converted_frequencies = pandas_to_kraken_ohlc_frequencies(frequencies)
    assert converted_frequencies == frequencies_test
    with pytest.raises(ValueError) as e_info:
        pandas_to_kraken_ohlc_frequencies(["6M"])
    assert "Unsupported frequency" in str(e_info.value)


def test_check_trades_ohlc_start_end_dates():
    start_date = pd.to_datetime("2021-08-23 05:37:50", format="%Y-%m-%d %H:%M:%S")
    end_date = pd.to_datetime("2021-09-06 13:10:23", format="%Y-%m-%d %H:%M:%S")

    ohlc_date = pd.to_datetime("2021-08-23 06:21:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "1T")
    ohlc_date = pd.to_datetime("2021-09-06 13:06:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "1T")

    ohlc_date = pd.to_datetime("2021-08-23 06:21:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "3T")
    ohlc_date = pd.to_datetime("2021-09-06 13:06:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "3T")

    ohlc_date = pd.to_datetime("2021-08-23 06:20:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "5T")
    ohlc_date = pd.to_datetime("2021-09-06 13:05:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "5T")

    ohlc_date = pd.to_datetime("2021-08-23 06:15:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "15T")
    ohlc_date = pd.to_datetime("2021-09-06 13:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "15T") is False

    ohlc_date = pd.to_datetime("2021-08-23 06:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "30T")
    ohlc_date = pd.to_datetime("2021-09-06 13:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "30T") is False

    ohlc_date = pd.to_datetime("2021-08-23 06:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "1H")
    ohlc_date = pd.to_datetime("2021-09-06 13:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "1H") is False

    ohlc_date = pd.to_datetime("2021-08-23 06:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "2H")
    ohlc_date = pd.to_datetime("2021-09-06 12:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "2H") is False

    ohlc_date = pd.to_datetime("2021-08-23 04:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "4H") is False
    ohlc_date = pd.to_datetime("2021-09-06 12:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "4H") is False

    ohlc_date = pd.to_datetime("2021-08-23 06:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "6H")
    ohlc_date = pd.to_datetime("2021-09-06 12:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "6H") is False

    ohlc_date = pd.to_datetime("2021-08-23 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "8H") is False
    ohlc_date = pd.to_datetime("2021-09-06 08:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "8H") is False

    ohlc_date = pd.to_datetime("2021-09-06 13:06:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "12H")
    ohlc_date = pd.to_datetime("2021-09-06 13:06:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "12H")

    ohlc_date = pd.to_datetime("2021-08-23 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "1D") is False
    ohlc_date = pd.to_datetime("2021-09-06 12:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "1D")

    ohlc_date = pd.to_datetime("2021-08-23 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "3D")
    ohlc_date = pd.to_datetime("2021-09-06 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "3D") is False

    ohlc_date = pd.to_datetime("2021-08-23 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(start_date, ohlc_date, "1W-MON") is False
    ohlc_date = pd.to_datetime("2021-09-06 00:00:00", format="%Y-%m-%d %H:%M:%S")
    assert check_trades_ohlc_start_end_dates(end_date, ohlc_date, "1W-MON") is False


def test_adjust_ohlc_frequency_dates(capfd):
    # Test with adjusted dates on 1W frequency
    start_datetime = datetime.datetime.strptime(
        "2021-03-28 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    end_datetime = datetime.datetime.strptime(
        "2021-05-04 15:00:00", "%Y-%m-%d %H:%M:%S"
    )
    df_ohlc_not_adjusted = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1W_not_adjusted.csv",
        index_col="time",
        parse_dates=True,
    )
    df_ohlc = adjust_ohlc_frequency_dates(
        start_datetime, end_datetime, "1W-MON", df_ohlc_not_adjusted, "GRTETH"
    )
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1W.csv",
        index_col="time",
        parse_dates=True,
    )
    assert df_ohlc.equals(df_ohlc_test)

    # Test with empty adjusted DataFrame on 1W frequency
    capfd.readouterr()
    adjust_ohlc_frequency_dates(
        start_datetime, end_datetime, "1W-MON", pd.DataFrame(), "GRTETH"
    )
    captured = capfd.readouterr()
    test_output = "GRTETH 1W-MON: Not enough data.\n"
    assert captured.out == test_output

    # Test without adjusted dates on 1H frequency
    df_ohlc_not_adjusted = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1H.csv",
        index_col="time",
        parse_dates=True,
    )
    df_ohlc = adjust_ohlc_frequency_dates(
        start_datetime, end_datetime, "1H", df_ohlc_not_adjusted, "GRTETH"
    )
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1H.csv",
        index_col="time",
        parse_dates=True,
    )
    assert df_ohlc.equals(df_ohlc_test)


def test_trades_to_ohlc():
    df_trades = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00.csv",
        index_col="time",
        parse_dates=True,
    )
    # Test with volume in base asset.
    df_ohlc = trades_to_ohlc(df_trades, "1W-MON", False)
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00"
        "-00_1W_not_adjusted.csv",
        index_col="time",
        parse_dates=True,
    )
    df_ohlc_test.index.freq = "W-MON"
    df_ohlc["volume"] = df_ohlc["volume"].apply(lambda x: int(100 * x))
    df_ohlc_test["volume"] = df_ohlc_test["volume"].apply(lambda x: int(100 * x))
    assert df_ohlc.equals(df_ohlc_test)

    # Test with volume in quote asset
    df_ohlc = trades_to_ohlc(df_trades, "1W-MON", True)
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00"
        "-00_1W_not_adjusted_quote.csv",
        index_col="time",
        parse_dates=True,
    )
    df_ohlc_test.index.freq = "W-MON"
    df_ohlc["volume"] = df_ohlc["volume"].apply(lambda x: int(100 * x))
    df_ohlc_test["volume"] = df_ohlc_test["volume"].apply(lambda x: int(100 * x))
    assert df_ohlc.equals(df_ohlc_test)
