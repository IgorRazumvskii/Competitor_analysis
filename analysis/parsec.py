import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


URLS = {
    "valta": "https://valta.ru",
    "oldFarm": "https://dogeat.ru",
    "valtaS":lambda vendor_code: f"https://valta.ru/search/?q={vendor_code}",
    "4lapy":lambda search_text: f"https://new.4lapy.ru/search/filter/?query={search_text}&skipQueryCorrection=0",
    "zoozavr":lambda search_text: f"https://zoozavr.ru/search/results/?qt={search_text}&searchType=zoo&searchMode=common",
    "oldFarmS":lambda search_text: f"https://www.dogeat.ru/catalog/?q={search_text}",
}


def json_to_dict(filename: str) -> dict | None:
    try:
        with open(filename) as file:
            return json.load(file)
    except FileNotFoundError or FileExistsError as e:
        pass
    return None


class Parser:
    def __init__(self):
        self.session = requests.Session()

    def getSoup(self, url):
        req = self.session.get(url)
        if req.status_code != 200:
            print("PARSE ERROR")
            return None
        return BeautifulSoup(req.text, "html.parser")

    def parseValta(self, vendor_code: str):
        url = URLS["valtaS"](vendor_code)
        soup = self.getSoup(url)
        good_url, price = None, None
        if not soup: return None
        goods = soup.findAll('div', class_="p-i")
        for good in goods:
            article = good.find('div', class_="p-i__article")
            if article.text.split()[1] != vendor_code: continue
            price = good.find("div", class_="p-i__price-block").find("span").text.strip()
            good_url = good.find("a", class_="p-i__img").get("href")
            break
        if not good_url:
            return None
        price = str(float(price.split()[0]))
        soup = self.getSoup(f"{URLS['valta']}{good_url}")
        descriptions = soup.find("div", class_="detail__about")
        descriptions = descriptions.findAll("p")
        descriptions = list(map(lambda x: x.text.strip(), descriptions))
        return {
            "store": "valta",
            "name": descriptions[0],
            "price": price,
            "desc": " ".join(descriptions[1:])
        }

    #TODO! Selenium
    def parse4Lapy(self, search_text):
        option = Options()
        option.add_argument('--disable-infobars')
        self.browser = webdriver.Chrome(options=option)
        self.session.headers.update({
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36 '})
        url = URLS["4lapy"](search_text)
        #init selenium headless browser
        self.browser.get(url)
        time.sleep(20)
        print("Доспал")
        #get all divs
        goods = self.browser.find_elements(By.TAG_NAME, "div")
        for good in goods:
            print(good.text, good.get_attribute("class"))
            #print(good.find("div", class_="p-i__info").text)



    def parseZoozavr(self, vendor_code):
        url = URLS["zoozavr"](vendor_code)
        soup = self.getSoup(url)
        if not soup: return None
        print(soup)


    def parseOldFarm(self, vendor_code):
        url  = URLS["oldFarmS"](vendor_code)
        soup  = self.getSoup(url)
        soup = soup.find("div", class_="product-wrap")
        soup = soup.find_all("div", class_="product-item")
        if len(soup) != 1: return None
        else: soup = soup[0]
        url = soup.find("a", class_="product-item__link").get("href")
        url = f"{URLS['oldFarm']}{url}"
        soup = self.getSoup(url)
        price = soup.find("span", class_="product-info__value regionPriceList").text.strip()
        price = price.replace(u'\xa0', ' ')[:-3]
        text = soup.find("h1", class_="heading heading_product").text.strip()
        desc = soup.find("article", class_="article article_tabs").findAll("p")
        desc = " ".join(map(lambda p: p.text.strip(), desc))
        return {
            "store":  "oldFarm",
            "name":   text,
            "price":  price,
            "desc":   desc
        }


    def run(self, user_id: str, vendor_code: str) -> dict:
        response = {
            "user_id":  user_id,
            "vendor_code": vendor_code,
            "parsed": []
        }
        response["parsed"].append(self.parseValta(vendor_code))
        response["parsed"].append(self.parseOldFarm(vendor_code))
        return response


if __name__ == "__main__":
    parser = Parser()
    print(parser.run("test", "7173549"))
    #print(parser.parseOldFarm("7173549"))
