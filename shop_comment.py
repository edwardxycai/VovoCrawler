
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
url_list = list()


def request_page(url):
    try:
        # pi = random.randint(0, 299)
        pi = 100
        x_url = url.split()[0]
        res = requests.get(x_url, headers=header, proxies=plist[pi])
        res.encoding = "utf-8"
        return res
    except requests.exceptions.ConnectionError:
        pi = (pi + 1) % 300
        pi = (pi + 1) % 300
        # res.close()
        res = requests.get(x_url, headers=header, proxies=plist[pi])
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


def write_comment(res, url):
    # shop comment patterns:
    # -----------------------------------
    # pattern 1
    # <p>...</p>
    # <p>sdbsbasbssf</p>
    # -----------------------------------
    # pattern 2
    # <div>...<div>
    # <div>sfsjfkjsfjsl</div>
    # -----------------------------------
    # pattern 3
    # <div>...</div>
    #   <p>...</p>
    #     <span>...</span>
    #     <span>sjfjsfdsfjsjfsj</span>
    # -----------------------------------
    html = BeautifulSoup(res.text, "lxml")
    # get one page of comment hyperlinks for certain shop
    str_comment = ""
    desc = html.find("div", {"class": "description"})
    p_paras = desc.find_all_next(text=True)

    # p_paras = desc.find_all("p")
    for p_para in p_paras:
        span_para = p_para.find_all("span")
        for span in span_para:
            span.extract()
        b_para = p_para.find_all("b")
        for b in b_para:
            b.extract()
        img_para = p_para.find_all("img")
        for img in img_para:
            img.extract()

        str_comment += p_para.get_text()

    s_list = url.split()
    str_data = '{ "shopObjectId": ' + s_list[1] + ', "name": ' + s_list[2] + ', "url": ' + s_list[0] + \
               ', "commentContent": "' + str_comment + '" }'
    col4.insert_one(json.loads(str_data))


def scrap_shop(urls):
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        future_obj = {executor.submit(request_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_obj, 100):
            url = future_obj[future]
            try:
                res = future.result()
                process_comment(res, url)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


def scrap_comment(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_obj = {executor.submit(request_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_obj, 100):
            url = future_obj[future]
            try:
                res = future.result()
                write_comment(res, url)
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


def process_comment(res, url):
    html = BeautifulSoup(res.text, "lxml")
    # get one page of comment hyperlinks for certain shop
    containers = html.find_all("a", {"itemprop": "discussionUrl url"})

    comment_list = list()
    for container in containers:
        # comment_list = url + ObjectId + name
        s_list = url.split()
        t_str = site + container["href"] + " " + s_list[1] + " " + s_list[2]
        comment_list.append(t_str)

    scrap_comment(comment_list)


if __name__ == "__main__":
    cursor_size = 1
    b_page = 1
    # get (15) shops of one page each time
    while True:
        # get cursor from sitemap-3 with page number from 'b_page' to 'e_page'
        myQuery = {"page": {"$gte": b_page, "$lt": b_page + cursor_size}}
        results = list(col3.find(myQuery))
        object_list = list()
        name_list = list()
        url_list = list()
        if len(results) > 0:
            # process documents in cursor one by one
            for result in results:
                # populate url_list)
                # url_list = url + ObjectId + name
                tmp_str = site + result["comment"] + " " + str(result["_id"]) + " " + result["name"]
                url_list.append(tmp_str)

            process_shop()
            b_page += cursor_size
        else:
            break

    client.close()
