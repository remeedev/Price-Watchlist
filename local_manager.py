import sqlite3
from local import setup_db, verify_link
from price_getter import get_price

def read_db(db:sqlite3.Connection)->None:
    """
        Prints the database contents, excluding links
    """
    cursor = db.cursor()
    listings = cursor.execute("SELECT name, price FROM products")
    listings = listings.fetchall()
    print(f"Here are the listings:\n")
    for listing in listings:
        print(f"{listing[0]} ~~ ${format(listing[1], ',')}")

def add_to_db(db:sqlite3.Connection)->None:
    """
        Adds a link, after verifying, to the database
        Parameters:
            db (Connection): The database connection Object.
    """
    cursor = db.cursor()
    link = input("Enter link of listing to add (including the https:// section): ")
    if verify_link(link):
        print("Link has been verified!\nAdding the link to the database...")
        name = link.split("/")[3].split("#")[0]
        price = get_price(link)
        cursor.execute("INSERT INTO products VALUES(?, ?, ?)", (name, link, price))
        db.commit()
        print(f"{name} ~~ ${format(price, ',')}\nAdded to database!")
    else:
        print("The link was not verified properly, try again later!")

def remove_from_db(db:sqlite3.Connection)->None:
    """
        Removes an item from the database with an index.
        Parameters:
            db (Connection): The database connection Object.
    """
    print("Enter the number of item to remove...")
    cursor = db.cursor()
    listings = cursor.execute("SELECT name, link FROM products")
    listings = listings.fetchall()
    for i, listing in enumerate(listings):
        print(f"{i}: {listing[0]}")
    selection = input("Option> ")
    if not selection.isdigit():
        return
    if int(selection) >= len(listings):
        return
    link = listings[int(selection)]
    print(link)
    cursor.execute("DELETE FROM products WHERE name = ? AND link = ?", link)
    db.commit()

def main()->None:
    try:
        open("prices.db", "r")
        db = sqlite3.connect("prices.db")
    except:
        open("prices.db", "w")
        db = sqlite3.connect("prices.db")
        setup_db(db)
    print("Welcome to the price tracker watchlist!")
    option = " "
    functions = [read_db, add_to_db, remove_from_db]
    while option != "":
        print("Select one of the following:")
        for i, function in enumerate(functions):
            print(f"{i}) {function.__name__.replace("db", "database").replace("_", " ")}")
        print("Leave blank to exit program.")
        option = input("> ")
        if not option.isdigit():
            continue
        if int(option) >= len(functions):
            continue
        print("\n"*5)
        functions[int(option)](db)
        print("\n"*5)

if __name__ == "__main__":
    main()
