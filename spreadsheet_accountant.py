from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from price_getter import get_price
from notifier import message_user as notify
import json
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)

def read(spreadsheet_id:str, range_name:str)->list:
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
        return error

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
        return error

spreadsheet_id = ""
spreadsheet_range = ""

def setup():
    """
        Sets up the spreadsheet id and spreadsheet range
        Returns:
            (str): spreadsheet ID
            (str): range for spreadsheets
    """
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

def updatePrices()->dict:
    """
        Reads the spreadsheets, retrieves links, gets price, returns price.
        Returns:
            (dict): item names and prices
    """
    price_list = {}
    set_values = read(spreadsheet_id, spreadsheet_range)
    for row in range(len(set_values)):
        for col in range(len(set_values[row])):
            val = set_values[row][col]
            if val == " $0":
                set_values[row][col] = 0
            if "https" in val:
                new_price = get_price(val)
                set_values[row][col-1] = new_price
                price_list[set_values[row][col]] = new_price
    write(spreadsheet_id, spreadsheet_range, "USER_ENTERED", set_values)
    return price_list

def main():
    """
        Main function, processes everything.
    """
    prices = {}
    notify("Starting excel updater!")
    interval = 30
    time_elapsed = 0
    while True:
        try:
            now = datetime.now()
            print(now.strftime("%d/%m/%Y %H:%M:%S"), "~~ Getting price list, time elapsed without notifying alive: ", time_elapsed)
            if time_elapsed > 60*60*4:
                time_elapsed = 0
                notify("Program is still running...")
            interval = 30
            temp_prices = updatePrices()
            keys = list(prices.keys())
            for i in keys:
                if i not in temp_prices.keys():
                    notify(f"{i} has been removed from the watchlist.")
                    del prices[i]
            keys = list(temp_prices.keys())
            for i in keys:
                if i not in prices.keys():
                    notify(f"{i} has been added to the watchlist.\nPrice: ${format(temp_prices[i], ',')}")
                else:
                    if temp_prices[i] > prices[i]:
                        notify(f"{i} has increased price from ${format(prices[i], ',')} to ${format(temp_prices[i], ',')}")
                    elif temp_prices[i] < prices[i]:
                        notify(f"{i} has decreased price from ${format(prices[i], ',')} to ${format(temp_prices[i], ',')}")
            prices = temp_prices
            sleep(60*5)
            time_elapsed += 60*5
        except:
            notify(f"Excel updater has disconnected! Retrying in {interval} seconds...")
            interval+=30
            sleep(interval)
            time_elapsed += interval

if __name__ == "__main__":
    spreadsheet_id, spreadsheet_range = setup()
    main()
