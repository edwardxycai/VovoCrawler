from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
import re
import json
import requests

#page = 51
#while True:
rootURL = "http://www.ipeen.com.tw"
url = 'https://www.ipeen.com.tw/comment/1736710'
#print("处理页面： ", url)
try:
    response = requests.get(url)
except HTTPError:
    print("好像是抓完了")

html = BeautifulSoup(response.text)

# print(html)
# html.find_all("li", {"class":"list-rst"})
# for r in html.find_all("a", class_="list-rst"):
# for r in html.find_all("a", {"class": "a37 ga_tracking"}, {"data-action": "food_navigation"},
#                        href=re.compile("/search/taiwan/000/")):
level = 1

# pattern 1
# <p>...</p>
# <p>sdbsbasbssf</p>

# pattern 2
# <div>...<div>
# <div>sfsjfkjsfjsl</div>

# pattern 3
# <div>...</div>
#   <p>...</p>
#     <span>...</span>
#     <span>sjfjsfdsfjsjfsj</span>


desc = html.find("div", {"class": "description"})
data = []
p_paras = desc.find_all("p")
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

    print(p_para.get_text())


#    // *[ @ id = "comment"] / section / div / div[3] / div / p[1] / text()[1]
#     print(container.p.string)

#     c_data = {}
#     #print(container)
#     # c_data['level'] = 1
#     c_data['href'] = container['href']
#     c_data['text'] = container.text
#     data.append(c_data)
#     #print(json.dumps(data))
# data = '{ "level": 1, "url": "' + url + '", "childURL": ' + json.dumps(data) + ' }'
# with open("sitemap.json", "w", encoding='utf-8') as writeJSON:
#     writeJSON.write(data)

# with open("sitemap.json", "r", encoding='utf-8') as readJSON:
#     data = json.load(readJSON)
#
# #print(data)
# childURLs = data["childURL"]
# #print(urls)
# for child in childURLs:
#     url = rootURL + child["href"]
#     try:
#         print(url)
#         response = urlopen(url)
#     except HTTPError:
#         print("好像是抓完了")
#
#     html = BeautifulSoup(response)
#     #print(html)
#
#     containers = html.find_all("div", {"class": "serShop"})
#     print(containers)
#     data = []
#     for container in containers:
#         c_data = {}
#         print(type(container))
#         c_data["href"] = container.find("a")["href"]
#         # c_data['level'] = 1
#         ##c_data['href'] = container['href']
#         #c_data['text'] = container.find("a")["text"]
#         c_data["data-sid"] = container["data-sid"]
#         c_data["data-shopname"] = container.find("a")["data-shopname"]
#         data.append(c_data)
#         print(data)
#         print(json.dumps(data))
#
#     # ja = r.find("small", class_="list-rst__name-ja")
#     # en = r.find("a", class_="list-rst__name-main js-detail-anchor")
#     # print(en)
#     # scores = r.find_all("b", class_="c-rating__val")
#     # print(scores)
#     # print(scores[0].text, scores[1].text, scores[2].text, en.text, ja.text, en["href"])
# #page = page + 1
