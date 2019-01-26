# -*- coding:utf-8 -*-
'''
Created on 20160827
@author: qiukang
'''
import requests
import time
import threading
from bs4 import BeautifulSoup
# HTML
#請求頭
header = {
'Accept':'text/html,application/xhtml xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-CN,zh;q=0.8',
'Connection':'keep-alive',
'Host':'www.zhongchou.com',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2593.0 Safari/537.36'
}
data = set()
no = 0
lock = threading.Lock()
# 獲得專案url列表
def getItems(urllist,thno):
# print urllist
# print thno," begin at",time.clock()
global no,lock,data
for url in urllist:
r1 = requests.get(url,headers=header)
html = r1.text.encode('utf8')
start = 5000
while  True:
index = html.find("deal-show", start)
if index == -1:
break
lock.acquire()
data.add("http://www.zhongchou.com/deal-show/" html[index 10:index 19] "\n")
start = index    1000
lock.release()
# print thno," end at",time.clock()
if __name__ == '__main__':
start = time.clock()
allpage = 30  #頁數
allthread = 10 #執行緒數
per = (int)(allpage/allthread)
urllist = []
ths = []
for page in range(allpage):
if page==0:
url = 'http://www.zhongchou.com/browse/di'
else:
url = 'http://www.zhongchou.com/browse/di-p' str(page 1)
urllist.append(url)
for i in range(allthread):
# print urllist[i*(per):(i 1)*(per)]
low = i*allpage/allthread#注意寫法
high = (i 1)*allpage/allthread
# print low,' ',high
th = threading.Thread(target = getItems,args= (urllist[low:high],i))
ths.append(th)
for th in ths:
th.start()
for th in ths:
th.join()
items = open('pymulti.txt','a')
items.write("".join(data))
items.close()
end = time.clock()
print('it takes %s Seconds to get %s items '%(end-start,len(data)))