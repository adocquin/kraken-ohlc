import logging

import pandas as pd

from .config import Config
from .io import create_data_directory, define_filepath, read_csv
from .ohlc import adjust_ohlc_frequency_dates, trades_to_ohlc
from .trades import download_trades

logger: logging.Logger = logging.getLogger(__name__)


def handle_pair_trades(
    pair: str, config: Config, data_folder_path: str
) -> pd.DataFrame:
    """
    If does not exist yet, download trade history for specified pair and
    configuration and save it as pandas DataFrame.

    :param pair: Pair to download trade history.
    :param config: Config object.
    :param data_folder_path: Data folder path as string.
    :return: Pair trade history as pandas DataFrame.
    """
    # Get pair trades
    trades_filepath = define_filepath(
        "trade_history", pair, config.start_datetime, config.end_datetime
    )
    df_trades = read_csv(data_folder_path + "/" + trades_filepath)
    if df_trades.empty:
        df_trades = download_trades(
            config.ka, pair, config.start_datetime, config.end_datetime
        )
        if config.save_trade_history_as_csv:
            df_trades.to_csv(data_folder_path + "/" + trades_filepath)
            logger.info(f"{pair}: Trades saved to {trades_filepath}.")
    else:
        logger.info(f"{pair}: Trades already existing at {trades_filepath}.")
    return df_trades


def handle_pair_frequency_ohlc(
    pair: str,
    config: Config,
    df_trades: pd.DataFrame,
    frequency: str,
    data_folder_path: str,
) -> None:
    """
    If does not exist yet, create OHLC DataFrame and save it as CSV for specified
    pair and frequency from trades DataFrame.

    :param pair: Pair to generate OHLC.
    :param config: Config object.
    :param df_trades: Pair trades as pandas DataFrame.
    :param frequency: OHLC frequency as string.
    :param data_folder_path: Data folder path as string.
    :return: None
    """
    ohlc_filepath = define_filepath(
        "ohlc",
        pair,
        config.start_datetime,
        config.end_datetime,
        frequency,
        config.volume_in_quote_asset,
    )
    df_ohlc = read_csv(data_folder_path + "/" + ohlc_filepath)
    if df_ohlc.empty:
        # Convert trade history to ohlc for specified frequency
        df_ohlc = trades_to_ohlc(df_trades, frequency, config.volume_in_quote_asset)
        df_ohlc = adjust_ohlc_frequency_dates(
            config.start_datetime, config.end_datetime, frequency, df_ohlc, pair
        )
        if not df_ohlc.empty:
            df_ohlc.to_csv(data_folder_path + "/" + ohlc_filepath)
            frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
            logger.info(f"{pair} {frequency}: Saved to {ohlc_filepath}.")
    else:
        frequency = frequency.replace("T", "M").replace("1W-MON", "1W")
        logger.info(f"{pair} {frequency}: Already existing at {ohlc_filepath}.")


def kraken_ohlc(data_folder_path: str) -> None:
    """
    Kraken OHLC main loop, call loops for pair download and ohlc generation.

    :param data_folder_path: Data folder path as string.
    :return: None
    """
    create_data_directory(data_folder_path)
    config = Config("config.yaml")

    for pair in config.pairs:
        df_trades = handle_pair_trades(pair, config, data_folder_path)
        for frequency in config.ohlc_frequencies:
            handle_pair_frequency_ohlc(
                pair, config, df_trades, frequency, data_folder_path
            )
