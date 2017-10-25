# cnca
#此爬虫为聚焦爬虫
#主要抓取认证认可业务统一查询平台。获取公司的证书信息！


执行爬虫操作：
1.
执行文件在bin目录下

insert_url.py
这个文件用来插入需要抓取的公司信息。将公司名 构造成 org_list 列表。
执行插入
2.进入虚拟环境，运行爬虫 python start_spider,必须先插入需要抓取的url，否则爬虫运行之后
会阻塞等待，无法继续！
3.在redis中 lpush键值为 cnca:start_urls 起始url.

LPUSH cnca:start_urls 'http://cx.cnca.cn/rjwcx/web/cert/publicCert.do?progId=10&org='


4.抓取的数据缓存在redis中。

[可以在管道中自定义存储到那个地方。]







页面分析记录：


http://cx.cnca.cn/rjwcx/web/cert/index.do?url=web/cert/show3C.do%3F


rzjgId=01   --> "rzjgId":"CNCA-R-2002-001",
&
certNo=00114E22766R2L/3502  --> "certNumber":"00114E22766R2L/3502",
&
checkC=719613713   --->  "checkC":719613713,




         "certNumber":"00114E22766R2L/3502",
            "orgName":"漳州灿坤实业有限公司",
            "rzjgId":"CNCA-R-2002-001",
            "authProjCode":"A020101",
            "certiEDate":"2017-12-01",
            "certiStatus":"01",
            "zersda":"20170103",
            "showtemp":"1",
            "rzjgIdName":"中国质量认证中心",
            "authProjCodeName":"环境管理体系认证",
            "certiStatusName":"有效",
            "checkC":719613713,
            "row":1


            "certNumber":"00216Q10097R1S",
            "orgName":"山东泓达生物科技有限公司",
            "rzjgId":"CNCA-R-2002-002",
            "authProjCode":"A010101",
            "certiEDate":"2018-09-15",
            "certiStatus":"01",
            "zersda":"20160115",
            "showtemp":"1",
            "rzjgIdName":"方圆标志认证集团有限公司",
            "authProjCodeName":"质量管理体系认证（ISO9000）",
            "certiStatusName":"有效",
            "checkC":-1506848832,
            "row":1
        },




orgName:漳州灿坤实业有限公司
orgCode:739547709
method:queryCertByOrg
needCheck:false
checkC:2468144422
randomCheckCode:7
queryType:public
page:1
rows:10
checkCode:


orgName:漳州灿坤实业有限公司
orgCode:000000000
method:queryCertByOrg
needCheck:false
checkC:1247458372
randomCheckCode:7
queryType:public
page:1
rows:10
checkCode:




http://cx.cnca.cn/rjwcx/web/cert/publicCert.do?progId=10&title=%E8%AE%A4%E8%AF%81%E7%BB%93%E6%9E%9C%0A%09%20%20%20%20%20%20%20%20

//img[@id="checkCodeImg"]/@src  验证码连接


1.搜索公司 PSOT
http://cx.cnca.cn/rjwcx/web/cert/queryOrg.do?progId=10

query str:
progId:10

Form Data:
certNumber:
orgName:山东泓达生物科技有限公司
queryType:public
checkCode:12        验证码：采用识别或者打码平台.

返回这个数据：
{
    "data":[
        {
            "orgCode":"760038087",
            "orgName":"山东泓达生物科技有限公司",
            "orgDistrictName":"",
            "checkC":"1190348542",
            "randomCheckCode":"12"
        },
        {
            "orgCode":"91371323760038087M",
            "orgName":"山东泓达生物科技有限公司",
            "orgDistrictName":"",
            "checkC":"1506768922",
            "randomCheckCode":"12"
        }
    ],
    "msg":"",
    "success":true
}


data 为空说明这个公司没有证书,直接 return 进行下一个请求
"success":false   验证码错误
----------------------------------完成这一步，已获取到组织列表》


2.点击公司后：POST
http://cx.cnca.cn/rjwcx/web/cert/list.do?progId=10

query str:
progId:10

Form Data:
orgName:山东泓达生物科技有限公司    公司名：
orgCode:760038087                机构代码：orgCode 在刚进来的请求中有
method:queryCertByOrg
needCheck:false
checkC:1190348542                    checkC :
randomCheckCode:12                   randomCheckCode  都在刚进来的那个json数据中有
queryType:public
page:1
rows:10
checkCode:


Rasponse:请求返回

 			"certNumber":"10416Q20770R1S",
            "orgName":"山东泓达生物科技有限公司",
            "rzjgId":"CNCA-R-2003-104",
            "authProjCode":"A010101",
            "certiEDate":"2018-09-15",
            "certiStatus":"01",
            "zersda":"20170616",
            "showtemp":"1",
            "rzjgIdName":"山东世通质量认证有限公司",
            "authProjCodeName":"质量管理体系认证（ISO9000）",
            "certiStatusName":"有效",
            "checkC":186916677,
            "row":1





3.点击证书：进入到证书页面的时候：
get请求：

请求证书的url; 分析网页js得到，不同类型证书的请求url

function getCertDetailUrl(certNo,rzjgId,showtemp,checkC){
	var url = "";
	if (showtemp == "1")  {                   // 服务体系认证
		url = url+"super/cert/superShow.do?rzjgId=" + rzjgId + "&certNo="
		+ certNo  + "&checkC=" + checkC;
	}
	if (showtemp == "2") { // 3C强制性认证
		 url = url+"super/cert/superShow3C.do?rzjgId=" + rzjgId + "&certNo="
				+ certNo  + "&checkC=" + checkC;
	}
	if (showtemp == "3")   {                  // 农食认证
		 url = url+"super/cert/superShowNs.do?rzjgId=" + rzjgId + "&certNo="
				+ certNo  + "&checkC=" + checkC;
	}
	if (showtemp == "4") {                  // 自愿性工业产品
		 url = url+"super/cert/superShowZyxGy.do?rzjgId=" + rzjgId + "&certNo="
				+ certNo  + "&checkC=" + checkC;
	}
	return url;
}


不同类型的证书url对比：
http://cx.cnca.cn/rjwcx/web/cert/show3C.do?rzjgId=01&certNo=2009010702358369&checkC=523111559
http://cx.cnca.cn/rjwcx/web/cert/showNs.do?rzjgId=CNCA-R-2002-002&certNo=002FSMS1300012&checkC=1033651830
http://cx.cnca.cn/rjwcx/web/cert/showNs.do?rzjgId=CNCA-R-2002-002&certNo=002FSMS1300012&checkC=1033651570
http://cx.cnca.cn/rjwcx/web/cert/showNs.do?rzjgId=CNCA-R-2002-002&certNo=002FSMS1300012&checkC=1033652090


证书页面：
http://cx.cnca.cn/rjwcx/web/cert/

querystr:

rzjgId=CNCA-R-2002-002
certNo=002FSMS1300012
checkC=1033651830





解析数据：
showtemp:1

//table[@id="cert_info"]//tr

//table[@id="org_info"]//tr

//table[@class="datagrid-btable"]//tr


showtemp：3 农药认证
直接请求内嵌页面返回500错误
可能是被反爬
解决：先请求外层页面，拿到请求头后再，请求内层页面。




http://cx.cnca.cn/rjwcx/web/cert/index.do?url=web/cert/showNs.do%3FrzjgId=CNCA-R-2002-002%26certNo=002FSMS1300012%26checkC=1033651765



['丹阳特瑞莱电子有限公司',"山东泓达生物科技有限公司",'扬州三开电器有限公司']