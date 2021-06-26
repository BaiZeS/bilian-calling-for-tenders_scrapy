# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy

class SpiderZhaobiaoSpider(scrapy.Spider):
    name = 'spider_zhaobiao'
    allowed_domains = ['ebnew.com','ss.ebnew.com']
    
    #定义检索关键字
    keys = []

    #定义管道字典
    sql_data = dict(
        projectcode = '',  # 项目编号
        web = '',  # 信息来源网站
        keyword = '',  # 关键字
        detail_url = '',  # 招标详细页网址
        title = '',  # 第三方网站发布标题
        toptype = '',  # 信息类型
        province = '',  # 归属省份
        product = '',  # 产品范畴
        industry = '',  # 归属行业
        tendering_manner = '',  # 招标方式
        publicity_date = '',  # 招标公示日期
        expiry_date = '',  # 招标截止时间
    )

    #定义表单字典
    form_data = dict(
        infoClassCodes = '',
        rangeType = '',
        projectType	 = 'bid',
        fundSourceCodes = '',
        dateType = '',
        startDateCode = '',
        endDateCode = '',
        normIndustry = '',
        normIndustryName = '',
        zone = '',
        zoneName = '',
        zoneText = '',
        key = '',
        pubDateType = '',
        pubDateBegin = '',
        pubDateEnd = '',
        sortMethod = 'timeDesc',
        orgName = '',
        currentPage = '2',
    )

    #初始化
    def __init__(self):
        self.keys.append(input('请输入检索关键字：'))
        # print(self.keys)

    #定义并提交url
    def start_requests(self):
        # self.form_data['key'] = input('请输入检索关键词：')
        # self.form_data['currentPage'] = input('请输入检索页码：')
        self.form_data['key'] = self.keys

        request =  scrapy.FormRequest(
            url = 'http://ss.ebnew.com/tradingSearch/index.htm',
            formdata = self.form_data,
            callback = self.parse_start,
        )
        request.meta['form_data'] = self.form_data
        yield request
    
    #定义多线程爬取
    def parse_start(self,response):
        print('开始分配线程')
        page_num = response.xpath('//form[@id="pagerSubmitForm"]/a/text()').extract()
        page_max = max([int(page) for page in page_num if re.match('\d+',page)])
        # 测试模式
        print(page_max)
        # page_max = 2

        for i in range(1,page_max+1):
            form_data = deepcopy(response.meta['form_data'])
            form_data['currentPage'] = str(i)
            request = scrapy.FormRequest(
                url = 'http://ss.ebnew.com/tradingSearch/index.htm',
                formdata = form_data,
                callback = self.parse_1,
            )
            request.meta['form_data'] = form_data
            yield request
        # yield request

    #一级页面处理
    def parse_1(self,response):
        print('进入一级页面')
        info_s = response.xpath('//div[@class="ebnew-content-list"]/div')
        for info in info_s:
            #深copy存储数组
            parse_sql_data = deepcopy(self.sql_data)
            #提取需要的数据
            parse_sql_data['keyword'] = response.meta['form_data'].get('key') # 关键字
            parse_sql_data['detail_url'] = info.xpath('./div/a/@href').extract_first() # 招标详细页网址
            # parse_sql_data['web'] = '必联网'  # 信息来源网站
            parse_sql_data['web'] = response.url
            parse_sql_data['title'] = info.xpath('./div/a/text()').extract_first()  # 第三方网站发布标题
            parse_sql_data['toptype'] = info.xpath('./div[1]/i[1]/text()').extract_first()  # 信息类型
            parse_sql_data['province'] = info.xpath('./div[2]/div[2]/p[2]/span[@class="item-value"]/text()').extract_first()  # 归属省份
            parse_sql_data['product'] = info.xpath('./div[2]/div[1]/p[2]/span[@class="item-value"]/text()').extract_first()  # 产品范畴
            parse_sql_data['tendering_manner'] = info.xpath('./div[2]/div[1]/p[1]/span[@class="item-value"]/text()').extract()  # 招标方式
            parse_sql_data['publicity_date'] = re.sub(r'[^0-9\-]','',info.xpath('./div[1]/i[2]/text()').extract_first()) if info.xpath('./div[1]/i[2]/text()').extract_first() else '' # 招标公示日期
            parse_sql_data['expiry_date'] = info.xpath('./div[2]/div[2]/p[1]/span[@class="item-value"]/text()').extract_first()  # 招标截止时间
            # print(parse_sql_data)
            #构造request
            request = scrapy.Request(
                url = parse_sql_data['detail_url'],
                callback = self.parse_2,
            )
            request.meta['parse_sql_data'] = parse_sql_data
            #进入二级页面抓取数据
            yield request
    
    #二级页面出路
    def parse_2(self,response):
        print('进入二级页面')
        #获取存储数据
        parse_sql_data = response.meta['parse_sql_data']
        parse_sql_data['projectcode'] = response.xpath('//div[@class="position-relative"]//li[@id="bidcode"]/span[2]/text()').extract_first()  # 项目编号
        parse_sql_data['industry'] = response.xpath('//div[@class="position-relative"]/ul/li[8]/span[@class="item-value"]/text()').extract_first()  # 归属行业
        #筛选项目编号：
        if not parse_sql_data['projectcode']:
            projectcode = re.findall('(项目编码|项目标号|采购文件编号|招标编号|项目编号|竞价文件编号)[：:]{0,1}\s{0,2}\n*(</span\s*>)*\n*(<span.*?>)*\n*(<u*?>)*\n*([a-zA-Z0-9\-_\[\]]{1,100})',response.body.decode(response.encoding)) # 正文中筛选项目编号
            parse_sql_data['projectcode'] = projectcode[5]
        print(parse_sql_data['projectcode'])
        yield parse_sql_data