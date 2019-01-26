
import concurrent.futures
import requests
import sys
from bs4 import BeautifulSoup
import re
import json
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class SiteMap:
    def __init__(self, urls):
        # connection
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["CB104T3"]
        self.col1 = self.db["sitemap-1"]
        self.col2 = self.db["sitemap-2"]

        self.header = {'User-Agent':
                       'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)\
                       Chrome/71.0.3578.98 Safari/537.36'}
        self.proxylist = [{"http": "37.187.120.123:80"},
                          {"https": "206.189.36.198:8080"},
                          {"https": "178.128.31.153:8080"},
                          {"http": "167.114.180.102:8080"},
                          {"http": "104.131.214.218:80"},
                          {"http": "167.114.196.153:80"},
                          {"http": "142.93.66.59:8080"},
                          {"http": "200.254.125.5:80"},
                          {"http": "193.70.52.233:80"},
                          {"http": "212.23.250.46:80"}]

        try:
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            print("Server not available")

        self.rootURL = "http://www.ipeen.com.tw"
        self.url = 'http://www.ipeen.com.tw/taiwan/channel/F'
        self.urls = None
        self.pi = 0

    def request_page(self, url):
        try:
            res = requests.get(url, headers=self.header, proxies=self.proxylist[self.pi])
            res.encoding = "utf-8"
        except requests.exceptions.ConnectionError:
            self.pi = (self.pi + 1) % 10
            res.close()
            res = requests.get(url, headers=self.header, proxies=self.proxylist[self.pi])
            res.encoding = "utf-8"
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
        finally:
            return res

    def write_lvl_1(self, res):
        html = BeautifulSoup(res.text, "lxml")
        containers = html.find_all("a",
                                   {"data-action": "food_navigation"},
                                   {"class": "a37 ga_tracking"},
                                   href=re.compile("/search/taiwan/000/"))
        data = []
        for container in containers:
            c_data = dict()
            c_data['href'] = container['href'].replace("taiwan", "taipei")
            c_data['text'] = container.text
            data.append(c_data)

        dataStr = '{ "level": "1", "datetime": "' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
                  '", "url": "' + url + '", "childURL": ' + json.dumps(data) + ' }'
        self.col1.insert_one(json.loads(dataStr))

    def scrap(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(self.request_page, url): url for url in self.urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Execption as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    print('%r page length is %d' % (url, len(data)))

    def process_lvl_2(self):

        res = self.request_page(self.urls)
        soup = BeautifulSoup(res.text, "lxml")
        containers = soup.find_all("div", {"class": "serShop"})

        for child in self.childURLs:
            url = rootURL + child["href"]
            page = 1

            # get all pages of certain category
            ####################################
            while True:
                if page > 10:
                    break

                try:
                    response = requests.get(url, headers=header, proxies=proxylist[pi])
                    response.encoding = "utf-8"
                    while response.status_code != 200:
                        pi = (pi + 1) % 10
                        response.close()
                        response = requests.get(url, headers=header, proxies=proxylist[pi])
                        response.encoding = "utf-8"

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

                pageHTML = BeautifulSoup(response.text, "lxml")
                containers = pageHTML.find_all("div", {"class": "serShop"})
                #       print(containers)
                data = []

                # one page within certain cuisine category
                ##########################################
                for container in containers:
                    print(container)
                    c_data = dict()
                    tmp = container.find("a")
                    c_data["href"] = tmp["href"]
                    c_data["data-sid"] = container["data-sid"]
                    c_data["data-shopname"] = tmp["data-shopname"]
                    data.append(c_data)
                #           print(data)

                dataSTR = '{ "level": "2", "' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + \
                          '", "category": "' + child["text"] + '", "page": "' + str(page) + '", "url": "' \
                          + child["href"] + '", "childURL": ' + json.dumps(data) + ' }'
                col2.insert_one(json.loads(dataSTR))

                url = pageHTML.find("a", {"data-action": "page"}, {"data-label": str(page + 1)})["href"]
                page = page + 1
                # print(url)

            client.close()


def main():
    sm = SiteMap()
    # get level 1 restaurant category
    res = sm.request_page(sm.url)
    # write level 1 restaurant category to mongodb, DB: CB104T3, Collection: sitemap-1
    sm.write_lvl_1(res)

    # read restaurant category from sitemap-1
    data_json = sm.col1.find_one()
    child_urls = data_json["childURL"]
    sm_list = list()
    nchild = 0
    for child in child_urls:
        sm_tmp = SiteMap()
        sm_tmp.urls = sm_tmp.root_url + child["href"]
        sm_list.append(sm_tmp)





if __name__ == '__main__:':
    main()
