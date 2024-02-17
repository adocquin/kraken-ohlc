"""Tests fixtures."""

import os
import shutil
from typing import Callable
from unittest import mock

import pandas as pd
import pytest
import vcr
from krakenapi import KrakenApi

from krakenohlc import Config, handle_pair_trades


@pytest.fixture
def mock_correct_config() -> str:
    """
    Open correct config.yaml file in tests/fixtures folder and return
    content as  string.

    Returns:
        str: Correct config.yaml file content.
    """
    with open("tests/fixtures/config.yaml", "r") as stream:
        correct_config: str = stream.read()
    return correct_config


@pytest.fixture
def mock_config_error() -> Callable[[str, type], str]:
    """
    Mock configuration file error and return the error.

    Returns:
        Callable[[str, type], str]: Mock configuration file error and
            return the error.
    """

    def _mock_config_error(config: str, error_type: type) -> str:
        """
        Mock configuration file error and return the error.

        Args:
            config (str): Configuration file content.
            error_type (type): Error type.

        Returns:
            str: Error message.
        """
        mock_file: mock.Mock = mock.mock_open(read_data=config)
        with mock.patch("builtins.open", mock_file) as mock_open:
            if error_type == FileNotFoundError:
                mock_open.side_effect = FileNotFoundError()
            with pytest.raises(error_type) as e_info:
                Config("tests/fixtures/config.yaml")
        e_info_value: str = str(e_info.value)
        return e_info_value

    return _mock_config_error


@pytest.fixture
def mock_config() -> Config:
    """
    Mock the Config object.

    Returns:
        Config: Mocked Config object.
    """
    config: Config = Config("tests/fixtures/config.yaml")
    config.ka = KrakenApi()
    return config


@pytest.fixture
def mock_pair() -> str:
    """
    Get a mock pair.

    Returns:
        str: The mock pair.
    """
    return "GRTETH"


@pytest.fixture
def mock_test_data_path() -> str:
    """
    Get the test data path.

    Returns:
        str: The test data path.
    """
    return "tests/fixtures/data"


@pytest.fixture
@vcr.use_cassette("tests/fixtures/vcr_cassettes/krakenohlc_setup.yaml")
def mock_df_trade(mock_pair, mock_config, mock_test_data_path) -> pd.DataFrame:
    df_trade: pd.DataFrame = handle_pair_trades(
        mock_pair, mock_config, mock_test_data_path
    )
    return df_trade


@pytest.fixture
def cleandir(mock_test_data_path):
    # Create test output directories
    os.mkdir(mock_test_data_path)
    os.mkdir(mock_test_data_path + "/trade_history")
    os.mkdir(mock_test_data_path + "/ohlc")
    yield
    shutil.rmtree(mock_test_data_path)
