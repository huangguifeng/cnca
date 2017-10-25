# -*- coding: utf-8 -*-
import re
import time
import json
import redis
import urllib
import scrapy
import subprocess
from scrapy_redis.spiders import RedisSpider
from toredis import insert_start_url
from AuthCnca.items  import ShowTempOneItem,ShowTempThreeItem,ShowTempTwoItem,ShowTempFourItem
class CncaSpider(RedisSpider):
    name = "cnca"
    allowed_domains = ["cx.cnca.cn"]
    base_url = 'http://cx.cnca.cn/rjwcx/web/cert/publicCert.do?progId=10'
    search_url = 'http://cx.cnca.cn/rjwcx/web/cert/queryOrg.do?progId=10'
    cert_url = 'http://cx.cnca.cn/rjwcx/web/cert/list.do?progId=10'
    # start_urls = [base_url]
    redis_key = 'cnca:start_urls'

    def parse(self, response):
        '''请求验证码'''
        url = response.url
        url = urllib.unquote(url).decode('utf-8')
        re_com = re.compile(r'http://cx\.cnca\.cn/rjwcx/web/cert/publicCert\.do\?progId=10&org=(.*)')
        self.org = re_com.findall(url)[0]
        # 验证码url
        captcha_url ='http://cx.cnca.cn/rjwcx/checkCode/rand.do?d=%s'%str(int(time.time()*1000))

        yield scrapy.Request(url=captcha_url,callback=self.org_list)

    def org_list(self,response):

        '''请求组织列表数据'''

        checkcode = self.parse_captcha(response)

        From_data = {
            'certNumber':"",
            'orgName':self.org,
            'queryType':'public',
            'checkCode':'%s'%checkcode
        }
        yield scrapy.FormRequest(url=self.search_url, formdata=From_data, callback=self.parse_org)

    def parse_org(self, response):
        '''获取到组织列表,发送列表里的每个公司请求，获取到证书'''
        # todo: 这里获取到组织列表json数据

        try:



            org_json = response.body
            org_dict = json.loads(org_json)
            org_list = org_dict["data"]

            if not org_dict['success']:
                self.parse(response)
                return
            # todo:利用延迟加入start_urls，在第一个请求验证码通过后再发送，让两个验证码请求错开
            insert_start_url()

            if not org_list:
                #如果搜索数据空，表示该公司没有认证证书
                print u'搜索结果为空:\t'+ self.org
                return

            for org in org_list:
                Form_Data ={
                    'orgName':org["orgName"],
                    'orgCode':org["orgCode"],
                    'method':'queryCertByOrg ',
                    'needCheck':'false',
                    'checkC':org["checkC"],
                    'randomCheckCode':org["randomCheckCode"],
                    'page': '1',
                    'rows': '10',
                }
                # 获取单个组织的证书数据请求
                yield scrapy.FormRequest(url=self.cert_url,
                                         formdata=Form_Data,
                                         callback=self.parse_cert,
                                         )
        except Exception as e:
            print '[INFO]:',e

    def parse_cert(self,response):
        '''
        获取到证书列表
        '''
        cert_json = response.body
        cert_dict = json.loads(cert_json)

        # 有4中不同的证书,需要分别构造不同的请求，
        if not cert_dict["success"]:
            return
        cert_list = cert_dict["rows"]
        for node in cert_list:
            # 调用request_cert_url　返回证书url,继续请求。
            url = self.request_cert_url(node)
            showtemp = node["showtemp"]

            if showtemp == '3':
                #　类型为3的直接请求返回服务器错误，单独处理这个 农食认证
                f_url = 'http://cx.cnca.cn/rjwcx/web/cert/index.do?url=web/cert/showNs.do?'

                querystr = 'rzjgId' + node["rzjgId"] + '&certNo=' + node["certNumber"] + \
                           '&checkC=' + str(node["checkC"])

                yield scrapy.Request(url=f_url+querystr,meta={'url':url,'showtemp':showtemp},
                                     callback=self.request_ns)

            yield scrapy.Request(url=url,meta={"showtemp":showtemp},callback=self.parse_cert_data)

    def request_ns(self,response):
        '''showtemp 为3的直接请求返回服务器错误 这里请求内层网页'''
        url = response.meta['url']
        yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_cert_data)

    def request_cert_url(self,node):

        '''构造证书url'''
        cert_result_url= 'http://cx.cnca.cn/rjwcx/web/cert/'

        # 查询字符串
        # print node["rzjgId"]
        # print node["certNumber"]
        # print node["checkC"]
        querystr = "?rzjgId=" + node["rzjgId"] + '&certNo=' + node["certNumber"] + '&checkC=' + str(node["checkC"])
        url = ""
        # 服务体系认证
        if node["showtemp"] == "1":
            url = cert_result_url + "show.do"+  querystr
        # 3C强制性认证
        if node["showtemp"] == "2":
            url = cert_result_url + "show3C.do" + querystr

        # 农食认证
        if node["showtemp"] == "3":
            url = cert_result_url + "showNs.do" + querystr

        # 自愿性工业产品
        if node["showtemp"] == "4":
            url = cert_result_url + "showZyxGy.do" + querystr

        return url

    def parse_cert_data(self,response):
        # 获取showtemp编号，用来判断是那一类型的证书
        showtemp = response.meta['showtemp']
        # 写到这里获取到showtemp：1 证书页面数据了

        if showtemp == '1':
           yield self.insert_one_item(response,showtemp)

        if showtemp == '2':
            yield self.insert_two_item(response,showtemp)

        if showtemp == '3':
            #农业类型的证书
            yield self.insert_three_item(response,showtemp)

        if showtemp == '4':
            yield self.insert_four_item(response,showtemp)

    def insert_one_item(self,response,showtemp):
        item = ShowTempOneItem()
        # 证书信息
        cert_info = response.xpath('//table[@id="cert_info"]//tr')

        item['cert_num'] = cert_info[0].xpath('.//td/text()')[1:2].extract()
        item['cert_status'] = cert_info[0].xpath('.//td/text()')[3:4].extract()

        item['pub_data'] = cert_info[1].xpath('.//td/text()')[1:2].extract()
        item['end_data'] = cert_info[1].xpath('.//td/text()')[3:4].extract()

        item['first_data'] = cert_info[2].xpath('.//td/text()')[1:2].extract()
        item['info_pub'] = cert_info[2].xpath('.//td/text()')[3:4].extract()

        item['cert_program'] = cert_info[3].xpath('.//td/text()')[1:2].extract()
        item['cert_according'] = cert_info[3].xpath('.//td/text()')[3:4].extract()

        item['supervise'] = cert_info[4].xpath('.//td/text()')[1:2].extract()
        item['echo_num'] = cert_info[4].xpath('.//td/text()')[3:4].extract()

        item['cert_work'] = cert_info[5].xpath('.//td/text()')[1:2].extract()
        item['paramcover_place'] = cert_info[6].xpath('.//td/text()')[1:2].extract()

        item['cert_addr'] = cert_info[7].xpath('.//td/text()')[1:2].extract()
        item['cert_mark'] = cert_info[8].xpath('.//td/text()')[1:2].extract()

        # 获证组织基本信息
        org_info = response.xpath('//table[@id="org_info"]//tr')
        item['org_name'] = org_info[0].xpath('.//td/text()')[1:2].extract()
        item['org_code'] = org_info[0].xpath('.//td/text()')[3:4].extract()
        item['org_people'] = org_info[1].xpath('.//td/text()')[3:4].extract()
        item['org_addr'] = org_info[2].xpath('.//td/text()')[1:2].extract()

        # 证书变化历史轨迹
        cert_history = response.xpath('//table[@id="cert_history"]//tbody/tr')
        cert_his = []
        for node in cert_history:
            items = {}
            try:
                td = node.xpath('.//td')
                recp = re.compile(r'<.*?>')
                items['activity'] = recp.sub("", td[1:2].extract())
                items['describe'] = recp.sub("", td[2:3].extract())
                items['activeDate'] = recp.sub("", td[3:4].extract())
                items['checkGroup'] = recp.sub("", td[4:5].extract())
            except:
                pass
            cert_his.append(items)
        item['cert_history'] = cert_his
        item['showtemp'] = showtemp

        return item

    def insert_two_item(self,response,showtemp):

        cert_info = response.xpath('//table[@id="cert_info"]//tr')
        item = ShowTempTwoItem()

        item['cert_num'] = cert_info[0].xpath('.//td/text()')[1:2].extract()
        item['cert_status'] = cert_info[0].xpath('.//td/text()')[3:4].extract()
        item['pub_data'] = cert_info[1].xpath('.//td/text()')[1:2].extract()
        item['end_data'] = cert_info[1].xpath('.//td/text()')[3:4].extract()
        item['first_data'] = cert_info[2].xpath('.//td/text()')[1:2].extract()
        item['info_pub'] = cert_info[2].xpath('.//td/text()')[3:4].extract()
        item['according'] = cert_info[3].xpath('.//td/text()')[1:2].extract()
        item['product_type'] = cert_info[4].xpath('.//td/text()')[1:2].extract()
        item['master_product_name'] = cert_info[5].xpath('.//td/text()')[1:2].extract()
        item['product_name'] = cert_info[6].xpath('.//td/text()')[1:2].extract()
        item['model'] = cert_info[7].xpath('.//td/text()')[1:2].extract()

        app_info = response.xpath('//table[@id = "app_info"]//tr')

        item['consigner_name'] = app_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['consigner_code'] = app_info[0].xpath('.//td/text()')[3:4].extract()  # 组织机构代码
        item['consigner_area'] = app_info[1].xpath('.//td/text()')[1:2].extract()  # 所在国别地区
        item['consigner_addr'] = app_info[1].xpath('.//td/text()')[3:4].extract()  # 组织地址

        producer_info = response.xpath('//table[@id="manu_info"]//tr')
        item['producer_name'] = producer_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['producer_code'] = producer_info[0].xpath('.//td/text()')[3:4].extract()  # 组织机构代码
        item['producer_area'] = producer_info[1].xpath('.//td/text()')[1:2].extract()  # 所在国别地区
        item['producer_addr'] = producer_info[1].xpath('.//td/text()')[3:4].extract()  # 组织地址

        fac_info = response.xpath('//table[@id="fac_info"]//tr')
        item['manu_name'] = fac_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['manu_code'] = fac_info[0].xpath('.//td/text()')[3:4].extract()  # 组织机构代码
        item['manu_area'] = fac_info[1].xpath('.//td/text()')[1:2].extract()  # 所在国别地区
        item['manu_addr'] = fac_info[1].xpath('.//td/text()')[3:4].extract()  # 组织地址
        item['showtemp'] = showtemp
        return item

    def insert_three_item(self,response,showtemp):

        item = ShowTempThreeItem()

        # 证书信息
        cert_info = response.xpath('//table[@id="cert_info"]//tr')
        item['cert_num'] = cert_info[0].xpath('.//td/text()')[1:2].extract()
        item['cert_status'] = cert_info[0].xpath('.//td/text()')[3:4].extract()
        item['pub_data'] = cert_info[1].xpath('.//td/text()')[1:2].extract()
        item['end_data'] = cert_info[1].xpath('.//td/text()')[3:4].extract()
        item['first_data'] = cert_info[2].xpath('.//td/text()')[1:2].extract()
        item['info_pub'] = cert_info[2].xpath('.//td/text()')[3:4].extract()
        item['cert_program'] = cert_info[3].xpath('.//td/text()')[1:2].extract()
        item['cert_mark'] = cert_info[4].xpath('.//td/text()')[1:2].extract()
        item['personnel_num'] = cert_info[4].xpath('.//td/text()')[3:4].extract()
        item['cert_work'] = cert_info[6].xpath('.//td//textarea/text()')[0:1].extract()
        item['according'] = cert_info[7].xpath('.//td/text()')[1:2].extract()
        try:
            item['cert_addr'] = cert_info[8].xpath('.//td/text()')[1:2].extract()
        except:
            item['cert_addr'] = ""
        # 组织机构
        org_info = response.xpath('//table[@id="app_info"]//tr')

        item['org_name'] = org_info[0].xpath('.//td/text()')[1:2].extract()
        item['org_code'] = org_info[0].xpath('.//td/text()')[3:4].extract()
        item['org_addr'] = org_info[2].xpath('.//td/text()')[1:2].extract()

        # 产品信息
        prod_info = response.xpath('//table[@id="prod_info"]//tr')[1:]
        prod_list = []
        for node in prod_info:
            items = {}
            items['product_type'] = node.xpath('.//td/text()')[0:1].extract()  # 产品类别
            items['product_name'] = node.xpath('.//td/text()')[1:2].extract()  # 产品名称
            items['product_addr'] = node.xpath('.//td/text()')[2:3].extract()  # 生产地址
            items['product_turnout'] = node.xpath('.//td/text()')[3:4].extract()  # 产量
            items['product_output'] = node.xpath('.//td/text()')[4:5].extract()  # 年产值
            prod_list.append(items)
        item['product_info']  =prod_list
        item['showtemp'] = showtemp
        return item

    def insert_four_item(self,response,showtemp):
        item= ShowTempFourItem()
        cert_info = response.xpath('//table[@id="cert_info"]//tr')
        item['cert_num'] = cert_info[0].xpath('.//td/text()')[1:2].extract()
        item['cert_status'] = cert_info[0].xpath('.//td/text()')[3:4].extract()
        item['pub_data'] = cert_info[1].xpath('.//td/text()')[1:2].extract()
        item['end_data'] = cert_info[1].xpath('.//td/text()')[3:4].extract()
        item['info_pub'] = cert_info[2].xpath('.//td/text()')[1:2].extract()
        item['cert_program'] = cert_info[3].xpath('.//td/text()')[1:2].extract() # 认证项目
        item['cert_mark'] = cert_info[3].xpath('.//td/text()')[3:4].extract()  # 证书使用的认可标识
        item['cert_according'] = cert_info[4].xpath('.//td/text()')[1:2].extract()  # 认证依据
        item['product_name'] = cert_info[5].xpath('.//td/text()')[1:2].extract()  # 产品名称
        item['model'] = cert_info[6].xpath('.//td/text()')[1:2].extract()  # 规格型号

        app_info = response.xpath('//table[@id = "app_info"]//tr')

        item['consigner_name'] = app_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['consigner_addr'] = app_info[0].xpath('.//td/text()')[3:4].extract()  # 组织地址

        producer_info = response.xpath('//table[@id="manu_info"]//tr')
        item['producer_name'] = producer_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['producer_addr'] = producer_info[0].xpath('.//td/text()')[3:4].extract()  # 组织地址

        fac_info = response.xpath('//table[@id="fac_info"]//tr')
        item['manu_name'] = fac_info[0].xpath('.//td/text()')[1:2].extract()  # 组织名称
        item['manu_addr'] = fac_info[0].xpath('.//td/text()')[3:4].extract()  #
        item['showtemp'] = showtemp
        return item

    def parse_captcha(self,response):
        '''将请求回来的验证码进行处理'''

        filename = 'captcha.jpg'
        with open(filename, "w") as f:
            f.write(response.body)
        # 调用tesseract-orc识别验证吗，返回验证码计算结果
        captcha = self.tesseract(filename)
        return captcha

    def tesseract(self,filePath):
        '''调用系统的tesseract命令, 对图片进行OCR中文识别
            fontyp 为针对这次爬虫训练的字体库
        '''

        subprocess.call(["tesseract", "-l", "fontyp",'-psm', '7', filePath, 'output'])

        with open("output.txt", 'r') as f:
            text = f.read().strip(" ").decode('utf-8')
        try:
            # 　去掉验证码中的空格
            text = re.sub(r' ', "", text)

            dnum_list = [u'零', u'壹', u'貳', u'叁', u'肆',
                         u'伍',u'陆',u'柒',u'捌',u'玖']

            one = text[0:1]  # 第一个数字
            two = text[2:3]  # 第二个数字
            sign = text[1:2]  # 运算符
            print one,two

            # 计算验证码结果，中文数字，利用列表的下标转成数字计算.
            # 运算符识别不是100%准确，所有加了几个经常错误识别的符号做容错处理
            if sign == '+' or sign == u'十':
                return dnum_list.index(one) + dnum_list.index(two)
            if sign == 'x' or sign == 'X':
                return dnum_list.index(one)*dnum_list.index(two)
            if sign == '-' or sign == '－' or sign == '`':
                return dnum_list.index(one) - dnum_list.index(two)
        except Exception as e:
            print e
