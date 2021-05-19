import yaml
import datetime
from typing import TypedDict
from krakenapi import KrakenApi


class DownloadAllAssociatedPairs(TypedDict):
    """
    download_all_associated_pairs config option dictionary hint typing.
    """

    enabled: bool
    quote_assets: list
    excluded_base_assets: list


class Config:
    """
    Configuration object based on configuration file.
    """

    start_datetime = datetime.datetime
    end_datetime = datetime.datetime
    save_trade_history_as_csv: bool
    download_all_associated_pairs: DownloadAllAssociatedPairs
    download_custom_pairs: list
    ka: KrakenApi
    pairs: list
    ohlc_frequencies: list

    def __init__(self, config_file: str) -> None:
        """
        Initialize the Config object.

        :param config_file: Configuration file path as string.
        """
        self.__read_config_file(config_file)
        self.__check_configuration()
        self.__handle_ohlc_frequencies()
        self.ka = KrakenApi()
        self.__get_config_pairs()

    def __read_config_file(self, config_file: str) -> None:
        """
        Read passed config file assign class attributes.

        :param config_file: COnfiguration file path as string.
        :return: None
        """
        try:
            with open(config_file, "r") as stream:
                try:
                    config = yaml.load(stream, Loader=yaml.SafeLoader)
                    self.start_datetime = datetime.datetime.strptime(
                        config.get("download_start_date"), "%Y-%m-%d %H:%M:%S"
                    )
                    self.end_datetime = datetime.datetime.strptime(
                        config.get("download_end_date"), "%Y-%m-%d " "%H:%M:%S"
                    )
                    self.save_trade_history_as_csv = config.get(
                        "save_trade_history_as_csv"
                    )
                    self.download_all_associated_pairs = config.get(
                        "download_all_associated_pairs"
                    )
                    if not self.download_all_associated_pairs.get("enabled"):
                        self.download_custom_pairs = config.get("download_custom_pairs")
                    self.ohlc_frequencies = config.get("ohlc_frequencies")
                except (ValueError, TypeError, AttributeError, yaml.YAMLError) as e:
                    raise ValueError(f"Configuration file incorrectly formatted: {e}")
        except EnvironmentError:
            raise FileNotFoundError("Configuration file not found.")

    def __check_configuration(self) -> None:
        """
        Check configuration object attributes values.

        :return: None
        """
        if not self.start_datetime:
            raise ValueError("Please provide a trades download start date.")
        if not self.end_datetime:
            raise ValueError("Please provide a trades download end date.")
        if not self.save_trade_history_as_csv:
            raise ValueError("Please provide save_trade_history value (True or False).")
        if self.download_all_associated_pairs.get("enabled"):
            if not self.download_all_associated_pairs.get("quote_assets"):
                raise ValueError("Please provide quotes assets to download.")
        if (
            not self.download_all_associated_pairs.get("enabled")
            and not self.download_custom_pairs
        ):
            raise ValueError("Please provide pairs to download option.")
        if not self.ohlc_frequencies:
            raise ValueError("Please provide ohlcv frequencies.")

    def __handle_ohlc_frequencies(self) -> None:
        """
        Convert configuration file frequencies to pandas frequencies format.

        :return: None
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
        for frequency in self.ohlc_frequencies:
            if frequency not in supported_frequencies:
                raise ValueError(
                    f"Unsupported frequency {frequency}. Supported "
                    f"frequencies: {supported_frequencies}"
                )
            frequency.replace("M", "T").replace("1W", "1W-MON")
            frequencies.append(frequency)
        self.ohlc_frequencies = frequencies

    def __get_config_pairs(self) -> None:
        """
        Set list of pairs to download from based on Config attributes.

        :return: None
        """
        pairs = list()
        asset_pairs = list(self.ka.get_asset_pairs().keys())

        if self.download_all_associated_pairs.get("enabled"):
            quote_assets = self.download_all_associated_pairs.get("quote_assets")
            for quote_asset in quote_assets:
                asset = self.ka.get_asset_altname(quote_asset)
                pairs += [pair for pair in asset_pairs if asset in pair]
                if not pairs:
                    raise ValueError(
                        f"No tradable pairs available on Kraken for {quote_asset}."
                    )
        else:
            for pair in self.download_custom_pairs:
                if pair not in asset_pairs:
                    raise ValueError(f"{pair} pair not available on Kraken.")
            pairs = self.download_custom_pairs

        pairs = [
            pair
            for pair in pairs
            if not any(
                base_asset in pair
                for base_asset in self.download_all_associated_pairs.get(
                    "excluded_base_assets"
                )
            )
        ]
        self.pairs = pairs
