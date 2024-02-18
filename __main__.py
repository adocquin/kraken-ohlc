import logging

from krakenohlc import kraken_ohlc

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s:%(name)s: %(message)s",
        level=logging.INFO,
    )
    kraken_ohlc("data")
