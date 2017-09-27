# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Com163Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ThreadItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    content_html = scrapy.Field()
    pub_date = scrapy.Field()
    update_time = scrapy.Field()
    tags = scrapy.Field()
    source = scrapy.Field()
    channel = scrapy.Field()
