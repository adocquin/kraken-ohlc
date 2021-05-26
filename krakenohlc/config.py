import yaml
import datetime
from typing import TypedDict
from krakenapi import KrakenApi
from .ohlc import pandas_to_kraken_ohlc_frequencies


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
        self.__read_configuration_file(config_file)
        self.__check_configuration()
        self.ohlc_frequencies = pandas_to_kraken_ohlc_frequencies(self.ohlc_frequencies)
        self.ka = KrakenApi()
        self.__get_configuration_pairs()

    def __read_configuration_file(self, config_file: str) -> None:
        """
        Read passed config file assign class attributes.

        :param config_file: Configuration file path as string.
        :return: None
        """
        try:
            with open(config_file, "r") as stream:
                try:
                    config = yaml.load(stream, Loader=yaml.SafeLoader)
                    self.start_datetime = config.get("download_start_date")
                    self.end_datetime = config.get("download_end_date")
                    self.save_trade_history_as_csv = config.get(
                        "save_trade_history_as_csv"
                    )
                    self.download_all_associated_pairs = config.get(
                        "download_all_associated_pairs"
                    )
                    if not self.download_all_associated_pairs.get("enabled"):
                        self.download_custom_pairs = config.get("download_custom_pairs")
                    self.ohlc_frequencies = config.get("ohlc_frequencies")
                except (AttributeError, yaml.YAMLError) as e:
                    raise AttributeError(
                        f"Configuration file incorrectly formatted: {e}"
                    )
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

        try:
            self.start_datetime = datetime.datetime.strptime(
                self.start_datetime, "%Y-%m-%d %H:%M:%S"
            )
        except ValueError as e:
            raise ValueError(f"Download start date incorrectly formatted: {e}")
        try:
            self.end_datetime = datetime.datetime.strptime(
                self.end_datetime, "%Y-%m-%d %H:%M:%S"
            )
        except ValueError as e:
            raise ValueError(f"Download end date incorrectly formatted: {e}")

        if not self.ohlc_frequencies:
            raise ValueError("Please provide ohlcv frequencies.")

        if not self.save_trade_history_as_csv:
            raise ValueError("Please provide save_trade_history value (True or False).")

        if self.download_all_associated_pairs.get("enabled"):
            if not self.download_all_associated_pairs.get("quote_assets"):
                raise ValueError("Please provide quotes assets to download.")
        elif not self.download_custom_pairs:
            raise ValueError("Please provide pairs to download option.")

    def __get_configuration_pairs(self) -> None:
        """
        Set Config list of pairs to download based on configuration options.

        :return: None
        """
        asset_pairs = list(self.ka.get_asset_pairs().keys())
        if self.download_all_associated_pairs.get("enabled"):
            # Download pairs from Kraken
            self.pairs = list()
            quote_assets = self.download_all_associated_pairs.get("quote_assets")
            for quote_asset in quote_assets:
                asset = self.ka.get_asset_altname(quote_asset)
                self.pairs += [pair for pair in asset_pairs if asset in pair]
                if not self.pairs:
                    raise ValueError(
                        f"No tradable pairs available on Kraken for {quote_asset}."
                    )
            # Remove excluded base assets
            self.pairs = [
                pair
                for pair in self.pairs
                if not any(
                    base_asset in pair
                    for base_asset in self.download_all_associated_pairs.get(
                        "excluded_base_assets"
                    )
                )
            ]
        else:
            for pair in self.download_custom_pairs:
                if pair not in asset_pairs:
                    raise ValueError(f"{pair} pair not available on Kraken.")
            self.pairs = self.download_custom_pairs
