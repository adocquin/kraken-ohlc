from krakenohlc import define_filepath, read_csv, create_data_directory
import os
import pandas as pd
import pytest


def test_define_filepath():
    # Assert filepath generation for OHLC data
    correct_filepath = "ohlc/AAVEXBT_2020-03-28T00-00-00_2021-05-04T15-00-00_4H.csv"
    filepath = define_filepath(
        "ohlc", "AAVEXBT", "2020-03-28 00:00:00", "2021-05-04 " "15:00:00", "4H"
    )
    assert filepath == correct_filepath

    # Assert path generation for trade history data
    correct_filepath = (
        "trade_history/AAVEXBT_2020-03-28T00-00-00_2021-05-04T15-00-00.csv"
    )
    filepath = define_filepath(
        "trade_history", "AAVEXBT", "2020-03-28 00:00:00", "2021-05-04 " "15:00:00"
    )
    assert filepath == correct_filepath


def test_read_csv(tmpdir):
    # Empty DataFrame when file not fount
    df = read_csv("missing.csv")
    assert df.empty

    # Empty DataFrame on empty file
    df_path = tmpdir.join("empty.csv")
    df_path.write("")
    df = read_csv(df_path)
    assert df.empty

    # Raise value error when parsing error
    df_path = tmpdir.join("parsing_error.csv")
    df_path.write("column\n,1,,")
    with pytest.raises(ValueError) as e_info:
        read_csv(df_path)
    assert f"Can't read csv at {df_path}" in str(e_info.value)

    # Raise value error when directory
    with pytest.raises(ValueError) as e_info:
        read_csv(tmpdir)
    assert f"Can't read csv at {tmpdir}" in str(e_info.value)

    # Raise value error when no time column
    df_content = pd.DataFrame(
        data=[[1, 2], [1, 2]], columns=["first_col", "second_col"]
    )
    csv_path = tmpdir.join("df_test.csv")
    df_content.to_csv(csv_path)
    with pytest.raises(ValueError) as e_info:
        read_csv(csv_path)
    assert f"Can't read csv at {csv_path}" in str(e_info.value)


def test_create_data_directory(request):
    os.chdir(request.fspath.dirname)

    # Check directory creation
    create_data_directory()
    assert os.path.exists("data/ohlc") == 1
    assert os.path.exists("data/trade_history") == 1

    # Check no error when directories already exist
    create_data_directory()

    os.chdir(request.config.invocation_dir)
    assert 1 == 1
