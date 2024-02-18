import logging
import os
import shutil
from unittest.mock import patch

import pandas as pd
import pytest
import vcr

from krakenohlc import handle_pair_frequency_ohlc, handle_pair_trades, kraken_ohlc


@pytest.fixture
def cleandir(mock_test_data_path):
    # Create test output directories
    os.mkdir(mock_test_data_path)
    os.mkdir(mock_test_data_path + "/trade_history")
    os.mkdir(mock_test_data_path + "/ohlc")
    yield
    shutil.rmtree(mock_test_data_path)


@pytest.mark.usefixtures("cleandir")
def test_handle_pair_trades(
    caplog, mock_pair, mock_config, mock_test_data_path, mock_df_trade
):
    # Test trades DataFrame was correctly saved and is return
    caplog.set_level(logging.INFO)
    df_trades_read = handle_pair_trades(mock_pair, mock_config, mock_test_data_path)
    assert df_trades_read.shape == mock_df_trade.shape
    test_output = (
        "GRTETH: Trades already existing at "
        "trade_history/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00"
        ".csv.\n"
    )
    assert test_output in caplog.text


@pytest.mark.usefixtures("cleandir")
def test_handle_pair_frequency_ohlc(
    caplog, mock_pair, mock_config, mock_df_trade, mock_test_data_path
):
    caplog.set_level(logging.INFO)
    # Test OHLC DataFrames are correctly generated and saved
    frequencies = [
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
    for frequency in frequencies:
        handle_pair_frequency_ohlc(
            mock_pair, mock_config, mock_df_trade, frequency, mock_test_data_path
        )
        frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
        df_ohlc = pd.read_csv(
            f"{mock_test_data_path}/ohlc/GRTETH_2021-03-28T00-00-00_2021-05-04T15"
            f"-00-00_{frequency}.csv",
            index_col="time",
            parse_dates=True,
        )
        df_ohlc_test = pd.read_csv(
            f"tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00"
            f"-00_{frequency}.csv",
            index_col="time",
            parse_dates=True,
        )
        pd.testing.assert_frame_equal(df_ohlc, df_ohlc_test)

    # Test OHLC DataFrames aren't created again if already existing.
    for frequency in frequencies:
        handle_pair_frequency_ohlc(
            mock_pair, mock_config, mock_df_trade, frequency, mock_test_data_path
        )
        frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
        test_output = (
            f"GRTETH {frequency}: Already existing at ohlc/GRTETH_2021-"
            f"03-28T00-00-00_2021-05-04T15-00-00_{frequency}.csv.\n"
        )
        assert test_output in caplog.text


@vcr.use_cassette("tests/fixtures/vcr_cassettes/test_kraken_ohlc.yaml")
def test_kraken_ohlc(mock_test_data_path):
    with patch(
        "krakenohlc.krakenohlc.create_data_directory", return_value=None
    ) as mock_create_data_directory, patch(
        "krakenohlc.krakenohlc.handle_pair_trades", return_value=None
    ) as mock_handle_pair_trades, patch(
        "krakenohlc.krakenohlc.handle_pair_frequency_ohlc", return_value=None
    ) as mock_fake_handle_pair_frequency_ohlc:
        kraken_ohlc(mock_test_data_path)
        mock_create_data_directory.assert_called_once_with(mock_test_data_path)
        assert mock_handle_pair_trades.call_count == 91
        assert mock_fake_handle_pair_frequency_ohlc.call_count == 364
