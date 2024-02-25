# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WangspiderItem(scrapy.Item):
    head = scrapy.Field()
    url = scrapy.Field()
    imgUrl = scrapy.Field()
    tag = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    pass