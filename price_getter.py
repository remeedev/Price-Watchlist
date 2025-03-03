import requests
from bs4 import BeautifulSoup

prices_requested = 0

def mercadolibre(parser:BeautifulSoup) -> int|None:
    """
    Gets the price from mercado libre link
    Parameters:
        parser (bs4): parser object
    """
    innerText = ["cc" if "cuotas" in s else int(s.replace(".", "")) for s in parser.find_all(class_="ui-pdp-price__main-container")[0].get_text(separator="\n").split("\n") if s.replace(".", "").isdigit() or "cuotas" in s]
    return int(innerText[-1 if "cc" not in innerText else innerText.index("cc")-1])

def ebay(parser:BeautifulSoup) -> float|None:
    """
    Gets the price from ebay link
    Parameters:
        parser (bs4): parser object
    """
    return float(parser.select(".x-price-primary")[0].text.replace("US $", ""))

def amazon(parser:BeautifulSoup) -> float|None:
    """
    Gets the price from amazon link, tends to fail due to scraping detection
    Parameters:
        parser (bs4): parser object
    """
    try:
        return float(parser.select(".aok-offscreen")[0].text.split(" ")[0].replace("US$", ""))
    except:
        return None

def get_price(link:str)->int|float|None:
    global prices_requested
    """
    Returns price of item with link of item, only works with MercadoLibre
    Parameters:
        link (str): link of the item you want to keep a hold of
    Return:
        (int) currentPrice of item
    """
    shop = link.split(".")[1]
    allow_list = [mercadolibre, ebay, amazon]
    if shop not in [s.__name__ for s in allow_list]:
        print("Link is not from the allowed shops!")
        print(f"Allow list: {[s.__name__ for s in allow_list]}")
        return None
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; AS; en-US) like Gecko",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "Mozilla/5.0 (Windows NT 6.1; rv:48.0) Gecko/20100101 Firefox/48.0",
        "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36 Edge/80.0.361.109",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"
    ]
    headers = {
        "User-Agent": user_agents[prices_requested%len(user_agents)]
    }
    prices_requested += 1
    req = requests.get(link, headers=headers)
    res = req.text
    soup = BeautifulSoup(res, 'lxml')
    try:
        return allow_list[[s.__name__ for s in allow_list].index(shop)](soup)
    except:
        return -1
