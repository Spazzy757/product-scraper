import requests
import time

from bs4 import BeautifulSoup
from datetime import datetime
from elasticsearch import Elasticsearch

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
}
es = Elasticsearch([{"host": "es01", "port": 9200}])


def main():
    url = "https://www.komplett.no/sitemap.products.xml"
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, "html.parser")
    products = soup.find_all("loc")
    for product in products:
        product_req = requests.get(product.get_text(), headers)
        product_soup = BeautifulSoup(product_req.content, "html.parser")
        data = {}
        html = product_soup.body
        data["title"] = get_title(html)
        data["price"] = get_price(html)
        data["description"] = get_description(html)
        data["image_urls"] = get_image_urls(html)
        data["url"] = product.get_text()
        insert_into_elasticsearch(data)


def get_title(html):
    info = html.find_all("h1", class_="product-main-info-webtext1")
    if len(info) > 0:
        return info[0].get_text().strip()


def get_price(html):
    info = html.find_all("span", class_="product-price-now")
    if len(info) > 0:
        return float(
            info[0].get_text().replace("-", "00").replace("\xa0", "").replace(",", ".")
        )


def get_description(html):
    info = html.find_all("div", class_="product-responsive-info")
    if len(info) > 0:
        return info[0].get_text().strip()


def get_image_urls(html):
    image_list = []
    for image in html.find_all("img", class_="item-content"):
        image_list.append(f"https://www.komplett.no{image.get('src')}")
    return image_list


def insert_into_elasticsearch(data):
    res = es.index(index="products", body=data)
    print(res)


if __name__ == "__main__":
    time.sleep(30)
    main()
