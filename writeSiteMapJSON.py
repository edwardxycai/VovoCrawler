
from urllib.request import urlopen, urlretrieve
import json
import os

for m in range(0, 12):
    print("现在处理" + str(m + 1) + "月")
    url = "https://www.google.com/doodles/json/2018/" + str(m + 1) + "?hl=zh_TW"

    response = urlopen(url)
    doodles = json.load(response)
    #print(doodles)
    for d in doodles:

        url = "http:" + d["url"]
        print(d["title"], url)

        dir = "doodles/" + str(m + 1) + "/"

        if not os.path.exists(dir):
            os.mkdir(dir)

        fname = dir + url.split("/")[-1]

        print(fname)
        # response = urlopen(url)
        # img = response.read()
        #
        # f = open(fname, "wb")
        # f.write(img)
        # f.close()

        urlretrieve(url, fname)