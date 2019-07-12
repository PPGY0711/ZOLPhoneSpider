# -*- coding: utf-8 -*-
from scrapy import cmdline
import redis
# import time
# import os
# from multiprocessing import  Process,Pool  # Python多进程，用于动态添加start_urls

conn = redis.Redis(host='127.0.0.1', port=6379, password='123456')
for i in range(105):
    conn.lpush('Zol:start_urls',
               'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'.format(str(i)))
    # 每隔8分钟插入一条start_url
    # time.sleep(480)
cmdline.execute("scrapy crawl Zol".split())
