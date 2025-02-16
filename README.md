# Price Watchlist

## Dependencies:

- google api libraries
- beautiful soup

## Setup

1. Follow the [google sheets API](https://developers.google.com/sheets/api/quickstart/python) quickstart to generate token.json by running quickstart.py (given inside of the quickstart page).
1. Get the [bot token](https://core.telegram.org/api) and send the bot a message, finish setup by running `python notifier.py`
1. Run `python price_getter.py`, complete setup.

## Features

- Automatic messages to user on price change
- Constant updates on program running
- Automatic updating of excel spreadsheet for prices
