import os
import shutil
import pytest
import pandas as pd
import vcr
from unittest.mock import patch
from krakenohlc import (
    Config,
    handle_pair_trades,
    handle_pair_frequency_ohlc,
    kraken_ohlc,
)
from krakenapi import KrakenApi

TEST_DATA_PATH: str = "tests/fixtures/data"


@pytest.fixture
def cleandir():
    # Create test output directories
    os.mkdir(TEST_DATA_PATH)
    os.mkdir(TEST_DATA_PATH + "/trade_history")
    os.mkdir(TEST_DATA_PATH + "/ohlc")
    yield
    shutil.rmtree(TEST_DATA_PATH)


@pytest.mark.usefixtures("cleandir")
class TestKrakrenOHLC:
    config: Config
    pair: str = "GRTETH"
    df_trades = pd.DataFrame

    @vcr.use_cassette("tests/fixtures/vcr_cassettes/test_handle_pair_trades.yaml")
    def setup(self):
        # Config object creation
        self.config = Config("tests/fixtures/config.yaml")
        self.config.ka = KrakenApi()
        # Test trades download and DataFrame creation
        self.df_trades = handle_pair_trades(self.pair, self.config, TEST_DATA_PATH)

    def test_handle_pair_trades(self, capfd):
        # Test trades DataFrame was correctly saved and is return
        capfd.readouterr()
        df_trades_read = handle_pair_trades(self.pair, self.config, TEST_DATA_PATH)
        assert df_trades_read.shape == self.df_trades.shape
        captured = capfd.readouterr()
        test_output = (
            "GRTETH: Trades already existing at "
            "trade_history/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00-00"
            ".csv.\n"
        )
        assert captured.out == test_output

    def test_handle_pair_frequency_ohlc(self, capfd):
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
                self.pair, self.config, self.df_trades, frequency, TEST_DATA_PATH
            )
            frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
            df_ohlc = pd.read_csv(
                f"{TEST_DATA_PATH}/ohlc/GRTETH_2021-03-28T00-00-00_2021-05-04T15"
                f"-00-00_{frequency}.csv"
                , index_col="time"
                , parse_dates=True
            )
            df_ohlc_test = pd.read_csv(
                f"tests/fixtures/tests_data/GRTETH_2021-03-28T00-00-00_2021-05-04T15-00"
                f"-00_{frequency}.csv"
                , index_col="time"
                , parse_dates=True
            )
            assert df_ohlc.equals(df_ohlc_test)

        # Test OHLC DataFrames aren't created again if already existing.
        for frequency in frequencies:
            capfd.readouterr()
            handle_pair_frequency_ohlc(
                self.pair, self.config, self.df_trades, frequency, TEST_DATA_PATH
            )
            captured = capfd.readouterr()
            frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
            test_output = (
                f"GRTETH {frequency}: Already existing at ohlc/GRTETH_2021-"
                f"03-28T00-00-00_2021-05-04T15-00-00_{frequency}.csv.\n"
            )
            assert captured.out == test_output

    @staticmethod
    def fake_create_data_directory(data_folder_path: str):
        return

    @staticmethod
    def fake_handle_pair_trades(
        pair: str,
        config: Config,
        data_folder_path: str,
    ):
        return

    @staticmethod
    def fake_handle_pair_frequency_ohlc(
        pair: str,
        config: Config,
        df_trades: pd.DataFrame,
        frequency: str,
        data_folder_path: str,
    ):
        return

    @vcr.use_cassette("tests/fixtures/vcr_cassettes/test_kraken_ohlc.yaml")
    def test_kraken_ohlc(self):
        with patch(
            "krakenohlc.krakenohlc.create_data_directory", wraps=self.fake_create_data_directory
        ) as mock_create_data_directory, patch(
            "krakenohlc.krakenohlc.handle_pair_trades",
            wraps=self.fake_handle_pair_trades,
        ) as mock_handle_pair_trades, patch(
            "krakenohlc.krakenohlc.handle_pair_frequency_ohlc",
            wraps=self.fake_handle_pair_frequency_ohlc,
        ) as mock_fake_handle_pair_frequency_ohlc:
            kraken_ohlc(TEST_DATA_PATH)
            mock_create_data_directory.assert_called_once_with(TEST_DATA_PATH)
            assert mock_handle_pair_trades.call_count == 73
            assert mock_fake_handle_pair_frequency_ohlc.call_count == 292
