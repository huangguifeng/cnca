# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ShowTempOneItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 服务体系认证 showtemp:1
    cert_num = scrapy.Field()#证书编号
    cert_status = scrapy.Field() #证书状态
    pub_data = scrapy.Field()#颁证日期
    end_data = scrapy.Field()#证书到期日期
    first_data = scrapy.Field()#初次获证日期
    info_pub  = scrapy.Field()#信息上报日期
    cert_program = scrapy.Field()#认证项目
    cert_according = scrapy.Field()#认证依据
    supervise = scrapy.Field()#监督次数
    echo_num = scrapy.Field() #再次认证次数
    cert_work = scrapy.Field() #业务范围
    paramcover_place = scrapy.Field()#是否覆盖多场所
    cert_addr = scrapy.Field() #认证覆盖的场所名称及地址
    cert_mark= scrapy.Field()   #证书使用的认可标识

    org_name = scrapy.Field()#组织名称
    org_code = scrapy.Field()#组织代码
    org_addr = scrapy.Field()#组织地址
    org_people= scrapy.Field()#本证书体系覆盖人数

    cert_history = scrapy.Field() # 证书变化历史轨迹
    showtemp = scrapy.Field()    #　证书的类型
    crawl_data = scrapy.Field() #　爬取时间

class ShowTempTwoItem(scrapy.Item):
    '''3c证书　showtemp:2'''
    cert_num = scrapy.Field()#证书编号
    cert_status = scrapy.Field() #证书状态
    pub_data = scrapy.Field()#颁证日期
    end_data = scrapy.Field()#证书到期日期
    first_data = scrapy.Field()#初次获证日期
    info_pub = scrapy.Field()  # 信息上报日期
    according = scrapy.Field()#认证依据
    product_type = scrapy.Field() #产品类别
    master_product_name = scrapy.Field() #主产品名称
    product_name = scrapy.Field() #次产品名称
    model = scrapy.Field() #规格型号

    consigner_name = scrapy.Field() #组织名称
    consigner_code = scrapy.Field() #组织机构代码
    consigner_area = scrapy.Field()#所在国别地区
    consigner_addr = scrapy.Field()#组织地址

    producer_name = scrapy.Field() #组织名称
    producer_code =  scrapy.Field() #组织机构代码
    producer_area = scrapy.Field()#所在国别地区
    producer_addr = scrapy.Field()#组织地址

    manu_name = scrapy.Field() #组织名称
    manu_code = scrapy.Field() #组织机构代码
    manu_area= scrapy.Field()#所在国别地区
    manu_addr = scrapy.Field()#组织地址

    showtemp = scrapy.Field()
    crawl_data = scrapy.Field()

class ShowTempThreeItem(scrapy.Item):
    '''
    农业类证书　showtemp:3
    '''
    cert_num = scrapy.Field()#证书编号
    cert_status = scrapy.Field() #证书状态
    pub_data = scrapy.Field()#颁证日期
    end_data = scrapy.Field()#证书到期日期
    first_data = scrapy.Field()#初次获证日期
    info_pub = scrapy.Field()  # 信息上报日期
    cert_program = scrapy.Field()  # 认证项目

    cert_mark = scrapy.Field()  # 证书使用的认可标识
    personnel_num = scrapy.Field()  # 认证相关员工数量
    cert_work = scrapy.Field()#认证范围
    according = scrapy.Field()#认证依据
    cert_addr = scrapy.Field()  # 认证覆盖的场所名称及地址

    org_name = scrapy.Field()#组织名称
    org_code = scrapy.Field()#组织代码
    org_addr = scrapy.Field()#组织地址

    product_info = scrapy.Field() #　产品类别

    showtemp = scrapy.Field()
    crawl_data = scrapy.Field()

class ShowTempFourItem(scrapy.Item):

    cert_num = scrapy.Field()#证书编号
    cert_status = scrapy.Field() #证书状态
    pub_data = scrapy.Field()#颁证日期
    end_data = scrapy.Field()#证书到期日期
    info_pub = scrapy.Field()  # 信息上报日期
    cert_program = scrapy.Field()  # 认证项目
    cert_mark = scrapy.Field()  # 证书使用的认可标识
    cert_according = scrapy.Field()  # 认证依据
    product_name = scrapy.Field()  # 产品名称
    model = scrapy.Field()  # 规格型号

    consigner_name = scrapy.Field() #组织名称
    consigner_addr = scrapy.Field()#组织地址

    producer_name = scrapy.Field() #组织名称
    producer_addr = scrapy.Field()#组织地址

    manu_name = scrapy.Field() #组织名称
    manu_addr = scrapy.Field()#组织地址

    showtemp = scrapy.Field()
    crawl_data = scrapy.Field()
