import json
import time
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fuzzywuzzy.fuzz import token_sort_ratio as ncmp

URLS = {
    "valta": "https://valta.ru",
    "oldFarm": "https://dogeat.ru",
    "bethoven": "https://www.bethowen.ru",
    "valtaS":lambda vendor_code: f"https://valta.ru/search/?q={vendor_code}",
    "4lapy":lambda search_text: f"https://new.4lapy.ru/search/filter/?query={search_text}&skipQueryCorrection=0",
    "zoozavr":lambda search_text: f"https://zoozavr.ru/search/results/?qt={search_text}&searchType=zoo&searchMode=common",
    "oldFarmS":lambda search_text: f"https://www.dogeat.ru/catalog/?q={search_text}",
    "bethovenS":lambda search_text: f"https://www.bethowen.ru/search/?q={search_text}",
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

    def selenium_init(self):
        options = Options()
        self.driver  = webdriver.Chrome(options=options)


    def getSoup(self, url):
        req = self.session.get(url)
        if req.status_code != 200:
            print("PARSE ERROR")
            return None
        return BeautifulSoup(req.text, "html.parser")

    def parseValta(self, old_json):
        vendor_code = old_json["vendor_code"]
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
        old_json["name"] = descriptions[0]
        descriptions = " ".join(descriptions[1:])
        old_json["text"] = descriptions[1:]
        old_json["store"]["name"] = "Valta"
        old_json["price"] = price
        return old_json

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



    def parseZoozavr(self, vendor_code, username):
        url = URLS["zoozavr"](vendor_code)
        soup = self.getSoup(url)
        if not soup: return None
        print(soup)

    def perform_json(self, vendor_code, username):
        return {
            "vendor_code": vendor_code,
            "user":{
                "username": "admin"
            },
            "name": None,
            "price": None,
            "text": None,
            "store":{
                "name": None,
            }
        }

    def parseOldFarm(self, old_json):
        vendor_code  = old_json["vendor_code"]

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
        old_json["name"] = text
        old_json["text"] = desc
        old_json["store"]["name"] = "OldFarm"
        old_json["price"] = price
        return old_json

    def parseBethoven(self, json):
        vendor_code = json["vendor_code"]
        url = URLS["bethovenS"](vendor_code)
        self.driver.get(url)
        elem = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dgn-flex')]"))
        )
        goods = elem.find_elements(By.XPATH, "//div[contains(@class, 'pr-card__description')]")
        if not goods: return None
        mxnum = 0
        mxgood = None
        for idx, good in enumerate(goods):
            name = good.find_element(By.CLASS_NAME, "sale-gray-dark")
            cmp = ncmp(vendor_code, name.text)
            if cmp > mxnum:
                mxnum = cmp
                mxgood = idx
        json["store"]["name"] = "Bethoven",
        if mxnum < 76:
            json["name"] = "Н/Д",
            json["text"] = "Н/Д",
            json["price"] = "Н/Д"
            return json
        element = goods[mxgood]
        json["name"] = element.find_element(By.CLASS_NAME, "sale-gray-dark").text
        json["text"] = "Н/Д"
        price = str(float(element.find_element(By.CLASS_NAME, "pr-card__retail-price").text.replace('\u20BD', '').replace(' ', '')))
        json["price"] = price
        return json

    def run(self, user_id: str, vendor_code: str) -> dict:
        clean_json = self.perform_json(vendor_code, user_id)
        repsonse = [self.parseValta(deepcopy(clean_json)), self.parseOldFarm(deepcopy(clean_json))]
        bet_copy = deepcopy(clean_json)
        bet_copy["vendor_code"] = repsonse[0]["name"]
        self.selenium_init()
        repsonse.append(self.parseBethoven(bet_copy))
        repsonse[-1]["vendor_code"]  =  repsonse[0]["vendor_code"]
        return repsonse

