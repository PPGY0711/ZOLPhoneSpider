# -*- coding: utf-8 -*-
from scrapy import cmdline
import redis
import time
from multiprocessing import Process  # Python多进程，用于动态添加start_urls


def process_url(wTime):
    conn = redis.Redis(host='127.0.0.1', port=6379, password='123456')
    for i in range(1, 105):
        print('ready to crawl No.{} main page: '.format(str(i)) +
              'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'.format(str(i)))
        conn.lpush('Zol:start_urls',
                   'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'.format(str(i)))
        # 每隔5分钟插入一条start_url
        time.sleep(wTime)


if __name__ == '__main__':
    p = Process(target=process_url, args=(300,))
    p.daemon = True  # 加入daemon
    p.start()
    print('Main Process: Scrapy crawl Zol')
    cmdline.execute("scrapy crawl Zol".split())




