# ChatShape

**Python scripts to generate shaped word clouds from chat logs.** Currently supports Google Hangouts and Facebook Messenger log formats.

<p align="center">
<img src="https://github.com/MasterScrat/ChatShape/raw/master/renders/Florian_Laurent_10001_1000.png" width="600" height="376">
</p>

## How to use it?

### 1. Download your chat logs

#### Google Hangouts

Use Google Takeout: https://accounts.google.com/ServiceLogin?service=backup

Ask for an archive containing your chat logs. Extract the file called `Hangouts.json` and put it in the `raw` folder of ChatShape.

*Google switched from "Google Talk" to "Google Hangouts" mid-2013. You will only get your Hangouts logs.*

#### Facebook Messenger

1. Go to "Settings" from the top right drop-down menu.
2. Click on "Download a copy of your Facebook data" at the bottom of the General section.
3. Click on "Start My Archive". It will take Facebook a while to generate it.
4. Once it is done download and extract the archive, move the file `messages.htm` in the `raw` folder of ChatShape.

### 2. Parse the logs into ChatShape format

* Google Hangouts: `python parse_hangouts.py`
* Facebook Messenger: `python parse_messenger.py`

This will generate pickle files in the `data` folder.

### 3. Render the logs

`python cloud.py -d data/hangouts.pkl data/messenger.pkl`


## Improvement ideas

* Integrate with [gtalk_export](https://github.com/coandco/gtalk_export/) to handle Google Talk format.
* Parsers for more chat platforms: WhatsApp? Pidgin? ...
* WordCloud has some issues with non-English languages. For example in French it will transform "ouais" (yep) in "ouai". Fixing this would probably require a pull request on the WordCloud project.
* For now if the phrase "don't worry" appears a lot, "don't" will be removed (as a stopword) and only "worry" will appear in the cloud. This is misleading. It would be interesting to implement an n-gram approach to consider groups of words. [This example from WordCloud](https://github.com/amueller/word_cloud/blob/bc8e76ef98e3fdfa506deb56a3050e7a481e99ef/examples/bigrams.py) could be a good starting point.
* Figure out OWN_NAME automatically.
* Handle group chats.

Pull requests welcome!


## Misc

* Word cloud generated using https://github.com/amueller/word_cloud
* Stopwords from https://github.com/6/stopwords-json
* Code under MIT license