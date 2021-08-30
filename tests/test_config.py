from unittest import mock
from krakenohlc import Config
import pytest
import datetime
from krakenapi import KrakenApi
import vcr


class TestConfig:
    correct_config: str

    def setup(self):
        # Initialize test reference configuration.
        self.correct_config = self.__get_correct_config()

    @staticmethod
    def __get_correct_config() -> str:
        """
        Open correct config.yaml file in tests/fixtures folder and return content as
        string.
        :return: Correct config.yaml file content as string.
        """
        with open("tests/fixtures/config.yaml", "r") as stream:
            correct_config = stream.read()
        return correct_config

    @staticmethod
    def __mock_config_error(config: str, error_type: type) -> str:
        """
        Mock configuration file error and return the error.
        :param config: Configuration to use as string.
        :param error_type: Raised error type to catch.
        :return: Error value as string.
        """
        mock_file = mock.mock_open(read_data=config)
        with mock.patch("builtins.open", mock_file) as mock_open:
            if error_type == FileNotFoundError:
                mock_open.side_effect = FileNotFoundError()
            with pytest.raises(error_type) as e_info:
                Config("tests/fixtures/config.yaml")
        e_info_value = str(e_info.value)
        return e_info_value

    def test_default_config_file(self):
        # Test if config.yaml has changed.
        with open("config.yaml", "r") as stream:
            config = stream.read()
        assert config == self.correct_config

    def test_config_init_properties(self):
        # Test object properties are correctly assigned.
        # Config with all associated pairs
        config = Config("tests/fixtures/config.yaml")
        assert type(config.start_datetime) == datetime.datetime
        assert config.start_datetime == datetime.datetime.strptime(
            "2021-03-28 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
        assert type(config.end_datetime) == datetime.datetime
        assert config.end_datetime == datetime.datetime.strptime(
            "2021-05-04 15:00:00", "%Y-%m-%d %H:%M:%S"
        )
        assert type(config.save_trade_history_as_csv) == bool
        assert config.save_trade_history_as_csv is True
        assert type(config.download_all_associated_pairs) == dict
        assert config.download_all_associated_pairs.get("enabled") is True
        assert config.download_all_associated_pairs.get("quote_assets") == ["XBT"]
        assert config.download_all_associated_pairs.get("excluded_base_assets") == [
            ".d",
            "ZCAD",
            "ZEUR",
            "ZGBP",
            "ZJPY",
            "ZUSD",
        ]
        assert type(config.ka) == KrakenApi
        assert type(config.ohlc_frequencies) == list
        assert config.ohlc_frequencies == ["1H", "4H", "1D", "1M"]

        # Config with custom pairs
        config = self.__get_correct_config()
        config_custom_pairs = config.replace("enabled: True", "enabled: False")
        mock_file = mock.mock_open(read_data=config_custom_pairs)
        with mock.patch("builtins.open", mock_file):
            config = Config("tests/fixtures/config.yaml")
        assert type(config.download_custom_pairs) == list
        assert config.download_custom_pairs == ["GRTETH", "KEEPXBT"]

    def test_read_configuration_file(self):
        # Test raise FileNotFoundError.
        e_info_value = self.__mock_config_error(self.correct_config, FileNotFoundError)
        assert e_info_value == "Configuration file not found."

        # Test incorrect format
        e_info_value = self.__mock_config_error("", AttributeError)
        assert "Configuration file incorrectly formatted:" in e_info_value

    def test_check_configuration(self):
        # Test missing download start date.
        config_missing_api_public_key = self.correct_config.replace(
            'download_start_date: "2021-03-28 00:00:00"',
            "",
        )
        e_info_value = self.__mock_config_error(
            config_missing_api_public_key, ValueError
        )
        assert e_info_value == "Please provide a trades download start date."
        # Test missing download end date.
        config_missing_api_public_key = self.correct_config.replace(
            'download_end_date: "2021-05-04 15:00:00"', ""
        )
        e_info_value = self.__mock_config_error(
            config_missing_api_public_key, ValueError
        )
        assert e_info_value == "Please provide a trades download end date."

        # Test start date incorrectly formatted.
        config_bad_download_start_date = self.correct_config.replace(
            'download_start_date: "2021-03-28 00:00:00"',
            'download_start_date: "21-03-28 00:00:00"',
        )
        e_info_value = self.__mock_config_error(
            config_bad_download_start_date, ValueError
        )
        assert "Download start date incorrectly formatted:" in e_info_value
        # Test end date incorrectly formatted.
        config_bad_download_end_date = self.correct_config.replace(
            'download_end_date: "2021-05-04 15:00:00"',
            'download_end_date: "21-05-04 15:00:00"',
        )
        e_info_value = self.__mock_config_error(
            config_bad_download_end_date, ValueError
        )
        assert "Download end date incorrectly formatted:" in e_info_value

        # Test missing OHLC frequency list
        config_missing_ohlc_frequencies = self.correct_config.replace(
            "ohlc_frequencies:\n  - 1H\n  - 4H\n  - 1D\n  - 1M", ""
        )
        e_info_value = self.__mock_config_error(
            config_missing_ohlc_frequencies, ValueError
        )
        assert e_info_value == "Please provide ohlcv frequencies."

        # Test missing save trade history as csv
        config_missing_save_trade_history = self.correct_config.replace(
            "save_trade_history_as_csv: True", ""
        )
        e_info_value = self.__mock_config_error(
            config_missing_save_trade_history, ValueError
        )
        assert (
            e_info_value == "Please provide save_trade_history value (True or False)."
        )

        # Test missing quote assets to download
        config_missing_quote_assets = self.correct_config.replace(
            "  quote_assets:\n    - XBT", ""
        )
        e_info_value = self.__mock_config_error(config_missing_quote_assets, ValueError)
        assert e_info_value == "Please provide quotes assets to download."

        # Test missing pairs to download option
        config_missing_pairs = self.correct_config.replace(
            "enabled: True", "enabled: False"
        )
        config_missing_pairs = config_missing_pairs.replace(
            "download_custom_pairs:\n  - GRTETH\n  - KEEPXBT", ""
        )
        e_info_value = self.__mock_config_error(config_missing_pairs, ValueError)
        assert e_info_value == "Please provide pairs to download option."

    def test_get_configuration_pairs(self):
        # Test no tradable pairs available for quote asset
        with vcr.use_cassette(
            "tests/fixtures/vcr_cassettes/test_no_tradable_pairs" ".yaml"
        ):
            with pytest.raises(ValueError) as e_info:
                Config("tests/fixtures/config.yaml")
            assert "No tradable pairs available on Kraken for " in str(e_info.value)

        # Test pair not available on Kraken
        with vcr.use_cassette(
            "tests/fixtures/vcr_cassettes/test_pair_not_available" ".yaml"
        ):
            config_pair_not_available = self.correct_config.replace(
                "enabled: True", "enabled: False"
            )
            config_pair_not_available = config_pair_not_available.replace(
                "download_custom_pairs:\n  - GRTETH\n  - KEEPXBT",
                "download_custom_pairs:\n  - FAKE",
            )
            e_info_value = self.__mock_config_error(
                config_pair_not_available, ValueError
            )
            assert e_info_value == "FAKE pair not available on Kraken."

