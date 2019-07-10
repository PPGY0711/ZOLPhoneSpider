# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymongo
import re
import scrapy
import copy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class ZolPipeline(object):
    def __init__(self):
        self.file = codecs.open(filename='parameter.json', mode='w+', encoding='utf-8')

    def process_item(self, item, spider):
        str = json.dumps(dict(item), ensure_ascii=False) + '\n'
        print(str)
        self.file.write(str)
        yield item

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

        for Item in item:
            print(Item)
            postItem = dict(Item)
            self.db.phoneList.insert(postItem) #collection name = phoneList


#实现图片选取与下载（分类按手机名创建主文件夹，图片类别名创建子文件夹
#已弃用，图片无须下载到本地。
class ImgDownLoadPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        """处理imgitem中的图片链接和下载"""
        for Item in item:
            #print(Item)
            for key, valuelist in Item['phonePic'].items():
                for image_url in valuelist:
                    imgName = image_url.split('/')[-1]
                    #print(image_url, imgName, Item['phoneName'][0])
                    # Unsolved: 这里Request一直是返回不了，抛出NoneType错误
                    # 但是在ZOLSpider当中测试爬取一条图片链接可以返回图片对象
                    yield scrapy.Request(image_url, callback=self.file_path,
                                         meta={'name': copy.deepcopy(imgName),
                                         'phoneName': copy.deepcopy(Item['phoneName'][0])}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        """分文件夹储存"""
        print(request.url)
        name = response.meta['name']
        mainFile = re.sub(r'[？\\*|“<>:/]', '', response.meta['phoneName'])
        print(mainFile, name)
        filename = u'full/{0}/{1}'.format(mainFile, name)
        return filename

    def item_completed(self, results, item, info):
        print(results)
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item
