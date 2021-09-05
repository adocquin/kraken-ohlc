import pytest
import datetime
import pandas as pd
from krakenohlc import (
    pandas_to_kraken_ohlc_frequencies,
    check_trades_ohlc_start_end_dates,
    adjust_ohlc_frequency_dates,
    trades_to_ohlc,
)


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
        "1T",
        "3T",
        "5T",
        "15T",
        "30T",
        "1H",
        "2H",
        "4H",
        "6H",
        "8H",
        "12H",
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
    start_datetime = pd.to_datetime(
        datetime.datetime.strptime("2021-03-28 00:00:00", "%Y-%m-%d %H:%M:%S")
    )
    end_datetime = pd.to_datetime(
        datetime.datetime.strptime("2021-05-04 15:00:00", "%Y-%m-%d %H:%M:%S")
    )
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "1T")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "1T")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "3T")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "3T")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "5T")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "5T")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "15T")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "15T")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "30T")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "30T")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "1H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "1H")
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "2H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "2H") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "4H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "4H") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "6H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "6H") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "8H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "8H") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "12H")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "12H") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "1D")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "1D") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "3D")
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "3D") is False
    assert check_trades_ohlc_start_end_dates(start_datetime, True, "1W-MON") is False
    assert check_trades_ohlc_start_end_dates(end_datetime, True, "1W-MON") is False


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
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1W_not_adjusted.csv"
    )
    df_ohlc = adjust_ohlc_frequency_dates(start_datetime,
                                          end_datetime,
                                          "1W-MON",
                                          df_ohlc_not_adjusted,
                                          "GRTETH")
    df_ohlc.reset_index(drop=True, inplace=True)
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1W.csv"
    )
    assert df_ohlc.equals(df_ohlc_test)

    # Test with empty adjusted DataFrame on 1W frequency
    df_ohlc_not_adjusted = df_ohlc_not_adjusted.iloc[[0, -1]].reset_index(drop=True)
    capfd.readouterr()
    df_ohlc = adjust_ohlc_frequency_dates(start_datetime,
                                          end_datetime,
                                          "1W-MON",
                                          df_ohlc_not_adjusted,
                                          "GRTETH")
    captured = capfd.readouterr()
    test_output = "GRTETH 1W-MON: Not enough data.\n"
    assert captured.out == test_output

    # Test without adjusted dates on 1H frequency
    df_ohlc_not_adjusted = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1H.csv"
    )
    df_ohlc = adjust_ohlc_frequency_dates(start_datetime,
                                          end_datetime,
                                          "1H",
                                          df_ohlc_not_adjusted,
                                          "GRTETH")
    df_ohlc.reset_index(drop=True, inplace=True)
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/"
        "GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00_1H.csv"
    )
    assert df_ohlc.equals(df_ohlc_test)


def test_trades_to_ohlc():
    df_trades = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00.csv",
        index_col="time",
        parse_dates=True
    )
    df_ohlc = trades_to_ohlc(df_trades, "1W-MON")
    df_ohlc_test = pd.read_csv(
        "tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00"
        "-00_1W_not_adjusted"
        ".csv",
        index_col="time",
        parse_dates=True
    )
    df_ohlc_test.index.freq = "W-MON"
    df_ohlc['volume'] = df_ohlc['volume'].apply(lambda x: int(100 * x))
    df_ohlc_test['volume'] = df_ohlc_test['volume'].apply(lambda x: int(100 * x))
    assert df_ohlc.equals(df_ohlc_test)
