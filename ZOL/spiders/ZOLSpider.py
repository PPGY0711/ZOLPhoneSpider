# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import ZolItem
from ..items import imgItem
import copy
from lxml import etree
from scrapy_splash import SplashRequest
from scrapy_redis.spiders import RedisSpider


class ZolSpider(RedisSpider):
    """改用RedisSpider"""
    name = 'Zol'
    # offset = 1
    itemcnt = 4966
    # 非分布式爬虫设置start_urls
    #url = 'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'
    # start_urls = [url.format(str(offset))]
    # 分布式爬虫设置start_urls
    redis_key = 'Zol:start_urls'

    def parse(self, response):
        """分页面爬取一页所有的手机信息"""
        # first session
        prefix = 'http://detail.zol.com.cn'

        links = response.xpath('//div[@class="pic-box SP"]/a/@href').extract()
        boxs = response.xpath('//div[@class="pic-box SP"]')
        print("This page contains {} items".format(str(len(boxs))))
        for i in range(1, len(links) + 1):  # for test
            item = ZolItem()
            # 评分相关选项，默认值全为0
            item['phoneGrade'] = 0
            item['phoneCTimes'] = 0
            item['phoneEval'] = {}
            item['phoneNews'] = {}
            imgitem = imgItem()
            imgitem['imgUrls'] = {}
            # 处理商品缩略图
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
        urls = response.xpath('//*[@id="_j_tag_nav"]/ul/li')
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        suffix = ''
        for i in range(len(urls)):
            if urls[i].xpath('a/text()').extract_first() == '参数':
                suffix = urls[i].xpath('a/@href').extract_first()
                break
        if suffix != '':
            paramurl = prefix+str(suffix)
            item['phonePic'] = {}
            item['phoneID'] = self.itemcnt
            # imgitem['imgPhone'] = ''
            imgitem['imgPhoneID'] = self.itemcnt
            self.itemcnt += 1
            print("phoneID:{} --entering parameter parse".format(item['phoneID']))
            yield scrapy.Request(paramurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)}
                                 , callback=self.param_parse_page, dont_filter=True)
        else:
            print("phoneID:{} --entering item parse".format(item['phoneID']))
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
            item['phoneBrand'] = response.xpath('//a[@id="_j_breadcrumb"]/text()').extract_first()[:-2]
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
        urls = response.xpath('//*[@id="_j_tag_nav"]/ul/li')
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        suffix = ''
        for i in range(len(urls)):
            if urls[i].xpath('a/text()').extract_first() == '图片':
                suffix = urls[i].xpath('a/@href').extract_first()
                break
        if suffix != '':
            picurl = prefix + str(suffix)
            print("phoneID:{0} phoneName:{1} --entering picture parse".format(item['phoneID'], item['phoneName']))
            yield scrapy.Request(picurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                 callback=self.pic_parse_page, dont_filter=True)
        else:
            suffix = ''
            for i in range(len(urls)):
                if urls[i].xpath('a/text()').extract_first() == '评测行情':
                    suffix = urls[i].xpath('a/@href').extract_first()
                    break
            if suffix != '':
                newsurl = prefix+str(suffix)
                print("phoneID:{0} phoneName:{1} --entering news parse".format(item['phoneID'], item['phoneName']))
                yield scrapy.Request(newsurl, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.news_parse_page, dont_filter=True)
            else:
                print("phoneID:{0} phoneName:{1} --entering item parse".format(item['phoneID'], item['phoneName']))
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
            urls = response.xpath('//*[@id="_j_tag_nav"]/ul/li')
            item = response.meta['item']
            imgitem = response.meta['imgitem']
            suffix = ''
            for i in range(len(urls)):
                if urls[i].xpath('a/text()').extract_first() == '评测行情':
                    suffix = urls[i].xpath('a/@href').extract_first()
                    break
            if suffix != '':
                pageurl = prefix + str(suffix)
            else:
                pageurl = prefix

            # 处理图片准备
            picdivide = {}

            tmpath = response.xpath('//div[@class="wrapper clearfix"]/div[@class="content"]')
            if tmpath.xpath('//div[@class="pics-category"]') != [] and \
                response.xpath('//div[@class="section-header"]/h3/text()').extract_first() != '产品图片 ':
                if tmpath.xpath('//div[@class="cate-item color-cate-item"]') != []:
                    url = prefix + tmpath.xpath('//ul[@class="pics-category-list color-cate-list"]/li[1]/a/@href')\
                                                .extract_first()
                    activeNum = 1
                    # print(url)
                    print("phoneID:{0} phoneName:{1} --entering pic following parse".format(item['phoneID'],
                                                                                            item['phoneName']))
                    # picType 记录图片分类：0表示颜色分类；1表示类型分类
                    yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(pageurl),
                                                    'picdivide': copy.deepcopy(picdivide),
                                                    'activeNum': copy.deepcopy(activeNum),
                                                    'imgitem': copy.deepcopy(imgitem), 'picType': copy.deepcopy(0)},
                                         callback=self.pic_parse_following_page, dont_filter=True)

                elif tmpath.xpath('//div[@class="cate-item"]') != []:
                    url = prefix + tmpath.xpath('//ul[@class="pics-category-list"]/li[2]/a/@href').extract_first()
                    activeNum = 0
                    # print(url)
                    print("phoneID:{0} phoneName:{1} --entering pic following parse".format(item['phoneID'],
                                                                                            item['phoneName']))
                    yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(pageurl),
                                                    'picdivide': copy.deepcopy(picdivide),
                                                    'activeNum': copy.deepcopy(activeNum),
                                                    'imgitem': copy.deepcopy(imgitem), 'picType': copy.deepcopy(1)},
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
                if len(pics) >= 5:
                    imgitem['imgUrls'][str(typeName).strip()] = pics[:5]
                    item['phonePic'] = pics[:5]
                else:
                    imgitem['imgUrls'][str(typeName).strip()] = pics
                    item['phonePic'] = pics
                # 全部图片处理完了再抓新闻
                # print(imgitem['imgUrls'])
                print("phoneID:{0} phoneName:{1} --entering pic download parse".format(item['phoneID'],
                                                                                        item['phoneName']))
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item)
                                     , 'articleurl': copy.deepcopy(pageurl),
                                     'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.img_download_parse, dont_filter=True)

    def pic_parse_following_page(self, response):
        """爬取图片页颜色标签下每种颜色的前五张图片所在网址，不足五张则存所有网址链接"""
        prefix = 'http://detail.zol.com.cn'
        articleurl = response.meta['articleurl']
        picType = response.meta['picType']
        if picType == 0:
            wholecate = response.xpath('//div[@class="cate-item color-cate-item"]//li')
            # print(wholecate.xpath('a/text()').extract())
            cateNames = response.xpath('//ul[@class="pics-category-list color-cate-list"]/li/a/text()').extract()
        else:
            wholecate = response.xpath('//div[@class="cate-item"]//li')[1:]
            # print(wholecate.xpath('a/text()').extract())
            cateNames = response.xpath('//ul[@class="pics-category-list"]/li/a/text()').extract()[1:]
        activeNum = response.meta['activeNum']
        for i in range(1, len(wholecate) + 1):
            if wholecate[i-1].xpath('a[@class="active"]') != []:
                activeNum = i
                break
        typeName = response.xpath('//div[@class="section-header"]/h3/text()').extract_first()
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        picdivide = response.meta['picdivide']

        # 两种图片分类都有时，只爬颜色分类图；只有一种类型时爬该类型分类（只有类型时依旧不爬全部图片）
        # 有一种例外，当分类只有颜色时，底下可能显示的仍是“产品图片，此时取href得到的url不完整，这种情况在前一个函数处理
        if typeName is not None:
            link = response.xpath('//ul[@class="picture-list clearfix"]')
            links = link.xpath('li/a/@href').extract()
            pics = []
            for link in links:
                pics.append(str(link))

            # 图片选取：没有分类的选前五张，不足五张选全部
            imgitem['imgPhoneID'] = item['phoneID']
            if len(pics) >= 5:
                imgitem['imgUrls'][str(typeName).strip()] = pics[:5]
                picdivide[str(typeName).strip()] = pics[:5]
            else:
                imgitem['imgUrls'][str(typeName).strip()] = pics
                picdivide[str(typeName).strip()] = pics
            item['phonePic'] = imgitem['imgUrls']
        if activeNum + 1 <= len(wholecate):
            url = prefix + wholecate[activeNum].xpath('a/@href').extract_first()
            # print(url)
            print("phoneID:{0} phoneName:{1} --entering pic following parse".format(item['phoneID'],
                                                                                   item['phoneName']))
            yield scrapy.Request(url, meta={'item': copy.deepcopy(item), 'articleurl': copy.deepcopy(articleurl),
                                            'picdivide': copy.deepcopy(picdivide), 'imgitem': copy.deepcopy(imgitem),
                                            'activeNum': copy.deepcopy(activeNum), 'picType': copy.deepcopy(picType)},
                                 callback=self.pic_parse_following_page, dont_filter=True)
        else:
            print("phoneID:{0} phoneName:{1} --entering pic download parse".format(item['phoneID'],
                                                                                   item['phoneName']))
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
                            if allInfo.xpath\
                                        ('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()') \
                                    == [] or allInfo \
                                    .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()') \
                                    == []:
                                artRecord['articleAuthor'] = 'Anonymous'
                            else:
                                artRecord['articleAuthor'] = allInfo.xpath\
                                        ('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()')\
                                        .extract_first() + allInfo \
                                        .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()')\
                                        .extract_first()
                            articleInfos.append(artRecord)

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
                            if allInfo.xpath\
                               ('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()') \
                               == [] or allInfo \
                               .xpath('div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()')\
                               == []:
                                artRecord['articleAuthor'] = 'Anonymous'
                            else:
                                artRecord['articleAuthor'] = allInfo.xpath \
                                    ('div[@class="article-source clearfix"]/div[@class="article-author"]/span/text()') \
                                    .extract_first() + allInfo \
                                    .xpath(
                                    'div[@class="article-source clearfix"]/div[@class="article-author"]/a/text()') \
                                    .extract_first()
                            articleInfos.append(artRecord)

                    item[itemArtDic[nodeIds[i]]] = articleInfos
        print("phoneID:{0} phoneName:{1} --entering item parse".format(item['phoneID'], item['phoneName']))
        yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                             callback=self.item_parse, dont_filter=True)

    def img_download_parse(self, response):
        """爬取图片名，准备下载图片"""
        prefix = 'http://detail.zol.com.cn'
        # 这个函数实现item和imgitem中每个图片链接都换成.jpg
        articleurl = response.meta['articleurl']
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        if imgitem['imgUrls'] != {}:
            print(item['phoneName'], imgitem['imgUrls'])
            # 每个link调用一次response去搜该图片的jpg链接，返回来的图片是url，单张图片处理函数入口。
            cate = []
            for key in imgitem['imgUrls'].keys():
                cate.append(key)
            url = imgitem['imgUrls'][cate[0]][0]
            if url[0] == '/':
                url = prefix + url
            yield SplashRequest(url,
                                meta={'imgitem': copy.deepcopy(imgitem), 'item': copy.deepcopy(item),
                                      'cate': copy.deepcopy(cate), 'i': copy.deepcopy(0), 'j': copy.deepcopy(0),
                                      'articleurl': copy.deepcopy(articleurl)},
                                callback=self.single_pic_parse, dont_filter=True,
                                args={'wait': 0.5, 'url': url, 'http_method': 'GET'})
        else:
            if articleurl == prefix:
                print("phoneID:{0} phoneName:{1} --entering item parse".format(item['phoneID'], item['phoneName']))
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.item_parse, dont_filter=True)
            else:
                print("phoneID:{0} phoneName:{1} --entering news parse".format(item['phoneID'], item['phoneName']))
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
        cate = response.meta['cate']
        totalj = len(cate)
        totali = len(imgitem['imgUrls'][cate[j]])
        i += 1

        # srcrapy-slpash 处理JS加载的页面
        picurl = str(response.xpath('//*[@id="j_Image"]/@src').extract_first())

        imgitem['imgUrls'][cate[j]][i-1] = picurl
        if i == totali:
            j += 1
            i = 0

        if j == totalj:
            item['phonePic'] = imgitem['imgUrls']
            if articleurl == prefix:
                print("phoneID:{0} phoneName:{1} --entering item parse".format(item['phoneID'], item['phoneName']))
                yield scrapy.Request(url=prefix, meta={'item': copy.deepcopy(item), 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.item_parse, dont_filter=True)
            else:
                print("phoneID:{0} phoneName:{1}--entering news parse".format(item['phoneID'], item['phoneName']))
                yield scrapy.Request(url=articleurl, meta={'item': copy.deepcopy(item)
                                     , 'imgitem': copy.deepcopy(imgitem)},
                                     callback=self.news_parse_page, dont_filter=True)
        else:
            if imgitem['imgUrls'][cate[j]][i][0] == '/':
                imgitem['imgUrls'][cate[j]][i] = prefix + imgitem['imgUrls'][cate[j]][i]
            yield SplashRequest(imgitem['imgUrls'][cate[j]][i],
                                meta={'imgitem': copy.deepcopy(imgitem), 'item': copy.deepcopy(item),
                                      'cate': copy.deepcopy(cate), 'i': copy.deepcopy(i), 'j': copy.deepcopy(j),
                                      'articleurl': copy.deepcopy(articleurl)},
                                callback=self.single_pic_parse, dont_filter=True,
                                args={'wait': 0.5, 'url': imgitem['imgUrls'][cate[j]][i],
                                      'http_method': 'GET'})

    def item_parse(self, response):
        """返回Item"""
        item = response.meta['item']
        imgitem = response.meta['imgitem']
        cate = []
        for key in imgitem['imgUrls']:
            cate.append(key)
        for j in range(len(cate)):
            while 'None' in imgitem['imgUrls'][cate[j]]:
                imgitem['imgUrls'][cate[j]].remove('None')
        piclinks = []
        for j in range(len(imgitem['imgUrls'])):
            for link in imgitem['imgUrls'][cate[j]]:
                piclinks.append(link)
        item['phonePic'] = piclinks
        # print(item['phoneID'])
        yield item
        # print(item)

    def test_pic_parse(self, response):
        """检查图片下载问题"""
        print(response.url)
        print(response.body)
