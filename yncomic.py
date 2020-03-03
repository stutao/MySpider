# -*- coding:utf-8 -*-
"""
__author__ = "TomTao"
"""

"""
反向解析了网站js加密url方式,通过requests进行爬取.
应该可以修改为分布式,或者使用队列
改进方式--待修改
	1,可以采用scrapy,加强代码健壮性,
	2,写入数据库,web直接通过对方url实行漫画展示(可能不是很好)

爬取一念漫画内容 安装依赖如下,
python3.6以上,
pip install requests lxml
pip install requests

网站编码这样查看
# print(requests.get(url).encoding)
# ISO-8859-1

输出格式是json 有些还没完善的地方后续有时间继续修改
"""

import json
import requests
import base64
import re
from lxml import etree


def print_list(text):
    print('>>' * 20)
    for i, name in enumerate(text, 1):
        print('{0}--{1}'.format(i, name))
    print('>>' * 20)


def req(key=None, url=None, **kwargs):
    if key:
        search_domain = kwargs['search_domain']
        search_req = requests.get(search_domain.format(key)).text
        search_html = etree.HTML(search_req)

        href = search_html.xpath(r"//div[@id='dmList']/ul/li/p/a/@href")
        text = search_html.xpath(r"//div[@id='dmList']/ul/li/p/a/img/@alt")
        return href, text
    elif url:
        domain = kwargs['domain']
        r = requests.get(url).text
        html = etree.HTML(r.encode('ISO-8859-1'))
        page_href = html.xpath("//div[@id='play_0']/ul/li/a/@href")
        href_list = list(map(lambda x: domain + x, page_href))
        title = html.xpath("//div[@id='play_0']/ul/li/a/@title")
        return href_list, title
    else:
        return


def get_chapter_urls_map(href_list, title):
    pics_urls_list = []
    # # 构成[[倒数第一urls],[倒数第二urls],[倒数第三urls]]
    for page in href_list:
        r = requests.get(page).text
        r0 = re.findall(r'qTcms_S_m_murl_e="(.*?)";', r)[0]
        r_decode = base64.b64decode(r0)
        r_urls = str(r_decode, encoding='UTF-8')
        r_urls_lis = r_urls.split('$qingtiandy$')
        pics_urls_list.append(r_urls_lis)
    chapter_urls_map = dict(zip(title, pics_urls_list))
    return chapter_urls_map


if __name__ == '__main__':
    search_domain = r'http://www.yn887.com/statics/search.aspx?key={}'
    domain = r'http://www.yn887.com/'
    # print(href)
    count = 1
    while count <= 3:
        key = input('Input Comic Name:')
        href, text = req(key=key, search_domain=search_domain)
        if len(href) <= 0:
            if count==3:
                print('重新启动吧')
                break
            else:
                print('没有找到{},还有{}次机会,请重新输入:'.format(key, 3-count))
                count += 1
        else:
            count = 1
            while count <=3:
                print_list(text)
                index = input('请输入序号:')
                if not index.isdigit() and int(index) > len(href):
                    if count == 3:
                        print('重新来过吧')
                        break
                    else:

                        print("重新输入,还有{}次".format(3-count))
                        count += 1
                else:
                    print(f'开始获取{text[int(index) - 1]}')
                    url = domain + href[int(index) - 1]
                    href_list, title = req(url=url, domain=domain)
                    chapter_urls_map = get_chapter_urls_map(href_list, title)
                    with open(text[int(index) - 1] + ".json", 'w', encoding='UTF-8') as fp:
                        fp.write(json.dumps(chapter_urls_map))
                    print(f"写入{text[int(index) - 1]}.json文件成功")
                    # 获取完成 写入成功

                    break
            break

