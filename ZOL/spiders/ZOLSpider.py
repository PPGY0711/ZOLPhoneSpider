# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import ZolItem
import copy
import time
from lxml import etree

class ZolSpider(scrapy.Spider):
    name = 'Zol'
    offset = 1
    itemcnt = 1
    url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'
    start_urls = [url.format(str(offset))]

    def parse(self, response):
        #first session
        prefix = 'http://detail.zol.com.cn'
        #print("11--------------------------------------------")
        links = response.xpath('//div[@class="pic-box SP"]/a/@href').extract()
        print(len(links))
        for link in links:
            item = ZolItem()
            #print(link)
            yield scrapy.Request(prefix+str(link), meta={'item': copy.deepcopy(item)}
                                 , callback=self.first_parse_page, dont_filter=True)

        #second session
        m_page = 1
        #print("12--------------------------------------------")
        if self.offset < m_page:
            self.offset += 1
            time.sleep(5) #scrapy one page and stop 5 seconds
            #print(self.url.format(str(self.offset)))
            yield scrapy.Request(self.url.format(str(self.offset)), callback=self.parse, dont_filter=True)

    def first_parse_page(self, response):
        prefix = 'http://detail.zol.com.cn'
        #print("21--------------------------------------------")
        urls = response.xpath('//*[@id="_j_tag_nav"]/ul')
        navitems = urls.xpath('li/a/text()').extract()
        paramindex = navitems.index('参数')
        paramurl = response.xpath('//*[@id="_j_tag_nav"]/ul/li[{}]/a'.format(str(paramindex + 2)))
        suffix = paramurl.xpath('@href').extract_first()
        if suffix is not None:
            paramurl = prefix+str(suffix)
            item = response.meta['item']
            item['phonePic'] = {}
            yield scrapy.Request(paramurl, meta={'item': copy.deepcopy(item)}, callback=self.param_parse_page
                                 , dont_filter=True)

    def param_parse_page(self, response):
        #print("31---------------------------------")
        condition = response.xpath('//h1[@class="product-model__name"]').extract_first()
        #print("condition is: ", self.itemcnt, condition)
        item = response.meta['item']
        if condition is not None:
            pName = response.xpath('//h1[@class="product-model__name"]/text()').extract_first()[:-2]
            if response.xpath('//h2[@class="product-model__alias"]/text()').extract_first() is not None:
                alias = response.xpath('//h2[@class="product-model__alias"]/text()').extract_first()
                item['phoneName'] = [pName, alias]
            else:
                item['phoneName'] = [pName]
            item['phoneID'] = self.itemcnt
            self.itemcnt += 1

            node_list = response.xpath('//div[@class="detailed-parameters"]')
            paramdicts = {}
            infocategory = node_list.xpath('//td[@class = "hd"]/text()').extract()
            for j in range(1, len(node_list.xpath('//td[@class = "hd"]/text()').extract())+1):
                infotable = node_list.xpath('table[{}]'.format(str(j)))
                infoitemheader = []
                infoitemctnt = []
                for i in range(1, len(infotable.xpath('tr'))+1):
                    if infotable.xpath('tr[{}]/th/span[@*]/text()'.format(str(i))).extract() != []:
                        infoitemheader.append(re.sub(r'^,','',re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/th/span[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    elif infotable.xpath('tr[{}]/th/a[@*]/text()'.format(str(i))).extract() != []:
                        infoitemheader.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/th/a[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    if infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() != [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() == []:
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/td/span[@*]/text()'
                                            .format(str(i))).extract())\
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    elif infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() == [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() != []:
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/td/span/a[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    elif infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() != [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() != []:
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/td/span[@*]/text()'
                                            .format(str(i))).extract()).replace('，', ',')
                                            .replace('>', '').replace('＞', '').replace('\r\n', ',').strip() +
                                            ','.join(infotable.xpath('tr[{}]/td/span/a[@*]/text()'
                                            .format(str(i))).extract())\
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', '').strip())))
                    paramdicts[infocategory[j-1]] = dict(zip(infoitemheader, infoitemctnt))
            item['phoneParam'] = paramdicts

        #picture spider
        prefix = 'http://detail.zol.com.cn'
        #print("21--------------------------------------------")
        urls = response.xpath('//div[@id="_j_tag_nav"]/ul')
        navitems = urls.xpath('li/a/text()').extract()
        try:
            picindex = navitems.index('图片')
            picurl = response.xpath('//*[@id="_j_tag_nav"]/ul/li[{}]/a'.format(str(picindex + 2)))

            suffix = picurl.xpath('@href').extract_first()
            if suffix is not None:
                picurl = prefix+str(suffix)

                #print(paramurl == 'http://detail.zol.com.cnhttp//detail.zol.com.cn')
                yield scrapy.Request(picurl, meta={'item': copy.deepcopy(item)},
                                     callback=self.pic_parse_page, dont_filter=True)
        except Exception as e:
            yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)},
                                 callback=self.item_parse, dont_filter=True)

    def pic_parse_page(self, response):
        #print("41---------------------------------")
        prefix = 'http://detail.zol.com.cn'

        #颜色页面种类：有两种分类的；仅有颜色分类；两者都没有
        item = response.meta['item']
        condition = response.xpath('//div[@class="product-model page-title clearfix"]/h1/text()').extract_first()
        #print(condition)
        if condition != []:

            # 准备评测行情页面的Spider
            urls = response.xpath('//div[@id="_j_tag_nav"]/ul')
            navitems = urls.xpath('li/a/text()').extract()
            # print("导航栏: ", navitems)
            try:
                pageindex = navitems.index('评测行情')
                pageurl = prefix + \
                          str(response.xpath(
                              '//*[@id="_j_tag_nav"]/ul/li[{}]/a/@href'.format(str(pageindex + 2))).extract_first())
                #print(pageurl)
            except Exception as e:
                pageurl = prefix

            picdivide = {}
            tmpath = response.xpath('//div[@class="content"]')
            if tmpath.xpath('//a[@class="active"]') != []:
                if tmpath.xpath('//ul[@class="pics-category-list"]/li[2]/a/@href').extract_first() != []:
                    url = prefix + tmpath.xpath('//ul[@class="pics-category-list"]/li[2]/a/@href').extract_first()
                    #print(url == 'http://detail.zol.com.cnhttp//detail.zol.com.cn')
                    yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(pageurl),
                                                    'picdivide': copy.deepcopy(picdivide)},
                                                     callback=self.pic_parse_following_page, dont_filter=True)
            elif tmpath.xpath('//div[@class="pics-category"]') != []:
                url = prefix + tmpath.xpath('//li[1]/a/@href').extract_first()
                #print(url == 'http://detail.zol.com.cnhttp//detail.zol.com.cn')
                yield scrapy.Request(url, meta={'item': copy.deepcopy(item),
                                                    'picdivide': copy.deepcopy(picdivide)},
                                     callback=self.pic_parse_following_page, dont_filter=True)
            #直接在当前页处理图片链接
            else:
                typeName = response.xpath('//div[@class="section-header"]/h3/text()').extract_first()
                link = response.xpath('//ul[@class="picture-list clearfix"]')
                links = link.xpath('li/a/@href').extract()
                pics = []
                for link in links:
                    pics.append(prefix + str(link))
                item['phonePic'] = {str(typeName).strip(): pics}
                if pageurl != prefix:
                    yield scrapy.Request(pageurl, meta={'item': copy.deepcopy(item)
                                         , 'articleurl': copy.deepcopy(pageurl)},
                                         callback=self.news_parse_page, dont_filter=True)
                else:
                    yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)},
                                         callback=self.item_parse, dont_filter=True)

    def pic_parse_following_page(self, response):
        #print('51--------------------------------------')
        prefix = 'http://detail.zol.com.cn'
        articleurl = response.meta['articleurl']
        wholecate = response.xpath('//div[@class="pic-cate-content"]//li')

        activeNum = 1
        for i in range(1, len(wholecate) + 1):
            if wholecate[i-1].xpath('a[@class="active"]') != []:
                activeNum = i
                break
        typeName = response.xpath('//div[@class="section-header"]/h3/text()').extract_first()
        item = response.meta['item']
        picdivide = response.meta['picdivide']

        if typeName is not None and typeName != u'评测长图':
            link = response.xpath('//ul[@class="picture-list clearfix"]')
            links = link.xpath('li/a/@href').extract()
            pics = []
            for link in links:
                pics.append(prefix + str(link))
            picdivide[str(typeName).strip()] = pics
            item['phonePic'] = picdivide
        if activeNum + 1 <= len(wholecate):
            url = prefix + wholecate[activeNum].xpath('a/@href').extract_first()
            yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(articleurl),
                                            'picdivide': copy.deepcopy(picdivide)},
                                 callback=self.pic_parse_following_page, dont_filter=True)
        else:
            if articleurl != prefix:
                yield scrapy.Request(articleurl, meta={'item': copy.deepcopy(item)},
                                     callback=self.news_parse_page, dont_filter=True)
            else:
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)},
                                 callback=self.item_parse, dont_filter=True)

    def news_parse_page(self, response):
        prefix = 'http://detail.zol.com.cn'
        #评测行情页面：可能的条目有“专业评测”，“热门新闻”
        item = response.meta['item']
        condition = response.xpath('//div[@class="product-model page-title clearfix"]/h1/text()').extract_first()

        if condition != []:

            nodeIds = response.xpath('//div[@class="section-article"]/div/@id').extract()
            if 'bbsDoc' in nodeIds:
                del nodeIds[nodeIds.index('bbsDoc')]

            articleNums = [0]*2
            itemArtDic = {'newsDoc': 'phoneNews', 'evalDoc': 'phoneEval'}
            if len(nodeIds) != 0:
                for i in range(len(nodeIds)):

                    if i == 0:
                        articleSet = response\
                            .xpath('//div[@id="' + nodeIds[i] + '"]/ul[@class="content-list"]/li[@class=" clearfix"]')\
                            .extract()

                    else:
                        page = response.xpath('//div[@id="' + nodeIds[i] + '"]/textarea').extract_first()\
                            .replace('<textarea>', '').replace('</textarea>', '')
                        page = etree.HTML(page)
                        articleSet = page \
                            .xpath('//div[@id="' + nodeIds[i] + '"]/ul[@class="content-list"]/li[@class=" clearfix"]') \

                    articleNums[i] = len(articleSet)

                    articleInfos = []
                    for j in range(1, articleNums[i] + 1):
                        artRecord = {}
                        allInfo = response.xpath('//div[@id="' + nodeIds[i]
                                              + '"]/ul/li[{}]'.format(str(j)))
                        artRecord['articleID'] = j
                        artRecord['articleLink'] = allInfo.xpath('a/@href').extract_first()
                        artRecord['articleTitle'] = allInfo.xpath('div[@class="article-title"]/a/text()')\
                            .extract_first()
                        artRecord['articlePara'] = allInfo.xpath('p/text()').extract_first()
                        artRecord['articleDate'] = allInfo\
                            .xpath('div[@class="article-source clearfix"]/span[@class="article-date"]/text()')\
                            .extract_first()
                        try:
                            artRecord['articleAuthor'] = allInfo\
                                .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()')\
                                .extract_first() \
                                + " " + allInfo \
                                .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()')\
                                .extract_first()
                        except Exception as e:
                            artRecord['articleAuthor'] = 'Anonymous'
                        articleInfos.append(artRecord)

                    item[itemArtDic[nodeIds[i]]] = articleInfos

        yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)},
                             callback=self.item_parse, dont_filter=True)


    def item_parse(self, response):

        item = response.meta['item']
        yield copy.deepcopy(item)
