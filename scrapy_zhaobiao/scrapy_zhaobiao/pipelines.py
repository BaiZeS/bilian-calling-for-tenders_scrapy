# -*- coding: utf-8 -*-
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyZhaobiaoPipeline(object):
    def __init__(self):
        #初始化数据库
        self.mysql_conn = pymysql.Connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            password = input('请输入Sql数据库密码：'),
            database = 'scrapy_db',
            charset = 'utf8'
        )
    
    def process_item(self, item, spider):
        #创建光标对象
        cs = self.mysql_conn.cursor()
        # print(cs)
        #将传入的字典转换成字符串
        sql_key = ','.join([key for key in item.keys()])
        sql_val = ','.join(['"%s"' % item[key] for key in item.keys()])
        #构建数据库插入语句
        sql_str = 'insert into zhaobiao_tb (%s) value (%s);' % (sql_key,sql_val)
        #写入数据库
        cs.execute(sql_str)
        self.mysql_conn.commit()
        #打印调试
        print('success!')
        return item
