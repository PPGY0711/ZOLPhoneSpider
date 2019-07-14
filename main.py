# -*- coding: utf-8 -*-
from scrapy import cmdline
import redis
import time
from multiprocessing import Process  # Python多进程，用于动态添加start_urls
import docker  # 管理docker容器，防止爬虫处理过程中splash对js渲染页面请求过多导致的连接终止


def process_url(wTime):
    """动态添加start_urls"""
    conn = redis.Redis(host='127.0.0.1', port=6379, password='123456')
    for i in range(1, 201):
        print('ready to crawl No.{} main page: '.format(str(i)) +
              'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'.format(str(i)))
        # 当前最热门手机
        # conn.lpush('Zol:start_urls',
        #            'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_{}.html'.format(str(i)))
        # 历史最热门手机
        conn.lpush('Zol:start_urls',
                   'http://detail.zol.com.cn/history/subcate57_0_1_0_0_{}.html'.format(str(i)))
        # 每隔8分钟插入一条start_url
        time.sleep(wTime)


def control_docker():
    """Docker进程，每24mins重新运行Splash容器"""
    client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
    container_id = client.containers.run(image='scrapinghub/splash', ports={8050: 8050}, detach=True)
    for i in range(1, 45):
        print("scrapinghub/splash ready to start.")
        time.sleep(1440)
        print(container_id.logs())
        print("scrapinghub/splash ready to restart.")
        container_id.restart()
    container_id.kill()


if __name__ == '__main__':
    p1 = Process(target=process_url, args=(480,))
    p1.daemon = True  # 加入daemon
    p1.start()

    p2 = Process(target=control_docker)
    p2.daemon = True
    p2.start()

    print('Main Process: Scrapy crawl Zol --nolog')
    cmdline.execute("scrapy crawl Zol".split())

"""
所有热门手机开始url(1-104):'http://detail.zol.com.cn/cell_phone_index/subcate57_0_list_1_0_1_1_0_1.html'
历史热门手机开始url(1-200):'http://detail.zol.com.cn/history/subcate57_0_1_0_0_1.html'
"""