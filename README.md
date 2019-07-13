# ZOLphoneSpider
使用scrapy开发的ZOL爬虫，爬取ZOL热门手机板块的手机信息。    

## 运行环境

- 开发语言：Python3  
- 系统：Windows/MacOS/Linux  
- 依赖库：scrapy/scrapy-splash/scrapy-redis/lxml/docker  
- 服务：Docker 18.09.2(实验环境为Windows10，所安装的是Docker for Windows，其他系统请自行解决）  
- 数据库：MongoDB  

## 数据结构

**手机信息表 phoneList**

| 数据项   | 字段名      | 属性          | 数据类型 | 备注                                                         |
| -------- | ----------- | ------------- | -------- | ------------------------------------------------------------ |
| 记录编号 | _id         | Primary   key | ObjectId | MongoDB为文档生成的唯一主键                                  |
| 手机编号 | phoneID     | Not   null    | Int      | 记录手机项数                                                 |
| 手机品牌 | phoneBrand  | Not   null    | String   | 保存手机品牌信息   可能为子品牌                              |
| 手机名称 | phoneName   | Not   null    | String   | 保存手机名称   可能有别名                                    |
| 展示图片 | phoneIcon   | Not   null    | String   | 保存产品展示图片链接                                         |
| 手机参数 | phoneParam  |               | Dict     | 保存手机详细参数   key、value均为String                      |
| 手机图片 | phonePic    |               | LISt     | 保存手机图片链接                 |
| 评测文章 | phoneEval   |               | List     | 保存手机评测文章信息   列表项为Dict，包含文章ID、Author、Link、Title、Theme Picture、Abstract、Date |
| 热门新闻 | phoneNews   |               | List     | 保存手机热门新闻信息   列表项为Dict，包含文章ID、Author、Link、Title、Theme Picture、Abstract、Date |
| 手机评分 | phoneGrade  | Not Null      | Double   | 记录手机评分（0-5）                                          |
| 评分人数 | phoneCTimes | Not Null      | Int      | 记录已为该手机打分人数                                       |

## 使用说明
针对ZOL（中关村在线）热门手机板块开发的scrapy爬虫，由scrapy-splash提供JS渲染服务。  
由test.py提供爬虫入口，而非命令行输入scrapy crawl 'SpiderName' 运行。  
引入scrapy-redis主要是为了减少爬取过程中item的损失，但也可以单机使用分布式爬取。  
  
## 分布式爬虫用法实现
**1.运行前安装并配置以下环境**
- Python3
- Scrapy
- Scrapy-splash
- MongoDB
- redis
- Docker

**2.打开MongoDB和redis服务**  
**3.下载并解压，把文件名改为ZOLSpider**  
**4.打开多个cmd，把路径都切换到ZOLSpider目录下，输入 scrapy crawl Zol --nolog**  
```
e.g.  
C:\Users\Administrator>D:  

D:\>cd D:\Scrapy\ZOL  

D:\Scrapy\ZOL>scrapy crawl Zol --nolog
```
**5.打开cmd，把路径切换到redis目录下，开启redis客户端（如果redis设置过password，需要先认证）**  
```

C:\Users>d:

D:\>cd redis

D:\Redis>redis-cli -h 127.0.0.1 -p 6379

127.0.0.1:6379> LPUSH Zol:start_urls http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_1.html
```
**6.在终端中可看见爬取过程，数据存储在MangoDB的tbdb库的taobao表中（存储位置可在pipelines.py中修改）**  
**7.程序结束后，清除redis中的缓存**  
```
127.0.0.1:6379> flushdb
```

## IDE运行
**1.实验环境：Pycharm 2019.1.3**  
**2.Python多进程实现连接redis、mongoDB数据库，DockerClient实现操作Docker服务**  
**3.如要改动redis、mongoDB连接信息，在settings.py中修改对应设置**  
```
#for redis connection
REDIS_URL = None  # 一般情况可以省去
REDIS_HOST = '127.0.0.1'  # 也可以根据情况改成 localhost
REDIS_PORT = 6379
REDIS_PARAMS = {
    'password': '123456'
}

for mongoDB connection
MONGO_HOST = '118.25.188.238'
MONGO_PORT = 27017
MONGO_DB = 'phoneYelp'
MONGO_COLL = 'phoneList'
MONGO_USER = 'phoneYelp_rw'
MONGO_PSW = '123456'
```