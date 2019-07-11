from scrapy.utils.project import get_project_settings
import random

settings = get_project_settings()

class ProcessHeaderMidware():
    """随机生成请求头"""

    def process_request(self, request, spider):
        """从列表中随机获取header，并传给user_agent进行使用"""
        ua = random.choice(settings.get('USER_AGENT_LIST'))
        spider.logger.info(msg='now entring download midware')
        if ua:
            request.headers['User-Agent'] = ua
            spider.logger.info(u'User-Agent is : {} {}'.format(request.headers.get('User-Agent'), request))
        pass
