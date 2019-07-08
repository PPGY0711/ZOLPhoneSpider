# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZolItem(scrapy.Item):

    #basicInfo
    phoneID = scrapy.Field()        #手机编号
    phoneName = scrapy.Field()      #手机名称
    #Parameters
    phoneParam = scrapy.Field()     #手机参数
    #colors
    phonePic = scrapy.Field()       #手机图片
    #evaluation
    phoneEval = scrapy.Field()      #专业评测
    #news
    phoneNews = scrapy.Field()      #热门新闻




