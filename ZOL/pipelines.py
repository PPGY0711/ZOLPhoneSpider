# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymongo
from .items import ZolItem, imgItem
import re
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class ZolPipeline(object):
    def __init__(self):
        self.file = codecs.open(filename='parameter.json', mode='w+', encoding='utf-8')

    def process_item(self, item, spider):
        if isinstance(item, ZolItem):
            str = json.dumps(dict(item), ensure_ascii=False) + '\n'
            print(str)
            self.file.write(str)


    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        self.file.close()

class MongoPipeline(object):
    def __init__(self, databaseIp='127.0.0.1', databasePort=27017,
                 user='phoneYelp_rw', password='123456', mongodbName='phoneYelp'):
        client = pymongo.MongoClient(databaseIp, databasePort)
        self.db = client[mongodbName]
        self.db.authenticate(user, password)

    def process_item(self, item, spider):
        if isinstance(item, ZolItem):
            postItem = dict(item)
            self.db.phoneList.insert(postItem) #collection name = phoneList
            return item


#实现这两个流水线先后工作
#实现图片选取与下载（分类按手机名创建主文件夹，图片类别名创建子文件夹
#图片选取标准：每种手机在其颜色分类当中每个分类选取5张图，不足者取全部。

class ImgDownLoadPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if isinstance(item, imgItem):
            for j in range(len(item['imgCate'])):
                for i in range(1, len(item['imgUrls'][item['imgCate'][j]]) + 1):
                    print(item['imgUrls'][item['imgCate'][j]][i-1], item['imgUrls'][item['imgCate'][j]][i-1] is None)
                    if item['imgUrls'][item['imgCate'][j]][i-1] is not None:
                        imgName = item['imgUrls'][item['imgCate'][j]][i-1].split('/')[-1]
                        print(imgName)
                        yield Request(item['imgUrls'][item['imgCate'][j]][i-1],
                                      meta={'name': imgName, 'phoneName': item['imgPhone']})

    def file_path(self, request, response=None, info=None):
        name = response.meta['name']
        subFile = name[:str(name).index('_')]
        mainFile = response.meta['phoneName']
        #print(mainFile, subFile, name)
        filename = u'{0}/{1}/{2}'.format(mainFile, subFile, name)
        return filename
