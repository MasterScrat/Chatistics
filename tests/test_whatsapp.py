# Install pytest and run tests from project root with `python -m pytest`
import os
from parsers.whatsapp import parse_messages
from parsers.config import config
import pandas as pd
from datetime import datetime


TEST_DATA_LOCATION = os.path.join('tests', 'test_data', 'whatsapp')

ground_truth_chat1 = {
        'text': [
            "This is a test message",
            "This message is from Alice Placeholder",
            "This is a test answer from John Doe",
            'This message should have "outgoing = True", as John Doe is the person exporting their logs in this test scenario',
            'This message should have "outgoing = False"',
            "The following messages will test some corner cases"
            ],
        'outgoing': [False, False, True, True, False, True],
        'senderName': ['Alice Placeholder', 'Alice Placeholder', 'John Doe', 'John Doe', 'Alice Placeholder', 'John Doe']
        }

ground_truth_chat2 = {
        'datetime': [
            datetime(2019, 9, 17, 16, 37, 47),
            datetime(2019, 9, 17, 16, 38, 6),
            datetime(2019, 9, 17, 16, 38, 59),
            datetime(2019, 9, 17, 16, 39, 52),
            ]
        }

ground_truth_chat3 = {
        'datetime': [
            datetime(2019, 2, 11, 14, 18),
            datetime(2019, 2, 11, 14, 21),
            datetime(2019, 2, 11, 14, 21),
            datetime(2019, 2, 11, 14, 21),
            datetime(2019, 2, 11, 14, 22),
            datetime(2019, 2, 11, 14, 25),
            datetime(2019, 2, 11, 14, 33),
            datetime(2019, 2, 11, 14, 48),
            datetime(2019, 2, 11, 14, 51),
            ]
        }


def test_parse_chat_info_chat1():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat.txt')], 'John Doe')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat1)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.text == df_truth.iloc[i].text
        assert row.outgoing == df_truth.iloc[i].outgoing  # using `is` doesn't work here (bool vs. np.bool)
        assert row.senderName == df_truth.iloc[i].senderName

def test_parse_eu_datetime_chat2():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat 2.txt')], 'John Doe')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat2)
    assert len(df_truth) == len(df)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.timestamp == df_truth.iloc[i].datetime.timestamp()

def test_parse_us_datetime_chat3():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat 3.txt')], 'John Doe')
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat3)
    assert len(df_truth) == len(df)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.timestamp == df_truth.iloc[i].datetime.timestamp()
