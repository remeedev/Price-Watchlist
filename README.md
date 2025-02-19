# Price Watchlist

Tracks the prices of listings in real time, sends constant updates (Watchlist updates and price changes). Updates a database to store the prices, or an google sheets, if the Google Sheets API is connected. It updates prices from certain stores online without using their API.

# Installation

1. Download the source code using the command `git clone https://github.com/remeedev/Price-Watchlist.git`
1. Enter the directory
1. Install the required modules ([BeautifulSoup](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://pypi.org/project/beautifulsoup4/&ved=2ahUKEwjwyqSQ2M6LAxXjTDABHaqxHioQFnoECBQQAQ&usg=AOvVaw3asbpXIi2G3wc2fGLJ448a), [Google Sheets API](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://developers.google.com/sheets/api/guides/concepts&ved=2ahUKEwjr0qic2M6LAxXXSTABHaaZMo8QFnoECAkQAQ&usg=AOvVaw1tzQTchAiT5Tf-jvRJ10Og) if you plan on connecting to a sheets and [sqlite3](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://pypi.org/project/db-sqlite3/&ved=2ahUKEwi0pdK02M6LAxUSQjABHZZGBV4QFnoECBAQAQ&usg=AOvVaw3g7SVcFAX9JcBxwD0TZU-Q) if planning to use locally).

# Usage

1. Local Run
    1. Run `python local.py`
    1. Enter the links to be added to the watchlist
    1. Press enter to finish adding links
    1. Done
1. Google Sheets Run
    1. Go through the [Google Sheets API Quickstart](https://developers.google.com/sheets/api/quickstart/python).
    1. Open the `quickstart.py` (from the API Quickstart).
    1. Edit the Scopes line to
    ```
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    ```
    1. Run `python quickstart.py` and give access to your application.
    1. Run `spreadsheet_accountant.py`
    1. Done
1. Turn on Telegram notifier
    1. Create a bot by texting @BotFather in Telegram to create a bot.
    1. Run `python notifier.py`
    1. Enter the token given to you by @BotFather
    1. Text your bot.
    1. Press Enter.
    1. Follow the verification steps (making sure you are the user).
    1. Done, every other program will use Telegram to notify you.

# Issues or questions

To report an issue use the [Issues Tab](https://github.com/remeedev/Price-Watchlist/issues) in github.

# Author

[Remeedev](https://github.com/remeedev)
