# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import ZolItem
from ..items import imgItem
import copy
import time
from lxml import etree
from scrapy_splash import SplashRequest
from scrapy_redis.spiders import RedisSpider


class ZolSpider(RedisSpider):
    """改用RedisSpider"""
    name = 'Zol'
    # offset = 1
    itemcnt = 1
    #url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'
    # start_urls = [url.format(str(offset))]
    redis_key = 'Zol:start_urls'

    def parse(self, response):
        """分页面爬取一页所有的手机信息"""
        # first session
        prefix = 'http://detail.zol.com.cn'

        links = response.xpath('//div[@class="pic-box SP"]/a/@href').extract()
        boxs = response.xpath('//div[@class="pic-box SP"]')

        for i in range(1,len(links) + 1):  # for test
            item = ZolItem()
            # 评分相关选项，默认值全为0
            item['phoneGrade'] = 0
            item['phoneCTimes'] = 0
            imgitem = imgItem()
            # 处理商品缩略图
            #print(len(boxs), len(links))
            item['phoneIcon'] = boxs[i-1].xpath('@data-rel').extract_first().replace('_280x210', '')
            yield scrapy.Request(prefix+str(links[i-1]), meta={'item': copy.deepcopy(item),
                                 'imgitem': copy.deepcopy(imgitem)}
                                 , callback=self.first_parse_page, dont_filter=True)

        # second session
        # """下一页，用于scrapy爬虫，非分布式"""
        # m_page = 1
        # # m_page = 1 #for test
        #
        # if self.offset < m_page:
        #     self.offset += 1
        #     # time.sleep(10) # scrapy one page and stop 10 seconds
        #     print('handling for page {}'.format(str(self.offset)))
        #     yield scrapy.Request(self.url.format(str(self.offset)), callback=self.parse, dont_filter=True)

    def first_parse_page(self, response):
        """准备爬取参数页"""
        prefix = 'http://detail.zol.com.cn'

        urls = response.xpath('//*[@id="_j_tag_nav"]/ul')
        navitems = urls.xpath('li/a/text()').extract()
        #print(navitems)
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        try:
            paramindex = navitems.index('参数')
            paramurl = response.xpath('//*[@id="_j_tag_nav"]/ul/li[{}]/a'.format(str(paramindex + 2)))
            suffix = paramurl.xpath('@href').extract_first()
            if suffix is not None:
                paramurl = prefix+str(suffix)
                item['phonePic'] = {}
                yield scrapy.Request(paramurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)}
                                     , callback=self.param_parse_page, dont_filter=True)
        except Exception as e:
            yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                 callback=self.item_parse, dont_filter=True)


    def param_parse_page(self, response):
        """爬取参数页，准备爬取图片页"""
        condition = response.xpath('//h1[@class="product-model__name"]').extract_first()
        imgitem = response.meta['imgitem']
        item = response.meta['item']
        if condition is not None:
            pName = response.xpath('//h1[@class="product-model__name"]/text()').extract_first()[:-2]
            if response.xpath('//h2[@class="product-model__alias"]/text()').extract_first() is not None:
                alias = response.xpath('//h2[@class="product-model__alias"]/text()').extract_first()
                item['phoneName'] = ','.join([pName, alias])
            else:
                item['phoneName'] = pName
            item['phoneID'] = self.itemcnt
            item['phoneBrand'] = response.xpath('//a[@id="_j_breadcrumb"]/text()').extract_first()[:-2]
            imgitem['imgPhone'] = ''
            imgitem['imgPhoneID'] = self.itemcnt
            imgitem['imgCate'] = []
            imgitem['imgUrls'] = {}
            self.itemcnt += 1

            node_list = response.xpath('//div[@class="detailed-parameters"]')
            paramdicts = {}
            infocategory = node_list.xpath('//td[@class = "hd"]/text()').extract()
            for j in range(1, len(node_list.xpath('//td[@class = "hd"]/text()').extract())+1):
                infotable = node_list.xpath('table[{}]'.format(str(j)))
                infoitemheader = []
                infoitemctnt = []

                # 增加字符串进一步过滤条件

                for i in range(1, len(infotable.xpath('tr'))+1):
                    if infotable.xpath('tr[{}]/th/span[@*]/text()'.format(str(i))).extract() != []:
                        # print(infotable.xpath('tr[{}]/th/span[@*]/text()'
                        #                     .format(str(i))).extract())
                        infoitemheader.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/th/span[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    elif infotable.xpath('tr[{}]/th/a[@*]/text()'.format(str(i))).extract() != []:
                        # print(infotable.xpath('tr[{}]/th/a[@*]/text()'
                        #                     .format(str(i))).extract())
                        infoitemheader.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/th/a[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    if infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() != [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() == []:
                        # print(','.join(infotable.xpath('tr[{}]/td/span[@*]/text()'
                        #                     .format(str(i))).extract()))
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/td/span[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').replace('\xa0x1', ',').strip())))
                    elif infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() == [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() != []:
                        # print(','.join(infotable.xpath('tr[{}]/td/span/a[@*]/text()'
                        #                     .format(str(i))).extract()))
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', ','
                                            .join(infotable.xpath('tr[{}]/td/span/a[@*]/text()'
                                            .format(str(i))).extract())
                                            .replace('，', ',').replace('>', '').replace('＞', '')
                                            .replace('\r\n', ',').strip())))
                    elif infotable.xpath('tr[{}]/td/span[@*]/text()'.format(str(i))).extract() != [] and \
                        infotable.xpath('tr[{}]/td/span/a[@*]/text()'.format(str(i))).extract() != []:
                        """ 去掉“更多XXX＞”，“手机性能排行>”，“进入官网>>>”，
                        “查看外观>”，“续航测试>”，“样张秀>”，“高清像素手机>”，“高像素自拍手机>”"""
                        infostr1 = ','.join(infotable.xpath('tr[{}]/td/span[@*]/text()'
                                            .format(str(i))).extract()).replace('，', ',')\
                                            .replace('>', '').replace('＞', '').replace('\r\n', '').strip()

                        infostr2 = ','.join(infotable.xpath('tr[{}]/td/span/a[@*]/text()'
                                    .format(str(i))).extract()).replace('，', ',').replace('手机性能排行', '')\
                                    .replace('样张秀', '').replace('进入官网', '').replace('查看外观', '')\
                                    .replace('高清像素手机', '').replace('高像素自拍手机', '')\
                                    .replace('续航测试', '').replace('>', '').replace('\r\n', ',').strip()
                        if '＞' in infostr2:
                            infostr2 = ''
                        # print(re.sub(r'^,', '', re.sub(r',{2,}', ',', infostr1+infostr2.strip())))
                        infoitemctnt.append(re.sub(r'^,', '', re.sub(r',{2,}', ',', infostr1+infostr2.strip())))

                    paramdicts[infocategory[j-1]] = dict(zip(infoitemheader, infoitemctnt))
            item['phoneParam'] = paramdicts

        # picture spider
        prefix = 'http://detail.zol.com.cn'

        urls = response.xpath('//div[@id="_j_tag_nav"]/ul')
        navitems = urls.xpath('li/a/text()').extract()
        try:
            picindex = navitems.index('图片')
            picurl = response.xpath('//*[@id="_j_tag_nav"]/ul/li[{}]/a'.format(str(picindex + 2)))

            suffix = picurl.xpath('@href').extract_first()
            if suffix is not None:
                picurl = prefix+str(suffix)
                # imgitem['imgUrls'] = {}
                # print(paramurl == 'http://detail.zol.com.cnhttp//detail.zol.com.cn')
                yield scrapy.Request(picurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.pic_parse_page, dont_filter=True)
        except Exception as e:
            try:
                newsindex = navitems.index('评测行情')
                newsurl = response.xpath('//*[@id="_j_tag_nav"]/ul/li[{}]/a'.format(str(newsindex + 2)))
                suffix = newsurl.xpath('@href').extract_first()
                if suffix is not None:
                    newsurl = prefix+str(suffix)
                    # imgitem['imgUrls'] = {}
                    # print(paramurl == 'http://detail.zol.com.cnhttp//detail.zol.com.cn')
                    yield scrapy.Request(newsurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                         callback=self.news_parse_page, dont_filter=True)
            except Exception as e2:
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.item_parse, dont_filter=True)

    def pic_parse_page(self, response):
        """准备爬取图片页"""

        prefix = 'http://detail.zol.com.cn'

        # 颜色页面种类：有两种分类的；仅有颜色分类；两者都没有
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        condition = response.xpath('//div[@class="product-model page-title clearfix"]/h1/text()').extract_first()
        # print(condition)
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
                # print(pageurl)
            except Exception as e:
                pageurl = prefix

            # 处理图片准备
            picdivide = {}
            tmpath = response.xpath('//div[@class="content"]')
            if tmpath.xpath('//a[@class="active"]') != []:
                if tmpath.xpath('//ul[@class="pics-category-list color-cate-list"]/li[1]/a/@href') != []:
                    url = prefix + tmpath.xpath('//ul[@class="pics-category-list color-cate-list"]/li[1]/a/@href')\
                                                .extract_first()
                    activeNum = 1
                    yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(pageurl),
                                                    'picdivide': copy.deepcopy(picdivide),
                                                    'activeNum': copy.deepcopy(activeNum),
                                                    'imgitem': copy.deepcopy(imgitem)},
                                         callback=self.pic_parse_following_page, dont_filter=True)
            elif tmpath.xpath('//ul[@class="pics-category-list color-cate-list"]/li[1]/a/@href') != []:
                url = prefix + tmpath.xpath('//li[1]/a/@href').extract_first()
                activeNum = 1
                yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(pageurl),
                                                'picdivide': copy.deepcopy(picdivide),
                                                'activeNum': copy.deepcopy(activeNum),
                                                'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.pic_parse_following_page, dont_filter=True)

            # 直接在当前页处理图片链接
            else:
                typeName = response.xpath('//div[@class="section-header"]/h3/text()').extract_first()
                link = response.xpath('//ul[@class="picture-list clearfix"]')
                links = link.xpath('li/a/@href').extract()
                pics = []
                for link in links:
                    pics.append(prefix + str(link))

                # 图片选取：没有分类的选前五张，不足五张选全部
                imgitem['imgPhoneID'] = item['phoneID']
                imgitem['imgPhone'] = str(item['phoneID']) + '_' + str(item['phoneName'][0])
                imgitem['imgCate'] = [str(typeName).strip()]
                if len(pics) >= 5:
                    imgitem['imgUrls'][str(typeName).strip()] = pics[:5]
                    item['phonePic'] = pics[:5]
                else:
                    imgitem['imgUrls'][str(typeName).strip()] = pics
                    item['phonePic'] = pics
                # 全部图片处理完了再抓新闻
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)
                                     , 'articleurl': copy.deepcopy(pageurl),
                                     'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.img_download_parse, dont_filter=True)

    def pic_parse_following_page(self, response):
        """爬取图片页颜色标签下每种颜色的前五张图片所在网址，不足五张则存所有网址链接"""

        prefix = 'http://detail.zol.com.cn'
        articleurl = response.meta['articleurl']
        wholecate = response.xpath('//div[@class="cate-item color-cate-item"]//li')
        # print(wholecate.xpath('a/text()').extract())
        colorNames = response.xpath('//ul[@class="pics-category-list color-cate-list"]/li/a/text()').extract()

        activeNum = response.meta['activeNum']
        for i in range(1, len(wholecate) + 1):
            if wholecate[i-1].xpath('a[@class="active"]') != []:
                activeNum = i
                break
        typeName = response.xpath('//div[@class="section-header"]/h3/text()').extract_first()
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        picdivide = response.meta['picdivide']

        # 只爬颜色分类图
        if typeName is not None:
            #print(item['phoneName'], typeName, colorNames)
            link = response.xpath('//ul[@class="picture-list clearfix"]')
            links = link.xpath('li/a/@href').extract()
            pics = []
            for link in links:
                pics.append(str(link))

            # 图片选取：没有分类的选前五张，不足五张选全部
            imgitem['imgPhoneID'] = item['phoneID']
            imgitem['imgPhone'] = str(item['phoneID']) + '_' + str(item['phoneName'][0])
            imgitem['imgCate'] = colorNames
            if len(pics) >= 5:
                imgitem['imgUrls'][str(typeName).strip()] = pics[:5]
                picdivide[str(typeName).strip()] = pics[:5]
            else:
                imgitem['imgUrls'][str(typeName).strip()] = pics
                picdivide[str(typeName).strip()] = pics
            item['phonePic'] = imgitem['imgUrls']
        if activeNum + 1 <= len(wholecate):
            url = prefix + wholecate[activeNum].xpath('a/@href').extract_first()
            yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(articleurl),
                                            'picdivide': copy.deepcopy(picdivide), 'imgitem': copy.deepcopy(imgitem),
                                            'activeNum': copy.deepcopy(activeNum)},
                                 callback=self.pic_parse_following_page, dont_filter=True)
        else:
            yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem),
                                                   'articleurl': copy.deepcopy(articleurl)},
                                 callback=self.img_download_parse, dont_filter=True)

    def news_parse_page(self, response):
        """爬取新闻、评测等信息"""
        prefix = 'http://detail.zol.com.cn'
        # 评测行情页面：可能的条目有“专业评测”，“热门新闻”
        item = response.meta['item']
        imgitem = response.meta['imgitem']
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
                        page = response.xpath('//div[@class="section-article"]')

                    else:
                        page = '<div id="' + nodeIds[i] + '">' + \
                               response.xpath('//div[@id="' + nodeIds[i] + '"]/textarea').extract_first()\
                            .replace('<textarea>', '').replace('</textarea>', '')
                        page = etree.HTML(page)
                        # print(response.xpath('//div[@id="' + nodeIds[i] + '"]/textarea').extract_first()\
                        #     .replace('<textarea>', '').replace('</textarea>', ''))
                        articleSet = page \
                            .xpath('//ul[@class="content-list"]/li[@class=" clearfix"]')
                        # print(etree.tostring(page).decode("GBK"))

                    articleNums[i] = len(articleSet)
                    # print(nodeIds[i], articleNums[i])
                    articleInfos = []
                    for j in range(1, articleNums[i] + 1):
                        if i == 0:
                            artRecord = {}
                            allInfo = page.xpath('//div[@id="' + nodeIds[i]
                                                 + '"]/ul/li[{}]'.format(str(j)))
                            # print(allInfo)
                            artRecord['articleID'] = j
                            artRecord['articleLink'] = allInfo.xpath('a/@href').extract_first()
                            artRecord['articleTitle'] = allInfo.xpath('div[@class="article-title"]/a/text()')\
                                .extract_first()
                            artRecord['articlePic'] = allInfo.xpath('//span[@class="img"]/img/@src').extract_first()\
                                                                    .replace('_200x150', '')
                            artRecord['articlePara'] = allInfo.xpath('p/text()').extract_first()
                            artRecord['articleDate'] = allInfo\
                                .xpath('div[@class="article-source clearfix"]/span[@class="article-date"]/text()')\
                                .extract_first()
                        else:
                            artRecord = {}
                            allInfo = page.xpath('//div[@id="' + nodeIds[i]
                                                 + '"]/ul/li[{}]'.format(str(j)))[0]
                            # print(allInfo)
                            artRecord['articleID'] = j
                            artRecord['articleLink'] = allInfo.xpath('a/@href')[0]
                            artRecord['articleTitle'] = allInfo.xpath('div[@class="article-title"]/a/text()')[0]
                            artRecord['articlePic'] = allInfo.xpath('//span[@class="img"]/img/@src')[0]\
                                                                    .replace('_200x150', '')
                            artRecord['articlePara'] = allInfo.xpath('p/text()')[0]
                            artRecord['articleDate'] = allInfo\
                                .xpath('div[@class="article-source clearfix"]/span[@class="article-date"]/text()')[0]

                        try:
                            artRecord['articleAuthor'] = allInfo.xpath\
                                ('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()')[0]\
                                + " " + allInfo \
                                .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()')[0]

                        except Exception as e:
                            artRecord['articleAuthor'] = 'Anonymous'
                        articleInfos.append(artRecord)

                    item[itemArtDic[nodeIds[i]]] = articleInfos

        yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                             callback=self.item_parse, dont_filter=True)

    def img_download_parse(self, response):
        """爬取图片名，准备下载图片"""
        prefix = prefix = 'http://detail.zol.com.cn'
        # 这个函数实现item和imgitem中每个图片链接都换成.jpg
        articleurl = response.meta['articleurl']
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        try:
            # 每个link调用一次response去搜该图片的jpg链接，返回来的图片是url，单张图片处理函数入口。
            yield SplashRequest(imgitem['imgUrls'][imgitem['imgCate'][0]][0],
                                meta={'imgitem': copy.deepcopy(imgitem), 'item': copy.deepcopy(item),
                                'i': copy.deepcopy(0), 'j': copy.deepcopy(0), 'articleurl': copy.deepcopy(articleurl)},
                                callback=self.single_pic_parse, dont_filter=True, args={'wait': 1})
        except Exception as e:
            if articleurl == prefix:
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.item_parse, dont_filter=True)
            else:
                yield scrapy.Request(url=articleurl, meta={'item': copy.deepcopy(item)
                                     , 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.news_parse_page, dont_filter=True)

    def single_pic_parse(self, response):
        """图片单页面处理"""
        prefix = 'http://detail.zol.com.cn'
        imgitem = response.meta['imgitem']
        item = response.meta['item']
        articleurl = response.meta['articleurl']
        i = int(response.meta['i'])
        j = int(response.meta['j'])
        totalj = len(imgitem['imgCate'])
        totali = len(imgitem['imgUrls'][imgitem['imgCate'][j]])
        i += 1

        # srcrapy-slpash 处理JS加载的页面
        picurl = str(response.xpath('//*[@id="j_Image"]/@src').extract_first())

        imgitem['imgUrls'][imgitem['imgCate'][j]][i-1] = picurl
        if i == totali:
            j += 1
            i = 0

        if j == totalj:
            item['phonePic'] = imgitem['imgUrls']
            if articleurl == prefix:
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.item_parse, dont_filter=True)
            else:
                yield scrapy.Request(url=articleurl, meta={'item': copy.deepcopy(item)
                                     , 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.news_parse_page, dont_filter=True)
        else:
            yield SplashRequest(imgitem['imgUrls'][imgitem['imgCate'][j]][i],
                                meta={'imgitem': copy.deepcopy(imgitem), 'item': copy.deepcopy(item),
                                'i': copy.deepcopy(i), 'j': copy.deepcopy(j), 'articleurl': copy.deepcopy(articleurl)},
                                callback=self.single_pic_parse, dont_filter=True, args={'wait': 1})

    def item_parse(self, response):
        """返回Item"""
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        for j in range(len(imgitem['imgCate'])):
            while 'None' in imgitem['imgUrls'][imgitem['imgCate'][j]]:
                imgitem['imgUrls'][imgitem['imgCate'][j]].remove('None')
        piclinks = []
        for j in range(len(imgitem['imgUrls'])):
            for link in imgitem['imgUrls'][imgitem['imgCate'][j]]:
                piclinks.append(link)
        item['phonePic'] = piclinks
        # print(item['phoneID'])
        yield item
        # print(item)

    def test_pic_parse(self, response):
        """检查图片下载问题"""
        print(response.url)
        print(response.body)
