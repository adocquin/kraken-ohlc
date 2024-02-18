import datetime
from unittest import mock

import pytest
import vcr
from krakenapi import KrakenApi

from krakenohlc import Config


def test_default_config_file(mock_correct_config):
    # Test if config.yaml has changed.
    with open("config.yaml", "r") as stream:
        config = stream.read()
    assert config == mock_correct_config


@vcr.use_cassette("tests/fixtures/vcr_cassettes/test_config_init_properties.yaml")
def test_config_init_properties(mock_correct_config):
    # Test object properties are correctly assigned.
    # Config with all associated pairs
    config = Config("tests/fixtures/config.yaml")
    assert isinstance(config.start_datetime, datetime.datetime)
    assert config.start_datetime == datetime.datetime.strptime(
        "2021-03-28 00:00:00", "%Y-%m-%d %H:%M:%S"
    )
    assert isinstance(config.end_datetime, datetime.datetime)
    assert config.end_datetime == datetime.datetime.strptime(
        "2021-05-04 15:00:00", "%Y-%m-%d %H:%M:%S"
    )
    assert isinstance(config.save_trade_history_as_csv, bool)
    assert config.save_trade_history_as_csv is True
    assert isinstance(config.download_all_associated_pairs, dict)
    assert config.download_all_associated_pairs.get("enabled") is True
    assert config.download_all_associated_pairs.get("quote_assets") == ["XXBT", "USDT"]
    assert config.download_all_associated_pairs.get("excluded_base_assets") == [
        ".d",
        "ZCAD",
        "ZEUR",
        "ZGBP",
        "ZJPY",
        "ZUSD",
    ]
    assert isinstance(config.ka, KrakenApi)
    assert config.ohlc_frequencies == ["1min", "1h", "4h", "1D"]

    # Config with custom pairs
    config = mock_correct_config
    config_custom_pairs = config.replace("enabled: True", "enabled: False")
    mock_file = mock.mock_open(read_data=config_custom_pairs)
    with mock.patch("builtins.open", mock_file):
        config = Config("tests/fixtures/config.yaml")
    assert config.download_custom_pairs == ["GRTETH", "KEEPXBT"]


def test_read_configuration_file(mock_correct_config, mock_config_error):
    # Test raise FileNotFoundError.
    e_info_value: str = mock_config_error(mock_correct_config, FileNotFoundError)
    assert "Configuration file not found." in e_info_value

    # Test incorrect format
    e_info_value: str = mock_config_error("", AttributeError)
    assert "Configuration file incorrectly formatted:" in e_info_value


def test_check_configuration(mock_correct_config, mock_config_error):
    # Test missing download start date.
    config_missing_api_public_key = mock_correct_config.replace(
        'download_start_date: "2021-03-28 00:00:00"',
        "",
    )
    e_info_value: str = mock_config_error(config_missing_api_public_key, ValueError)
    assert "Please provide a trades download start date." in e_info_value
    # Test missing download end date.
    config_missing_api_public_key = mock_correct_config.replace(
        'download_end_date: "2021-05-04 15:00:00"', ""
    )
    e_info_value = mock_config_error(config_missing_api_public_key, ValueError)
    assert "Please provide a trades download end date." in e_info_value

    # Test start date incorrectly formatted.
    config_bad_download_start_date = mock_correct_config.replace(
        'download_start_date: "2021-03-28 00:00:00"',
        'download_start_date: "21-03-28 00:00:00"',
    )
    e_info_value = mock_config_error(config_bad_download_start_date, ValueError)
    assert "Download start date incorrectly formatted." in e_info_value
    config_bad_download_start_date = mock_correct_config.replace(
        'download_start_date: "2021-03-28 00:00:00"',
        'download_start_date: "2121-03-28 00:00:00"',
    )
    e_info_value = mock_config_error(config_bad_download_start_date, ValueError)
    assert "The start date must be in the past." in e_info_value

    # Test end date incorrectly formatted.
    config_bad_download_end_date = mock_correct_config.replace(
        'download_end_date: "2021-05-04 15:00:00"',
        'download_end_date: "21-05-04 15:00:00"',
    )
    e_info_value = mock_config_error(config_bad_download_end_date, ValueError)
    assert "Download end date incorrectly formatted." in e_info_value

    # Test missing OHLC frequency list
    config_missing_ohlc_frequencies = mock_correct_config.replace(
        "ohlc_frequencies:\n  - 1M\n  - 1H\n  - 4H\n  - 1D", ""
    )
    e_info_value = mock_config_error(config_missing_ohlc_frequencies, ValueError)
    assert "Please provide ohlc frequencies." in e_info_value

    # Test missing volume in quote asset
    config_missing_save_trade_history = mock_correct_config.replace(
        "volume_in_quote_asset: False", ""
    )
    e_info_value = mock_config_error(config_missing_save_trade_history, ValueError)
    assert (
        "Please provide volume_in_quote_asset value " "(True or False)." in e_info_value
    )

    # Test missing save trade history as csv
    config_missing_save_trade_history = mock_correct_config.replace(
        "save_trade_history_as_csv: True", ""
    )
    e_info_value: str = mock_config_error(config_missing_save_trade_history, ValueError)
    assert "Please provide save_trade_history value (True or False)." in e_info_value

    # Test missing quote assets to download
    config_missing_quote_assets = mock_correct_config.replace(
        "  quote_assets:\n    - XXBT\n    - USDT", ""
    )
    e_info_value: str = mock_config_error(config_missing_quote_assets, ValueError)
    assert "Please provide quotes assets to download." in e_info_value

    # Test missing pairs to download option
    config_missing_pairs = mock_correct_config.replace(
        "enabled: True", "enabled: False"
    )
    config_missing_pairs = config_missing_pairs.replace(
        "download_custom_pairs:\n  - GRTETH\n  - KEEPXBT", ""
    )
    e_info_value: str = mock_config_error(config_missing_pairs, ValueError)
    assert "Please provide pairs to download option." in e_info_value


def test_get_configuration_pairs(mock_correct_config, mock_config_error):
    # Test no tradable pairs available for quote asset
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_no_tradable_pairs.yaml"):
        with pytest.raises(ValueError) as e_info:
            Config("tests/fixtures/config.yaml")
        assert "No tradable pairs available on Kraken for " in str(e_info.value)

    # Test pair not available on Kraken
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_pair_not_available.yaml"):
        config_pair_not_available = mock_correct_config.replace(
            "enabled: True", "enabled: False"
        )
        config_pair_not_available = config_pair_not_available.replace(
            "download_custom_pairs:\n  - GRTETH\n  - KEEPXBT",
            "download_custom_pairs:\n  - FAKE",
        )
        e_info_value: str = mock_config_error(config_pair_not_available, ValueError)
        assert "FAKE pair not available on Kraken." in e_info_value
