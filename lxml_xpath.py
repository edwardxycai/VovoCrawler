from lxml import etree
# text = '''
# <div>
#     <ul>
#          <li class="item-0"><a href="link1.html">first item</a></li>
#          <li class="item-1"><a href="link2.html">second item</a></li>
#          <li class="item-inactive"><a href="link3.html"><span class="bold">third item</span></a></li>
#          <li class="item-1"><a href="link4.html">fourth item</a></li>
#          <li class="item-0"><a href="link5.html">fifth item</a></li>
#      </ul>
#  </div>
# '''
# html = etree.HTML(text)
# result = etree.tostring(html, pretty_print=True)
# print(result)

html = etree.parse('hello.html')
print(type(html))
result = html.xpath('//li')
print(result)
print( len(result))
print(type(result))
print(type(result[0]))

result = html.xpath('//li/@class')
print(result)

result = html.xpath('//li/a[@href="link1.html"]')
print(result)

# 获取 <li> 标签下的所有 <span> 标签
# 注意这么写是不对的
# result = html.xpath('//li/span')

# text = '''
# <div>
#     <ul>
#          <li class="item-0"><a href="link1.html">first item</a></li>
#          <li class="item-1"><a href="link2.html">second item</a></li>
#          <li class="item-inactive"><a href="link3.html"><span class="bold">third item</span></a></li>
#          <li class="item-1"><a href="link4.html">fourth item</a></li>
#          <li class="item-0"><a href="link5.html">fifth item</a></li>
#      </ul>
#  </div>
# '''

result = html.xpath('//li//span')
print(result)

# 获取 <li> 标签下的所有 class，不包括 <li>
result = html.xpath('//li/a//@class')
print("获取 <li> 标签下的所有 class，不包括 <li>", result)

# 获取最后一个 <li> 的 <a> 的 href
result = html.xpath('//li[last()]/a/@href')
print(result)

# 获取倒数第二个元素的内容
result = html.xpath('//li[last()-1]/a')
print(result[0].text)

# 获取 class 为 bold 的标签名
result = html.xpath('//*[@class="bold"]')
print(result[0].tag)
