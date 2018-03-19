# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from mv import settings
import pymysql

class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        yield scrapy.Request(item['image_url'])

    def item_completed(self, results, item, info):
        image_url = [x['path'] for ok, x in results if ok]

        if not image_url:
            raise DropItem("Item contains no images")

        item['image_url'] = image_url
        return item



# 用于数据库存储
class DBPipeline(object):
    def __init__(self):
        # 连接数据库
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=3306,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor();

    def process_item(self, item, spider):
        try:
            # 查重处理
            self.cursor.execute(
                """select * from mv where img_url = %s""",
                item['img_url'])
            # 是否有重复数据
            repetition = self.cursor.fetchone()

            # 重复
            if repetition:
                pass

            else:
                # 插入数据
                self.cursor.execute(
                    """insert into mv(name, info, rating, num ,quote, img_url)
                    value (%s, %s, %s, %s, %s, %s)""",
                    (item['name'],
                     item['info'],
                     item['rating'],
                     item['num'],
                     item['quote'],
                     item['img_url']))

            # 提交sql语句
            self.connect.commit()

        except Exception as error:
            # 出现错误时打印错误日志
            print('cuole')
        return item