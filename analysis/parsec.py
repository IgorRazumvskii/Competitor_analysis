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
    "valta":lambda vendor_code: f"https://valta.ru/search/?q={vendor_code}",
    "4lapy":lambda search_text: f"https://new.4lapy.ru/search/filter/?query={search_text}&skipQueryCorrection=0",
    "zoozavr":lambda search_text: f"https://zoozavr.ru/search/results/?qt={search_text}&searchType=zoo&searchMode=common"
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
        # option = Options()
        # option.add_argument('--disable-infobars')
        # self.browser = webdriver.Chrome(options=option)
        # self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36 '})


    def getSoup(self, url):
        req = self.session.get(url)
        if req.status_code != 200:
            print("PARSE ERROR")
            return None
        return BeautifulSoup(req.text, "html.parser")

    def parseValta(self, vendor_code: str):
        url = URLS["valta"](vendor_code)
        soup = self.getSoup(url)
        if not soup: return None
        goods = soup.findAll('div', class_="p-i")
        for good in goods:
            article = good.find('div', class_="p-i__article")
            if article.text.split()[1] != vendor_code: continue
            info = good.find("div", class_="p-i__info")
            text = info.findAll("a")[0].text.strip()
            price = good.find("div", class_="p-i__price-block").find("span").text.strip()
        return {"Название": f"{text}",
                "Цена": f"{price}"}

    #TODO! Selenium
    def parse4Lapy(self, search_text):
        url = URLS["4lapy"](search_text)
        #init selenium headless browser
        self.browser.get(url)



    def parseZoozavr(self, vendor_code):
        url = URLS["zoozavr"](vendor_code)
        soup = self.getSoup(url)
        if not soup: return None
        goods = soup.findAll("div", class_="WC WF")
        for good in goods:
            print(good)
            info = good.find("a", class_="eB").text.split().strip()
            print(info)


if __name__ == "__main__":
    parser = Parser()
    parser.parseValta("70085281")

    #parser.parse4Lapy("Кошачий корм")
    #parser.parseZoozavr("70085281")