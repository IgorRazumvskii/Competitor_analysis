import enum
import json
import time
import requests
from queue import Queue
from copy import deepcopy
from bs4 import BeautifulSoup
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fuzzywuzzy.fuzz import token_sort_ratio as ncmp

SELENIUM_TIMEOUT_ERROR = 10

URL = {
    "valta": {
        "url": "https://valta.ru",
        "search_form": "search/?q=$"
    },
    "old_farm": {
        "url": "https://www.dogeat.ru",
        "search_form": "catalog/?q=$"
    },
    "4_lapy": {
        "url": "https://new.4lapy.ru",
        "search_form": "search/filter/?query=$&skipQueryCorrection=0"
    },
    "bethoven": {
        "url": "https://www.bethowen.ru",
        "search_form": "search/?q=$"
    },
    "kotmatros": {
        "url": "https://kotmatros.ru",
        "search_form": "search/$"
    },
    "magizoo": {
        "url": "https://magizoo.ru",
        "search_form": "search/?q=$&s="
    },
    "zoomag": {
        "url": "https://zoomag.ru",
        "search_form": "search/?match=all&subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q=$"
    },
    "zoozavr": {
        "url": "https://zoozavr.ru",
        "search_form": "search/results/?qt=$&searchType=zoo&searchMode=common"
    }
}


class ParserERRORS(enum.Enum):
    PARSER_ERROR = -2
    CONNECTION_ERROR = -1
    NOT_FOUND_ERROR = 0
    PARSED = 1


def perform_json(vendor_code, username):
    return {
        "vendor_code": vendor_code,
        "user": {
            "username": username
        },
        "name": "Н/Д",
        "price": "Н/Д",
        "text": "Н/Д",
        "store": {
            "name": None,
        }
    }


class MultiParser:
    def __init__(self, headless=True):
        self.session = requests.Session()
        options = Options()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def get_by_url(self, url: str) -> BeautifulSoup | None:
        req = self.session.get(url)
        if req.status_code != 200:
            return None
        return BeautifulSoup(req.text, "html.parser")


def parse_valta(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Valta"
    url = f'{URL["valta"]["url"]}/{URL["valta"]["search_form"]}'
    url = url.replace("$", search_object)
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = soup.findAll('div', class_="p-i")
    if not goods:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    god = None
    for good in goods:
        article = good.find('div', class_="p-i__article").text
        article = article.replace("Артикул:", "")
        article = article.strip()
        if article == search_object:
            god = good
            break
    else:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    url = soup.find("a", class_="p-i__img").get("href")
    if not url:
        return shell, ParserERRORS.PARSER_ERROR
    price = god.find("div", class_="p-i__price-block").text
    if not price:
        return shell, ParserERRORS.PARSER_ERROR
    price = price.replace('руб', '').replace(' ', '')
    price = str(float(price))
    url = URL["valta"]["url"] + url
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    name = soup.find("div", class_="detail__title desktop")
    if not name:
        return shell, ParserERRORS.PARSER_ERROR
    name = name.find("h1")
    if not name:
        return shell, ParserERRORS.PARSER_ERROR
    name = name.text
    desc = soup.find("div", class_="detail__about")
    if not desc:
        return shell, ParserERRORS.PARSER_ERROR
    desc = desc.text.replace('<br>', '\n')
    desc = desc.split()
    desc = list(map(lambda el: el.strip(), desc))
    desc = " ".join(desc)

    shell["name"] = name
    shell["text"] = desc
    shell["price"] = price
    return shell, ParserERRORS.PARSED


def parse_oldfarm(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Old_farm"
    url = f'{URL["old_farm"]["url"]}/{URL["old_farm"]["search_form"]}'
    url = url.replace("$", search_object)
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = soup.findAll('div', class_="product-item__main")
    if len(goods) != 1:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    good = goods[0]
    url = good.find("div", "product-item__img")
    if not url:
        return shell, ParserERRORS.PARSER_ERROR
    url = url.find("a")
    if not url:
        return shell, ParserERRORS.PARSER_ERROR
    url = URL["old_farm"]["url"] + url.get("href")
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.PARSER_ERROR
    desc = soup.find("article", class_="article_tabs")
    if not desc:
        return shell, ParserERRORS.PARSER_ERROR
    price = soup.find("span", class_="regionPriceList")
    if not price:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    price = price.text.replace('\xa0', '').replace('р.', '0')
    price = str(float(price.strip()))
    name = soup.find("h1", class_="heading_product")
    if not name:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    shell["name"] = name.text
    shell["text"] = desc.text
    shell["price"] = price
    return shell, ParserERRORS.PARSED


def parse_bethoven(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Bethoven"
    url = f'{URL["bethoven"]["url"]}/{URL["bethoven"]["search_form"]}'
    url = url.replace("$", search_object)
    try:
        mp.driver.get(url)
        goods = WebDriverWait(mp.driver, SELENIUM_TIMEOUT_ERROR).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'dgn-flex')]")
            )
        )
    except Exception:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = goods.find_elements(By.XPATH, "//a[contains(@class, 'sale-gray-dark')]")
    if not goods:
        return shell, ParserERRORS.PARSER_ERROR
    mxidx = -1
    mxnum = 0
    for idx, good in enumerate(goods):
        num = ncmp(search_object, good.text)
        if num > mxnum:
            mxnum = num
            mxidx = idx
    if mxnum < 75:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    good = goods[mxidx]
    url = good.get_attribute("href")
    card = None
    try:
        mp.driver.get(url)
        card = WebDriverWait(mp.driver, SELENIUM_TIMEOUT_ERROR).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'card_detail__info-container')]")
            )
        )
    except Exception:
        return shell, ParserERRORS.CONNECTION_ERROR
    if not card:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    name = card.find_element(By.XPATH, "//div[contains(@class, 'card_detail__title')]")
    name = name.find_element(By.XPATH, ".//h1").text
    price = card.find_element(By.XPATH, "//div[contains(@class, 'retail-price')]")
    price = str(float(price.text.replace('\xa0', '').replace("Цена:", "").replace("₽", "").replace(" ", "")))
    shell["name"] = name
    shell["price"] = price
    return shell, ParserERRORS.PARSED


def parse_4Lapy(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "4_Lapy"
    url = f"{URL['4_lapy']['url']}/{URL['4_lapy']['search_form']}"
    url = url.replace("$", search_object)
    try:
        mp.driver.get(url)
        elem = WebDriverWait(mp.driver, SELENIUM_TIMEOUT_ERROR).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@class, 'ProductsList_root__')]"))
        )
    except Exception:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = elem.find_elements(By.XPATH, ".//article")
    if not goods:
        return shell, ParserERRORS.PARSER_ERROR
    mxidx = -1
    mxnum = 0
    for idx, good in enumerate(goods):
        name = good.find_element(By.XPATH, ".//img").get_attribute("alt")
        num = ncmp(name, search_object)
        if num > mxnum:
            mxidx = idx
            mxnum = num
    if mxidx == -1 or mxnum < 76:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    good = goods[mxidx]
    name = good.find_element(By.XPATH, ".//img").get_attribute("alt")
    price = good.find_element(By.XPATH, ".//div[contains(@class, 'text-price-big')]").text.replace('\u20BD',
                                                                                                   '').replace(' ', '')
    shell["name"] = name
    shell["price"] = str(float(price))
    return shell, ParserERRORS.PARSED


def parse_kotmatros(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Kotmatros"
    url = f"{URL['kotmatros']['url']}/{URL['kotmatros']['search_form']}"
    url = url.replace('$', search_object)
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = soup.findAll("div", class_="c-products-thumbs__item")
    finded = None
    for good in goods:
        art = good.find("span", class_="c-value__value-text").text
        if art == shell["vendor_code"]:
            finded = good
            break
    else:
        return shell, ParserERRORS.PARSER_ERROR
    href = finded.find("a", class_="c-product-thumb__name").get("href")
    if not href:
        return shell, ParserERRORS.PARSER_ERROR
    url = f'{URL["kotmatros"]["url"]}{href}'
    soup = mp.get_by_url(url)
    desc = soup.findAll("section", class_="c-content-tabs__content")
    if not desc:
        return shell, ParserERRORS.PARSER_ERROR
    desc = list(map(lambda el: el.text, desc))
    if len(desc) > 3:
        desc = desc[:-2]
    desc = " ".join(desc)
    desc = desc.replace('\n', '').replace('\t', '')
    name = soup.find("h1", class_="c-header_h1").text
    price = soup.find("span", class_="c-product-add-to-cart__price").text
    price = str(float(price.replace('\u20BD', '').replace(' ', '')))
    shell["name"] = name
    shell["text"] = desc
    shell["price"] = price
    return shell, ParserERRORS.PARSED


def parse_magizoo(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Magizoo"
    url = f"{URL['magizoo']['url']}/{URL['magizoo']['search_form']}"
    url = url.replace('$', search_object)
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = soup.findAll("div", class_="item")
    if not goods or len(goods) != 1:
        return shell, ParserERRORS.PARSER_ERROR
    good = goods[0]
    href = good.find("a", class_="link-base").get("href")
    url = f'{URL["magizoo"]["url"]}{href}'
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    name = soup.find("h1", class_="site-title").text
    price = soup.find("span", class_="product-checkout__price").text
    price = price.replace('\u20BD', '').replace(' ', '').strip()
    price = str(float(price))
    shell["name"] = name
    shell["price"] = price
    return shell, ParserERRORS.PARSED


def parse_zoomag(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Zoomag"
    url = f"{URL['zoomag']['url']}/{URL['zoomag']['search_form']}"
    url = url.replace('$', search_object)
    soup = mp.get_by_url(url)
    if not soup:
        return shell, ParserERRORS.CONNECTION_ERROR
    goods = soup.findAll("a", class_="product-title")
    if not goods:
        return shell, ParserERRORS.PARSER_ERROR
    mxnum = 0
    mxa = None
    for good in goods:
        text = good.get("title").strip()
        if text:
            num = ncmp(text, search_object)
            if num > mxnum:
                mxnum = num
                mxa = good
    if not mxa or mxnum < 66:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    url = mxa.get("href")
    soup = mp.get_by_url(url)
    prices = soup.findAll("label", class_="price-line")
    price_val = None
    for price in prices:
        inp = price.find("input", checked=True)
        if inp:
            price_val = price.find("bdi", class_="auth_order").text
    if not price_val:
        return shell, ParserERRORS.PARSER_ERROR
    price_val = price_val.replace('\u20BD', '').replace(' ', '').strip()
    price_val = str(float(price_val))
    name = soup.find("span", class_="ty-product-block-title-desc").text
    desc = soup.find("div", id="content_opisanie").text.strip()
    desc += soup.find("div", id="content_sostav").text.strip()
    shell["name"] = name
    shell["text"] = desc
    shell["price"] = price_val
    return shell, ParserERRORS.PARSED


def parse_zoozavr(shell: dict, search_object: str, mp=MultiParser()) -> (dict, int):
    shell["store"]["name"] = "Zoozavr"
    url = f"{URL['zoozavr']['url']}/{URL['zoozavr']['search_form']}"
    url = url.replace('$', search_object)
    try:
        mp.driver.get(url)
    except Exception:
        return shell, ParserERRORS.CONNECTION_ERROR
    try:
        WebDriverWait(mp.driver, SELENIUM_TIMEOUT_ERROR).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-product-id]"))
        )
    except Exception:
        return shell, ParserERRORS.PARSER_ERROR
    goods = mp.driver.find_elements(By.CSS_SELECTOR, "section[data-product-id]")
    if not goods or len(goods) != 1:
        return shell, ParserERRORS.NOT_FOUND_ERROR
    good = goods[0]
    href = good.find_element(By.CLASS_NAME, "bX").get_attribute("href")
    soup = mp.get_by_url(href)
    price = soup.find("p", class_="bo_9")
    if not price:
        return shell, ParserERRORS.PARSER_ERROR
    price = price.text.replace('\u20BD', '').replace(' ', '').strip()
    price = str(float(price))
    desc = soup.find("div", class_="_2k").text
    desc = desc.strip()
    name = soup.find("h1", class_="_2_0").text
    shell["name"] = name
    shell["text"] = desc
    shell["price"] = price
    return shell, ParserERRORS.PARSED



def parse_one_thread(username: str, vendor_code: str) -> list | str:
    responce = []
    clean_shell = perform_json(vendor_code, username)

    # Начальный request-парсинг по артиклу
    print("Парсим валту")
    valta, valta_status = parse_valta(deepcopy(clean_shell), vendor_code)
    print("Парсим старую ферму")
    oldfarm, oldfarm_status = parse_oldfarm(deepcopy(clean_shell), vendor_code)
    if not valta_status == ParserERRORS.PARSED and not oldfarm_status == ParserERRORS.PARSED:
        return valta_status
    name = None
    if valta_status == ParserERRORS.PARSED:
        name = valta["name"]
    else:
        name = oldfarm["name"]

    # print("Парсим бетховен")
    # bethoven, bethoven_status = parse_bethoven(deepcopy(clean_shell), name, mp=MultiParser(headless=True))
    print("Парсим 4 лапы")
    ch_lapy, ch_lapy_status = parse_4Lapy(deepcopy(clean_shell), name, mp=MultiParser(headless=True))
    return [valta, oldfarm, ch_lapy]


def parse_multithreaded(username: str, vendor_code: str) -> list | ParserERRORS:
    def parse_wrapper(shell: dict, search_object: str, queue: Queue, func) -> None:
        queue.put(func(shell, search_object))

    def unpack_queue(que: Queue) -> list:
        ans = []
        while not que.empty():
            ans.append(que.get())
        return ans

    def thread_control(ths: list) -> None:
        for th in ths:
            th.start()
        for th in ths:
            th.join()

    queue = Queue()
    shell = perform_json(vendor_code, username)
    threads = [
        Thread(target=parse_wrapper, args=(deepcopy(shell), vendor_code, queue, parse_valta)),
        Thread(target=parse_wrapper, args=(deepcopy(shell), vendor_code, queue, parse_oldfarm)),
        Thread(target=parse_wrapper, args=(deepcopy(shell), vendor_code, queue, parse_kotmatros)),
        Thread(target=parse_wrapper, args=(deepcopy(shell), vendor_code, queue, parse_magizoo))
    ]
    print("Первая ступень парсинга(Requests)")
    thread_control(threads)
    print("Первая ступень отпарсилась")
    data = unpack_queue(queue)
    ctr = 0
    name = None
    result = []
    for res, status in data:
        if status != ParserERRORS.PARSED:
            ctr += 1
        else:
            name = res["name"]
        result.append(res)
    if not name or ctr == 2:
        return ParserERRORS.PARSER_ERROR
    halfname = name[:(len(name) // 2)]
    threads = [
        Thread(target=parse_wrapper, args=(deepcopy(shell), name, queue, parse_4Lapy)),
        Thread(target=parse_wrapper, args=(deepcopy(shell), halfname, queue, parse_zoomag)),
        Thread(target=parse_wrapper, args=(deepcopy(shell), vendor_code, queue, parse_zoozavr)),
    ]
    print("Вторая ступень парсинга(Selenium)")
    thread_control(threads)
    print("Вторая ступень отпарсилась")
    data = unpack_queue(queue)
    for data_elem in data:
        result.append(data_elem[0])
    return result


def parse(username: str, vendor_code: str, multithreaded=False) -> list | ParserERRORS:
    if multithreaded:
        return parse_multithreaded(username, vendor_code)
    return parse_one_thread(username, vendor_code)


if __name__ == "__main__":
    # print(parse("admin", "7173549"))
    ans = parse("admin", "70085281", multithreaded=True)
    for a in ans:
        print(a)
    #shell = perform_json( "7173549", "admin")
    #print(parse_bethoven(deepcopy(shell), "7173549", mp=MultiParser(headless=False)))
