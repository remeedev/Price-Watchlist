from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from price_getter import get_price
import json
from datetime import datetime, timedelta
from notifier import message_user as notify
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None

def setup_creds()->None:
    """
        Sets up the credentials for the user in case they are not already set.
    """
    global creds
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

setup_creds()

def read(spreadsheet_id:str, range_name:str)->list[list[str | int | float]] | None:
    """
        Reads contents from a google spreadsheet.
        Parameters:
            spreadsheet_id (str): ID for the spreadsheet being used, should be automatically gotten upon running for the first time
            range_name (str): Range selected, also setup through the initial setup
        Returns:
            Values of the cells in range.
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        return rows
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def write(spreadsheet_id:str, range_name:str, value_input_option:str, values:list)->None:
    """
        writes contents to a google spreadsheet.
        Parameters:
            spreadsheet_id (str): ID for the spreadsheet being used, should be automatically gotten upon running for the first time
            range_name (str): Range selected, also setup through the initial setup
            value_input_option (str): chosen whether to enter plain text (RAW) or to allow to contextualize (USER_ENTERED).
            values (list): Values to write in range
        Returns:
            Not really useful I guess :p
    """
    try:
        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

spreadsheet_id = ""
spreadsheet_range = ""

def setup():
    """
        Sets up the spreadsheet id and spreadsheet range
        Returns:
            (str): spreadsheet ID
            (str): range for spreadsheets
    """
    global notify
    try:
        content = json.loads(open("excel_config.json").read())
        return content["id"], content["range"]
    except FileNotFoundError:
        print("Running setup for spreadsheet accountant...")
        url = input("Paste the link of the spreadsheet (including the https:// part): ").split('/')[5]
        print(f"ID set as: {url}")
        print("Enter a random cell in sheet1 and the press '=' then select the range to be used, this code removes any formulas so don't include them.")
        range_selected = input("Select the part of the spreadsheets with links and price sections before them and paste reference (include the =): ").replace("=", "")
        print(f"Range set as: {range_selected}")
        open("excel_config.json", "w").write(json.dumps({"id":url, "range":range_selected}))
        return url, range_selected

def update_prices()->dict:
    """
        Reads the spreadsheets, retrieves links, gets price, returns price.
        Returns:
            (dict): item names and prices
    """
    price_list = {}
    set_values = read(spreadsheet_id, spreadsheet_range)
    if set_values == None:
        return price_list
    for row in range(len(set_values)):
        for col in range(len(set_values[row])):
            val = set_values[row][col]
            if val == " $0":
                set_values[row][col] = 0
            if type(val) == str:
                if "https" in val:
                    new_price = get_price(val)
                    if new_price != None and new_price >= 0:
                        set_values[row][col-1] = new_price
                        price_list[set_values[row][col]] = new_price
                    elif new_price == -1:
                        set_values[row][col-1] = "No Longer Available"
    write(spreadsheet_id, spreadsheet_range, "USER_ENTERED", set_values)
    return price_list

def main():
    """
        Main function, processes everything.
    """
    prices = {}
    notify("Starting excel updater!")
    disconnected = False
    start_time = datetime.now()
    error_interval = 30
    interval = 30
    check_times = 5*60
    while True:
        try:
            now = datetime.now()
            print(now.strftime("%d/%m/%Y %H:%M:%S"), "~~ Getting price list.")
            if (now-start_time).seconds > 60*60*4:
                start_time = datetime.now()
                notify("Program is still running...")
            temp_prices = update_prices()
            keys = list(prices.keys())
            for i in keys:
                if i not in temp_prices.keys():
                    notify(f"{i} has been removed from the watchlist.")
                    del prices[i]
            keys = list(temp_prices.keys())
            for i in keys:
                if temp_prices[i] == None:
                    notify(f"{i}\n\nWasn't able to retrieve the price!")
                    continue
                if i not in prices.keys():
                    notify(f"{i} has been added to the watchlist.\nPrice: ${format(temp_prices[i], ',')}")
                else:
                    if temp_prices[i] > prices[i]:
                        notify(f"{i} has increased price from ${format(prices[i], ',')} to ${format(temp_prices[i], ',')}")
                    elif temp_prices[i] < prices[i]:
                        notify(f"{i} has decreased price from ${format(prices[i], ',')} to ${format(temp_prices[i], ',')}")
            prices = temp_prices
            seconds_missing = ((now+timedelta(seconds=check_times)) - datetime.now()).seconds
            if seconds_missing > check_times:
                seconds_missing = 5
            print(f"Check completed, {seconds_missing} seconds until next check of prices...")
            interval = 30
            if disconnected:
                disconnected = False
                notify("Excel updater has finally reconnected!")
            sleep(seconds_missing)
        except RefreshError as e:
            print("Asking for credentials...")
            setup_creds()
        except Exception as e:
            print(e)
            disconnected = True
            notify(f"Excel updater has disconnected! Retrying in {interval} seconds...")
            interval+=error_interval
            sleep(interval)

if __name__ == "__main__":
    spreadsheet_id, spreadsheet_range = setup()
    main()
