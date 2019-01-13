
import concurrent.futures
import requests
import sys
from bs4 import BeautifulSoup
import datetime
import time
import random
import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

header = {'User-Agent':
          'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)\
          Chrome/71.0.3578.98 Safari/537.36'}

# mongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["CB104T3"]

try:
    client.admin.command('ismaster')
except ConnectionFailure:
    print("Server not available")

col3 = db["sitemap-3"]
col4 = db["comment"]
col5 = db["free-proxy"]

# load proxy list
plist = list()
data_json = col5.find_one()
proxies = data_json["proxylist"]
for proxy in proxies:
    p_data = dict()
    p_data[proxy["protocol"]] = proxy["ipport"]
    plist.append(p_data)

site = "http://www.ipeen.com.tw"
top_url = "http://www.ipeen.com.tw/taipei/channel/F"
# cat_url = None
cat_list = list()
category = None
categoryID = None
page = None
url_list = list()
cc_list = list()    # comment content list


def request_page(url):
    try:
        # pi = random.randint(0, 299)
        pi = 100
        res = requests.get(url, headers=header, proxies=plist[pi])
        res.encoding = "utf-8"
        return res
    except requests.exceptions.ConnectionError:
        pi = (pi + 1) % 300
        pi = (pi + 1) % 300
        # res.close()
        res = requests.get(url, headers=header, proxies=plist[pi])
        res.encoding = "utf-8"
        return res
    except requests.Timeout as e:
        print(e)
        sys.exit(1)
    except requests.TooManyRedirects as e:
        print(e)
        sys.exit(1)
    except requests.HTTPError as e:
        # 404, 503, 500, 403 etc.
        print(e.response.status_code)
        sys.exit(1)
    except requests.RequestException as e:
        print(e)
        sys.exit(1)


def produce_comment(res):
    html = BeautifulSoup(res.text, "lxml")
    # get one page of comment hyperlinks for certain shop

    # // *[ @ id = "comment"] / section / div / div[3] / div[1] / p[2] / span / text()
    str_data = ""
    article = html.find("div", {"class": "description"})
    containers = article.find_all("p")
    if containers is not None:
        for container in containers:
            str_data += container.text

        str_data = '{ "comment": "' + str_data + '" }'
        cc_list.append(str_data)


def scrap_shop(urls):
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        future_obj = {executor.submit(request_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_obj, 100):
            url = future_obj[future]
            try:
                res = future.result()
                process_comment(res)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


def scrap_comment(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_obj = {executor.submit(request_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_obj, 100):
            url = future_obj[future]
            try:
                res = future.result()
                produce_comment(res)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


def process_shop():
    p = 0
    urls = list()

    while p < len(url_list):
        # copy 1 to 5 shop'(s) url(s) to urls
        b_more_to_process = True
        urls.append(url_list[p])
        if (p + 1) % 5 == 0:    # if 5 urls were in urls, then call scrap
            scrap_shop(urls)
            b_more_to_process = False
            urls = list()
            time.sleep(2)

        p += 1

    if b_more_to_process:
        scrap_shop(urls)
        time.sleep(2)


def process_comment(res):
    global cc_list

    html = BeautifulSoup(res.text, "lxml")
    # get one page of comment hyperlinks for certain shop
    containers = html.find_all("a", {"itemprop": "discussionUrl url"})

    comment_list = list()
    for container in containers:
        comment_list.append(site + container["href"])

    scrap_comment(comment_list)
    for cc in cc_list:
        col4.insert_one(json.loads(cc))

    cc_list = list()


if __name__ == "__main__":
    cursor_size = 1
    b_page = 1
    # get (15) shops of one page each time
    while True:
        # get cursor from sitemap-3 with page number from 'b_page' to 'e_page'
        myQuery = {"page": {"$gte": b_page, "$lt": b_page + cursor_size}}
        results = list(col3.find(myQuery))
        url_list = list()
        if len(results) > 0:
            # process documents in cursor one by one
            for result in results:
                # categoryID = result["categoryID"]
                # category = result["category"]
                # page = result["page"]
                # populate url_list
                url_list.append(site + result["comment"])

            process_shop()
            b_page += cursor_size
        else:
            break

    client.close()
