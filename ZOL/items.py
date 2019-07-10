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
    phonePic = scrapy.Field()       #图片链接
    #evaluation
    phoneEval = scrapy.Field()      #专业评测
    #news
    phoneNews = scrapy.Field()      #热门新闻
    #score
    phoneGrade = scrapy.Field()     #手机评分
    phoneCTimes = scrapy.Field()    #打分人数

class imgItem(scrapy.Item):
    #for phone pictures download
    imgPhoneID = scrapy.Field()     #手机ID
    imgUrls = scrapy.Field()        #图片链接
    imgCate = scrapy.Field()        #图片类别
    imgPhone = scrapy.Field()       #文件夹名



