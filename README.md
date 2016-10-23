# ChatShape

**Python scripts to generate word clouds in your shape from chat logs**

<p align="center">
<img src="https://github.com/MasterScrat/ChatShape/raw/master/renders/Florian_Laurent_10001_1000.png" width="600" height="376">
</p>


## How to use it?

### 1. Download your chat logs

#### Google Hangouts

Use Google Takeout: https://accounts.google.com/ServiceLogin?service=backup

Ask for an archive containing your chat logs. Extract the file called `Hangouts.json` and put it in the `raw` folder of ChatShape.

*Note that Google switched from "Google Talk" to "Google Hangouts" mid-2013. You will only get your Hangouts logs.*

#### Facebook Messenger

1. Go to "Settings" from top right drop-down
2. Click on "Download a copy of your Facebook data." at the bottom of the General section
3. Click on "Start My Archive". It will take Facebook a while to generate it
4. Once it is done download and extract the archive
5. Move the file `messages.htm` in the `raw` folder of ChatShape

### 2. Parse the log to ChatShape format

* Google Hangouts: `python parse_hangouts.py`
* Facebook Messenger: `python parse_messenger.py`

### 3. Render the logs

`python cloud.py -d data/hangouts.pkl data/messenger.pkl`


## Improvement ideas

Pull requests welcome!

* Integrate with [gtalk_export](https://github.com/coandco/gtalk_export/) to handle Google Talk format.
* WordCloud has some issues with non-English languages. For example in French it will transform "ouais" (yep) in "ouai". Fixing this would probably require a pull request on the WordCloud project.
* For now if the phrase "don't worry" appears a lot, "don't" will be removed (as a stopword) and only "worry" will appear in the cloud. This is misleading. It would be interesting to implement an n-gram approach to consider groups of words. [This example from WordCloud](https://github.com/amueller/word_cloud/blob/bc8e76ef98e3fdfa506deb56a3050e7a481e99ef/examples/bigrams.py) could be a good starting point.
* Figure out OWN_NAME automatically.
* Handle group chats.
