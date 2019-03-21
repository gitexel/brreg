# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    company = scrapy.Field()
    Address = scrapy.Field()
    announcement = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    branch = scrapy.Field()
