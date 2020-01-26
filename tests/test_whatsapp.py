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
            "The following messages will test some corner cases",
            "👨‍🦰 👨🏿‍🦰 👨‍🦱 👨🏿‍🦱 🦹🏿‍♂️",
            "בְּרֵאשִׁית, בָּרָא אֱלֹהִים, אֵת הַשָּׁמַיִם, וְאֵת הָאָרֶץ",
            "Ṱ̺̺̕o͞ ̷i̲̬͇̪͙n̝̗͕v̟̜̘̦͟o̶̙̰̠kè͚̮̺̪̹̱̤ ̖t̝͕̳̣̻̪͞h̼͓̲̦̳̘̲e͇̣̰̦̬͎ ̢̼̻̱̘h͚͎͙̜̣̲ͅi̦̲̣̰̤v̻͍e̺̭̳̪̰-m̢iͅn̖̺̞̲̯̰d̵̼̟͙̩̼̘̳ ̞̥̱̳̭r̛̗̘e͙p͠r̼̞̻̭̗e̺̠̣͟s̘͇̳͍̝͉e͉̥̯̞̲͚̬͜ǹ̬͎͎̟̖͇̤t͍̬̤͓̼̭͘ͅi̪̱n͠g̴͉ ͏͉ͅc̬̟h͡a̫̻̯͘o̫̟̖͍̙̝͉s̗̦̲.̨̹͈̣",
            "𝕋𝕙𝕖 𝕢𝕦𝕚𝕔𝕜 𝕓𝕣𝕠𝕨𝕟 𝕗𝕠𝕩 𝕛𝕦𝕞𝕡𝕤 𝕠𝕧𝕖𝕣 𝕥𝕙𝕖 𝕝𝕒𝕫𝕪 𝕕𝕠𝕘",
            "⒯⒣⒠ ⒬⒰⒤⒞⒦ ⒝⒭⒪⒲⒩ ⒡⒪⒳ ⒥⒰⒨⒫⒮ ⒪⒱⒠⒭ ⒯⒣⒠ ⒧⒜⒵⒴ ⒟⒪⒢",
            "˙ɐnbᴉlɐ ɐuƃɐɯ ǝɹolop ʇǝ ǝɹoqɐl ʇn ʇunpᴉpᴉɔuᴉ ɹodɯǝʇ poɯsnᴉǝ op pǝs 'ʇᴉlǝ ƃuᴉɔsᴉdᴉpɐ ɹnʇǝʇɔǝsuoɔ 'ʇǝɯɐ ʇᴉs ɹolop ɯnsdᴉ ɯǝɹo˥",
            "田中さんにあげて下さい",
            "和製漢語",
            "ด้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็ ด้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็ ด้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็็้้้้้้้้็็็็็้้้้้็็็็",
            "ÅÍÎÏ˝ÓÔÒÚÆ☃",
            "\n[1.2.2019, 00:00:00] John Doe: this line is not a message on its own",
            "¯\\_(ツ)_/¯",
            "What is that?\n2/11/19, 14:48 Alice Placeholder: this is a message from another chat!",
            "This is the last message of this test file."
            ],
        'outgoing': [False, False, True, True, False, True, True, True, False, True, False, False, False, False, False, True, True, True, True, False],
        'senderName': ['Alice Placeholder', 'Alice Placeholder', 'John Doe', 'John Doe', 'Alice Placeholder', 'John Doe', 'John Doe', 'John Doe', 'Alice Placeholder', 'John Doe', 'Alice Placeholder', 'Alice Placeholder', 'Alice Placeholder', 'Alice Placeholder', 'Alice Placeholder', 'John Doe', 'John Doe', 'John Doe', 'John Doe', 'Alice Placeholder']
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
            datetime(2019, 10, 11, 14, 25),
            datetime(2019, 2, 11, 14, 33),
            datetime(2019, 2, 11, 14, 48),
            datetime(2019, 2, 11, 14, 51),
            ]
        }

ground_truth_chat4 = {
        'datetime': [
            datetime(2019, 9, 17, 8, 30, 52),
            datetime(2019, 9, 17, 16, 30, 10),
            datetime(2019, 9, 18, 16, 50, 32),
            ],
        'text': [
            'US datetime format',
            'US datetime format',
            'US datetime format',
            ],
        'senderName': [
            'John Doe',
            'John Doe',
            'John Doe',
            ]
        }


def test_parse_chat_info_chat1():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat.txt')], 'John Doe', True)
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat1)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.text == df_truth.iloc[i].text
        assert row.outgoing == df_truth.iloc[i].outgoing  # using `is` doesn't work here (bool vs. np.bool)
        assert row.senderName == df_truth.iloc[i].senderName

def test_parse_eu_datetime_chat2():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat 2.txt')], 'John Doe', True)
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat2)
    assert len(df_truth) == len(df)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.timestamp == df_truth.iloc[i].datetime.timestamp()

def test_parse_us_datetime_chat3():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat 3.txt')], 'John Doe', True)
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat3)
    assert len(df_truth) == len(df)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.timestamp == df_truth.iloc[i].datetime.timestamp()

def test_parse_us_datetime_chat4():
    data = parse_messages([os.path.join(TEST_DATA_LOCATION, '_chat 4.txt')], 'John Doe', True)
    df = pd.DataFrame(data, columns=config['ALL_COLUMNS'])
    df_truth = pd.DataFrame(ground_truth_chat4)
    assert len(df_truth) == len(df)
    for i, row in df.iloc[:len(df_truth)].iterrows():
        assert row.timestamp == df_truth.iloc[i].datetime.timestamp()
        assert row.text == df_truth.iloc[i].text
        assert row.senderName == df_truth.iloc[i].senderName
