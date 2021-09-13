# Kraken OHLC
For specified dates, pairs and frequencies, download trades from
[Kraken](https://kraken.com) exchange
[public API](https://www.kraken.com/u/security/api), aggregate OHLC data and save it 
as CSV.

# Output
Kraken OHLC will create two folders at specified path: **trade_history** and **ohlc**.

#### Structure example

```
data
└───ohlc
│   │   AAVEXBT_2021-05-04T13-00-00_2021-05-04T15-00-00_1H.csv
│   │   ADAXBT_2021-05-04T13-00-00_2021-05-04T15-00-00_1H.csv
│   
└───trade_history
    │   AAVEXBT_2021-05-04T13-00-00_2021-05-04T15-00-00.csv
    │   ADAXBT_2021-05-04T13-00-00_2021-05-04T15-00-00.csv
```

### OHLC data
For specified pairs and frequencies in configuration files, OHLC dataframes will be 
created and saved as CSV in **ohlc** folder.<br>
OHLC are saved with name *PAIR_DOWNLOAD_START_DATE_DOWNLOAD_END_DATE_FREQUENCY.csv*.<br>
By default the volume is aggregated by the base asset, if you want to aggregate it 
with the quote asset set *volume_in_quote_asset* to *True* in configuration file.
OHLC will then by savec in *PAIR_DOWNLOAD_START_DATE_DOWNLOAD_END_DATE_FREQUENCY_quote.
csv* format.
Dates are in *YYYY-MM-DDTHH-MI-Sec* format.

If OHLC file for specific configuration already exist, it will not be generated again.

#### OHLC CSV example

|time                         |open    |high      |low|close|volume            |
|-----------------------------|--------|----------|---|-----|------------------|
|2021-05-04 13:00:00          |0.008945|0.009032  |0.008909|0.008909|102.95793562      |
|2021-05-04 14:00:00          |0.008891|0.008891  |0.008621|0.008697|46.800853210000014|

### Trade history data
If enabled in configuration file, downloaded trades will be saved as CSV in 
*trade_history* folder.<br>
Trades are saved with name *PAIR_DOWNLOAD_START_DATE_DOWNLOAD_END_DATE.csv*.<br>
Dates are in *YYYY-MM-DDTHH-MI-Sec* format.

If trade history file for specific configuration already exist, it will not be 
downloaded again.

#### Trade history CSV example

|time                         |price   |volume    |buy/sell|market/limit|miscellaneous|
|-----------------------------|--------|----------|--------|------------|-------------|
|2021-05-04 13:02:18.454200064|0.008945|0.08562438|s       |l           |             |
|2021-05-04 13:04:50.460200192|0.008927|0.08579703|s       |l           |             |
|2021-05-04 13:17:37.996599808|0.008975|0.08579703|b       |l           |             |



# Configuration file
Configuration file example:
https://github.com/FuturBroke/kraken-ohlc/blob/main/config.yaml

### Parameters:
- **download_start_date**: Trades download start date, must be in *YYYY-MM-DD HH:MI:Sec*
  format.
- **download_end_date**: Trades download end date, must be in *YYYY-MM-DD HH:MI:Sec*
  format.
- **ohlc_frequencies**: List OHLC frequencies aggregate trades data. Supported 
  frequencies are: *1M*, *3M*, *5M*, *15M*, *30M*, *1H*, *2H*, *4H*, *6H*, *8H*, *12H*,
  *1D*, *3D*, *1W*.
- **volume_in_quote_asset**: true if you want to aggregate the volume by the quote 
  asset.
- **save_trade_history**: *True* if you want to save downloaded trades as CSV in a 
  *trade_history* folder, *False* otherwise.
  
**download_all_associated_pairs:**
  - **enabled**: *True* if download all pairs associated to specified quote asset 
    excepted excluded base assets, *False* otherwise.
  - **quote_assets**: List of quote assets to download pairs.
  - **excluded_base_assets**: List of quote assets to exclude from downloaded pairs.

- **download_custom_pairs**: List of pairs to download if *enabled* in 
  *download_all_associated_pairs* is *False*.

# How to run it
## Docker image
You can download the image directly from [Docker Hub](https://hub.docker.com/) using:
```sh
docker pull futurbroke/kraken-ohlc:latest
```
To start the container with restart as system reboot use:
```sh
docker run -v CONFIGURATION_FILE_PATH:/app/config.yaml \
 -v DATA_FOLDER_PATH:/app/data \
 --name kraken-ohlc \
 --restart=on-failure futurbroke/kraken-ohlc
```
- **CONFIGURATION_FILE_PATH**: Configuration folder filepath (e.g., *~/dev/config.yaml*).
- **DATA_FOLDER_PATH**: Data folder for downloaded trades and OHLC CSV (e.g., 
  *~/dev/data/*).

To see container logs:
```sh
docker logs kraken-ohlc
```
To stop and delete the container:
```sh
docker kill kraken-ohlc
docker rm kraken-ohlc
```

## Usage without Docker
You must specify your configuration in a *config.yaml* file in the *Kraken-OHLC* root 
folder.<br>

Install python plugins requirements inside repository folder using:
```sh
python -m pip install -r requirements.txt
```
You can launch the program from the folder where you downloaded the repository folder using:
```sh
python kraken-ohlc
```
Or inside Kraken-OHLC repository directory using:
```sh
python __main__.py
```

## License
[GPL-3.0](https://github.com/FuturBroke/kraken-ohlc/blob/main/README.md)

# How to contribute
Thanks for your interest in contributing to the project. You can contribute freely by
creating an issue, fork or create a pull request. Before issuing a pull request, make
sure the changes did not break any existing functionality by running unit tests in the 
base directory:
```sh
pytest
```