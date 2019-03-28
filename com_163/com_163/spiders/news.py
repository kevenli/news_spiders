# -*- coding: utf-8 -*-
import scrapy
from ..items import ThreadItem
import time, datetime
import six
import logging
from scrapy.linkextractors import LinkExtractor
from scrapy.link import Link
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from dateutil.parser import *
from ..exceptions import PageParseException

logger = logging.getLogger(__name__)

def required_fields_check(func):
    def wraper(*args):
        item = func(*args)
        if 'title' not in item:
            raise PageParseException('No titie found')

        if 'content' not in item:
            raise PageParseException('No content found')


        return item
    return wraper

class PubdateProcessor(object):
    def __call__(self, values):
        for value in values:
            date_extracted = parse(value, fuzzy=True)
            if date_extracted is not None:
                return value

class NewsSpider(scrapy.Spider):
    name = 'news'
    allowed_domains = [
        'news.163.com',
        'money.163.com',
        'tech.163.com',
        'daxue.163.com',
        'ent.163.com',
        'sports.163.com',
        'auto.163.com',
        'lady.163.com',
        'war.163.com',
    ]
    start_urls = [
        'http://tech.163.com/',
        'http://news.163.com/rank/',
        'http://news.163.com/',
        'http://ent.163.com/',
        'http://war.163.com/',
        'http://money.163.com/',
    ]

    link_extractor = LinkExtractor()

    def extract_links(self, response):
        for sel in response.xpath('//a'):
            title = sel.xpath('text()').extract_first()
            link = sel.xpath('@href').extract_first()
            if link is None or link == "#":
                continue

            if link.startswith('javascript'):
                continue

            link = six.moves.urllib.parse.urljoin(response.url, link)
            url, fragment = six.moves.urllib.parse.urldefrag(link)
            link_obj = Link(url =url, text=title, fragment=fragment)
            yield link_obj

    def parse(self, response):
        for link in self.extract_links(response):
            request = scrapy.Request(link.url, callback=self.parse_content_page)
            yield request

    def parse_content_page(self, response):
        for link in self.extract_links(response):
            request = scrapy.Request(link.url, callback=self.parse_content_page)
            yield request

        parsers = [#self.content_parse,
                   self.content_parse2,
                   #self.content_parse3,
                   self.content_parse4,
                   self.content_parse5,
                   self.content_parse6,
                ]

        parsed_item = None
        for parse in parsers:
            try:
                parsed_item = parse(response)
                parsed_item['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                parsed_item['source'] = u'网易新闻'
                yield parsed_item
                break
            except PageParseException as e:
                pass

        if parsed_item is None:
            logger.warning('Page %s cannot be parsed' % response.url)

    # example http://ent.163.com/17/0927/03/CVAFCKCO00038FO9.html
    @required_fields_check
    def content_parse2(self, response):
        l = ItemLoader(item=ThreadItem(), response=response)
        l.default_output_processor = TakeFirst()
        l.add_xpath('title', '//div[@class="post_content_main"]/h1/text()')
        l.add_xpath('content', '//div[@class="post_text"]')
        l.add_xpath('pub_date', '//div[@class="post_time_source"]/text()', PubdateProcessor())
        l.add_value('url', response.url)
        l.add_xpath('channel', '//div[@class="post_crumb"]/a[1]/text()')
        return l.load_item()

    # # http://news.163.com/photoview/00AN0001/2276586.html
    # @required_fields_check
    # def content_parse3(self, response):
    #     l = ItemLoader(item=ThreadItem(), response=response)
    #     l.default_output_processor = TakeFirst()
    #     l.add_xpath('title', '//div[@class="post_content_main"]/h1/text()')
    #     l.add_xpath('content', '//textarea[@name="gallery-data"]')
    #     l.add_value('url',  response.url)  # you can also use literal values
    #     l.add_xpath('pub_date', '//headline/span/text()', PubdateProcessor())
    #     return l.load_item()

    # http://caozhi.news.163.com/17/0926/13/CV8VL2V4000181TI.html
    @required_fields_check
    def content_parse4(self, response):
        l = ItemLoader(item=ThreadItem(), response=response)
        l.default_output_processor = TakeFirst()
        l.add_xpath('title', '//div[@class="brief"]/h1/text()')
        l.add_xpath('content', '//div[@class="endText"]')
        l.add_xpath('pub_date', '//div[@class="pub_time"]/text()', PubdateProcessor())
        l.add_value('url',  response.url)
        return l.load_item()


    # http://war.163.com/photoview/4T8E0001/2276650.html
    @required_fields_check
    def content_parse5(self, response):
        l = ItemLoader(item=ThreadItem(), response=response)
        l.default_output_processor = TakeFirst()
        l.add_xpath('title', '//div[@class="headline"]/h1/text()')
        l.add_xpath('content', '//textarea[@name="gallery-data"]/text()')
        l.add_xpath('pub_date', '//div[@class="headline"]/span/text()', PubdateProcessor())
        l.add_value('url', response.url)
        l.add_xpath('channel', '//div[@class="nav-left"]/a[2]/text()')
        return l.load_item()


    # http://daxue.163.com/16/0128/14/BEE1U9K7009163JD.html
    @required_fields_check
    def content_parse6(self, response):
        l = ItemLoader(item=ThreadItem(), response=response)
        l.default_output_processor = TakeFirst()
        l.add_xpath('title', '//h1[@id="h1title"]/text()')
        l.add_xpath('content', '//div[@id="endText"]')
        l.add_xpath('pub_date', '//div[@class="ep-time-soure cDGray"]/text()', PubdateProcessor())
        l.add_value('url', response.url)
        l.add_xpath('channel', '//span[@class="ep-crumb JS_NTES_LOG_FE"]/a[1]/text()')
        return l.load_item()