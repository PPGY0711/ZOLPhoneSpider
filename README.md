# ZOLphoneSpider

使用scrapy开发的ZOL爬虫，爬取ZOL热门手机板块的手机信息。

## 运行环境

开发语言：Python3
系统：Windows/MacOS/Linux
依赖库：scrapy/scrapy-splash/lxml
服务：Docker 18.09.2
数据库：MongoDB

## 数据结构

手机信息表 phoneList

| 数据项   | 字段名      | 属性          | 数据类型 | 备注                                                         |
| -------- | ----------- | ------------- | -------- | ------------------------------------------------------------ |
| 记录编号 | _id         | Primary   key | ObjectId | MongoDB为文档生成的唯一主键                                  |
| 手机编号 | phoneID     | Not   null    | Int      | 记录手机项数                                                 |
| 手机品牌 | phoneBrand  | Not   null    | String   | 保存手机品牌信息   可能为子品牌                              |
| 手机名称 | phoneName   | Not   null    | String   | 保存手机名称   可能有别名                                    |
| 展示图片 | phoneIcon   | Not   null    | String   | 保存产品展示图片链接                                         |
| 手机参数 | phoneParam  |               | Dict     | 保存手机详细参数   key、value均为String                      |
| 手机图片 | phonePic    |               | Dict     | 保存手机图片链接   key为String   value为List                 |
| 评测文章 | phoneEval   |               | List     | 保存手机评测文章信息   列表项为Dict，包含文章ID、Author、Link、Title、Theme Picture、Abstract、Date |
| 热门新闻 | phoneNews   |               | List     | 保存手机热门新闻信息   列表项为Dict，包含文章ID、Author、Link、Title、Theme Picture、Abstract、Date |
| 手机评分 | phoneGrade  | Not Null      | Double   | 记录手机评分（0-5）                                          |
| 评分人数 | phoneCTimes | Not Null      | Int      | 记录已为该手机打分人数                                       |

## 使用说明
针对ZOL（中关村在线）热门手机板块开发的scrapy爬虫，由scrapy-splash提供JS渲染服务。
由test.py提供爬虫入口，而非命令行输入scrapy crawl 'SpiderName' 运行。
