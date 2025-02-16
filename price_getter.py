import requests
from bs4 import BeautifulSoup

def get_price(link:str)->int:
    """
    Returns price of item with link of item, only works with MercadoLibre
    Parameters:
        link (str): link of the item you want to keep a hold of
    Return:
        (int) currentPrice of item
    """
    shop = link.split(".")[1]
    allow_list = ["mercadolibre"]
    if shop not in allow_list:
        print("Link is not from the allowed shops!")
        print(f"Allow list: {allow_list}")
        return 0
    req = requests.get(link)
    res = req.text
    soup = BeautifulSoup(res, "html.parser")
    price_pretty = soup.select("[data-testid='price-part']")
    for i in price_pretty:
        if "Antes: " not in str(i):
            return int(i.text.replace("$", "").replace(".", ""))
    return 0
