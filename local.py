import sqlite3
from price_getter import get_price
from datetime import datetime, timedelta
from time import sleep
from notifier import message_user as notify

def verify_link(link:str)->bool:
    if get_price(link) == None:
        print("There was an error adding the link.\nTry again later.")
        return False
    return True

def setup_db(db:sqlite3.Connection):
    print("Welcome to the setup of the local database!")
    cursor = db.cursor()
    cursor.execute("CREATE TABLE if not exists products(name TEXT, link TEXT, price INTEGER)")
    print("You are about to be asked to enter the links (including the https:// part) of objects to track the price of...")
    link = " "
    data = []
    while link != "":
        link = input("Enter a link (leave blank to stop adding): ")
        if link == "":
            break
        if verify_link(link):
            name = link.split("/")[3].split("#")[0]
            price = get_price(link)
            print(f"Added the {name} to watchlist, current price: ${format(price, ",")}")
            data.append((name, link, price))
    print("Pushing all items to the database...")
    cursor.executemany("INSERT INTO products VALUES(?, ?, ?)", data)
    db.commit()
    print("Loaded database!")

def constant_updating(db):
    print("Run local_manager.py to add, remove, or view values in the database.")
    notify("Starting price tracker!")
    prices = {}
    now = datetime.now()
    interval = 30
    error_time = 0
    check_interval = 30
    cursor = db.cursor()
    retrying = False
    while True:
        try:
            right_now = datetime.now()
            if (right_now-now).seconds > 4*60*60:
                notify("I am still alive!")
                now = right_now
            print(f"{right_now} ~~ Starting price check...")
            links = cursor.execute("SELECT link FROM products").fetchall()
            new_prices = {}
            for link in links:
                new_prices[link[0]] = get_price(link[0])
            prev_links = list(prices.keys())
            for link in prev_links:
                if link not in list(new_prices.keys()):
                    notify(f"Removed {link} from watchlist.")
            prev_links = list(new_prices.keys())
            for link in prev_links:
                if link not in list(prices.keys()):
                    notify(f"{link} was added to the watchlist!\nCurrent price: ${format(new_prices[link], ',')}")
                else:
                    if prices[link] > new_prices[link]:
                        notify(f"{link} has decreased price from ${format(prices[link], ',')} to ${format(new_prices[link], ',')}")
                    elif new_prices[link] > prices[link]:
                        notify(f"{link} has increased price from ${format(prices[link], ',')} to ${format(new_prices[link], ',')}")
            prices = new_prices
            print("Updating prices...")
            cursor.executemany("UPDATE products SET price = ? WHERE link = ?", list(new_prices.items()))       
            db.commit()
            if retrying:
                retrying = False
                notify("Price tracker is connected again!")
                error_time = 0
            missing = ((right_now + timedelta(seconds=check_interval))-datetime.now()).seconds
            print(f"Prices updated! {missing} seconds until next check!")
            sleep(missing)
        except Exception as err:
            print(err)
            error_time+=interval
            retrying = True
            notify(f"Price tracker has disconnected, retrying in {error_time} seconds!")
            sleep(error_time)

def main():
    try:
        open("prices.db", "r")
        db = sqlite3.connect("prices.db")
    except:
        open("prices.db", "w")
        db = sqlite3.connect("prices.db")
        setup_db(db)
    constant_updating(db)

if __name__ == "__main__":
    main()
