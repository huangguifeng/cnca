#!/usr/bin/env python2
# -*- coding=utf-8 -*-
'''
将需要爬取的公司加入到redis缓存库中
'''

import redis


def main():

    base_url = 'http://cx.cnca.cn/rjwcx/web/cert/publicCert.do?progId=10&org='
    org_list = [u'丹阳特瑞莱电子有限公司',u'漳州灿坤实业有限公司',u"山东泓达生物科技有限公司",
                u'扬州三开电器有限公司',u'广东有信无限股份有限公司',u"江苏传智博客有限公司"]
    url_list = (base_url+org for org in org_list)
    redis_client = redis.Redis(host="127.0.0.1", port=6379)

    for url in url_list:
        redis_client.lpush("start_urls",url)
        print '[INFO]:'+ url
    print '[INFO]:' + u'数据加入完成,可以执行爬虫!'
if __name__ == "__main__":
    main()






