# -*- coding:utf-8 -*-
"""
__author__ = "TomTao"
采用selenium自动化工具爬取漫画数据
适配漫漫看网站内容
https://manmankan.cc
"""
from selenium import webdriver
import os
import requests
import json
from time import sleep
import re

path = r"D:/study/chromedriver.exe"
path_prefix = r'D:/study/cartoon'
cartoon_url_map = {
    "斗罗大陆": r"https://manmankan.cc/manhua/49/",
    "斗破苍穹": r"https://manmankan.cc/manhua/40745/"
}

browser = webdriver.Chrome(executable_path=path)
for cy_title,url in cartoon_url_map.items():
    # 创建对应漫画主文件夹
    cytitle_path = os.path.join(path_prefix, cy_title)
    if cy_title not in os.listdir(path_prefix):
        os.mkdir(cytitle_path)
        print(f"{cy_title} 文件夹创建成功")
        print("*" * 30)

    chapter_name_url_map = {}
    if cy_title+".json" not in os.listdir(cytitle_path):
        print(f"准备开始爬取{cy_title}")
        browser.get(url)
        zhankai = browser.find_elements_by_xpath('//a[@id="zhankai"]')[0]
        zhankai.click()
        sleep(2)
        browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        # {"章节名":"url"}
        for index,href in enumerate(browser.find_elements_by_xpath("//ul[@id='mh-chapter-list-ol-0']/li/a")):
            chapter_name_url_map[href.text] = href.get_attribute('href')
        with open(os.path.join(cytitle_path,cy_title+".json"),'w',encoding="UTF-8") as f:
            f.write(json.dumps(chapter_name_url_map))
    else:
        print("章节名json")
        with open(os.path.join(cytitle_path,cy_title+".json"),'r',encoding="UTF-8") as p:
            chapter_name_url_map = json.loads(p.read())
    # print(chapter_name_url_map)
    # 存放所有的章节url
    # 这个存放是倒序的  最前面的是最后一章
    # 将最后图片名字切分出来,可以按照其中的数字进行排序
    chapter_name_picurls_map = {}
    if cy_title+"_url.json" not in os.listdir(cytitle_path):
        for k, v in chapter_name_url_map.items():
            browser.get(v)
            chapter_name_picurls_map[k] = [pic_url.get_attribute('value') for pic_url in browser.find_elements_by_tag_name('option')]
        with open(os.path.join(cytitle_path,cy_title+"_url.json"),"w",encoding="UTF-8") as u:
            u.write(json.dumps(chapter_name_picurls_map))
    else:
        print("章节page_url.json")
        with open(os.path.join(cytitle_path,cy_title+"_url.json"), 'r', encoding="UTF-8") as p:
            chapter_name_picurls_map = json.loads(p.read())
    print('图片href获取完毕,准备开始存储图片')
    # 获取图片并保存
    for name, urls in chapter_name_picurls_map.items():
        # 创建章节名字文件夹
        if name not in os.listdir(cytitle_path):
            # print('name',name)
            chapter_dir_path = os.path.join(cytitle_path, name)
            chapter_dir_path = re.sub(r"/", "(", chapter_dir_path)
            os.mkdir(chapter_dir_path)
            # 取出所有url通过requests进行图片下载
            for index, url in enumerate(urls, 1):
                file = requests.get(url)
                with open(os.path.join(chapter_dir_path, str(index) + '.jpg'), "wb") as fp:
                    fp.write(file.content)
            print(f'{name}下载完毕')
        else:
            continue
    print(f"{cy_title}已有章节全部下载完毕",end=" ")

browser.close()
