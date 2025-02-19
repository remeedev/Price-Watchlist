import requests
from bs4 import BeautifulSoup

def get_price(link:str)->int|float|None:
    """
    Returns price of item with link of item, only works with MercadoLibre
    Parameters:
        link (str): link of the item you want to keep a hold of
    Return:
        (int) currentPrice of item
    """
    shop = link.split(".")[1]
    allow_list = ["mercadolibre", "ebay"]
    if shop not in allow_list:
        print("Link is not from the allowed shops!")
        print(f"Allow list: {allow_list}")
        return None
    req = requests.get(link)
    res = req.text
    soup = BeautifulSoup(res, "html.parser")
    if allow_list[0] == shop:
        price_pretty = soup.select("[data-testid='price-part']")
        for i in price_pretty:
            if "Antes: " not in str(i):
                return int(i.text.replace("$", "").replace(".", ""))
    elif allow_list[1] == shop:
        price_pretty = soup.select(".x-price-primary")[0].text
        return float(price_pretty.replace("US $", ""))
    return None
